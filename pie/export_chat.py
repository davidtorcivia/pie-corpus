"""Chat and plain-text export layer, built on pie.export.build()'s output (export/README.md "Chat export").

Trainer-neutral: each chat example is {"messages": [{"role", "content"}, ...], "meta": {...}} with no
model-specific template, so Tinker (or any SFT trainer) applies the model's own renderer. The plain-text
files are for LM loss on the language itself.

Kinds (meta.task):
  task conversations   translate_en_pie, translate_pie_en, gloss, inflect, paradigm, cognates_to_pie:
                       one user prompt (several paraphrased templates, chosen deterministically) and the
                       task's exact output as the assistant turn, so a scorer can compare it directly
  pie_dialogue         PIE-only conversations from the dialogue genres, split into turns (meta.split:
                       "speaker", "english_quotes" or "sentence_qa"); in training, the dialogues that have no
                       English-input conversation, and one in PIE_PIE_EVERY of those that have (mode_plan)
  continuation         the opening of a hymn, story or charm in PIE; the assistant continues it
  en_dialogue          the same dialogues with English user input (meta.mode): en_pie (English user, PIE
                       replies), en_pie_gloss (PIE reply + "English: ..." line), mixed (the user switches
                       between English and PIE, the replies are PIE). Every aligned dialogue (align_english)
                       gets en_pie whole and en_pie_gloss and mixed (whole, or halves of 2+ exchanges) (mode_plan),
                       no assistant turn in more than DEDUP_CAP of them (self_overlap)
  translate_app        the translator: English in, "PIE: ..." / "Gloss: ..." / optional "Notes: ..." out
                       (app_format, parse_app), from every record with English, its sentences partitioned into
                       sentence-level and short-paragraph items; one in five is the inverse (PIE in,
                       "English: ..." / "Gloss: ..." out). The translation app's own dataset
                       (export/translator/, build_translator) has every item in both directions
  app_session          multi-turn translator sessions (train only, a small minority of multi-turn: at most
                       APP_SESSION_SHARE): adjacent en_pie items of the same text become one conversation of
                       2-3 consecutive requests in text order (the same items, not copies, so each sentence
                       is still in exactly one translator example)
  demo_chat            the hand-written demo seeds (data/export/demo_seeds.jsonl): English questions answered
                       with an existing training sentence or an engine form of a lexicon (or neologism) entry

Conversational eval: the dialogue records frozen in data/export/held_dialogues.json leave train in
pie.export.build() (eval_dialogue_records) and become eval conversations in every mode (meta.chat_eval).

Hold-out: nothing here re-splits. Each example inherits its split from build(): tasks from
train_tasks/eval_tasks, texts from train_records/eval_records. A paradigm goes to the split its lexeme's
inflection tasks went to (the same held-family and project-reconstruction decisions), so it never needs its
own predicate. The leakage check (leakage_report) fails the export when an eval item reappears in train.

Mix: mix_table groups the kinds (conversation, translation, grammar, comparative) and gives each split's
shares and the sampling weights that reach TARGET_MIX; chat/train_mix.jsonl (select_mix) is a subset of train
in those proportions.
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
PIE_PIE_EVERY = 2      # one aligned dialogue in two (crc32) is also a pie_pie conversation (mode_plan)
HELD_DIALOGUES = Path(__file__).resolve().parent.parent / "data/export/held_dialogues.json"
DEMO_SEEDS = Path(__file__).resolve().parent.parent / "data/export/demo_seeds.jsonl"
NEOLOGISM_CAP = 0.15           # PLAN.md Tier 3b: 10-15% of training tokens
NGRAM = 4
# kinds whose assistant turns are PIE sentences (assistant_pie, self_overlap)
PIE_OUT_KINDS = ("translate_en_pie", "pie_dialogue", "en_dialogue", "continuation", "demo_chat")

# ---------------------------------------------------------------- templates


def _pick(key: str, n: int) -> int:
    """A deterministic choice (crc32, not hash(): str hashes are salted per process)."""
    return zlib.crc32(key.encode("utf-8")) % n


# The model is a speaker of Proto-Indo-European (owner, 2026-10-30): one identity in every system prompt, human by
# omission (never a machine, never a linguist). PERSONA is the demo's own system prompt and opens most examples
# (persona()); the close variants keep the model from hanging on one exact string. Drills are a teacher going over
# the speaker's own grammar.
PERSONA = "You are a speaker of Proto-Indo-European. You think in it and answer in it."
PERSONA_VARIANTS = [
    "Proto-Indo-European is your own language. You think in it and answer in it.",
    "You speak Proto-Indo-European; it is your mother tongue.",
]
PERSONA_SHARE = 0.8     # of the examples of each kind, by crc32: the exact PERSONA; the rest a variant


def persona(key: str) -> str:
    n = _pick(key + "|persona", 100)
    return PERSONA if n < PERSONA_SHARE * 100 else PERSONA_VARIANTS[n % len(PERSONA_VARIANTS)]


TEACHER = [
    "A teacher is going over the grammar of your language with you. Answer exactly.",
    "Your teacher is drilling you on the forms and meaning of your language. Answer precisely.",
    "A teacher is testing how well you know your own language. Answer exactly, in the form asked.",
]
COGNATE_TEACHER = ("A teacher shows you words from languages that descend from yours and asks which word of your "
                   "language they come from.")

PIE_ONLY_SYSTEM = [
    "Reply only in your language.",
    "Answer in your own language, never in English.",
    "Every reply is in your language.",
]

CONTINUATION_SYSTEM = [
    "Carry on the text the user begins, in your language only.",
    "Continue the text you are given, in your own language.",
]

BILINGUAL_SYSTEM = ("The user writes in English. Reply in your language, then give an English translation "
                    "of your reply on its own line beginning \"English:\".")
EN_PIE_SYSTEM = "The user writes in English. Reply in your language."
MIXED_SYSTEM = "The user may write in English or in your language. Always reply in your language."
MODE_SYSTEM = {"en_pie": EN_PIE_SYSTEM, "en_pie_gloss": BILINGUAL_SYSTEM, "mixed": MIXED_SYSTEM}


def system(key: str, instruction: str | None = None) -> str:
    """The persona (persona()) followed by the kind's instruction."""
    return persona(key) + (" " + instruction if instruction else "")

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
        return (f" Write it as in the scholarly reconstruction {work}, in the project's notation.")
    return " Write it in the project's handbook convention."


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
    sysp = system(key, COGNATE_TEACHER if kind == "cognates_to_pie" else TEACHER[_pick(key + "|sys", len(TEACHER))])
    if kind in ("translate_en_pie", "translate_pie_en", "gloss"):
        sysp += _style_line(t.get("style"))
    extra = {k: t.get(k) for k in TASK_FLAGS + EVAL_KEYS}
    meta = _meta(kind, t.get("source_id"), rec, template=i, **extra)
    for k in ("accent", "coined"):       # the task's own flag wins (inflection targets are not records)
        if t.get(k):
            meta[k] = t[k]
    return {"messages": _msgs(sysp, ("user", user), ("assistant", t["output"])), "meta": meta}


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
    sysp = system(key, TEACHER[_pick(key + "|sys", len(TEACHER))])
    meta = _meta("paradigm", p["source_id"], None, template=i, block=p["block"], root_id=p["root_id"],
                 **inflect_flags)
    return {"messages": _msgs(sysp, ("user", user), ("assistant", p["output"])), "meta": meta}


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
                align: str, dropped: int, window: tuple[int, int] | None = None, **extra) -> dict:
    """One English-input conversation over the record's turns (EN_MODES); the assistant always speaks PIE.
    `window`: the (start, end) exchanges these turns are, when not the whole dialogue (meta.window)."""
    n_user = sum(r == "user" for r, _ in turns)
    key = rec["id"] if window is None else f"{rec['id']}|w{window[0]}"
    langs = _user_langs(key, n_user) if mode == "mixed" else ["en"] * n_user
    out, k = [], 0
    for r, ix in turns:
        e, p = " ".join(en[i] for i in ix), " ".join(sents[i] for i in ix)
        if r == "user":
            if langs[k] == "pie":
                out.append(("user", p))
            elif mode == "en_pie_gloss" and k == 0:
                out.append(("user", BILINGUAL_TEMPLATES[_pick(key + "|bt", len(BILINGUAL_TEMPLATES))]
                            .format(x=e)))
            else:
                out.append(("user", e))
            k += 1
        else:
            out.append(("assistant", f"{p}\nEnglish: {e}" if mode == "en_pie_gloss" else p))
    meta = _meta("en_dialogue", rec["id"], rec, mode=mode, split=method, align=align, turns=len(turns),
                 user_langs=langs if mode == "mixed" else None, dropped_trailing=dropped or None,
                 window=list(window) if window else None, **extra)
    return {"messages": _msgs(system(f"{rec['id']}|{mode}", MODE_SYSTEM[mode]), *out), "meta": meta}


