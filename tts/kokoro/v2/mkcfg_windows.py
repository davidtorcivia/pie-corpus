"""make the native-Windows configs from the WSL v2 ones"""
import yaml, random, sys
K = r"Q:/AI/PIE/train/kokoro"; R = r"Q:/AI/PIE/runs/kokoro-v2"; D = r"Q:/AI/PIE/data/tts-corpus-v2"
tr = open(f"{K}/training/v2_train_list.txt", encoding="utf-8").read().splitlines()
va = open(f"{K}/training/v2_val_list.txt", encoding="utf-8").read().splitlines()
random.seed(0)
open(f"{K}/training/v2_smoke_train.txt", "w", encoding="utf-8", newline="\n").write("\n".join(random.sample(tr, 240)) + "\n")
open(f"{K}/training/v2_smoke_val.txt", "w", encoding="utf-8", newline="\n").write("\n".join(random.sample(va, 16)) + "\n")
for name, src, log, lists, extra in (
        ("smoke1", "config_pie_v2_1.yml", f"{R}/smoke1", "smoke", {"epochs_1st": 2, "log_interval": 10}),
        ("stage1", "config_pie_v2_1.yml", f"{R}/stage1", "", {}),
        ("smoke2", "config_pie_v2_2.yml", f"{R}/smoke2", "smoke", {"epochs_2nd": 2, "log_interval": 10,
                                                                    "first_stage_path": f"{R}/smoke1/first_stage.pth"}),
        ("stage2", "config_pie_v2_2.yml", f"{R}/stage2", "", {"first_stage_path": f"{R}/stage1/first_stage.pth"})):
    c = yaml.safe_load(open(f"{K}/configs/{src}", encoding="utf-8"))
    c["log_dir"] = log
    if "pretrained_model" in c and c["pretrained_model"]:
        c["pretrained_model"] = f"{K}/training/kokoro_base.pth"
    dp = c["data_params"]
    dp["train_data"] = f"{K}/training/v2_{lists + '_' if lists else ''}train{'' if lists else '_list'}.txt"
    dp["val_data"] = f"{K}/training/v2_{lists + '_' if lists else ''}val{'' if lists else '_list'}.txt"
    dp["root_path"] = f"{D}/wavs"
    dp["OOD_data"] = f"{K}/training/OOD_texts.txt"
    c.update(extra)
    yaml.safe_dump(c, open(f"{K}/configs/v2w_{name}.yml", "w", encoding="utf-8"), sort_keys=False, allow_unicode=True)
    print(name, c["log_dir"], dp["train_data"], c.get("first_stage_path"), c.get("pretrained_model"), c.get("batch_size"), c.get("max_len"))
