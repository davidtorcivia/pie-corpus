"""the WSL configs (v2l_*) from the Windows ones (v2w_*): /mnt/q paths, audio from the local ext4 copy"""
import glob, os, yaml
K = "/mnt/q/AI/PIE/train/kokoro"
def fix(v):
    if isinstance(v, str) and v.startswith("Q:/"):
        v = "/mnt/q/" + v[3:]
    return v
def walk(o):
    if isinstance(o, dict): return {k: walk(fix(v)) for k, v in o.items()}
    if isinstance(o, list): return [walk(fix(v)) for v in o]
    return fix(o)
for p in sorted(glob.glob(f"{K}/configs/v2w_*.yml")):
    c = walk(yaml.safe_load(open(p, encoding="utf-8")))
    c["data_params"]["root_path"] = "/root/kokoro-ft/data-v2/wavs"
    out = p.replace("v2w_", "v2l_")
    yaml.safe_dump(c, open(out, "w", encoding="utf-8"), sort_keys=False, allow_unicode=True)
    print(os.path.basename(out), c["log_dir"], c["data_params"]["train_data"], c.get("first_stage_path"))
