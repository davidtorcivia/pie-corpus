"""The chat / plain-text export layer (pie/export_chat.py), through the production path scripts/export.py."""

import collections
import json
import runpy
import sys
from pathlib import Path

import pytest

import pie.export_chat as ec

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def exported(tmp_path_factory):
    """scripts/export.py main() into a temporary export/ (the real corpus, the real build)."""
    tmp = tmp_path_factory.mktemp("exp")
    (tmp / "export").mkdir()
    main = runpy.run_path(str(ROOT / "scripts/export.py"))["main"]
    main.__globals__["ROOT"] = tmp
    argv, sys.argv = sys.argv, ["export.py"]
    try:
        assert main() == 0
    finally:
        sys.argv = argv
    out = tmp / "export"
    load = lambda p: [json.loads(x) for x in (out / p).read_text("utf-8").splitlines()]
    return {"out": out, "train": load("chat/train.jsonl"), "eval": load("chat/eval.jsonl"),
            "train_mix": load("chat/train_mix.jsonl"),
            "train_tasks": load("train_tasks.jsonl"), "eval_tasks": load("eval_tasks.jsonl"),
            "train_records": load("train.jsonl"), "eval_records": load("eval.jsonl"),
            "eval_dialogues": load("eval_dialogues.jsonl"),
            "summary": json.loads((out / "chat/summary.json").read_text("utf-8"))}


