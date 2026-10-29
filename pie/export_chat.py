"""Chat and plain-text export layer, built on pie.export.build()'s output (export/README.md "Chat export").

Trainer-neutral: each chat example is {"messages": [{"role", "content"}, ...], "meta": {...}} with no
model-specific template, so Tinker (or any SFT trainer) applies the model's own renderer. The plain-text
files are for LM loss on the language itself.

Kinds (meta.task):
  task conversations   translate_en_pie, translate_pie_en, gloss, inflect, paradigm, cognates_to_pie:
                       one user prompt (several paraphrased templates, chosen deterministically) and the
                       task's exact output as the assistant turn, so a scorer can compare it directly
  pie_dialogue         PIE-only conversations from the dialogue genres, split into turns (meta.split:
                       "speaker" where the plan's clauses carry one, else "sentence_qa")
  continuation         the opening of a hymn, story or charm in PIE; the assistant continues it
  en_dialogue          the same dialogues with English user input (meta.mode): en_pie (English user, PIE
                       replies), en_pie_gloss (PIE reply + "English: ..." line), mixed (the user switches
                       between English and PIE, the replies are PIE); one mode per record, chosen by crc32.
                       Needs a sentence-by-sentence English alignment (align_english)
  demo_chat            the hand-written demo seeds (data/export/demo_seeds.jsonl): English questions answered
                       with an existing training sentence or an engine form of a lexicon (or neologism) entry

Conversational eval: the dialogue records frozen in data/export/held_dialogues.json leave train in
pie.export.build() (eval_dialogue_records) and become eval conversations in every mode (meta.chat_eval).

Hold-out: nothing here re-splits. Each example inherits its split from build(): tasks from
train_tasks/eval_tasks, texts from train_records/eval_records. A paradigm goes to the split its lexeme's
inflection tasks went to (the same held-family and project-reconstruction decisions), so it never needs its
own predicate. The leakage check (leakage_report) fails the export when an eval item reappears in train.
"""

from __future__ import annotations

import collections
import json
import random
import re
import sys
import unicodedata
import zlib
from pathlib import Path

DIALOGUE_GENRES = ("dialogue", "greeting", "challenge", "parley", "council", "farewell", "riddle")
CONTINUATION_GENRES = {"hymn": "hymn", "prayer": "prayer", "praise": "hymn of praise", "charm": "charm",
                       "healing": "healing charm", "myth": "story", "fable": "fable", "tale": "story",
                       "narrative": "story", "epic": "epic story", "parable": "parable"}
EN_MODES = ("en_pie", "en_pie_gloss", "mixed")     # English-input modes; mixed needs two user turns
HELD_DIALOGUES = Path(__file__).resolve().parent.parent / "data/export/held_dialogues.json"
DEMO_SEEDS = Path(__file__).resolve().parent.parent / "data/export/demo_seeds.jsonl"
NEOLOGISM_CAP = 0.15           # PLAN.md Tier 3b: 10-15% of training tokens
NGRAM = 4

# ---------------------------------------------------------------- templates


def _pick(key: str, n: int) -> int:
    """A deterministic choice (crc32, not hash(): str hashes are salted per process)."""
    return zlib.crc32(key.encode("utf-8")) % n


TASK_SYSTEM = [
    "You are an expert in reconstructed Proto-Indo-European (PIE).",
    "You are a historical linguist specializing in Proto-Indo-European.",
    "You know Proto-Indo-European (PIE) grammar, vocabulary and reconstruction well. Answer precisely.",
]

PIE_ONLY_SYSTEM = [
    "Answer only in Proto-Indo-European. Do not use English.",
    "You speak Proto-Indo-European. Reply only in PIE.",
    "Converse in reconstructed Proto-Indo-European only; every reply must be in PIE.",
]

CONTINUATION_SYSTEM = [
    "Continue the Proto-Indo-European text the user begins. Write only in PIE.",
    "You compose in Proto-Indo-European. Carry on the text you are given, in PIE only.",
]

BILINGUAL_SYSTEM = ("The user writes in English. Reply in Proto-Indo-European, then give an English translation "
                    "of your reply on its own line beginning \"English:\".")
EN_PIE_SYSTEM = "Reply in Proto-Indo-European."
MIXED_SYSTEM = "The user may write in English or in Proto-Indo-European. Always reply in Proto-Indo-European."
MODE_SYSTEM = {"en_pie": EN_PIE_SYSTEM, "en_pie_gloss": BILINGUAL_SYSTEM, "mixed": MIXED_SYSTEM}

TASK_TEMPLATES = {
    "translate_en_pie": [
        "Translate into Proto-Indo-European:\n\n{x}",
        "How would you say this in PIE?\n\n{x}",
        "Render this in reconstructed Proto-Indo-European: {x}",
        "Give me the PIE for: \"{x}\"",
        "Put this into Proto-Indo-European, please.\n\n{x}",
    ],
    "translate_pie_en": [
        "Translate this Proto-Indo-European into English:\n\n{x}",
        "What does this PIE mean?\n\n{x}",
        "English translation, please: {x}",
        "Translate from PIE: \"{x}\"",
        "Here is a line of reconstructed Proto-Indo-European. What does it say in English?\n\n{x}",
    ],
    "gloss": [
        "Gloss this PIE text morpheme by morpheme (Leipzig style):\n\n{x}",
        "Give an interlinear gloss of: {x}",
        "Write a word-by-word grammatical gloss for this Proto-Indo-European:\n\n{x}",
        "Analyze each word of this PIE line in Leipzig glossing notation: {x}",
    ],
    "inflect": [
        "What is the {long} of PIE *{lemma}?",
        "Inflect *{lemma} for {tag}.",
        "Give the {tag} form of the Proto-Indo-European word *{lemma}.",
        "PIE *{lemma}: {long}?",
        "Form the {long} ({tag}) of *{lemma}.",
    ],
    "paradigm": [
        "{verb} *{lemma}{what}.",
        "Give the paradigm of PIE *{lemma}{what}.",
        "Write out the forms of the Proto-Indo-European *{lemma}{what}, one cell per line.",
        "List the {what_plain} of *{lemma}.",
    ],
    "cognates_to_pie": [
        "These words are cognates: {x}. What Proto-Indo-European form do they continue?",
        "Reconstruct the PIE ancestor of: {x}",
        "From which PIE word do these descend? {x}",
        "Cognate set: {x}. Give the PIE reconstruction.",
    ],
}