def pie_dialogue(rec: dict, turns, sents: list[str], method: str, dropped: int,
                 window: tuple[int, int] | None = None, **extra) -> dict:
    msgs = _msgs(system(rec["id"], PIE_ONLY_SYSTEM[_pick(rec["id"] + "|sys", len(PIE_ONLY_SYSTEM))]), *[(r, " ".join(sents[i] for i in ix)) for r, ix in turns])
    return {"messages": msgs, "meta": _meta("pie_dialogue", rec["id"], rec, mode="pie_pie", split=method,
                                            turns=len(turns), dropped_trailing=dropped or None,
                                            window=list(window) if window else None, **extra)}


def mode_plan(rec_id: str, k: int) -> list[tuple[str, tuple[int, int]]]:
    """The training modes of an aligned, non-narrated dialogue of k exchanges (user turn + reply), as
    (mode, (start, end) exchanges). Each assistant turn lands in at most DEDUP_CAP (3) of them:
      en_pie        the whole dialogue, always
      en_pie_gloss  the whole dialogue when k <= 3; else one of two halves (exchanges [:k//2], [k//2:]), so a
                    half always has two or more exchanges (a dialogue stays multi-turn)
      mixed         k in (2, 3), not doubled: the whole dialogue; k >= 4: the other half (mixed needs two
                    user turns)
      pie_pie       the whole dialogue, on the doubled records: one in PIE_PIE_EVERY (crc32) of the aligned
                    dialogues is also a PIE-only conversation, the same exchanges with the user turns in PIE
    With k >= 4 crc32 picks which half is mixed."""
    doubled = _pick(rec_id + "|pp", PIE_PIE_EVERY) == 0
    whole = (0, k)
    if k == 1:
        plan = [("en_pie", whole), ("en_pie_gloss", whole)]
    elif k <= 3:
        plan = [("en_pie", whole), ("en_pie_gloss", whole)] + ([] if doubled else [("mixed", whole)])
    else:
        h = k // 2
        halves = [(0, h), (h, k)]
        if _pick(rec_id + "|half", 2):
            halves.reverse()
        plan = [("en_pie", whole), ("en_pie_gloss", halves[0]), ("mixed", halves[1])]
    return plan + ([("pie_pie", whole)] if doubled else [])


