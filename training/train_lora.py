"""LoRA / QLoRA supervised fine-tuning on the PIE chat export, for one CUDA GPU (tr-desktop's RTX 5090).

    python train_lora.py --model DIR --template {chatml,typewriter} --run NAME [--lr 2e-4 --epochs 3 --rank 16 ...]

What it does (docs/research/training-runs.md has the reasoning and the results):
- Renders every conversation itself, turn by turn, in the model's chat format (TEMPLATES), so the loss is on the
  assistant's replies only: system prompt and user turns are labels -100 (export/README.md "train on the assistant
  turns only"). `--check` prints one rendered example with its trained span and exits.
- Packs the rendered examples into --seq-long rows; an example never straddles two rows (its context stays with its
  replies), so each row ends in a short -100 filler tail.
- LoRA on every linear layer; bf16 or 4-bit (QLoRA); cuDNN attention (torch 2.11 on Windows has no flash kernel for
  the 5090); Liger fused kernels for Qwen3 / Llama; a VRAM cap so nothing spills into system RAM.
- AdamW, linear warm-up then cosine decay. Logs to RUNS/NAME/metrics.jsonl every --log-every steps.
- Each epoch: eval loss on export/chat/eval.jsonl, greedy generations for a fixed prompt set (generations-eN.jsonl),
  and the adapter saved (adapter-eN/).
"""
import argparse
import json
import math
import os
import random
import time
from pathlib import Path

import torch
from peft import LoraConfig, get_peft_model
from torch.nn.attention import SDPBackend, sdpa_kernel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

ATTN = [SDPBackend.CUDNN_ATTENTION, SDPBackend.FLASH_ATTENTION, SDPBackend.EFFICIENT_ATTENTION]

# (prefix of a turn, suffix of a turn); the assistant's content + suffix is what is trained
TEMPLATES = {
    # ChatML, as Qwen3-4B-Instruct-2507's template renders it without tools (no <think> blocks); the base model gets
    # the same format, so base and instruct runs are comparable
    "chatml": {"start": "", "turn": lambda r: (f"<|im_start|>{r}\n", "<|im_end|>\n"), "gen": "<|im_start|>assistant\n"},
    # base models (no chat tuning): their embeddings for <|im_start|>/<|im_end|> were never trained and LoRA can't train
    # embeddings, so a base model under ChatML never learns to stop (Qwen3-4B-Base, queue 1). Plain role labels, each
    # turn ended by the end-of-text token the base model already knows; "end" is filled per tokenizer in main()
    "plain": {"start": "", "turn": lambda r: (f"{r.capitalize()}: ", "\n\n"), "gen": "Assistant: ", "assistant_end": "eos"},
    # TypewriterLM's template (typewriter-1913-7B-sft-v2): bos, then "<|im_start|>role content<|im_end|> "
    "typewriter": {"start": "<|begin_of_text|>", "turn": lambda r: (f"<|im_start|>{r} ", "<|im_end|> "),
                   "gen": "<|im_start|>assistant "},
}


def encode(tok, tpl, messages, train_all_assistant=True):
    """(ids, labels) for one conversation: labels -100 except the assistant turns' content and end marker."""
    t = TEMPLATES[tpl]
    ids, labels = [], []

    def add(text, train):
        x = tok(text, add_special_tokens=False)["input_ids"]
        ids.extend(x)
        labels.extend(x if train else [-100] * len(x))

    if t["start"]:
        add(t["start"], False)
    for m in messages:
        pre, suf = t["turn"](m["role"])
        add(pre, False)
        train = m["role"] == "assistant" and train_all_assistant
        if m["role"] == "assistant" and t.get("assistant_end") == "eos":
            add(m["content"], train)
            ids.append(tok.eos_token_id)
            labels.append(tok.eos_token_id if train else -100)
            add("\n\n", False)
        else:
            add(m["content"] + suf, train)
    return ids, labels


