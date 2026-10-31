"""Tokens of train_mix under the Qwen3.6 renderer: as conversations (all assistant turns) and split into one
example per assistant turn (the cookbook's fix for a renderer without the extension property). Read-only."""
import json, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
os.environ["TINKER_API_KEY"] = open(r"B:\Dropbox\Dropbox\AI BRAIN\tinker.txt").read().strip()
from tinker_cookbook.renderers import TrainOnWhat, get_renderer
from tinker_cookbook.tokenizer_utils import get_tokenizer
from tinker_cookbook.supervised.data import conversation_to_datum
from tinker_cookbook import hyperparam_utils
import inspect
MODEL = "Qwen/Qwen3.6-35B-A3B"
tok = get_tokenizer(MODEL); rend = get_renderer("qwen3_5_disable_thinking", tok)
ex = [json.loads(l) for l in open(r"Q:\AI\PIE\data\train_mix_1102.jsonl", encoding="utf-8")]
conv = split = nsplit = loss = 0; mx = 0
for e in ex:
    msgs = e["messages"]
    d = conversation_to_datum(msgs, rend, max_length=8192, train_on_what=TrainOnWhat.ALL_ASSISTANT_MESSAGES)
    conv += d.model_input.length
    for i, m in enumerate(msgs):
        if m["role"] == "assistant":
            d = conversation_to_datum(msgs[:i + 1], rend, max_length=8192, train_on_what=TrainOnWhat.LAST_ASSISTANT_MESSAGE)
            split += d.model_input.length; nsplit += 1; mx = max(mx, d.model_input.length)
            loss += int(sum(d.loss_fn_inputs["weights"].tolist()))
print(f"examples {len(ex)} conv_tokens {conv} | split examples {nsplit} tokens {split} loss_tokens {loss} max {mx}")
print("recommended lr", hyperparam_utils.get_lr(MODEL))
print(inspect.signature(hyperparam_utils.get_lr))