def dialogue_chats(records: list[dict], skipped: collections.Counter, align_stats: collections.Counter | None = None,
                   all_modes: bool = False, **extra) -> list[dict]:
    """Conversations from every dialogue-genre record that splits into turns (dialogue_turns).

    Training (all_modes False): a record whose English aligns (align_english) and is not narrated gets the
    English-input modes of mode_plan (en_pie whole; en_pie_gloss and mixed whole or on disjoint halves of two
    or more exchanges; pie_pie whole on one in PIE_PIE_EVERY), so English input dominates and no assistant turn
    is in more than DEDUP_CAP of them; any other record is a pie_pie conversation (its only possible mode).
    The conversational eval (all_modes True): the whole
    dialogue in pie_pie and in every English mode. `extra` goes into every example's meta."""
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
        en, align = align_english(rec)
        if en is not None and narrated(en):
            align_stats[f"narrated:{align}"] += 1
            en = None
        elif en is None:
            align_stats[f"unaligned:{align}"] += 1
        else:
            align_stats[f"aligned:{align}"] += 1
        if all_modes or en is None:
            out.append(pie_dialogue(rec, turns, sents, method, dropped, **extra))
        if en is None:
            continue
        k = len(turns) // 2
        if all_modes:
            n_user = sum(r == "user" for r, _ in turns)
            for mode in (m for m in EN_MODES if m != "mixed" or n_user >= 2):
                out.append(en_dialogue(rec, turns, en, sents, mode, method, align, dropped, **extra))
            continue
        for mode, (a, b) in mode_plan(rec["id"], k):
            sub, win = turns[2 * a:2 * b], (None if (a, b) == (0, k) else (a, b))
            if mode == "pie_pie":
                out.append(pie_dialogue(rec, sub, sents, method, dropped, window=win, **extra))
            else:
                out.append(en_dialogue(rec, sub, en, sents, mode, method, align, dropped, window=win, **extra))
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
        out.append({"messages": _msgs(system(f"demo:{sd['id']}|{mode}", MODE_SYSTEM[mode]), *turns), "meta": meta})
    return out


# ---------------------------------------------------------------- continuation


def _grouped(records: list[dict]):
    """(source id, records) per translation text: a Tier 1 work's numbered lines in line order form one text
    (an item may join consecutive lines), every other record is its own."""
    works: dict[str, list[dict]] = {}
    order: list = []
    for r in records:
        if r.get("tier") == 1 and r.get("line_no") is not None and r.get("work_id"):
            if r["work_id"] not in works:
                works[r["work_id"]] = []
                order.append(("work", r["work_id"]))
            works[r["work_id"]].append(r)
        else:
            order.append(("rec", r))
    for kind, v in order:
        yield (v, sorted(works[v], key=lambda r: r["line_no"])) if kind == "work" else (v["id"], [v])


def _texts(records: list[dict]) -> list[tuple[str, list[str], list[str], dict]]:
    """(source id, PIE units, ASCII units, representative record) per text (_grouped: a Tier 1 work's lines in
    line order form one text; every other record is its own text)."""
    return [(sid, [r["pie"] for r in rs], [r["pie_ascii"] for r in rs], rs[0]) for sid, rs in _grouped(records)]


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
        sysp = system(sid, CONTINUATION_SYSTEM[_pick(sid + "|sys", len(CONTINUATION_SYSTEM))])
        out.append({"messages": _msgs(sysp, ("user", user), ("assistant", " ".join(parts[k:]))),
                    "meta": _meta("continuation", sid, rec, template=i, opening_units=k, units=len(parts),
                                  seen_in_train=rec.get("seen_in_train") if len(units) == 1 else None)})
    return out


# ---------------------------------------------------------------- translator (translate_app)

APP_SYSTEM = "Translate the user's English into your language, then gloss it word by word."     # after persona()
APP_INVERSE_SYSTEM = "Translate the user's words from your language into English, then gloss them word by word."
APP_CHUNK = (1, 1, 2, 3)        # sentences per item, by crc32: half sentence-level, half short paragraphs
APP_INVERSE_EVERY = 5           # one item in five (crc32) is the inverse PIE -> English mode
APP_SHORT = 3                   # an unaligned record is one item when it has at most this many sentences
APP_SESSION_SHARE = 0.10        # chained translator requests: at most this share of the multi-turn examples
APP_SESSION_LEN = (2, 2, 3)     # requests per session, by crc32
APP_FOLLOWUPS = ("{x}", "And this: {x}", "Next: {x}", "Now this one: {x}", "And how would you say this? {x}")
_FINAL = re.compile(r"[.?!;][\"'”’)]*$")


def app_format(pie: str, gloss: str | None, notes: str | None = None) -> str:
    """The translator's assistant turn (export/README.md "Translator format"): `PIE: ...`, `Gloss: ...`, then
    an optional `Notes: ...`, one field per line, in that order. parse_app inverts it."""
    return "\n".join([f"PIE: {pie}"] + ([f"Gloss: {gloss}"] if gloss else []) + ([f"Notes: {notes}"] if notes else []))


def app_inverse_format(english: str, gloss: str | None) -> str:
    return "\n".join([f"English: {english}"] + ([f"Gloss: {gloss}"] if gloss else []))


APP_FIELDS = ("PIE", "English", "Gloss", "Notes")


def parse_app(text: str) -> dict[str, str]:
    """{"PIE": ..., "Gloss": ..., "Notes": ...} (or "English" for the inverse) from a translator turn; a line
    that starts no field continues the previous one."""
    out: dict[str, str] = {}
    last = None
    for line in text.splitlines():
        m = re.match(r"(PIE|English|Gloss|Notes): ?(.*)", line)
        if m:
            last = m[1]
            out[last] = m[2].strip()
        elif last and line.strip():
            out[last] += " " + line.strip()
    return out


def _coined_note(toks: list[dict]) -> str | None:
    """Notes for the coined words of an item: modern coinages (Tier 3b neologisms) and project reconstructions."""
    neo = list(dict.fromkeys(t["form"] for t in toks if t.get("coined") == "neologism"))
    proj = list(dict.fromkeys(t["form"] for t in toks if t.get("coined") and t.get("coined") != "neologism"))
    parts = []
    if neo:
        parts.append(f"{', '.join(neo)}: {'a modern coinage' if len(neo) == 1 else 'modern coinages'} "
                     "built from inherited roots.")
    if proj:
        parts.append(f"{', '.join(proj)}: {'a project reconstruction' if len(proj) == 1 else 'project reconstructions'}"
                     ", not a standard handbook form.")
    return " ".join(parts) or None