def test_messages_are_trainer_neutral(exported):
    for split in ("train", "eval"):
        for e in exported[split]:
            roles = [m["role"] for m in e["messages"]]
            assert set(e) == {"messages", "meta"}
            assert all(set(m) == {"role", "content"} and isinstance(m["content"], str) and m["content"].strip()
                       for m in e["messages"])
            body = roles[1:] if roles[0] == "system" else roles
            assert "system" not in body
            assert body == ["user", "assistant"] * (len(body) // 2) and body, roles
            assert {"task", "source_id", "tier", "id"} <= set(e["meta"])
            assert "<|" not in json.dumps(e)          # no model template baked in


def test_task_conversations_are_the_task_views(exported):
    """Every task becomes one conversation whose assistant turn is the task's exact output, in its split."""
    for split in ("train", "eval"):
        tasks = exported[f"{split}_tasks"]
        chats = [e for e in exported[split] if e["meta"]["task"] in {t["task"] for t in tasks}]
        assert collections.Counter((e["meta"]["task"], e["meta"]["source_id"], e["messages"][-1]["content"])
                                   for e in chats) == \
            collections.Counter((t["task"], t["source_id"], t["output"]) for t in tasks)
    # several paraphrased templates per task are in use
    for task, tpls in ec.TASK_TEMPLATES.items():
        used = {e["meta"]["template"] for e in exported["train"] if e["meta"]["task"] == task}
        assert len(used) == len(tpls), task


def test_hold_out(exported):
    """Eval = the eval task views (Tier 1, eval-grade Tier 2, held families) and texts of eval records only;
    no eval source reappears in train under any kind or template; a paradigm follows its lexeme's
    inflection split; a project reconstruction never reaches eval."""
    tr = {e["meta"]["source_id"] for e in exported["train"]}
    ev = {e["meta"]["source_id"] for e in exported["eval"]}
    assert not tr & ev
    eval_ids = {r["id"] for r in exported["eval_records"]} | {r["work_id"] for r in exported["eval_records"]} | \
        {t["source_id"] for t in exported["eval_tasks"]} | {r["id"] for r in exported["eval_dialogues"]}
    assert ev <= eval_ids
    for split in ("train", "eval"):
        infl = {t["source_id"] for t in exported[f"{split}_tasks"] if t["task"] == "inflect"}
        par = {e["meta"]["source_id"] for e in exported[split] if e["meta"]["task"] == "paradigm"}
        assert par <= infl and len(par) > 0.9 * len(infl)
    assert not any(e["meta"].get("coined") for e in exported["eval"])
    assert exported["summary"]["leakage"]["ok"] and not exported["summary"]["leakage"]["failures"]
    assert all(f["task"] for f in exported["summary"]["leakage"]["flagged_seen_in_train"])


def test_kinds_and_summary(exported):
    s = exported["summary"]
    for split in ("train", "eval"):
        c = collections.Counter(e["meta"]["task"] for e in exported[split])
        assert s["examples_by_kind"][split] == dict(sorted(c.items()))
        assert s["examples"][split] == len(exported[split])
    c = s["examples_by_kind"]["train"]
    assert c["pie_dialogue"] and c["continuation"] and c["paradigm"] and c["demo_chat"]
    # English input is first-class: every aligned, non-narrated dialogue gets en_pie and en_pie_gloss
    aligned = sum(v for k, v in s["dialogue_english_alignment"]["train"].items() if k.startswith("aligned:"))
    assert s["modes"]["train"]["en_dialogue/en_pie"] == aligned
    by = collections.defaultdict(set)
    for e in exported["train"]:
        if e["meta"]["task"] in ec.DIALOGUE_KINDS:
            by[e["meta"]["source_id"]].add(e["meta"]["mode"])
    assert sum({"en_pie", "en_pie_gloss"} <= v for v in by.values()) == aligned
    assert s["english_input_conversations"]["train"] == c["en_dialogue"] + c["demo_chat"] >= 300
    assert {m.split("/")[1] for m in s["modes"]["train"]} == {"pie_pie", *ec.EN_MODES, "pie_en"}
    # pie_pie: the dialogues without English input, plus the whole of one aligned dialogue in PIE_PIE_EVERY
    # (the same exchanges as its English-input modes); still fewer than the English-input dialogues
    doubled = sum(ec._pick(sid + "|pp", ec.PIE_PIE_EVERY) == 0 for sid, v in by.items() if "en_pie" in v)
    pp = [e for e in exported["train"] if e["meta"]["task"] == "pie_dialogue"]
    assert sum(by[e["meta"]["source_id"]] >= {"en_pie", "pie_pie"} for e in pp) == doubled > 0.3 * aligned
    assert s["modes"]["train"]["pie_dialogue/pie_pie"] < c["en_dialogue"]
    assert 30 <= s["demo_seeds"]["used"] <= 60
    assert s["examples_by_kind"]["eval"]["continuation"]      # Tier 1 works continued
    assert set(s["pie_dialogue_split_method"]["train"]) <= {"speaker", "english_quotes", "sentence_qa"}
    assert s["neologism"]["share"] <= ec.NEOLOGISM_CAP
    assert s["provenance"]["include_pilot"] is False


def test_pie_only_conversations(exported):
    recs = {r["id"]: r for r in exported["train_records"]}
    for e in exported["train"]:
        m = e["meta"]
        if m["task"] == "pie_dialogue":
            assert "Proto-Indo-European" in e["messages"][0]["content"] or "PIE" in e["messages"][0]["content"]
            turns = [x["content"] for x in e["messages"][1:]]
            # the turns are the record's PIE, in order: the whole minus at most a dropped trailing question, or a
            # window of its exchanges
            pie = recs[m["source_id"]]["pie"]
            assert pie.startswith(" ".join(turns)) if not m.get("window") else " ".join(turns) in pie
            assert m["split"] in ("speaker", "english_quotes", "sentence_qa") and m["genre"] in ec.DIALOGUE_GENRES
        elif m["task"] == "en_dialogue":
            r = recs[m["source_id"]]
            assert e["messages"][0]["content"] == ec.MODE_SYSTEM[m["mode"]]
            en = ec.align_english(r)[0]
            for x in e["messages"][2::2]:            # the assistant always speaks PIE
                pie, _, eng = x["content"].partition("\nEnglish: ")
                assert pie in r["pie"] and (eng in " ".join(en)) and bool(eng) == (m["mode"] == "en_pie_gloss")
            users = [x["content"] for x in e["messages"][1::2]]
            langs = m.get("user_langs") or ["en"] * len(users)
            assert len(langs) == len(users) and (m["mode"] == "mixed") == (len(set(langs)) == 2)
            for u, lang in zip(users, langs):
                assert (u in r["pie"]) == (lang == "pie")
        elif m["task"] == "continuation" and m["tier"] != 1:
            r = recs[m["source_id"]]
            opening = e["messages"][1]["content"]
            assert e["messages"][2]["content"] in r["pie"] and r["genre"] in ec.CONTINUATION_GENRES
            assert r["pie"].endswith(e["messages"][2]["content"])
            assert any(s in opening for s in ec.sentences(r["pie"])[:1])


def test_text_views(exported):
    out = exported["out"]
    for split in ("train", "eval"):
        uni = (out / f"text/{split}.txt").read_text("utf-8").split("\n\n")
        asc = (out / f"text-ascii/{split}.txt").read_text("utf-8").split("\n\n")
        assert len(uni) == len(asc) == len(ec._texts(exported[f"{split}_records"]))
        assert all(p.strip() and "\n" not in p.strip() for p in uni)
    train_txt = (out / "text/train.txt").read_text("utf-8")
    for r in exported["eval_records"]:
        if not r["seen_in_train"] and len(r["pie"].split()) >= 3:
            assert r["pie"] not in train_txt
    # a Tier 1 work is one paragraph, in line order
    eval_txt = (out / "text/eval.txt").read_text("utf-8")
    work = sorted((r for r in exported["eval_records"] if r["work_id"] == "schleicher-fable-byrd-2013"),
                  key=lambda r: r["line_no"])
    assert " ".join(r["pie"] for r in work) in eval_txt.split("\n\n")


def test_flags_carried_into_meta(exported):
    recs = {r["id"]: r for r in exported["train_records"]}
    tasks = {(t["task"], t["source_id"], t["output"]): t for t in exported["train_tasks"]}
    n_acc = 0
    for e in exported["train"]:
        m = e["meta"]
        t = tasks.get((m["task"], m["source_id"], e["messages"][-1]["content"]))
        if t:
            for k in ("accent", "coined", "num_fallback"):
                assert m.get(k) == t.get(k), (k, m)
            n_acc += bool(t.get("accent"))
        r = recs.get(m["source_id"])
        if r:
            assert m.get("meter") == (r.get("meter") or None)
            assert m.get("neologism") == (True if r.get("neologism") is True else None)
    assert n_acc


# ---------------------------------------------------------------- unit tests (synthetic records)


def _rec(pie, english="", genre="dialogue", clauses=None, **kw):
    r = {"id": kw.pop("id", "t3-x-1"), "tier": 3, "pie": pie, "pie_ascii": pie, "english": english,
         "genre": genre, "tokens": []}
    if clauses is not None:
        r["generator"] = {"plan": {"clauses": clauses}}
    return {**r, **kw}


def test_dialogue_speaker_field_wins():
    c = [{"break": True, "speaker": "A", "question": True}, {"break": True, "speaker": "B"},
         {"break": True, "speaker": "B"}, {"break": True, "speaker": "A"}]
    turns, method, dropped = ec.dialogue_turns(_rec("kʷís h₁ési? h₁ésmi. h₁ésmi. h₁ési.", clauses=c))
    assert method == "speaker" and [r for r, _ in turns] == ["user", "assistant"] and dropped == 1
    c3 = [dict(x, speaker=s) for x, s in zip(c, "ABCA")]
    assert ec.dialogue_turns(_rec("a? b. c. d.", clauses=c3))[:2] == (None, "speaker_count")


def test_dialogue_qa_heuristic_is_conservative():
    turns, method, _ = ec.dialogue_turns(_rec("ḱludʰí. kʷís h₁ési? h₁ésmi wiHrós. kʷíd? nu."))
    assert method == "sentence_qa"
    assert turns == [("user", [0, 1]), ("assistant", [2]), ("user", [3]), ("assistant", [4])]
    # '?' disagreeing with the plan's question flag: skipped
    c = [{"break": True}, {"break": True}]
    assert ec.dialogue_turns(_rec("kʷís h₁ési? h₁ésmi.", clauses=c))[:2] == (None, "question_flag_mismatch")
    assert ec.dialogue_turns(_rec("h₁ésmi. h₁ési."))[:2] == (None, "no_question")
    assert ec.dialogue_turns(_rec("kʷís h₁ési?"))[:2] == (None, "no_answer")


def _d(train_records=(), eval_records=(), train_tasks=(), eval_tasks=()):
    return {"train_records": list(train_records), "eval_records": list(eval_records),
            "train_tasks": list(train_tasks), "eval_tasks": list(eval_tasks)}


def test_neologism_cap_warns_and_flags(capsys):
    neo = _rec("néwos wóyḱos h₁ésti.", "It is a new house.", genre="household", id="t3b-1", neologism=True)
    old = _rec("h₁éḱwos.", "A horse.", genre="household", id="t3-2")
    from pie.export import record_tasks
    d = _d([neo, old], train_tasks=record_tasks(neo) + record_tasks(old))
    c = ec.build_chat(d, lx=object())
    assert c["neologism"]["exceeded"] and c["neologism"]["share"] == 0.75
    assert "exceeds the 15% cap" in capsys.readouterr().err
    assert {e["meta"].get("neologism") for e in c["chat"]["train"] if e["meta"]["source_id"] == "t3b-1"} == {True}


def test_paraphrased_eval_item_in_train_fails():
    """The same eval item under another template (a paraphrase) in train is leakage."""
    t = {"task": "translate_pie_en", "input": "h₁éḱwōs tréxonti", "output": "Horses run.", "source_id": "t1-x"}
    with pytest.raises(ValueError, match="chat eval leakage"):
        ec.build_chat(_d(train_tasks=[t], eval_tasks=[dict(t, input="h₁éḱwōs tréxonti.")]), lx=object())
    ok = ec.build_chat(_d(train_tasks=[dict(t, source_id="t3-y", output="Other.")], eval_tasks=[t]), lx=object())
    assert ok["leakage"]["ok"]


def test_ngram_overlap_check():
    tr = [{"messages": [{"role": "user", "content": "x"}, {"role": "assistant", "content": "a b c d e"}],
           "meta": {"task": "continuation", "source_id": "s1"}}]
    ev = [{"messages": [{"role": "user", "content": "y"}, {"role": "assistant", "content": "a b c d e f"}],
           "meta": {"task": "continuation", "source_id": "s2"}}]
    r = ec.leakage_report(tr, ev, "")
    assert not r["ok"] and r["per_kind"]["continuation"]["max_overlap"] == pytest.approx(2 / 3, abs=1e-4)
    ev[0]["meta"]["seen_in_train"] = True               # deliberate formula reuse: reported, not failed
    r = ec.leakage_report(tr, ev, "")
    assert r["ok"] and r["flagged_seen_in_train"]


def test_templates_are_deterministic_and_features_described():
    assert ec._pick("translate_en_pie|t3-x|horse", 5) == ec._pick("translate_en_pie|t3-x|horse", 5)
    assert ec.describe_features("PRS.3SG") == "present third person singular"
    assert ec.describe_features("F.NOM.SG") == "feminine nominative singular"
    assert ec.describe_features("MID.AOR.1PL") == "middle aorist first person plural"


def test_conversational_eval_reservation(exported):
    """The frozen reservation (data/export/held_dialogues.json): those records are out of every train view and
    are eval conversations in every mode."""
    held = json.loads((ROOT / "data/export/held_dialogues.json").read_text("utf-8"))
    ids = set(held["records"])
    assert ec.held_dialogue_ids() == ids and len(ids) >= 10
    assert {r["id"] for r in exported["eval_dialogues"]} == ids          # all present while the batch is admitted
    assert not ids & {r["id"] for r in exported["train_records"]}
    assert not ids & {t["source_id"] for t in exported["train_tasks"]}
    assert not ids & {e["meta"]["source_id"] for e in exported["train"]}
    assert not ids & {t["source_id"] for t in exported["eval_tasks"]}     # chat only, not a task benchmark
    train_txt = (exported["out"] / "text/train.txt").read_text("utf-8")
    assert not any(r["pie"] in train_txt for r in exported["eval_dialogues"])
    ce = [e for e in exported["eval"] if e["meta"].get("chat_eval")]
    assert {e["meta"]["source_id"] for e in ce} == ids
    assert {e["meta"]["mode"] for e in ce} == {"pie_pie", *ec.EN_MODES}
    by = collections.Counter(e["meta"]["source_id"] for e in ce if e["meta"]["mode"] == "en_pie")
    assert set(by.values()) == {1} and len(by) == len(ids)             # every record aligns: an en_pie eval each
    assert exported["summary"]["chat_eval"]["reserved_records"] == len(ids)


def test_demo_seeds_are_corpus_or_engine_forms(exported):
    """Every demo answer is a sentence of a training record or an engine cell of a lexicon or neologism entry:
    never invented text."""
    from pie.neologism import with_neologisms
    from pie.realize import Lexicon
    nx = with_neologisms(Lexicon.load())
    train_pie = " ".join(r["pie"] for r in exported["train_records"])
    demos = [e for e in exported["train"] if e["meta"]["task"] == "demo_chat"]
    assert demos and not [e for e in exported["eval"] if e["meta"]["task"] == "demo_chat"]
    for e in demos:
        for x in e["messages"][2::2]:
            pie = x["content"].split("\nEnglish: ")[0]
            if len(pie.split()) > 1:
                assert pie in train_pie, pie
            else:
                lid = None
                for sd in ec.load_demo_seeds():
                    if sd["id"] == e["meta"]["seed"]:
                        lid = {t["answer"].get("lexeme") or t["answer"].get("neologism") for t in sd["turns"]}
                forms = {f for l in lid if l for v in nx.admissible_cells(l).values() for f in v}
                assert pie.rstrip(".") in forms or pie in train_pie, pie
        if any(sd["id"] == e["meta"]["seed"] and any("neologism" in t["answer"] for t in sd["turns"])
               for sd in ec.load_demo_seeds()):
            assert e["meta"]["coined"] == "neologism" and e["meta"]["neologism"] is True


# ---------------------------------------------------------------- English alignment (synthetic)


def test_align_english_splits_and_never_guesses():
    r = _rec("kʷís h₁ési? h₁ésmi wiHrós. nu h₁éymi.", "'Who are you?' 'I am a man. Now I go.'")
    assert ec.align_english(r) == (["Who are you?", "I am a man.", "Now I go."], "quotes")
    r = _rec("nu só wérh₁t. kʷís h₁ési? h₁ésmi.", 'Then he said: "Who are you?" "I am."')
    en, how = ec.align_english(r)
    assert how == "quotes_colon" and en == ["Then he said:", "Who are you?", "I am."] and ec.narrated(en)
    r = _rec("kʷíd h₁ésti? ne h₁ésti. gʷémt.", "What is it? It is not; it comes.")
    assert ec.align_english(r)[1] == "semicolon"
    # sentence counts that never agree, or questions on other sentences: skipped
    assert ec.align_english(_rec("kʷís h₁ési? h₁ésmi.", "Who are you? I am. I go."))[0] is None
    assert ec.align_english(_rec("kʷís h₁ési? h₁ésmi.", "Who are you. I am?")) == (None, "question_mismatch")
    # the 3b brief's turn markers are not English text
    r = _rec("kʷís h₁ési? h₁ésmi.", "User: Who are you? Model: I am.")
    assert ec.align_english(r)[0] == ["Who are you?", "I am."]


def test_quoted_speeches_are_turns():
    """An English that is only quoted speeches: each speech is a turn, speakers alternating (sentence_qa would
    have joined the asker's next line to the reply)."""
    r = _rec("kʷís h₁ésti? h₁ésmi gʰóstis. ph₃dʰí. kʷís h₁ési? h₁ésmi pótis.",
             "'Who is it?' 'I am a guest.' 'Drink!' 'Who are you?' 'I am the master.'")
    turns, method, dropped = ec.dialogue_turns(r)
    assert method == "english_quotes" and dropped == 1
    assert turns == [("user", [0]), ("assistant", [1]), ("user", [2]), ("assistant", [3])]
    # narration outside the quotes: not a pure exchange of speeches, the heuristic decides
    r = _rec("nu só wérh₁t. kʷís h₁ési? h₁ésmi.", 'Then he said: "Who are you?" "I am."')
    assert ec.dialogue_turns(r)[1] == "sentence_qa"
    # an apostrophe is not a quote
    r = _rec("kʷís h₁ési? h₁ésmi.", "'Whose son's son are you?' 'I am the king's.'")
    assert ec.dialogue_turns(r)[1] == "english_quotes"


def test_plan_english_field_wins():
    """The optional per-sentence plan field (planner-brief-v4.md): english on each sentence-initial clause."""
    c = [{"english": "Who are you?", "question": True}, {"break": True, "english": "I am a man; I go."}]
    r = _rec("kʷís h₁ési? h₁ésmi wiHrós h₁éymi-kʷe.", "Who are you? I am a man; I go.", clauses=c)
    assert ec.align_english(r) == (["Who are you?", "I am a man; I go."], "plan_english")
    c[1]["english"] = "I am a man?"
    assert ec.align_english(r) == (None, "plan_english_mismatch")


def test_english_modes_deterministic():
    c = [{"break": True, "speaker": s, "question": s == "user"} for s in ("user", "model", "user", "model")]
    r = _rec("kʷís h₁ési? h₁ésmi. kúdʰe h₁éysi? h₁éymi wóyḱom.",
             "Who are you? I am. Where are you going? I am going home.", clauses=c, id="t3b-x-1")
    one = ec.dialogue_chats([r], collections.Counter())
    assert one == ec.dialogue_chats([r], collections.Counter())
    # two exchanges, a doubled record: en_pie, en_pie_gloss and pie_pie, each the whole dialogue (mode_plan)
    assert [(e["meta"]["mode"], e["meta"].get("window")) for e in one] == \
        [("en_pie", None), ("en_pie_gloss", None), ("pie_pie", None)]
    assert [m["content"] for m in one[2]["messages"][1:]] == ["kʷís h₁ési?", "h₁ésmi.", "kúdʰe h₁éysi?",
                                                               "h₁éymi wóyḱom."]
    assert [m["content"] for m in one[0]["messages"][2::2]] == [m["content"] for m in one[2]["messages"][2::2]]
    allm = ec.dialogue_chats([r], collections.Counter(), all_modes=True, chat_eval=True)
    assert [e["meta"]["mode"] for e in allm] == ["pie_pie", *ec.EN_MODES]
    assert all(e["meta"]["chat_eval"] for e in allm)
    en_pie = allm[1]["messages"]
    assert en_pie[0] == {"role": "system", "content": "Reply in Proto-Indo-European."}
    assert [m["content"] for m in en_pie[1:]] == ["Who are you?", "h₁ésmi.", "Where are you going?", "h₁éymi wóyḱom."]
    assert allm[2]["messages"][2]["content"] == "h₁ésmi.\nEnglish: I am."
    mixed = allm[3]
    assert sorted(mixed["meta"]["user_langs"]) == ["en", "pie"]
    # a single-question dialogue has no mixed mode
    r1 = _rec("kʷís h₁ési? h₁ésmi.", "Who are you? I am.", id="t3-y-1")
    assert [e["meta"]["mode"] for e in ec.dialogue_chats([r1], collections.Counter(), all_modes=True)] == \
        ["pie_pie", "en_pie", "en_pie_gloss"]


# ---------------------------------------------------------------- the rebalance and the translator


def test_mode_plan_caps_each_turn_at_three():
    n_doubled = 0
    for rid in (f"t3-x-{i}" for i in range(40)):
        for k in range(1, 9):
            plan = ec.mode_plan(rid, k)
            doubled = ("pie_pie", (0, k)) in plan
            n_doubled += doubled
            assert plan[0] == ("en_pie", (0, k)) and plan[1][0] == "en_pie_gloss"
            assert doubled == (ec._pick(rid + "|pp", ec.PIE_PIE_EVERY) == 0)
            cover = collections.Counter(i for _m, (a, b) in plan for i in range(a, b))
            assert set(cover) == set(range(k)) and max(cover.values()) <= ec.DEDUP_CAP == 3
            assert set(cover.values()) == ({3} if doubled or k in (2, 3) else {2})
            # a dialogue stays multi-turn: a window has two or more exchanges whenever k allows it
            assert all(b - a >= min(2, k) for _m, (a, b) in plan)
            assert all(m != "mixed" or b - a >= 2 for m, (a, b) in plan)
    assert 0.3 < n_doubled / (40 * 8) < 0.7
    assert [m for m, _ in ec.mode_plan("x", 2)] == ["en_pie", "en_pie_gloss", "mixed"]
    assert [m for m, _ in ec.mode_plan("y", 2)] == ["en_pie", "en_pie_gloss", "pie_pie"]
    assert ec.mode_plan("y", 5) == [("en_pie", (0, 5)), ("en_pie_gloss", (2, 5)), ("mixed", (0, 2)),
                                    ("pie_pie", (0, 5))]


def test_self_overlap_cap_holds(exported):
    so = exported["summary"]["self_overlap"]
    assert so["cap"] == ec.DEDUP_CAP == 3
    assert so["dialogue_turns"]["max"] <= ec.DEDUP_CAP and so["dialogue_turns"][f"over_{ec.DEDUP_CAP}"] == 0
    assert so["dialogue_turns"]["histogram"]["3"]          # the doubled dialogues reach the cap
    assert so["dialogue_turns"]["items"] > 300
    # every dialogue example's assistant turns, counted directly
    c = collections.Counter()
    for e in exported["train"]:
        if e["meta"]["task"] in ec.DIALOGUE_KINDS:
            for x in {m["content"].split("\nEnglish: ")[0] for m in e["messages"] if m["role"] == "assistant"}:
                c[(e["meta"]["source_id"], x)] += 1
    assert max(c.values()) <= ec.DEDUP_CAP


def test_app_format_round_trips():
    t = ec.app_format("h₁éḱwos.", "horse-NOM.SG", "a note.")
    assert t == "PIE: h₁éḱwos.\nGloss: horse-NOM.SG\nNotes: a note."
    assert ec.parse_app(t) == {"PIE": "h₁éḱwos.", "Gloss": "horse-NOM.SG", "Notes": "a note."}
    assert ec.parse_app(ec.app_format("x y.", None)) == {"PIE": "x y."}
    assert ec.parse_app(ec.app_inverse_format("A horse.", "horse-NOM.SG")) == {"English": "A horse.",
                                                                             "Gloss": "horse-NOM.SG"}


def test_app_items_partition_sentences_with_sliced_gloss():
    toks = [{"form": f} for f in ("kʷís", "h₁ési", "h₁ésmi", "wiHrós", "nu", "h₁éymi")]
    toks[3]["coined"] = "neologism"
    r = _rec("kʷís h₁ési? h₁ésmi wiHrós. nu h₁éymi.", "Who are you? I am a man. Now I go.", id="t3-z-1",
             gloss="who-NOM.SG be-PRS.2SG be-PRS.1SG man-NOM.SG now go-PRS.1SG", tokens=toks)
    for rid in ("t3-z-1", "t3-z-2", "t3-z-3", "t3-z-4", "t3-z-5"):
        st = collections.Counter()
        items = ec.app_chats([dict(r, id=rid)], st)
        pies, engs = [], []
        for e in items:
            m, a = e["meta"], e["messages"][-1]["content"]
            if m["mode"] == "en_pie":
                assert e["messages"][0]["content"] == ec.APP_SYSTEM
                f = ec.parse_app(a)
                pies.append(f["PIE"]), engs.append(e["messages"][1]["content"])
                assert len(f["Gloss"].split()) == len(f["PIE"].split())
                assert ("wiHrós" in f["PIE"]) == ("wiHrós" in f.get("Notes", ""))
            else:
                assert e["messages"][0]["content"] == ec.APP_INVERSE_SYSTEM
                f = ec.parse_app(a)
                pies.append(e["messages"][1]["content"]), engs.append(f["English"])
            assert m["sentences"] == len(ec.sentences(pies[-1])) and m["unit"] == ("sentence" if m["sentences"] == 1
                                                                                  else "paragraph")
        assert " ".join(pies) == r["pie"] and " ".join(engs) == r["english"]      # each sentence once
        # the translator dataset: every item in both directions, the same PIE and English, paired by meta.item
        both = ec.app_chats([dict(r, id=rid)], collections.Counter(), both_directions=True)
        assert [e["meta"]["mode"] for e in both] == ["en_pie", "pie_en"] * (len(both) // 2)
        for a, b in zip(both[::2], both[1::2]):
            assert a["meta"]["item"] == b["meta"]["item"]
            fa, fb = ec.parse_app(a["messages"][2]["content"]), ec.parse_app(b["messages"][2]["content"])
            assert fa["PIE"] == b["messages"][1]["content"] and fb["English"] == a["messages"][1]["content"]
            assert fa["Gloss"] == fb["Gloss"]
        assert " ".join(e["messages"][1]["content"] for e in both[1::2]) == r["pie"]
        assert not any("item" in e["meta"] for e in items)
    # sessions: adjacent en_pie items of one text chained in order, the same turns, within the budget
    texts = [dict(r, id=f"t3-s-{i}") for i in range(30)]
    plain = ec.app_chats(texts, collections.Counter(), inverse=False)
    st = collections.Counter()
    sess = ec.app_chats(texts, st, inverse=False, sessions=4)
    ss = [e for e in sess if e["meta"]["task"] == "app_session"]
    assert len(ss) == 4 == sum(v for k, v in st.items() if k.startswith("session:"))
    assert all(2 <= e["meta"]["items"] <= 3 and e["meta"]["turns"] == len(e["messages"]) - 1 for e in ss)
    # the same assistant turns, in text order, each once
    flat = lambda xs: [m["content"] for e in xs for m in e["messages"] if m["role"] == "assistant"]
    assert flat(sess) == flat(plain)
    assert {e["messages"][0]["content"] for e in ss} == {ec.APP_SYSTEM}
    assert all(ec.assistant_pie(e) == " ".join(ec.parse_app(m["content"])["PIE"] for m in e["messages"][2::2])
               for e in ss)
    # a gloss without one word per PIE word is left out, never guessed
    st = collections.Counter()
    items = ec.app_chats([dict(r, gloss="who be")], st, inverse=False)
    assert st["gloss_mismatch"] == 1 and all("Gloss:" not in e["messages"][-1]["content"] for e in items)
    assert not any(e["meta"]["gloss_reference"] for e in items)
    # a long record whose English does not align is skipped; a short one is one item
    st = collections.Counter()
    long = _rec("a. b. c. d.", "A b c d.", id="t3-z-9")
    assert ec.app_chats([long], st) == [] and st["unaligned_long:count_mismatch"] == 1
    short = ec.app_chats([_rec("a. b.", "A b.", id="t3-z-8")], collections.Counter(), inverse=False)
    assert len(short) == 1 and short[0]["meta"]["sentences"] == 2
    # a title line (no final punctuation) is never joined to the next line
    work = [dict(_rec(p, e, genre="fable", id=f"t1-w-{i}", tier=1, work_id="w", line_no=i))
            for i, (p, e) in enumerate([("owis h₁éḱwōs-kʷe", "The Sheep and the Horses"), ("a b.", "A b."),
                                        ("c d.", "C d."), ("e f.", "E f.")])]
    for rid in "wxyz":
        items = ec.app_chats([dict(r, work_id=rid) for r in work], collections.Counter(), inverse=False)
        assert items[0]["messages"][1]["content"] == "The Sheep and the Horses"


def test_translator_conversations(exported):
    """translate_app: English in, the fixed format out; every train record with English is covered sentence by
    sentence; eval items come from the eval records only (Tier 1 has no gloss reference)."""
    recs = {r["id"]: r for r in exported["train_records"]}
    app = [e for e in exported["train"] if e["meta"]["task"] == "translate_app"]
    inv = [e for e in app if e["meta"]["mode"] == "pie_en"]
    assert app and 0.1 < len(inv) / len(app) < 0.3
    assert {e["meta"]["unit"] for e in app} == {"sentence", "paragraph"}
    covered = collections.defaultdict(list)
    for e in app:
        m, a = e["meta"], e["messages"][-1]["content"]
        f = ec.parse_app(a)
        r = recs[m["source_id"]]
        if m["mode"] == "en_pie":
            assert set(f) <= {"PIE", "Gloss", "Notes"} and list(f)[:2] == ["PIE", "Gloss"]
            pie, gloss = f["PIE"], f["Gloss"]
            words = [w.strip(".,;:!?") for w in pie.split()]
            coined = ({t["form"] for t in r["tokens"] if t.get("coined")}
                      if len(r["tokens"]) == len(r["pie"].split()) else set())
            # Notes names exactly the item's coined words (a neologism or a project reconstruction)
            assert ("Notes" in f) == bool(coined & set(words))
            if "Notes" in f:
                assert all(w in f["Notes"] for w in coined & set(words))
        else:
            pie, gloss = e["messages"][1]["content"], f["Gloss"]
            assert list(f) == ["English", "Gloss"]
        assert pie in r["pie"] and gloss in r["gloss"] and len(gloss.split()) == len(pie.split())
        covered[r["id"]].append(pie)
    # a session's requests (adjacent items of one text, chained) cover their sentences too
    ss = [e for e in exported["train"] if e["meta"]["task"] == "app_session"]
    assert ss and all(e["meta"]["mode"] == "en_pie" and 2 <= e["meta"]["items"] <= 3 for e in ss)
    for e in ss:
        for u, x in zip(e["messages"][1::2], e["messages"][2::2]):
            f = ec.parse_app(x["content"])
            assert set(f) <= {"PIE", "Gloss", "Notes"}
            covered[e["meta"]["source_id"]].append(f["PIE"])
        assert e["meta"]["source_id"] in recs and ec.assistant_pie(e) in recs[e["meta"]["source_id"]]["pie"]
    aligned = [r for r in exported["train_records"] if r.get("english") and ec.align_english(r)[0]]
    for r in aligned:
        assert sorted(ec.sentences(" ".join(covered[r["id"]]))) == sorted(ec.sentences(r["pie"])), r["id"]
    # Tier 3b gets the same English-input treatment
    neo = [e for e in exported["train"] if e["meta"].get("neologism")]
    assert {"translate_app/en_pie", "en_dialogue"} <= {ec.mix_key(e) for e in neo}
    assert {e["meta"]["mode"] for e in neo if e["meta"]["task"] == "en_dialogue"} >= {"en_pie", "en_pie_gloss"}
    # eval
    ev = [e for e in exported["eval"] if e["meta"]["task"] == "translate_app"]
    eval_ids = {r["id"] for r in exported["eval_records"]} | {r["work_id"] for r in exported["eval_records"]}
    assert ev and {e["meta"]["source_id"] for e in ev} <= eval_ids
    assert {e["meta"]["tier"] for e in ev} == {1, 2}
    assert all(e["meta"]["gloss_reference"] is (e["meta"]["tier"] == 2) for e in ev)
    assert all("Gloss:" not in e["messages"][-1]["content"] for e in ev if e["meta"]["tier"] == 1)
    kinds = exported["summary"]["leakage"]["per_kind"]
    assert kinds["translate_app/en_pie"]["n"] and kinds["translate_app/en_pie"]["max_overlap"] < 0.5


def test_translator_dataset(exported):
    """export/translator/: the translation app's data, every translator item in both directions (1:1), the
    chat split (eval items from eval records only), no sessions; chat/train.jsonl keeps the inverse small."""
    out = exported["out"] / "translator"
    load = lambda p: [json.loads(x) for x in (out / p).read_text("utf-8").splitlines()]
    tr, ev = load("train.jsonl"), load("eval.jsonl")
    s = json.loads((out / "summary.json").read_text("utf-8"))
    for split, exs in (("train", tr), ("eval", ev)):
        assert s["examples"][split] == len(exs) and {e["meta"]["task"] for e in exs} == {"translate_app"}
        modes = collections.Counter(e["meta"]["mode"] for e in exs)
        assert modes["en_pie"] == modes["pie_en"] == len(exs) // 2 > 0 and s["modes"][split] == dict(modes)
        pairs = collections.defaultdict(dict)
        for e in exs:
            pairs[e["meta"]["item"]][e["meta"]["mode"]] = e
            assert len(e["messages"]) == 3
        for p in pairs.values():
            a, b = p["en_pie"], p["pie_en"]
            assert ec.parse_app(a["messages"][2]["content"])["PIE"] == b["messages"][1]["content"]
            assert ec.parse_app(b["messages"][2]["content"])["English"] == a["messages"][1]["content"]
            assert a["meta"]["source_id"] == b["meta"]["source_id"]
    # the same items as the chat export's translator: en_pie of the translator = every chat translate_app item
    # and session request, whatever its chat direction
    chat_items = sum(1 if e["meta"]["task"] == "translate_app" else e["meta"]["items"]
                     for e in exported["train"] if e["meta"]["task"] in ("translate_app", "app_session"))
    assert chat_items == len(tr) // 2
    # hold-out: both directions of an eval item stay in eval
    tr_ids = {e["meta"]["source_id"] for e in tr} | {e["meta"]["source_id"] for e in exported["train"]}
    ev_ids = {r["id"] for r in exported["eval_records"]} | {r["work_id"] for r in exported["eval_records"]}
    assert {e["meta"]["source_id"] for e in ev} <= ev_ids and not tr_ids & {e["meta"]["source_id"] for e in ev}
    assert s["leakage"]["ok"] and not s["leakage"]["failures"]
    assert s["provenance"] == exported["summary"]["provenance"]
    # assistant-turn overlap only: the en_pie outputs' PIE (a pie_en item has it as input, by design)
    so = ec.self_overlap(tr)["all_kinds_sentences"]
    assert so == s["self_overlap"]["all_kinds_sentences"] and so["histogram"]["1"] > 0.9 * so["items"]


def test_turns_are_conversational(exported):
    """summary.json turns: user turns per kind/mode; multi-turn examples are mostly dialogue exchanges, the
    chained requests (demo seeds, app sessions) at most APP_SESSION_SHARE of them."""
    t = exported["summary"]["turns"]
    for split in ("train", "eval", "train_mix"):
        exs = exported[split]
        assert t[split] == ec.turn_table(exs)
        mt = t[split]["multi_turn"]
        assert mt["examples"] == sum(ec.user_turns(e) >= 2 for e in exs)
        assert mt["chained_share_of_multi_turn"] <= ec.APP_SESSION_SHARE + 0.005
    tr = t["train"]["multi_turn"]
    assert tr["by_source"]["dialogue"] > 200 and tr["by_source"]["chained"] > 0
    assert set(tr["by_source"]) <= {"dialogue", "chained"}
    assert t["train_mix"]["multi_turn"]["examples"] == tr["examples"]     # every multi-turn example is kept
    assert t["train"]["user_turns"]["pie_dialogue/pie_pie"]["4+"]


def test_translator_leakage_is_checked_on_the_pie():
    """An eval sentence that a train translator item (or translate_en_pie) already says fails, even inside a
    differently formatted turn."""
    r = _rec("h₁éḱwōs tréxonti.", "Horses run.", genre="household", id="t2-e-1",
             gloss="horse-NOM.PL run-PRS.3PL")
    tr = ec.app_chats([dict(r, id="t3-e-1")], collections.Counter(), inverse=False)
    ev = ec.app_chats([r], collections.Counter(), inverse=False)
    rep = ec.leakage_report(tr, ev, "")
    assert not rep["ok"] and "PIE verbatim in a train assistant turn" in rep["failures"][0]["why"]


def test_mix_and_train_mix(exported):
    s = exported["summary"]["mix"]
    tr = s["train"]
    assert set(tr["groups"]) == set(ec.TARGET_MIX)
    assert sum(g["examples"] for g in tr["groups"].values()) == len(exported["train"])
    assert tr["english_input_share_of_conversation"] > 0.6     # PIE -> English stays small in the chat data
    assert tr["groups"]["english_input"]["examples"] > tr["groups"]["pie_only_chat"]["examples"] * 5
    assert ec.TARGET_MIX == {"english_input": 0.50, "pie_to_english": 0.10, "pie_only_chat": 0.15, "grammar": 0.25}
    tm = exported["train_mix"]
    ids = {e["meta"]["id"] for e in exported["train"]}
    assert {e["meta"]["id"] for e in tm} <= ids and len({e["meta"]["id"] for e in tm}) == len(tm)
    eng = [e for e in tm if ec.mix_group(e) == "english_input"]
    assert len(eng) == tr["groups"]["english_input"]["examples"]          # every English-input example
    # each other group: its target share of english_input / TARGET, or all it has (no example repeated); a
    # group short of its target (pie_only_chat today) leaves English input above its 50%
    total = len(eng) / ec.TARGET_MIX["english_input"]
    for g, target in ec.TARGET_MIX.items():
        n = sum(ec.mix_group(e) == g for e in tm)
        assert n == (len(eng) if g == "english_input" else min(tr["groups"][g]["examples"], round(total * target)))
    assert len(eng) / len(tm) >= ec.TARGET_MIX["english_input"]
    assert s["train_mix"]["examples"] == len(tm) and s["train_mix"]["english_input_share"] > 0.45