CONTINUATION_TEMPLATES = [
    "{x}",
    "Continue this {genre}:\n\n{x}",
    "Here is the beginning of a PIE {genre}. Go on with it.\n\n{x}",
    "{x}\n\n(continue)",
]

BILINGUAL_TEMPLATES = [
    "{x}\n\n(Please answer in Proto-Indo-European.)",
    "Answer me in PIE: {x}",
    "Reply in reconstructed Proto-Indo-European. {x}",
]

FEATURE_WORDS = {
    "NOM": "nominative", "VOC": "vocative", "ACC": "accusative", "GEN": "genitive", "ABL": "ablative",
    "DAT": "dative", "LOC": "locative", "INS": "instrumental", "SG": "singular", "DU": "dual", "PL": "plural",
    "PRS": "present", "PST": "past (imperfect)", "AOR": "aorist", "PRF": "perfect", "FUT": "future",
    "IND": "indicative", "IMP": "imperative", "SBJV": "subjunctive", "OPT": "optative",
    "ACT": "active", "MID": "middle", "PTCP": "participle", "M": "masculine", "F": "feminine", "N": "neuter",
}
PERSON = {"1": "first person", "2": "second person", "3": "third person"}


def describe_features(tag: str) -> str:
    """PRS.3SG -> 'present third person singular'; F.NOM.SG -> 'feminine nominative singular'. Unknown
    parts are kept as written."""
    words = []
    for part in tag.split("."):
        m = re.fullmatch(r"([123])(SG|DU|PL)", part)
        if m:
            words += [PERSON[m[1]], FEATURE_WORDS[m[2]]]
        else:
            words.append(FEATURE_WORDS.get(part, part))
    return " ".join(words)


def _style_line(style: str | None) -> str:
    if not style:
        return ""
    if style.startswith("scholarly: "):
        work = style[len("scholarly: "):].replace(" (normalized notation)", "")
        return (f" The PIE follows the scholarly reconstruction {work}, normalized to the project's notation.")
    return " The PIE follows the project's handbook convention."


# ---------------------------------------------------------------- helpers


def sentences(text: str) -> list[str]:
    """Split at sentence-final punctuation followed by space (the plans' `break` units)."""
    return [s.strip() for s in re.split(r"(?<=[.?!])\s+", text.strip()) if s.strip()]


def _coined(rec: dict | None) -> str | None:
    """As pie.export.record_tasks: "neologism" when a token is one, else the first other coined flag."""
    flags = {w["coined"] for w in (rec or {}).get("tokens", []) if w.get("coined")}
    return "neologism" if "neologism" in flags else next(iter(sorted(flags)), None)


def _meta(kind: str, source_id: str, rec: dict | None, **extra) -> dict:
    m = {"task": kind, "source_id": source_id, "tier": (rec or {}).get("tier")}
    if rec:
        if rec.get("genre"):
            m["genre"] = rec["genre"]
        if rec.get("meter"):
            m["meter"] = rec["meter"]
        if rec.get("neologism") is True:
            m["neologism"] = True
        if _coined(rec):
            m["coined"] = _coined(rec)
    for k, v in extra.items():
        if v is not None:
            m[k] = v
    return m


def _msgs(system: str | None, *turns: tuple[str, str]) -> list[dict]:
    out = [{"role": "system", "content": system}] if system else []
    return out + [{"role": r, "content": c} for r, c in turns]


# ---------------------------------------------------------------- task conversations

TASK_FLAGS = ("accent", "coined", "num_fallback", "seen_in_train", "style", "root_id")
EVAL_KEYS = ("acceptable", "token_variants")


def task_chat(t: dict, rec: dict | None) -> dict:
    kind = t["task"]
    x = t["input"]
    key = f"{kind}|{t.get('source_id')}|{x}"
    if kind == "translate_en_pie":
        x = re.sub(r"^\[style: [^\]]*\] ", "", x)
    tpls = TASK_TEMPLATES[kind]
    i = _pick(key, len(tpls))
    if kind == "inflect":
        lemma, tag = x.rsplit(" ", 1)
        user = tpls[i].format(lemma=lemma, tag=tag, long=describe_features(tag))
    else:
        user = tpls[i].format(x=x)
    system = TASK_SYSTEM[_pick(key + "|sys", len(TASK_SYSTEM))]
    if kind in ("translate_en_pie", "translate_pie_en", "gloss"):
        system += _style_line(t.get("style"))
    extra = {k: t.get(k) for k in TASK_FLAGS + EVAL_KEYS}
    meta = _meta(kind, t.get("source_id"), rec, template=i, **extra)
    for k in ("accent", "coined"):       # the task's own flag wins (inflection targets are not records)
        if t.get(k):
            meta[k] = t[k]
    return {"messages": _msgs(system, ("user", user), ("assistant", t["output"])), "meta": meta}