def _app_units(rec: dict) -> tuple[list[tuple[str, str, str | None, list[dict]]] | None, str]:
    """(PIE, English, gloss or None, tokens) per sentence of a record, or (None, why). The gloss and tokens are
    sliced by each sentence's word count (sentences() keeps every word), only when the record's gloss (and its
    tokens) have exactly one entry per PIE word; otherwise the gloss is left out, never guessed."""
    pie = sentences(rec["pie"])
    en, how = align_english(rec)
    if en is None:
        if len(pie) > APP_SHORT:
            return None, f"unaligned_long:{how}"
        pie, en = [" ".join(pie)], [_clean_en(" ".join((rec.get("english") or "").split()))]
    words = [len(x.split()) for x in pie]
    gw = (rec.get("gloss") or "").split()
    toks = rec.get("tokens") or []
    gl = toks_ok = None
    if gw and len(gw) == sum(words):
        gl = gw
    if len(toks) == sum(words):
        toks_ok = toks
    out, i = [], 0
    for p, e, n in zip(pie, en, words):
        out.append((p, e, " ".join(gl[i:i + n]) if gl else None, toks_ok[i:i + n] if toks_ok else []))
        i += n
    return out, how if gl or not gw else f"{how}:gloss_mismatch"


def app_chats(records: list[dict], stats: collections.Counter, tasks: dict[str, dict] | None = None,
              inverse: bool = True, both_directions: bool = False, sessions: int = 0) -> list[dict]:
    """translate_app: English in, `PIE:` / `Gloss:` / `Notes:` out (app_format), from every record with English.

    Each text's sentences (a Tier 1 work: its lines) are partitioned into items of 1-3 sentences (APP_CHUNK, by
    crc32; a line without final punctuation, such as a title, ends its item), so every sentence is in exactly
    one item: sentence-level and short-paragraph items. A record whose
    English does not align sentence by sentence is one item when it is short (APP_SHORT), else skipped. One
    item in APP_INVERSE_EVERY is the inverse mode (PIE in, `English:` / `Gloss:` out) when `inverse`; with
    `both_directions` (the translator dataset, export/translator/) every item is emitted in both modes.
    `sessions` (the chat train split): at most this many app_session conversations, made by app_sessions from
    the adjacent en_pie items of texts picked by lowest crc32 (a budget, so chained requests stay a small
    minority of the multi-turn examples, APP_SESSION_SHARE). The gloss
    is the gloss task's own (the record's gloss, sliced per sentence); a record without one (Tier 1) gets no
    Gloss line (meta.gloss_reference false). `tasks`: source id -> its translate_en_pie task, whose acceptable
    alternatives and token variants an item of the whole record (or the matching words) carries for scoring."""
    tasks = tasks or {}
    out: list[dict] = []
    spans = []
    for sid, recs in _grouped(records):
        start = len(out)
        units: list[tuple[str, str, str | None, list[dict], dict]] = []
        for r in recs:
            if not r.get("english"):
                stats["no_english"] += 1
                continue
            u, how = _app_units(r)
            if u is None:
                stats[how] += 1
                continue
            if how.endswith("gloss_mismatch"):
                stats["gloss_mismatch"] += 1
            units += [(*x, r) for x in u]
        pos = 0
        while pos < len(units):
            n = min(APP_CHUNK[_pick(f"{sid}|app|{pos}", len(APP_CHUNK))], len(units) - pos)
            # a unit without sentence-final punctuation (a title, a formula) ends its item: nothing is joined
            # onto it without a boundary
            n = next((j + 1 for j in range(n - 1) if not (_FINAL.search(units[pos + j][0])
                                                          and _FINAL.search(units[pos + j][1]))), n)
            chunk = units[pos:pos + n]
            rs = list(dict.fromkeys(id(x[4]) for x in chunk))
            rec = chunk[0][4]
            src = rec["id"] if len(rs) == 1 else sid
            pie = " ".join(x[0] for x in chunk)
            eng = " ".join(x[1] for x in chunk)
            has_gloss = all(x[2] for x in chunk)
            gloss = " ".join(x[2] for x in chunk) if has_gloss else None
            toks = [t for x in chunk for t in x[3]]
            if both_directions:
                modes = ("en_pie", "pie_en")
            else:
                modes = ("pie_en" if inverse and _pick(f"{sid}|inv|{pos}", APP_INVERSE_EVERY) == 0 else "en_pie",)
            for mode in modes:
                whole = len(rs) == 1 and n == len([u for u in units if u[4] is rec])
                if mode == "en_pie":
                    msgs = _msgs(system(f"{sid}|{pos}", APP_SYSTEM), ("user", eng), ("assistant", app_format(pie, gloss, _coined_note(toks))))
                else:
                    msgs = _msgs(system(f"{sid}|{pos}", APP_INVERSE_SYSTEM), ("user", pie), ("assistant", app_inverse_format(eng, gloss)))
                t = tasks.get(rec["id"]) or {}
                extra = {"acceptable": t.get("acceptable") if whole and mode == "en_pie" else None}
                tv = t.get("token_variants")
                if mode == "en_pie" and len(rs) == 1 and tv and len(tv) == len(rec["pie"].split()):
                    start = sum(len(x[0].split()) for x in units[:pos] if x[4] is rec)
                    extra["token_variants"] = tv[start:start + len(pie.split())]
                seen = any(units[pos + j][4].get("seen_in_train") for j in range(n)) or None
                ns = len(sentences(pie))
                unit = "sentence" if ns == 1 else "paragraph"
                meta = _meta("translate_app", src, rec, mode=mode, unit=unit, sentences=ns, gloss_reference=has_gloss, style=t.get("style"), seen_in_train=seen,
                             accent=t.get("accent"), item=f"{sid}#{pos}" if both_directions else None, **extra)
                out.append({"messages": msgs, "meta": meta})
                stats[f"{mode}:{unit}"] += 1
            pos += n
        spans.append((sid, start, len(out)))
    if sessions:
        made, repl = 0, {}
        for sid, a, b in sorted(spans, key=lambda x: zlib.crc32(f"{x[0]}|sess".encode())):
            if made >= sessions:
                break
            new = app_sessions(sid, out[a:b], stats, sessions - made)
            k = sum(e["meta"]["task"] == "app_session" for e in new)
            if k:
                made += k
                repl[a] = (b, new)
        res, i = [], 0
        while i < len(out):
            if i in repl:
                b, new = repl[i]
                res += new
                i = b
            else:
                res.append(out[i])
                i += 1
        out = res
    return out


