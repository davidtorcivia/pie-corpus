import json, sys
sys.path.insert(0, "/Users/david/AI/PIE")
from pie.tts_data import text_label
LINES = [
 "h₁ésti ph₂tḗr.", "h₁éḱwos h₁ésti.", "h₁eǵóh₂ h₁éḱwom wéydmi.", "h₁yós h₁ésti, só h₁ésti.", "h₁é h₁ésti bʰréh₂tēr.",
 "ph₂tḗr h₁ésti h₂stḗr.", "gʰóstis h₁ésti.", "stéh₂ti gʰóstipotis.", "h₁ésti méh₂tēr.", "déh₃tor h₁ésti.",
 "bʰréh₂tēr.", "ph₂tḗr.", "méh₂tēr.", "swésōr.", "dʰugh₂tḗr.", "h₂stḗr.", "déh₃tor.",
 "h₁éḱwōs h₁ésti h₂ówis.", "h₁imés h₁éysmi.", "gʰóstey h₁ésti.", "h₁ésti gʰóstis h₁ésti.",
 "wérǵom h₁ésti.", "bʰéreti bʰréh₂tēr.", "h₃réǵs h₁ésti.", "pérḱus h₁ésti.", "h₂éḱmōn h₁ésti.",
 "h₂ówis h₁éḱwōs-kʷe.", "n̥sméy ń̥dʰgʷʰitom ḱléwos h₂yéwi dʰedʰh₁dʰí.", "dyḗws ph₂tḗr h₁ésti.", "h₁ésti h₁éḱwos ph₂tḗr.",
]
json.dump([{"text": t, "label": text_label(t)} for t in LINES], open(sys.argv[1], "w"), ensure_ascii=False, indent=0)
for t in LINES[:6]: print(t, "->", text_label(t))
