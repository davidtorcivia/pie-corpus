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
    # English input is first-class: every aligned, non-narrated dialogue gets an English-input conversation
    assert c["en_dialogue"] == sum(v for k, v in s["dialogue_english_alignment"]["train"].items()
                                   if k.startswith("aligned:"))
    assert s["english_input_conversations"]["train"] == c["en_dialogue"] + c["demo_chat"] >= 150
    assert {m.split("/")[1] for m in s["modes"]["train"]} == {"pie_pie", *ec.EN_MODES}
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
            # the turns are the record's PIE, in order, minus at most a dropped trailing question
            assert recs[m["source_id"]]["pie"].startswith(" ".join(turns))
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
    assert [e["meta"]["mode"] for e in one][0] == "pie_pie" and len(one) == 2
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