def app_sessions(sid: str, items: list[dict], stats: collections.Counter, limit: int = 1 << 30) -> list[dict]:
    """One text's translator items (in text order) with each run of adjacent en_pie items cut into sessions of
    APP_SESSION_LEN requests (crc32; a leftover single item stays as it is): one conversation, APP_SYSTEM, the
    items' own user and assistant turns in order, a follow-up user turn phrased by APP_FOLLOWUPS. Nothing new
    is said: every assistant turn is an item's app_format output. At most `limit` sessions."""
    out, i, made = [], 0, 0
    while i < len(items):
        run = 0
        while i + run < len(items) and items[i + run]["meta"]["mode"] == "en_pie":
            run += 1
        if run < 2 or made >= limit:
            out.append(items[i])
            i += 1
            continue
        j = i
        while j < i + run:
            n = min(APP_SESSION_LEN[_pick(f"{sid}|slen|{j}", len(APP_SESSION_LEN))], i + run - j)
            if n < 2 or made >= limit:
                out.append(items[j])
                j += 1
                continue
            grp = items[j:j + n]
            turns = []
            for k, e in enumerate(grp):
                eng, a = e["messages"][1]["content"], e["messages"][2]["content"]
                f = APP_FOLLOWUPS[_pick(f"{sid}|fu|{j + k}", len(APP_FOLLOWUPS))] if k else "{x}"
                turns += [("user", f.format(x=eng)), ("assistant", a)]
            ms = [e["meta"] for e in grp]
            srcs = {m["source_id"] for m in ms}
            meta = {"task": "app_session", "source_id": ms[0]["source_id"] if len(srcs) == 1 else sid,
                    **{k: v for k, v in ms[0].items() if k not in ("task", "source_id", "unit", "sentences",
                                                                    "acceptable", "token_variants", "coined",
                                                                    "neologism", "seen_in_train",
                                                                    "gloss_reference", "accent")},
                    "mode": "en_pie", "turns": 2 * n, "items": n, "sentences": sum(m["sentences"] for m in ms),
                    "gloss_reference": all(m.get("gloss_reference") for m in ms)}
            for k in ("coined", "neologism", "seen_in_train", "accent"):
                v = next((m[k] for m in ms if m.get(k)), None)
                if v is not None:
                    meta[k] = v
            if len(srcs) > 1:
                meta["source_ids"] = sorted(srcs)
            out.append({"messages": _msgs(system(f"session|{sid}|{made}", APP_SYSTEM), *turns), "meta": meta})
            stats[f"session:{n}"] += 1
            made += 1
            j += n
        i += run
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


_FIELD = re.compile(r"^(?:PIE|English|Gloss|Notes): ")


def _lines(text: str) -> list[str]:
    """A message's lines without a translator or gloss-line field label (`PIE: `, `English: `, ...), so n-grams
    never bridge a field."""
    return [_FIELD.sub("", x) for x in text.splitlines()]


def assistant_pie_turns(ex: dict) -> list[str] | None:
    """The PIE of each assistant turn, or None when the example says English or grammar: the PIE before an
    `English:` line (en_pie_gloss, demo_chat), the `PIE:` field (translate_app en_pie, app_session), the whole
    turn for the other PIE-output kinds."""
    m = ex["meta"]
    turns = [x["content"] for x in ex["messages"] if x["role"] == "assistant"]
    if m["task"] == "app_session" or (m["task"] == "translate_app" and m.get("mode") == "en_pie"):
        return [p for t in turns if (p := parse_app(t).get("PIE")) is not None]
    if m["task"] in PIE_OUT_KINDS:
        return [t.split("\nEnglish: ")[0] for t in turns]
    return None


def assistant_pie(ex: dict) -> str | None:
    """All the PIE an example's assistant turns say (assistant_pie_turns, joined), or None."""
    ts = assistant_pie_turns(ex)
    return " ".join(ts) if ts is not None else None