def _verb_block(cell: str) -> str | None:
    if cell.startswith("PTCP.") or ".FUT." in cell or cell.startswith("IMP.FUT"):
        return None
    m = re.fullmatch(r"(.*)\.[123](SG|DU|PL)", cell)
    return m[1] if m else None


BLOCK_WORDS = {
    "PRS": "present indicative active", "PST": "past (imperfect) indicative active",
    "AOR": "aorist indicative active", "PRF": "perfect indicative", "IMP": "imperative active",
    "SBJV": "subjunctive active", "OPT": "optative active", "MID.PRS": "present indicative middle",
    "MID.PST": "past (imperfect) indicative middle", "MID.AOR": "aorist indicative middle",
    "MID.IMP": "imperative middle", "MID.SBJV": "subjunctive middle", "MID.OPT": "optative middle",
}


def paradigm_task(lx, lid: str) -> dict | None:
    """lemma -> paradigm (PLAN.md Phase 7), from the engine's admissible cells, primary forms only: a noun's
    whole declension; an adjective in one gender; a verb's one finite block (its first, main block half the
    time, else another), chosen deterministically."""
    from .export import GENDER_TAG
    spec, lemma = lx.specs[lid], lx.entries[lid]["form"]
    h = zlib.crc32(lid.encode("utf-8"))
    fam = spec["family"]
    if fam == "adj":
        g = "mfn"[h % 3]
        cells = lx.admissible_cells(lid, g)
        gw = FEATURE_WORDS[GENDER_TAG[g]]
        what, plain, verb = f" in the {gw}", f"{gw} case forms", "Decline"
        rows = [(c, v[0]) for c, v in cells.items()]
        block = GENDER_TAG[g]
    elif fam == "verb":
        cells = lx.admissible_cells(lid)
        blocks = list(dict.fromkeys(b for b in map(_verb_block, cells) if b in BLOCK_WORDS))
        if not blocks:
            return None
        block = blocks[0] if h % 2 == 0 else blocks[(h // 2) % len(blocks)]
        bw = BLOCK_WORDS[block]
        what, plain, verb = f" in the {bw}", f"{bw} forms", "Conjugate"
        rows = [(c, v[0]) for c, v in cells.items() if _verb_block(c) == block]
    else:
        cells = lx.admissible_cells(lid)
        what, plain, verb = " in all cases and numbers", "case forms", "Decline"
        rows = [(c, v[0]) for c, v in cells.items()]
        block = "all"
    if len(rows) < 2:
        return None
    return {"task": "paradigm", "lemma": lemma, "block": block, "what": what, "what_plain": plain, "verb": verb,
            "output": "\n".join(f"{c}: {f}" for c, f in rows), "source_id": lid,
            "root_id": lx.entries[lid].get("root_id")}


def paradigm_chat(p: dict, inflect_flags: dict) -> dict:
    tpls = TASK_TEMPLATES["paradigm"]
    key = f"paradigm|{p['source_id']}"
    i = _pick(key, len(tpls))
    user = tpls[i].format(lemma=p["lemma"], what=p["what"], what_plain=p["what_plain"], verb=p["verb"])
    system = TASK_SYSTEM[_pick(key + "|sys", len(TASK_SYSTEM))]
    meta = _meta("paradigm", p["source_id"], None, template=i, block=p["block"], root_id=p["root_id"],
                 **inflect_flags)
    return {"messages": _msgs(system, ("user", user), ("assistant", p["output"])), "meta": meta}


def paradigm_chats(lx, tasks: list[dict]) -> list[dict]:
    """One paradigm per lexeme that has inflection tasks in this split (so the split, and the coined flag,
    are exactly build()'s)."""
    from .realize import accent_status
    lexemes = dict.fromkeys(t["source_id"] for t in tasks if t["task"] == "inflect")
    out = []
    for lid in lexemes:
        p = paradigm_task(lx, lid)
        if p:
            # the lexeme's flags: coined (Lexicon.coined, as inflection_tasks) and an unresolved accent
            flags = {"coined": lx.coined(lid) or None,
                     "accent": "unresolved" if accent_status(lid) == "unresolved" else None}
            out.append(paradigm_chat(p, flags))
    return out


# ---------------------------------------------------------------- English alignment

# sentence splits of a record's English, tried in order; the first that aligns wins (align_english)
_Q_CLOSE = "\"'”’"
EN_SPLITS = (
    ("plain", r"(?<=[.?!])\s+"),
    # a closing quote after the sentence's punctuation ('Come in!' 'Are you ...?')
    ("quotes", r"(?<=[.?!])[\"'”’]+\s+|(?<=[.?!])\s+"),
    # and a speech frame before an opening quote (Then the master spoke: "Who are you?")
    ("quotes_colon", r"(?<=[.?!])[\"'”’]+\s+|(?<=[.?!])\s+|(?<=:)\s+(?=[\"'“‘])"),
    # and at a semicolon (In the sky he is born; in the water he is born.), plain then with quotes
    ("semicolon", r"(?<=[.?!;])\s+"),
    ("quotes_semicolon", r"(?<=[.?!])[\"'”’]+\s+|(?<=[.?!;])\s+"),
)
SPEAKER_MARK = re.compile(r"^(?:user|model|assistant)\s*:\s*", re.I)


def _clean_en(seg: str) -> str:
    """One English sentence without its quotation marks or a "User:"/"Model:" turn marker (planner-brief-3b)."""
    seg = SPEAKER_MARK.sub("", seg.strip()).strip("\"“”").strip()
    if seg[:1] in "'‘":
        seg = seg[1:]
    if len(seg) > 1 and seg[-1] in "'’" and seg[-2] in ".?!":
        seg = seg[:-1]
    return seg.strip()


def _en_split(text: str, pattern: str) -> list[str]:
    return [c for c in (_clean_en(x) for x in re.split(pattern, text.strip())) if c]


def _parity(en: list[str], pie: list[str]) -> bool:
    return len(en) == len(pie) and [e.endswith("?") for e in en] == [x.endswith("?") for x in pie]


def align_english(rec: dict) -> tuple[list[str] | None, str]:
    """The record's English, one sentence per PIE sentence, or (None, why not).

    "plan_english": every sentence-initial plan clause (the first, and each with `break`) carries its own
    `english` (the optional plan field, docs/generation/planner-brief-v4.md): exact by construction.
    Otherwise the record's `english` is split at sentence ends (EN_SPLITS: plain, then also at a closing quote,
    then also at a "said:" frame before a quotation), and the first split whose sentence count equals the
    PIE's and whose questions ('?') fall on the same sentences is taken. Anything else is skipped, never
    guessed: "count_mismatch" or "question_mismatch" (of the last split tried)."""
    pie = sentences(rec["pie"])
    groups = _sentence_groups(rec)
    if groups and all(isinstance(g[0].get("english"), str) and g[0]["english"].strip() for g in groups):
        en = [_clean_en(g[0]["english"]) for g in groups]
        return (en, "plan_english") if _parity(en, pie) else (None, "plan_english_mismatch")
    why = "no_english"
    for name, pat in EN_SPLITS:
        en = _en_split(rec.get("english") or "", pat)
        if _parity(en, pie):
            return en, name
        if en:
            why = "count_mismatch" if len(en) != len(pie) else "question_mismatch"
    return None, why


_SPEECH = re.compile(r"(?:^|(?<=\s))[\"'“‘](.+?[.?!])[\"'”’](?=\s|$)", re.S)


def quote_turns(rec: dict) -> list[int] | None:
    """Sentences per quoted speech when the English is only quoted speeches (two or more) and their sentences are
    exactly the aligned English (align_english); else None."""
    text = (rec.get("english") or "").strip()
    speeches = [m[1] for m in _SPEECH.finditer(text)]
    if len(speeches) < 2 or _SPEECH.sub("", text).strip():
        return None
    en, _how = align_english(rec)
    if en is None:
        return None
    for _name, pat in EN_SPLITS:
        per = [_en_split(x, pat) for x in speeches]
        if [e for p in per for e in p] == en:
            return [len(p) for p in per]
    return None


def narrated(en: list[str]) -> bool:
    """A narrated dialogue ("Then the master said: ..."): its frames would be user turns that are not
    conversation, so the English-input modes skip it (pie_dialogue keeps it)."""
    return any(e.endswith(":") or re.search(r":\s*[\"'“‘]", e) for e in en)


# ---------------------------------------------------------------- PIE-only dialogues


def _sentence_groups(rec: dict) -> list[list[dict]] | None:
    """The plan's clauses grouped into sentences (a clause with `break` starts a new one); None without a
    plan or when the groups don't match the PIE's sentences."""
    plan = ((rec.get("generator") or {}).get("plan") or {})
    clauses = plan.get("clauses") or []
    groups: list[list[dict]] = []
    for i, c in enumerate(clauses):
        if i == 0 or c.get("break"):
            groups.append([c])
        else:
            groups[-1].append(c)
    return groups if groups and len(groups) == len(sentences(rec["pie"])) else None


def dialogue_turns(rec: dict) -> tuple[list[tuple[str, list[int]]], str, int] | tuple[None, str, int]:
    """Split a dialogue-genre record into (role, sentence indices) turns, user first.

    "speaker": every sentence's plan clauses name a speaker (Tier 3b / wave-2 plans); consecutive sentences
    of one speaker form a turn; exactly two speakers, the first is the user.
    "english_quotes": the record's English is nothing but quoted speeches ('Who is at the door?' 'I am a
    stranger. Make me sip!' ...), each a turn, the speakers alternating, the first is the user; used only when
    the speeches' sentences are exactly align_english's (so every PIE sentence falls in one speech).
    "sentence_qa" (conservative fallback): a run of questions is a user turn and the run of statements after
    it the assistant's reply; statements before the first question open the first user turn. The record is
    skipped when '?' and the plan's `question` flags disagree, or no question is answered.
    Returns (turns, method, dropped trailing sentences) or (None, reason, 0)."""
    sents = sentences(rec["pie"])
    groups = _sentence_groups(rec)
    if groups and all(any(c.get("speaker") for c in g) for g in groups):
        spk = [next(c["speaker"] for c in g if c.get("speaker")) for g in groups]
        if len(set(spk)) != 2:
            return None, "speaker_count", 0
        roles = ["user" if s == spk[0] else "assistant" for s in spk]
        method = "speaker"
    elif (spans := quote_turns(rec)) is not None:
        roles = [("user", "assistant")[k % 2] for k, n in enumerate(spans) for _ in range(n)]
        method = "english_quotes"
    else:
        q = [s.endswith("?") for s in sents]
        if groups and q != [any(c.get("question") for c in g) for g in groups]:
            return None, "question_flag_mismatch", 0
        if True not in q:
            return None, "no_question", 0
        first = q.index(True)
        roles = ["user" if (i < first or q[i]) else "assistant" for i in range(len(sents))]
        method = "sentence_qa"
    turns: list[tuple[str, list[int]]] = []
    for i, r in enumerate(roles):
        if turns and turns[-1][0] == r:
            turns[-1][1].append(i)
        else:
            turns.append((r, [i]))
    dropped = 0
    if turns and turns[-1][0] == "user":
        dropped = len(turns[-1][1])
        turns.pop()
    if turns and turns[0][0] == "assistant":
        return None, "starts_with_reply", 0
    if len(turns) < 2:
        return None, "no_answer", 0
    return turns, method, dropped


def held_dialogue_ids(root: Path | None = None) -> frozenset[str]:
    """The record ids reserved for the conversational eval (data/export/held_dialogues.json)."""
    path = HELD_DIALOGUES if root is None else Path(root) / "data/export/held_dialogues.json"
    if not path.exists():
        return frozenset()
    return frozenset(json.loads(path.read_text("utf-8"))["records"])


def _user_langs(rec_id: str, n_user: int) -> list[str]:
    """The mixed mode's per-user-turn language, by crc32; at least one English and one PIE turn."""
    langs = ["en" if _pick(f"{rec_id}|mix|{k}", 2) == 0 else "pie" for k in range(n_user)]
    if len(set(langs)) == 1:
        langs[-1] = "pie" if langs[-1] == "en" else "en"
    return langs


def en_dialogue(rec: dict, turns, en: list[str], sents: list[str], mode: str, method: str,
                align: str, dropped: int, **extra) -> dict:
    """One English-input conversation over the record's turns (EN_MODES); the assistant always speaks PIE."""
    n_user = sum(r == "user" for r, _ in turns)
    langs = _user_langs(rec["id"], n_user) if mode == "mixed" else ["en"] * n_user
    out, k = [], 0
    for r, ix in turns:
        e, p = " ".join(en[i] for i in ix), " ".join(sents[i] for i in ix)
        if r == "user":
            if langs[k] == "pie":
                out.append(("user", p))
            elif mode == "en_pie_gloss" and k == 0:
                out.append(("user", BILINGUAL_TEMPLATES[_pick(rec["id"] + "|bt", len(BILINGUAL_TEMPLATES))]
                            .format(x=e)))
            else:
                out.append(("user", e))
            k += 1
        else:
            out.append(("assistant", f"{p}\nEnglish: {e}" if mode == "en_pie_gloss" else p))
    meta = _meta("en_dialogue", rec["id"], rec, mode=mode, split=method, align=align, turns=len(turns),
                 user_langs=langs if mode == "mixed" else None, dropped_trailing=dropped or None, **extra)
    return {"messages": _msgs(MODE_SYSTEM[mode], *out), "meta": meta}


def dialogue_chats(records: list[dict], skipped: collections.Counter, align_stats: collections.Counter | None = None,
                   all_modes: bool = False, **extra) -> list[dict]:
    """pie_dialogue (mode pie_pie) for every dialogue-genre record that splits into turns, and, when its English
    aligns (align_english) and it is not narrated, an en_dialogue: one mode per record by crc32 (all_modes: every
    mode, for the eval). `extra` goes into every example's meta."""
    align_stats = collections.Counter() if align_stats is None else align_stats
    out = []
    for rec in records:
        if rec.get("genre") not in DIALOGUE_GENRES:
            continue
        turns, method, dropped = dialogue_turns(rec)
        if turns is None:
            skipped[method] += 1
            continue
        sents = sentences(rec["pie"])
        system = PIE_ONLY_SYSTEM[_pick(rec["id"] + "|sys", len(PIE_ONLY_SYSTEM))]
        msgs = _msgs(system, *[(r, " ".join(sents[i] for i in ix)) for r, ix in turns])
        out.append({"messages": msgs, "meta": _meta("pie_dialogue", rec["id"], rec, mode="pie_pie", split=method,
                                                     turns=len(turns), dropped_trailing=dropped or None, **extra)})
        en, align = align_english(rec)
        if en is None:
            align_stats[f"unaligned:{align}"] += 1
            continue
        if narrated(en):
            align_stats[f"narrated:{align}"] += 1
            continue
        align_stats[f"aligned:{align}"] += 1
        n_user = sum(r == "user" for r, _ in turns)
        modes = [m for m in EN_MODES if m != "mixed" or n_user >= 2]
        for mode in modes if all_modes else [modes[_pick(rec["id"] + "|mode", len(modes))]]:
            out.append(en_dialogue(rec, turns, en, sents, mode, method, align, dropped, **extra))
    return out


# ---------------------------------------------------------------- demo seeds


def load_demo_seeds(path: Path | None = None) -> list[dict]:
    path = path or DEMO_SEEDS
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text("utf-8").splitlines() if x.strip() and not x.startswith("//")]


def _seed_answer(src: dict, train: dict[str, dict], lex_ids: set[str], lx, nx) -> tuple[str, str, dict] | str:
    """(PIE, English, flags) for one seed answer, or the reason it is skipped. Sources: a sentence (or a run of
    sentences) of a TRAINING record, checked against its aligned English; or an engine cell of a lexicon entry
    that occurs in a training record (so never a held-out family), or of a neologism (flagged)."""
    if "record" in src:
        rec = train.get(src["record"])
        if rec is None:
            return "record_not_in_train"
        en, _a = align_english(rec)
        if en is None:
            return "record_unaligned"
        ix = src["sentence"] if isinstance(src["sentence"], list) else [src["sentence"]]
        sents = sentences(rec["pie"])
        if max(ix) >= len(sents):
            return "sentence_out_of_range"
        eng = " ".join(en[i] for i in ix)
        if eng != src["english"]:
            return "english_changed"
        return " ".join(sents[i] for i in ix), eng, {"source_record": rec["id"], "neologism": rec.get("neologism"),
                                                      "coined": _coined(rec)}
    from .realize import Lexicon
    if not isinstance(lx, Lexicon):
        return "no_lexicon"
    lid, cell = src.get("lexeme") or src.get("neologism"), src.get("cell", "NOM.SG")
    if "lexeme" in src:
        if lid not in lex_ids:
            return "lexeme_not_in_train"
        use, flags = lx, {"coined": lx.coined(lid) or None}
    else:
        if nx is None:
            return "no_neologisms"
        if lid not in nx.specs:
            return "neologism_unknown"
        use, flags = nx, {"coined": "neologism", "neologism": True}
    try:
        cells = use.admissible_cells(lid, src["gender"]) if src.get("gender") else use.admissible_cells(lid)
    except (KeyError, ValueError):
        return "no_cells"
    if not cells.get(cell):
        return "no_cell"
    form = cells[cell][0]
    return form + src.get("punct", "."), src["english"], {"source_lexeme": lid, **flags}


def demo_chats(seeds: list[dict], train_records: list[dict], lx, skipped: collections.Counter) -> list[dict]:
    """The demo seed conversations (English user turns; PIE answers, with the gloss line when the seed's crc32
    picks en_pie_gloss). A seed is skipped whole when any answer cannot be resolved (never invented)."""
    train = {r["id"]: r for r in train_records}
    lex_ids = {t.get("lex_id") for r in train_records for t in r.get("tokens", [])}
    nx = None
    if any("neologism" in t["answer"] for sd in seeds for t in sd["turns"]):
        from .realize import Lexicon
        if isinstance(lx, Lexicon):
            from .neologism import NEOLOGISMS, with_neologisms
            nx = with_neologisms(lx) if NEOLOGISMS.exists() else None
    out = []
    for sd in seeds:
        mode = sd.get("mode") or ("en_pie", "en_pie_gloss")[_pick(sd["id"] + "|mode", 2)]
        turns, flags, why = [], {}, None
        for t in sd["turns"]:
            a = _seed_answer(t["answer"], train, lex_ids, lx, nx)
            if isinstance(a, str):
                why = a
                break
            pie, eng, f = a
            turns += [("user", t["user"]), ("assistant", f"{pie}\nEnglish: {eng}" if mode == "en_pie_gloss" else pie)]
            if f.get("neologism"):
                flags["neologism"] = True
            if f.get("coined") and flags.get("coined") != "neologism":      # a neologism wins (pie.export)
                flags["coined"] = f["coined"]
        if why:
            skipped[why] += 1
            continue
        meta = _meta("demo_chat", f"demo:{sd['id']}", None, mode=mode, seed=sd["id"], turns=len(turns), **flags)
        out.append({"messages": _msgs(MODE_SYSTEM[mode], *turns), "meta": meta})
    return out


# ---------------------------------------------------------------- continuation


def _texts(records: list[dict]) -> list[tuple[str, list[str], list[str], dict]]:
    """(source id, PIE units, ASCII units, representative record) per text: a Tier 1 work's lines in line
    order form one text; every other record is its own text."""
    works: dict[str, list[dict]] = {}
    out: list = []
    for r in records:
        if r.get("tier") == 1 and r.get("line_no") is not None and r.get("work_id"):
            if r["work_id"] not in works:
                works[r["work_id"]] = []
                out.append(("work", r["work_id"]))
            works[r["work_id"]].append(r)
        else:
            out.append(("rec", r))
    res = []
    for kind, v in out:
        if kind == "work":
            lines = sorted(works[v], key=lambda r: r["line_no"])
            res.append((v, [r["pie"] for r in lines], [r["pie_ascii"] for r in lines], lines[0]))
        else:
            res.append((v["id"], [v["pie"]], [v["pie_ascii"]], v))
    return res


def continuation_chats(records: list[dict]) -> list[dict]:
    out = []
    for sid, units, _a, rec in _texts(records):
        genre = rec.get("genre")
        if genre not in CONTINUATION_GENRES:
            continue
        parts = units if len(units) > 1 else sentences(units[0])
        if len(parts) < 2:
            continue
        k = max(1, round(len(parts) * 0.4))
        i = _pick(sid + "|cont", len(CONTINUATION_TEMPLATES))
        user = CONTINUATION_TEMPLATES[i].format(x=" ".join(parts[:k]), genre=CONTINUATION_GENRES[genre])
        system = CONTINUATION_SYSTEM[_pick(sid + "|sys", len(CONTINUATION_SYSTEM))]
        out.append({"messages": _msgs(system, ("user", user), ("assistant", " ".join(parts[k:]))),
                    "meta": _meta("continuation", sid, rec, template=i, opening_units=k, units=len(parts),
                                  seen_in_train=rec.get("seen_in_train") if len(units) == 1 else None)})
    return out


# ---------------------------------------------------------------- plain text


def text_views(records: list[dict]) -> tuple[str, str]:
    """One text per paragraph (blank-line separated, each on one line): Unicode and pie_ascii."""
    t = _texts(records)
    return ("\n\n".join(" ".join(u) for _s, u, _a, _r in t) + "\n",
            "\n\n".join(" ".join(a) for _s, _u, a, _r in t) + "\n")


# ---------------------------------------------------------------- checks


def _words(s: str) -> list[str]:
    """Whitespace words, NFC, lowercased, edge punctuation stripped (a gloss word like slain-NOM.PL stays one)."""
    s = unicodedata.normalize("NFC", s).lower()
    return [w for w in (x.strip(".,;:!?\"“”'‘’()[]") for x in s.split()) if w]


def _ngrams(ws: list[str], n: int = NGRAM) -> set[tuple[str, ...]]:
    return {tuple(ws[i:i + n]) for i in range(len(ws) - n + 1)}


def _content(ex: dict, role: str) -> str:
    return "\n".join(m["content"] for m in ex["messages"] if m["role"] == role)


def leakage_report(train: list[dict], eval_: list[dict], train_text: str) -> dict:
    """Eval items must not reappear in train, even under another prompt template.

    Hard failures (the export raises): an eval source id that also has a train example; an eval (user,
    assistant) pair, or an eval assistant turn of >= 2 words, found verbatim in train; an eval assistant turn
    whose word 4-grams are >= 50% in train (PIE kinds only: English outputs share ordinary phrases). Eval
    items flagged seen_in_train (Tier 1 lines Tier 3 reuses on purpose, pie.export) are reported, not failed.
    Reported: the 4-gram overlap distribution per kind (all assistant turns, against every train message
    and the train plain text), and how many one-word answers (inflect, cognates_to_pie) occur as a word of
    the train plain text (a homograph, or a form shared across families)."""
    train_ids = {e["meta"]["source_id"] for e in train}
    train_pairs = {(_content(e, "user"), _content(e, "assistant")) for e in train}
    train_asst = {" ".join(_words(_content(e, "assistant"))) for e in train}
    grams: set = set()
    for e in train:
        for m in e["messages"]:
            if m["role"] != "system":
                grams |= _ngrams(_words(m["content"]))
    train_words: set = set()
    for para in train_text.split("\n\n"):
        ws = _words(para)
        grams |= _ngrams(ws)
        train_words.update(ws)
    english_out = {"translate_pie_en"}
    per_kind: dict[str, dict] = {}
    failures, flagged = [], []
    for e in eval_:
        m, a = e["meta"], _content(e, "assistant")
        ws = _words(a)
        g = _ngrams(ws)
        share = len(g & grams) / len(g) if g else None
        k = per_kind.setdefault(m["task"], {"n": 0, "with_ngrams": 0, "mean_overlap": 0.0, "max_overlap": 0.0,
                                            "any_overlap": 0, "single_word_in_train_text": 0})
        k["n"] += 1
        k["single_word_in_train_text"] += len(ws) == 1 and ws[0] in train_words
        if share is not None:
            k["with_ngrams"] += 1
            k["mean_overlap"] += share
            k["max_overlap"] = max(k["max_overlap"], share)
            k["any_overlap"] += share > 0
        why = []
        if m["source_id"] in train_ids:
            why.append("source_id in train")
        if (_content(e, "user"), a) in train_pairs:
            why.append("exact pair in train")
        if len(ws) >= 2 and " ".join(ws) in train_asst:
            why.append("assistant turn verbatim in train")
        if share is not None and share >= 0.5 and m["task"] not in english_out:
            why.append(f"4-gram overlap {share:.2f}")
        if why:
            (flagged if m.get("seen_in_train") else failures).append({"source_id": m["source_id"],
                                                                       "task": m["task"], "why": why})
    for k in per_kind.values():
        if k["with_ngrams"]:
            k["mean_overlap"] = round(k["mean_overlap"] / k["with_ngrams"], 4)
        k["max_overlap"] = round(k["max_overlap"], 4)
    return {"ngram": NGRAM, "per_kind": per_kind, "failures": failures,
            "flagged_seen_in_train": flagged, "ok": not failures}


def neologism_share(records: list[dict]) -> dict:
    """Share of training words from Tier 3b (neologism: true) records; PLAN.md caps it at 10-15%."""
    tot = neo = 0
    for r in records:
        n = len(_words(r["pie"]))
        tot += n
        neo += n if r.get("neologism") is True else 0
    share = neo / tot if tot else 0.0
    return {"neologism_words": neo, "total_words": tot, "share": round(share, 4), "cap": NEOLOGISM_CAP,
            "exceeded": share > NEOLOGISM_CAP}


def token_stats(chat: dict[str, list[dict]], texts: dict[str, str], tokenizer: str | None) -> dict:
    """Per split and kind: examples, content tokens (message contents, no chat template) and assistant
    tokens; for the plain text, tokens per word in Unicode and in pie_ascii. Without a tokenizer, words only."""
    enc = None
    if tokenizer:
        from tokenizers import Tokenizer   # optional: uv run --with tokenizers
        tok = Tokenizer.from_file(tokenizer)
        enc = lambda xs: [len(e.ids) for e in tok.encode_batch(xs, add_special_tokens=False)]
    out: dict = {"tokenizer": tokenizer}
    for split, exs in chat.items():
        kinds: dict[str, dict] = {}
        allc = [m["content"] for e in exs for m in e["messages"]]
        lens = iter(enc(allc)) if enc else None
        for e in exs:
            k = kinds.setdefault(e["meta"]["task"], {"examples": 0, "words": 0, "tokens": 0, "assistant_tokens": 0})
            k["examples"] += 1
            for m in e["messages"]:
                k["words"] += len(m["content"].split())
                if lens:
                    n = next(lens)
                    k["tokens"] += n
                    k["assistant_tokens"] += n if m["role"] == "assistant" else 0
        if not enc:
            for k in kinds.values():
                k.pop("tokens"), k.pop("assistant_tokens")
        out[split] = dict(sorted(kinds.items()))
    for name, txt in texts.items():
        paras = [p for p in txt.split("\n\n") if p.strip()]
        words = sum(len(p.split()) for p in paras)
        d = {"paragraphs": len(paras), "words": words}
        if enc:
            d["tokens"] = sum(enc(paras))
            d["tokens_per_word"] = round(d["tokens"] / words, 4) if words else None
        out[name] = d
    return out


# ---------------------------------------------------------------- build / write


def build_chat(d: dict, lx=None, seeds: list[dict] | None = None) -> dict:
    """The chat examples, text views and checks for build()'s splits. Raises on leakage. `seeds`: the demo seeds
    (default data/export/demo_seeds.jsonl)."""
    if lx is None:
        from .realize import Lexicon
        lx = Lexicon.load()
    seeds = load_demo_seeds() if seeds is None else seeds
    recs = {r["id"]: r for r in d["train_records"] + d["eval_records"]}
    skipped = {"train": collections.Counter(), "eval": collections.Counter()}
    align = {"train": collections.Counter(), "eval": collections.Counter()}
    demo_skipped: collections.Counter = collections.Counter()
    chat = {}
    for split in ("train", "eval"):
        tasks, records = d[f"{split}_tasks"], d[f"{split}_records"]
        exs = [task_chat(t, recs.get(t.get("source_id"))) for t in tasks]
        exs += paradigm_chats(lx, tasks)
        exs += dialogue_chats(records, skipped[split], align[split])
        exs += continuation_chats(records)
        if split == "train":
            exs += demo_chats(seeds, records, lx, demo_skipped)
        else:      # the conversational eval: the reserved dialogue records, in every mode
            exs += dialogue_chats(d.get("eval_dialogue_records", []), skipped[split], align[split], all_modes=True,
                                  chat_eval=True)
        random.Random(f"chat-{split}").shuffle(exs)
        for n, e in enumerate(exs):
            e["meta"]["id"] = f"{split}-{n:06d}"
        chat[split] = exs
    text = {split: text_views(d[f"{split}_records"]) for split in ("train", "eval")}
    leak = leakage_report(chat["train"], chat["eval"], text["train"][0])
    if not leak["ok"]:
        raise ValueError(f"chat eval leakage: {len(leak['failures'])} items, e.g. {leak['failures'][:3]}")
    neo = neologism_share(d["train_records"])
    if neo["exceeded"]:
        print(f"WARNING: Tier 3b neologism share {neo['share']:.1%} of training words exceeds the "
              f"{NEOLOGISM_CAP:.0%} cap (PLAN.md)", file=sys.stderr)
    return {"chat": chat, "text": text, "leakage": leak, "neologism": neo,
            "dialogue_skipped": {k: dict(v) for k, v in skipped.items()},
            "alignment": {k: dict(sorted(v.items())) for k, v in align.items()},
            "demo_seeds": {"seeds": len(seeds), "used": sum(e["meta"]["task"] == "demo_chat" for e in chat["train"]),
                           "skipped": dict(sorted(demo_skipped.items()))},
            "chat_eval": {"reserved_records": len(d.get("eval_dialogue_records", [])),
                          "held_dialogues": str(HELD_DIALOGUES.relative_to(HELD_DIALOGUES.parents[2]))}}


def write_chat(d: dict, out: Path, tokenizer: str | None = None, provenance: dict | None = None,
               lx=None) -> dict:
    """Write export/chat/{train,eval}.jsonl + summary.json, export/text/ and export/text-ascii/."""
    c = build_chat(d, lx)
    (out / "chat").mkdir(parents=True, exist_ok=True)
    for split, exs in c["chat"].items():
        (out / "chat" / f"{split}.jsonl").write_text(
            "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in exs), "utf-8")
    texts = {}
    for sub, i in (("text", 0), ("text-ascii", 1)):
        (out / sub).mkdir(parents=True, exist_ok=True)
        for split in ("train", "eval"):
            (out / sub / f"{split}.txt").write_text(c["text"][split][i], "utf-8")
            texts[f"{sub}/{split}.txt"] = c["text"][split][i]
    summary = {
        "provenance": provenance or {},
        "examples": {s: len(v) for s, v in c["chat"].items()},
        "examples_by_kind": {s: dict(sorted(collections.Counter(e["meta"]["task"] for e in v).items()))
                             for s, v in c["chat"].items()},
        "pie_dialogue_split_method": {s: dict(collections.Counter(e["meta"]["split"] for e in v
                                                                  if e["meta"]["task"] == "pie_dialogue"))
                                      for s, v in c["chat"].items()},
        "dialogue_records_skipped": c["dialogue_skipped"],
        # per dialogue record that splits into turns: aligned:<method> (gets an English-input conversation),
        # narrated:<method> (aligned, but "Then he said:" frames), unaligned:<reason> (skipped, never guessed)
        "dialogue_english_alignment": c["alignment"],
        "modes": {s: dict(sorted(collections.Counter(f"{e['meta']['task']}/{e['meta']['mode']}" for e in v
                                                     if e["meta"].get("mode")).items()))
                  for s, v in c["chat"].items()},
        "english_input_conversations": {s: sum(e["meta"].get("mode", "pie_pie") != "pie_pie" for e in v)
                                        for s, v in c["chat"].items()},
        "demo_seeds": c["demo_seeds"],
        "chat_eval": {**c["chat_eval"], "examples": dict(sorted(collections.Counter(
            f"{e['meta']['task']}/{e['meta']['mode']}" for e in c["chat"]["eval"] if e["meta"].get("chat_eval")).items()))},
        "neologism": c["neologism"],
        "leakage": c["leakage"],
        "tokens": token_stats(c["chat"], texts, tokenizer),
    }
    for name in ("train", "eval"):
        ta, tu = summary["tokens"].get(f"text-ascii/{name}.txt", {}), summary["tokens"].get(f"text/{name}.txt", {})
        if "tokens_per_word" in tu:
            summary["tokens"][f"{name}_tokens_per_word_unicode_vs_ascii"] = [tu["tokens_per_word"],
                                                                             ta["tokens_per_word"]]
    (out / "chat" / "summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n", "utf-8")
    return summary