def prompt_ids(tok, tpl, messages):
    """The prompt for generation: every turn before the last assistant turn, then the assistant header."""
    t = TEMPLATES[tpl]

    def end(role):
        return tok.eos_token + "\n\n" if role == "assistant" and t.get("assistant_end") == "eos" else t["turn"](role)[1]
    text = t["start"] + "".join(t["turn"](m["role"])[0] + m["content"] + end(m["role"]) for m in messages)
    return tok(text + t["gen"], add_special_tokens=False, return_tensors="pt")["input_ids"]


def pack(examples, seq):
    """Concatenate (ids, labels) into rows of exactly seq tokens; the last partial row is dropped."""
    rows, cur_i, cur_l = [], [], []
    for ids, lab in examples:
        if len(ids) > seq:                       # an over-long example: keep its last seq tokens (the replies)
            ids, lab = ids[-seq:], lab[-seq:]
        if len(cur_i) + len(ids) > seq:
            pad = seq - len(cur_i)               # an example never straddles two rows: the row's short tail is
            cur_i += [cur_i[-1]] * pad           # filler with -100 labels (a few % of tokens at these lengths)
            cur_l += [-100] * pad
            rows.append((cur_i, cur_l))
            cur_i, cur_l = [], []
        cur_i += ids
        cur_l += lab
    return torch.tensor([r[0] for r in rows]), torch.tensor([r[1] for r in rows])


def load_jsonl(p):
    return [json.loads(x) for x in Path(p).read_text("utf-8").splitlines() if x.strip()]