def leakage_report(train: list[dict], eval_: list[dict], train_text: str) -> dict:
    """Eval items must not reappear in train, even under another prompt template.

    Hard failures (the export raises): an eval source id that also has a train example; an eval (user,
    assistant) pair, or an eval assistant turn of >= 2 words, found verbatim in train; an eval assistant turn
    whose word 4-grams are >= 50% in train (PIE kinds only: English outputs share ordinary phrases). Eval
    items flagged seen_in_train (Tier 1 lines Tier 3 reuses on purpose, pie.export) are reported, not failed.
    A translator item (translate_app en_pie) is measured on its `PIE:` field, and also fails when that PIE is
    the whole PIE of a train assistant turn (assistant_pie); its inverse mode outputs English.
    Reported: the 4-gram overlap distribution per kind (all assistant turns, against every train message
    and the train plain text), and how many one-word answers (inflect, cognates_to_pie) occur as a word of
    the train plain text (a homograph, or a form shared across families)."""
    train_ids = {e["meta"]["source_id"] for e in train}
    train_pairs = {(_content(e, "user"), _content(e, "assistant")) for e in train}
    train_asst = {" ".join(_words(_content(e, "assistant"))) for e in train}
    train_pie = {" ".join(_words(p)) for e in train if (p := assistant_pie(e))}
    for e in train:          # a session's requests also count one by one (each is a translator item)
        if e["meta"]["task"] == "app_session":
            us = [x["content"] for x in e["messages"] if x["role"] == "user"]
            as_ = [x["content"] for x in e["messages"] if x["role"] == "assistant"]
            train_pairs |= set(zip(us, as_))
            train_asst |= {" ".join(_words(a)) for a in as_}
            train_pie |= {" ".join(_words(p)) for p in assistant_pie_turns(e)}
    grams: set = set()
    for e in train:
        for m in e["messages"]:
            if m["role"] != "system":
                for line in _lines(m["content"]):
                    grams |= _ngrams(_words(line))
    train_words: set = set()
    for para in train_text.split("\n\n"):
        ws = _words(para)
        grams |= _ngrams(ws)
        train_words.update(ws)
    english_out = {"translate_pie_en", "translate_app/pie_en"}
    per_kind: dict[str, dict] = {}
    failures, flagged = [], []
    for e in eval_:
        m, a = e["meta"], _content(e, "assistant")
        kind = f"{m['task']}/{m['mode']}" if m["task"] == "translate_app" else m["task"]
        ws = _words(a)
        # a translator turn's overlap is its PIE (an English gloss shares ordinary words)
        pie = parse_app(a).get("PIE") if kind == "translate_app/en_pie" else None
        g = _ngrams(_words(pie)) if pie is not None else _ngrams(ws)
        share = len(g & grams) / len(g) if g else None
        k = per_kind.setdefault(kind, {"n": 0, "with_ngrams": 0, "mean_overlap": 0.0, "max_overlap": 0.0,
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
        if pie is not None and len(_words(pie)) >= 2 and " ".join(_words(pie)) in train_pie:
            why.append("PIE verbatim in a train assistant turn")
        if share is not None and share >= 0.5 and kind not in english_out:
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


DIALOGUE_KINDS = ("pie_dialogue", "en_dialogue")
DEDUP_CAP = 3          # an assistant turn of a dialogue record is in at most this many dialogue-mode examples


def self_overlap(train: list[dict]) -> dict:
    """How often the same PIE is trained on as an assistant turn (the self-overlap of the modes).

    dialogue_turns: per (record, assistant turn) of the dialogue kinds, the number of dialogue-mode examples
    (pie_pie and the English modes) that have it; mode_plan caps it at DEDUP_CAP. all_kinds: per PIE sentence
    (normalized text) of every PIE-output kind (assistant_pie), the number of train examples whose assistant
    turns contain it (a single-sentence record is a translate_en_pie output and a translator item: 2 by
    design; a formula many records share counts once per example). ngram4: the same over word 4-grams."""
    turn = collections.Counter()
    sent: dict[str, set] = collections.defaultdict(set)
    gram: dict[tuple, set] = collections.defaultdict(set)
    for n, e in enumerate(train):
        m = e["meta"]
        if m["task"] in DIALOGUE_KINDS:
            for x in {x["content"].split("\nEnglish: ")[0] for x in e["messages"] if x["role"] == "assistant"}:
                turn[(m["source_id"], x)] += 1
        p = assistant_pie(e)
        if p:
            for x in sentences(p):
                sent[" ".join(_words(x))].add(n)
            for g in _ngrams(_words(p)):
                gram[g].add(n)

    def dist(counts) -> dict:
        c = list(counts)
        h = collections.Counter(min(x, 4) for x in c)
        return {"items": len(c), "max": max(c, default=0), "mean": round(sum(c) / len(c), 4) if c else 0.0,
                "histogram": {("4+" if k == 4 else str(k)): v for k, v in sorted(h.items())},
                f"over_{DEDUP_CAP}": sum(x > DEDUP_CAP for x in c)}
    return {"cap": DEDUP_CAP, "dialogue_turns": dist(turn.values()),
            "all_kinds_sentences": dist(len(v) for v in sent.values()),
            "all_kinds_ngram4": dist(len(v) for v in gram.values())}


ENGLISH_INPUT = ("translate_en_pie", "translate_app/en_pie", "app_session", "en_dialogue", "demo_chat")
# Conversation is the model's purpose and sets the mix's size (select_mix); translation is practice, not the
# product (owner, 2026-10-30: the translator app is not this model). cognates_to_pie stays in chat/train.jsonl but
# not in the mix: a speaker doesn't know the daughter languages.
MIX_GROUPS = {
    "conversation": ("en_dialogue", "demo_chat", "pie_dialogue", "continuation"),
    "translation": ("translate_en_pie", "translate_app/en_pie", "app_session", "translate_pie_en", "translate_app/pie_en"),
    "grammar": ("gloss", "inflect", "paradigm"),
    "comparative": ("cognates_to_pie",),
}
# the recommended sampling mix (export/README.md "Mix"): share of training examples per group
TARGET_MIX = {"conversation": 0.20, "translation": 0.50, "grammar": 0.30, "comparative": 0.0}


def mix_key(ex: dict) -> str:
    m = ex["meta"]
    return f"{m['task']}/{m['mode']}" if m["task"] == "translate_app" else m["task"]


def mix_group(ex: dict) -> str:
    k = mix_key(ex)
    return next(g for g, ks in MIX_GROUPS.items() if k in ks)


def mix_table(exs: list[dict], tokens: dict | None = None) -> dict:
    """Examples (and content tokens, from token_stats' per-key counts) per mix group, with shares; the
    English-input share; the Tier 3b (neologism: true) share of the chat examples."""
    ex = collections.Counter(mix_group(e) for e in exs)
    out: dict = {"groups": {}}
    tok_by_group = collections.Counter()
    if tokens:
        for k, v in tokens.items():
            g = next((g for g, ks in MIX_GROUPS.items() if k in ks), None)
            if g and "tokens" in v:
                tok_by_group[g] += v["tokens"]
    tt = sum(tok_by_group.values())
    for g in MIX_GROUPS:
        row = {"examples": ex[g], "share": round(ex[g] / len(exs), 4) if exs else 0.0}
        if tt:
            row["tokens"] = tok_by_group[g]
            row["token_share"] = round(tok_by_group[g] / tt, 4)
        # the per-example sampling weight that reaches the target mix (TARGET_MIX) from this split's counts
        row["target_share"] = TARGET_MIX[g]
        row["sampling_weight"] = round(TARGET_MIX[g] / row["share"], 3) if row["share"] else None
        out["groups"][g] = row
    out["conversation_share"] = out["groups"]["conversation"]["share"]
    eng = sum(mix_key(e) in ENGLISH_INPUT for e in exs)
    out["english_input_share"] = round(eng / len(exs), 4) if exs else 0.0
    neo = sum(e["meta"].get("neologism") is True for e in exs)
    out["tier3b_examples"] = neo
    out["tier3b_example_share"] = round(neo / len(exs), 4) if exs else 0.0
    return out


def select_mix(train: list[dict]) -> list[dict]:
    """chat/train_mix.jsonl: a subset of train in the TARGET_MIX proportions, without repeating an example (so
    the self-overlap cap holds). Every conversation example is kept and sets the size (conversation is TARGET_MIX's
    share of it); every other group keeps that size times its target share (or all it has), the ones with the
    lowest crc32 of their content, in train order."""
    by = collections.defaultdict(list)
    for e in train:
        by[mix_group(e)].append(e)
    total = len(by["conversation"]) / TARGET_MIX["conversation"]
    keep: set[int] = set()
    for g, t in TARGET_MIX.items():
        n = min(len(by[g]), round(total * t))
        ranked = sorted(by[g], key=lambda e: zlib.crc32(json.dumps(e["messages"], ensure_ascii=False).encode()))
        keep |= {id(e) for e in ranked[:n]}
    return [e for e in train if id(e) in keep]


def user_turns(ex: dict) -> int:
    return sum(m["role"] == "user" for m in ex["messages"])


CHAINED_KINDS = ("app_session", "demo_chat")       # a user's chained requests, not a conversation


def multi_turn_source(ex: dict) -> str:
    """dialogue (the exchanges of a dialogue text: each reply answers what was said), chained (CHAINED_KINDS:
    requests one after another), or other."""
    t = ex["meta"]["task"]
    return "dialogue" if t in DIALOGUE_KINDS else "chained" if t in CHAINED_KINDS else "other"


def turn_table(exs: list[dict]) -> dict:
    """User turns per example (1, 2, 3, 4+) per kind/mode, and the multi-turn (>= 2 user turns) examples by
    source (multi_turn_source) with their share of all examples."""
    by: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    src = collections.Counter()
    for e in exs:
        u = user_turns(e)
        m = e["meta"]
        by[f"{m['task']}/{m['mode']}" if m.get("mode") else m["task"]]["4+" if u >= 4 else str(u)] += 1
        if u >= 2:
            src[multi_turn_source(e)] += 1
    n = sum(src.values())
    return {"user_turns": {k: dict(sorted(v.items())) for k, v in sorted(by.items())},
            "multi_turn": {"examples": n, "share": round(n / len(exs), 4) if exs else 0.0,
                           "by_source": dict(sorted(src.items())),
                           "chained_share_of_multi_turn": round(src["chained"] / n, 4) if n else 0.0}}


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
        by_key: dict[str, dict] = {}
        neo = {"examples": 0, "words": 0, "tokens": 0}
        for e in exs:
            new = lambda: {"examples": 0, "words": 0, "tokens": 0, "assistant_tokens": 0}
            ks = [kinds.setdefault(e["meta"]["task"], new())]
            if mix_key(e) != e["meta"]["task"]:
                ks.append(by_key.setdefault(mix_key(e), new()))
            is_neo = e["meta"].get("neologism") is True
            for k in ks:
                k["examples"] += 1
            neo["examples"] += is_neo
            for m in e["messages"]:
                w = len(m["content"].split())
                n = next(lens) if lens else 0
                for k in ks:
                    k["words"] += w
                    k["tokens"] += n
                    k["assistant_tokens"] += n if m["role"] == "assistant" else 0
                if is_neo:
                    neo["words"] += w
                    neo["tokens"] += n
        if not enc:
            for k in [*kinds.values(), *by_key.values()]:
                k.pop("tokens"), k.pop("assistant_tokens")
            neo.pop("tokens")
        out[split] = dict(sorted(kinds.items()))
        out[f"{split}_by_mode"] = dict(sorted(by_key.items()))
        out[f"{split}_tier3b"] = neo
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
    app = {"train": collections.Counter(), "eval": collections.Counter()}
    chat = {}
    for split in ("train", "eval"):
        tasks, records = d[f"{split}_tasks"], d[f"{split}_records"]
        exs = [task_chat(t, recs.get(t.get("source_id"))) for t in tasks]
        exs += paradigm_chats(lx, tasks)
        exs += dialogue_chats(records, skipped[split], align[split])
        exs += continuation_chats(records)
        en_tasks = {t["source_id"]: t for t in tasks if t["task"] == "translate_en_pie"}
        demos = demo_chats(seeds, records, lx, demo_skipped) if split == "train" else []
        # chained requests (demo seeds, app sessions) stay <= APP_SESSION_SHARE of the multi-turn examples: the
        # multi-turn data is conversation (dialogue exchanges), not a talking dictionary
        multi = collections.Counter(multi_turn_source(e) for e in exs + demos if user_turns(e) >= 2)
        budget = max(0, int(multi["dialogue"] * APP_SESSION_SHARE / (1 - APP_SESSION_SHARE)) - multi["chained"]) \
            if split == "train" else 0
        exs += app_chats(records, app[split], en_tasks, sessions=budget)
        if split == "train":
            exs += demos
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
    tr = build_translator(d, chat)
    neo = neologism_share(d["train_records"])
    if neo["exceeded"]:
        print(f"WARNING: Tier 3b neologism share {neo['share']:.1%} of training words exceeds the "
              f"{NEOLOGISM_CAP:.0%} cap (PLAN.md)", file=sys.stderr)
    return {"chat": chat, "text": text, "leakage": leak, "neologism": neo, "self_overlap": self_overlap(chat["train"]),
            "translator": tr,
            "translate_app": {k: dict(sorted(v.items())) for k, v in app.items()},
            "dialogue_skipped": {k: dict(v) for k, v in skipped.items()},
            "alignment": {k: dict(sorted(v.items())) for k, v in align.items()},
            "demo_seeds": {"seeds": len(seeds), "used": sum(e["meta"]["task"] == "demo_chat" for e in chat["train"]),
                           "skipped": dict(sorted(demo_skipped.items()))},
            "chat_eval": {"reserved_records": len(d.get("eval_dialogue_records", [])),
                          "held_dialogues": str(HELD_DIALOGUES.relative_to(HELD_DIALOGUES.parents[2]))}}


def build_translator(d: dict, chat: dict[str, list[dict]]) -> dict:
    """export/translator/: the translation app's dataset, translate_app items in both directions (app_chats
    both_directions): every item once as en_pie and once as pie_en, paired by meta.item. Separate from the
    chat model's data (chat/train.jsonl keeps one inverse item in APP_INVERSE_EVERY): PIE -> English is for the
    app only. The same split (train records -> train, eval records -> eval); leakage is checked against the
    translator's train and the chat train together (a model trained on both must not see an eval item). Raises
    on leakage."""
    stats = {"train": collections.Counter(), "eval": collections.Counter()}
    exs = {}
    for split in ("train", "eval"):
        en_tasks = {t["source_id"]: t for t in d[f"{split}_tasks"] if t["task"] == "translate_en_pie"}
        xs = app_chats(d[f"{split}_records"], stats[split], en_tasks, both_directions=True)
        random.Random(f"translator-{split}").shuffle(xs)
        for n, e in enumerate(xs):
            e["meta"]["id"] = f"translator-{split}-{n:06d}"
        exs[split] = xs
    leak = leakage_report(exs["train"] + chat["train"], exs["eval"], "")
    if not leak["ok"]:
        raise ValueError(f"translator eval leakage: {len(leak['failures'])} items, e.g. {leak['failures'][:3]}")
    return {"examples": exs, "stats": {k: dict(sorted(v.items())) for k, v in stats.items()}, "leakage": leak,
            "self_overlap": self_overlap(exs["train"])}


def write_translator(c: dict, out: Path, provenance: dict | None = None) -> dict:
    """Write export/translator/{train,eval}.jsonl + summary.json from build_chat's translator."""
    t = c["translator"]
    (out / "translator").mkdir(parents=True, exist_ok=True)
    for split, exs in t["examples"].items():
        (out / "translator" / f"{split}.jsonl").write_text(
            "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in exs), "utf-8")
    so = t["self_overlap"]
    summary = {
        "provenance": provenance or {},
        "examples": {s: len(v) for s, v in t["examples"].items()},
        "modes": {s: dict(sorted(collections.Counter(e["meta"]["mode"] for e in v).items()))
                  for s, v in t["examples"].items()},
        "units": {s: dict(sorted(collections.Counter(f"{e['meta']['mode']}:{e['meta']['unit']}" for e in v).items()))
                  for s, v in t["examples"].items()},
        "gloss_reference": {s: sum(bool(e["meta"].get("gloss_reference")) for e in v)
                            for s, v in t["examples"].items()},
        "neologism_examples": {s: sum(e["meta"].get("neologism") is True for e in v)
                               for s, v in t["examples"].items()},
        # per split: items per mode and unit, and the records app_chats could not use
        "items": t["stats"],
        # assistant turns only: the PIE of the en_pie outputs (a pie_en item says that PIE as its input)
        "self_overlap": {"all_kinds_sentences": so["all_kinds_sentences"], "all_kinds_ngram4": so["all_kinds_ngram4"]},
        "leakage": t["leakage"],
    }
    (out / "translator" / "summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n",
                                                     "utf-8")
    return summary


def write_chat(d: dict, out: Path, tokenizer: str | None = None, provenance: dict | None = None,
               lx=None) -> dict:
    """Write export/chat/{train,eval}.jsonl + summary.json, export/text/, export/text-ascii/ and export/translator/.
    The returned summary carries the translator's summary under "translator" (not in chat/summary.json)."""
    c = build_chat(d, lx)
    (out / "chat").mkdir(parents=True, exist_ok=True)
    mix = select_mix(c["chat"]["train"])
    for name, exs in (*c["chat"].items(), ("train_mix", mix)):
        (out / "chat" / f"{name}.jsonl").write_text(
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
        "english_input_conversations": {s: sum(e["meta"]["task"] in ("en_dialogue", "demo_chat") for e in v)
                                        for s, v in c["chat"].items()},
        # translate_app items per mode and unit, and the records it could not use (no English; a long record
        # whose English does not align sentence by sentence; a gloss without one word per PIE word)
        "translate_app": c["translate_app"],
        "self_overlap": c["self_overlap"],
        "demo_seeds": c["demo_seeds"],
        "chat_eval": {**c["chat_eval"], "examples": dict(sorted(collections.Counter(
            f"{e['meta']['task']}/{e['meta']['mode']}" for e in c["chat"]["eval"] if e["meta"].get("chat_eval")).items()))},
        "neologism": c["neologism"],
        "leakage": c["leakage"],
        "tokens": token_stats(c["chat"], texts, tokenizer),
    }
    tk = summary["tokens"]
    summary["mix"] = {s: mix_table(v, {**tk.get(s, {}), **tk.get(f"{s}_by_mode", {})}) for s, v in c["chat"].items()}
    summary["turns"] = {**{s: turn_table(v) for s, v in c["chat"].items()}, "train_mix": turn_table(mix)}
    tm = token_stats({"train_mix": mix}, {}, tokenizer)
    summary["mix"]["train_mix"] = {**mix_table(mix, {**tm["train_mix"], **tm["train_mix_by_mode"]}), "examples": len(mix),
                                   "examples_by_kind": dict(sorted(collections.Counter(mix_key(e) for e in mix).items()))}
    for name in ("train", "eval"):
        ta, tu = summary["tokens"].get(f"text-ascii/{name}.txt", {}), summary["tokens"].get(f"text/{name}.txt", {})
        if "tokens_per_word" in tu:
            summary["tokens"][f"{name}_tokens_per_word_unicode_vs_ascii"] = [tu["tokens_per_word"],
                                                                             ta["tokens_per_word"]]
    (out / "chat" / "summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n", "utf-8")
    summary["translator"] = write_translator(c, out, provenance)
    return summary
