"""Tokens of a train_mix export under the Nemotron 3.5 Super renderer, for the Tinker cost estimate. Read-only: no
sampling, no training (the tokenizer and renderer are local; Tinker is asked only for the recommended LR).

    python -I measure_nemotron.py Q:\\AI\\PIE\\data\\train_mix_1103.jsonl
"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
os.environ["TINKER_API_KEY"] = open(r"B:\Dropbox\Dropbox\AI BRAIN\tinker.txt").read().strip()
from tinker_cookbook.renderers import TrainOnWhat, get_renderer
from tinker_cookbook.tokenizer_utils import get_tokenizer
from tinker_cookbook.supervised.data import conversation_to_datum
from tinker_cookbook import hyperparam_utils

MODEL = "nvidia/NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-BF16"
RENDERER = "nemotron3_ultra_disable_thinking"
tok = get_tokenizer(MODEL); rend = get_renderer(RENDERER, tok)
print("extension property:", getattr(rend, "has_extension_property", "n/a"))
ex = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8")]
conv = split = nsplit = loss = over = 0; mx = 0
for e in ex:
    msgs = e["messages"]
    conv += conversation_to_datum(msgs, rend, max_length=16384, train_on_what=TrainOnWhat.ALL_ASSISTANT_MESSAGES).model_input.length
    for i, m in enumerate(msgs):
        if m["role"] == "assistant":
            d = conversation_to_datum(msgs[:i + 1], rend, max_length=16384, train_on_what=TrainOnWhat.LAST_ASSISTANT_MESSAGE)
            n = d.model_input.length
            split += n; nsplit += 1; mx = max(mx, n); over += n > 4096
            loss += int(sum(d.loss_fn_inputs["weights"].tolist()))
print(f"conversations {len(ex)} conv_tokens {conv} | per-turn examples {nsplit} tokens {split} loss_tokens {loss} max {mx} over4096 {over}")
d = conversation_to_datum(ex[0]["messages"][:2], rend, max_length=4096, train_on_what=TrainOnWhat.LAST_ASSISTANT_MESSAGE)
print("sample render:", repr(tok.decode(d.model_input.to_ints()))[:600])
try:
    print("recommended lr", hyperparam_utils.get_lr(MODEL))
except Exception as e:
    print("get_lr:", type(e).__name__, e)