def gen_set(evals, n_per_task=12, seed=0):
    """A fixed prompt set from chat/eval.jsonl: up to n per task, the prompt being every turn before the first
    assistant turn, the reference that turn."""
    rng = random.Random(seed)
    by = {}
    for e in evals:
        by.setdefault(e["meta"]["task"] + ("/" + e["meta"]["mode"] if e["meta"].get("mode") else ""), []).append(e)
    out = []
    for k in sorted(by):
        xs = by[k][:]
        rng.shuffle(xs)
        for e in xs[:n_per_task]:
            msgs = e["messages"]
            i = next(j for j, m in enumerate(msgs) if m["role"] == "assistant")
            out.append({"kind": k, "id": e["meta"].get("id"), "prompt": msgs[:i], "reference": msgs[i]["content"]})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--template", choices=TEMPLATES, required=True)
    ap.add_argument("--run", required=True)
    ap.add_argument("--runs", default=r"Q:\AI\PIE\runs")
    ap.add_argument("--train", default=r"Q:\AI\PIE\data\train_mix.jsonl")
    ap.add_argument("--eval", default=r"Q:\AI\PIE\data\eval.jsonl")
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--rank", type=int, default=16)
    ap.add_argument("--alpha", type=int, default=32)
    ap.add_argument("--dropout", type=float, default=0.05)
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--accum", type=int, default=2)
    ap.add_argument("--seq", type=int, default=2048)
    ap.add_argument("--warmup", type=float, default=0.03)
    ap.add_argument("--quant", choices=("bf16", "4bit"), default="bf16")
    ap.add_argument("--liger", choices=("qwen3", "llama", "none"), default="none")
    ap.add_argument("--max-steps", type=int, default=0, help="stop early (smoke tests)")
    ap.add_argument("--gen-per-task", type=int, default=8)
    ap.add_argument("--gen-batch", type=int, default=24)
    ap.add_argument("--gen-file", default="", help="a frozen prompt set (training/gen_prompts_v1.jsonl) instead of gen_set")
    ap.add_argument("--max-new", type=int, default=160)
    ap.add_argument("--log-every", type=int, default=5)
    ap.add_argument("--check", action="store_true", help="print one rendered example with its trained span; exit")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    torch.manual_seed(a.seed)
    tok = AutoTokenizer.from_pretrained(a.model)
    train = load_jsonl(a.train)
    evals = load_jsonl(a.eval)
    if a.check:
        ex = next(e for e in train if e["meta"]["task"] == "en_dialogue")
        ids, lab = encode(tok, a.template, ex["messages"])
        print("RENDERED:\n" + tok.decode(ids))
        print("\nTRAINED SPAN:\n" + tok.decode([i for i, l in zip(ids, lab) if l != -100]))
        return

    torch.cuda.set_per_process_memory_fraction(0.92, 0)
    if a.liger == "qwen3":
        from liger_kernel.transformers import apply_liger_kernel_to_qwen3
        apply_liger_kernel_to_qwen3(rope=True, rms_norm=True, swiglu=True, fused_linear_cross_entropy=True)
    elif a.liger == "llama":
        from liger_kernel.transformers import apply_liger_kernel_to_llama
        apply_liger_kernel_to_llama(rope=True, rms_norm=True, swiglu=True, fused_linear_cross_entropy=True)
    run = Path(a.runs) / a.run
    run.mkdir(parents=True, exist_ok=True)
    random.Random(a.seed).shuffle(train)
    enc = [encode(tok, a.template, e["messages"]) for e in train]
    X, Y = pack(enc, a.seq)
    Xe, Ye = pack([encode(tok, a.template, e["messages"]) for e in evals], a.seq)
    gens = load_jsonl(a.gen_file) if a.gen_file else gen_set(evals, a.gen_per_task)
    trained_tokens = int((Y != -100).sum())
    steps_per_epoch = math.ceil(len(X) / (a.batch * a.accum))
    total = steps_per_epoch * a.epochs if not a.max_steps else a.max_steps
    cfg = {**vars(a), "rows": len(X), "row_tokens": len(X) * a.seq, "trained_tokens_per_epoch": trained_tokens,
           "eval_rows": len(Xe), "steps_per_epoch": steps_per_epoch, "total_steps": total, "gen_prompts": len(gens),
           "started": time.strftime("%Y-%m-%d %H:%M:%S")}
    prov = Path(a.train).with_name("provenance.json")
    if prov.exists():
        cfg["export_provenance"] = json.loads(prov.read_text("utf-8"))
    (run / "config.json").write_text(json.dumps(cfg, indent=1), "utf-8")

    q = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16,
                           bnb_4bit_use_double_quant=True) if a.quant == "4bit" else None
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, quantization_config=q,
                                                 attn_implementation="sdpa", device_map={"": 0})
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.enable_input_require_grads()
    model = get_peft_model(model, LoraConfig(r=a.rank, lora_alpha=a.alpha, lora_dropout=a.dropout,
                                             target_modules="all-linear", task_type="CAUSAL_LM"))
    model.train()   # from_pretrained returns eval mode, where gradient checkpointing is off
    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=a.lr, weight_decay=0.0, betas=(0.9, 0.999))
    warm = max(1, int(a.warmup * total))
    sched = torch.optim.lr_scheduler.LambdaLR(
        opt, lambda s: (s + 1) / warm if s < warm else 0.5 * (1 + math.cos(math.pi * (s - warm) / max(1, total - warm))))
    log = open(run / "metrics.jsonl", "a", encoding="utf-8")

    def write(d):
        log.write(json.dumps(d) + "\n")
        log.flush()

    def eval_loss():
        model.eval()
        tot, n = 0.0, 0
        with torch.no_grad(), sdpa_kernel(ATTN):
            for i in range(0, len(Xe), a.batch):
                x, y = Xe[i:i + a.batch].cuda(), Ye[i:i + a.batch].cuda()
                k = int((y[:, 1:] != -100).sum())
                tot += model(input_ids=x, labels=y).loss.item() * k
                n += k
        model.train()
        return tot / max(1, n)

    def generate(epoch):
        """Greedy (repetition penalty 1.1) on the fixed prompt set, batched with left padding."""
        model.eval()
        out = []
        end = tok.eos_token_id if TEMPLATES[a.template].get("assistant_end") == "eos" else tok.convert_tokens_to_ids("<|im_end|>")
        pad = tok.pad_token_id if tok.pad_token_id is not None else end
        with torch.no_grad(), sdpa_kernel(ATTN):
            for i in range(0, len(gens), a.gen_batch):
                chunk = gens[i:i + a.gen_batch]
                ps = [prompt_ids(tok, a.template, g["prompt"])[0] for g in chunk]
                L = max(len(p) for p in ps)
                ids = torch.full((len(ps), L), pad)
                att = torch.zeros((len(ps), L), dtype=torch.long)
                for k, p in enumerate(ps):
                    ids[k, L - len(p):], att[k, L - len(p):] = p, 1
                o = model.generate(input_ids=ids.cuda(), attention_mask=att.cuda(), max_new_tokens=a.max_new,
                                   do_sample=False, repetition_penalty=1.1, eos_token_id=end, pad_token_id=pad)
                for k, g in enumerate(chunk):
                    text = tok.decode(o[k, L:], skip_special_tokens=True).strip()
                    out.append({**{x: v for x, v in g.items() if x != "prompt"},
                                "user": next((m["content"] for m in reversed(g["prompt"]) if m["role"] == "user"), ""),
                                "output": text})
        (run / f"generations-e{epoch}.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in out),
                                                          "utf-8")
        model.train()

    write({"event": "start", **{k: cfg[k] for k in ("rows", "trained_tokens_per_epoch", "steps_per_epoch",
                                                    "total_steps")}})
    write({"event": "eval", "epoch": 0, "step": 0, "eval_loss": round(eval_loss(), 4)})
    step, t0, seen, t_last = 0, time.time(), 0, time.time()
    order = torch.randperm(len(X))
    for epoch in range(1, a.epochs + 1):
        order = torch.randperm(len(X))
        for b in range(0, len(order), a.batch * a.accum):
            idx = order[b:b + a.batch * a.accum]
            loss_acc, n_tok = 0.0, 0
            for j in range(0, len(idx), a.batch):
                x, y = X[idx[j:j + a.batch]].cuda(), Y[idx[j:j + a.batch]].cuda()
                with sdpa_kernel(ATTN):
                    loss = model(input_ids=x, labels=y).loss / math.ceil(len(idx) / a.batch)
                    loss.backward()
                loss_acc += loss.item()
                n_tok += x.numel()
            gn = torch.nn.utils.clip_grad_norm_(params, 1.0).item()
            opt.step(), sched.step(), opt.zero_grad(set_to_none=True)
            step += 1
            seen += n_tok
            if step % a.log_every == 0:
                torch.cuda.synchronize()
                dt = time.time() - t_last
                write({"event": "train", "epoch": round(epoch - 1 + (b + len(idx)) / len(order), 3), "step": step,
                       "loss": round(loss_acc, 4), "lr": sched.get_last_lr()[0], "grad_norm": round(gn, 3),
                       "tok_per_s": round(seen / dt), "gpu_gb": round(torch.cuda.max_memory_allocated() / 2**30, 1),
                       "elapsed_min": round((time.time() - t0) / 60, 2)})
                seen, t_last = 0, time.time()
            if a.max_steps and step >= a.max_steps:
                break
        write({"event": "eval", "epoch": epoch, "step": step, "eval_loss": round(eval_loss(), 4),
               "elapsed_min": round((time.time() - t0) / 60, 2)})
        generate(epoch)
        model.save_pretrained(run / f"adapter-e{epoch}")
        write({"event": "epoch_done", "epoch": epoch, "step": step})
        if a.max_steps and step >= a.max_steps:
            break
    write({"event": "done", "step": step, "elapsed_min": round((time.time() - t0) / 60, 2)})


if __name__ == "__main__":
    main()
