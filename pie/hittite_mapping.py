"""Hittite (TLHdig) lemma → PIE lexicon ids: the round-3 table data/research/formulas/mapping/hit.jsonl.

Two sources, in this order (hittite_table):
  1. kaikki + lexicon reflexes on the TLHdig stem keys, kept only if the TLHdig German gloss fits the
     dictionary gloss (fm.hittite_gloss_ok);
  2. Kloekhorst's EDHIL (fm.kloekhorst_entries): a TLHdig lemma is matched to a headword on the damaged
     key (edhil_stem_pattern), the headword is chosen by uniqueness or by gloss agreement, and its PIE
     line is resolved to lexicon ids, either as a whole form (fm.FuzzyPie) or, failing that, at the root
     (RootIndex): the root consonant skeleton must agree with a lexicon root AND the meaning must agree
     (gloss_agrees), or the lemma stays unmapped. Kloekhorst's own doubt is kept: a '?' on the PIE line,
     no PIE line, or a foreign (Luwian, Hurrian, Hattic ...) label leaves the lemma unmapped.

Names and function words are not content (fm.hit_pos) and are never mapped here.
"""

from __future__ import annotations

import collections
import re
import unicodedata
from pathlib import Path

from . import formula_search as fs
from . import formula_search_multi as fm

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- glosses

_EN_STOP = frozenset("""a an the to of in on at for with by from into onto up down out off away as or and be being been is
are it its one oneself one's someone something s o sth trans intr act midd vel sim etc kind type sort certain sg pl c n
adj adv postpos usually also very especially further thereby with without (here) here there""".split())
_DE_STOP = frozenset("""sich die der das den dem des ein eine einer eines einen zu zum zur von vom und oder mit in im an am
auf aus für u b art etwas jmd jemanden jemandem heth hatt luw hurr als nach durch gegen bei über unter nicht""".split())
_LIGHT_DE = frozenset({"machen", "sein", "werden", "haben", "lassen", "tun"})

# German glosses of TLHdig not covered by fm.HIT_DE_EN (general vocabulary; used only to compare a TLHdig
# gloss with Kloekhorst's English gloss and with the lexicon meaning, never to choose an etymon)
DE_EN_MORE = {
    "beschwören": "conjure incantation adjure", "schlachten": "slaughter butcher", "anstimmen": "sing intone chant",
    "versorgen": "provide supply care", "fortbringen": "carry bring away", "hinstellen": "place put set",
    "hinschaffen": "bring carry take", "beendigen": "finish end complete", "umkommen": "perish die",
    "niederhocken": "squat crouch", "herschicken": "send", "schicken": "send", "bekämpfen": "fight combat",
    "kompensieren": "compensate", "herfahren": "drive come", "drücken": "press", "singen": "sing",
    "zuteilen": "allot assign distribute", "spielen": "play", "bleiben": "remain stay", "behandeln": "treat",
    "zudecken": "cover", "bestreichen": "smear anoint", "schwören": "swear", "veranlassen": "cause",
    "ausbreiten": "spread", "verkünden": "announce proclaim", "zerstoßen": "crush pound", "jagen": "hunt chase",
    "spritzen": "sprinkle splash", "festdrücken": "press", "verflechten": "plait weave twist", "löschen": "extinguish quench",
    "anzünden": "kindle light", "brechen": "break", "zittern": "tremble shake", "ankündigen": "announce",
    "verbergen": "hide conceal", "graben": "dig", "äußern": "utter say", "berühren": "touch",
    "donnern": "thunder", "erkranken": "fall ill sick", "verfluchen": "curse", "orakeln": "oracle",
    "eintauchen": "dip immerse", "umwinden": "wrap wind", "fressen": "devour eat", "rebellieren": "rebel revolt",
    "schöpfen": "draw scoop", "überschreiten": "cross transgress", "entscheiden": "decide judge",
    "schreien": "cry shout scream", "brennen": "burn", "niederknien": "kneel", "reisen": "travel journey",
    "aufhäufen": "heap pile", "schweigen": "silent", "blasen": "blow", "aufziehen": "raise rear",
    "herausfinden": "find discover", "ritzen": "scratch carve", "abzählen": "count", "träufeln": "drip trickle",
    "hinhängen": "hang", "niederschlagen": "strike beat", "fließen": "flow", "schmücken": "adorn decorate",
    "spucken": "spit", "anrufen": "call invoke", "hinsetzen": "sit seat", "bellen": "bark", "filtern": "filter sieve",
    "tränken": "water drink", "freveln": "sin offend", "absondern": "separate", "entsprechen": "correspond",
    "sammeln": "gather collect", "hochheben": "lift raise", "aufstellen": "set erect place", "reiben": "rub",
    "vermindern": "diminish lessen", "eilen": "hurry hasten", "ernten": "harvest reap", "besänftigen": "appease soothe",
    "abkratzen": "scrape", "schließen": "close shut lock", "vertrocknen": "dry wither", "nennen": "call name",
    "weigern": "refuse", "hineinstecken": "insert put", "lecken": "lick", "hämmern": "hammer forge",
    "erfrischen": "refresh", "verschwinden": "disappear vanish", "zeugen": "beget generate", "walten": "rule govern",
    "besprengen": "sprinkle", "dämpfen": "steam", "aufteilen": "divide distribute", "pflanzen": "plant",
    "heilig": "holy sacred", "kultisch": "cultic sacred pure", "ungünstig": "unfavourable unfavorable",
    "gehörig": "belonging", "warmes": "warm", "stark": "strong powerful", "übrig": "remaining left", "süß": "sweet",
    "fröhlich": "cheerful glad joyful", "voll": "full", "wichtig": "important", "unsichtbar": "invisible",
    "umliegend": "surrounding", "blutig": "bloody", "westlich": "western west", "kleines": "small little",
    "satt": "sated satiated full", "leer": "empty", "frisch": "fresh", "hinterer": "rear back hind", "eben": "even level",
    "richtig": "right correct", "dunkel": "dark", "kurz": "short", "unrein": "impure unclean", "zornig": "angry",
    "gering": "small little low", "freundlich": "friendly kind", "vereinzelt": "single", "hoch": "high tall",
    "kundig": "skilled knowing", "rechts": "right", "oberer": "upper", "ruhmreich": "glorious", "hell": "bright light",
    "fertig": "ready finished", "gefäß": "vessel", "priester": "priest", "behälter": "container", "palast": "palace",
    "volk": "people", "fenster": "window", "elle": "cubit forearm", "tempel": "temple", "haus": "house",
    "herbst": "autumn", "frühling": "spring", "korb": "basket", "gras": "grass", "stoff": "cloth fabric",
    "gold": "gold", "silber": "silver", "schlaf": "sleep", "thron": "throne", "stuhl": "chair seat", "krug": "jug",
    "land": "land country", "pflanze": "plant", "brei": "porridge mush", "gegenstand": "object", "loch": "hole",
    "eibe": "yew", "schwur": "oath", "feind": "enemy", "blitz": "lightning", "dach": "roof", "regen": "rain",
    "angst": "fear", "schenkel": "thigh", "herr": "lord master", "reihe": "row line", "meer": "sea", "flügel": "wing",
    "figur": "figure", "fels": "rock cliff", "freude": "joy", "horn": "horn", "orakel": "oracle", "schoß": "lap",
    "fluch": "curse", "reinigung": "purification", "ufer": "bank shore", "zeichen": "sign", "recht": "right law",
    "sache": "thing matter", "krankheit": "illness disease", "wiese": "meadow", "gebäude": "building",
    "gesundheit": "health", "königin": "queen", "tier": "animal", "ecke": "corner", "finger": "finger",
    "donner": "thunder", "gerät": "implement tool", "flut": "flood", "teil": "part", "fundament": "foundation",
    "kampf": "battle fight", "tor": "gate", "lippe": "lip", "speer": "spear", "tuch": "cloth", "teig": "dough",
    "grenze": "border boundary", "säule": "pillar column", "rücken": "back", "brauch": "custom", "abend": "evening",
    "teich": "pond", "haufen": "heap pile", "sitz": "seat", "bett": "bed", "weisheit": "wisdom", "quelle": "spring source",
    "bein": "leg bone", "höhe": "height", "hunger": "hunger", "spur": "track trace trail", "wolke": "cloud",
    "arbeit": "work", "sesam": "sesame", "stimme": "voice", "kult": "cult", "zorn": "anger wrath", "bier": "beer",
    "speise": "food", "botschaft": "message", "versammlung": "assembly", "wohlbefinden": "well-being welfare",
    "vlies": "fleece", "libation": "libation", "brandopfer": "burnt offering", "ritual": "ritual",
    "verfehlung": "offence fault", "frieden": "peace", "glanz": "brightness splendour", "tote": "dead",
    "kämmerer": "chamberlain", "körperteil": "body part", "fackel": "torch", "riegel": "bolt bar",
    "brocken": "morsel crumb fragment", "klumpen": "lump", "güte": "goodness", "zauberei": "sorcery witchcraft",
    "entscheidung": "decision judgment", "bestrafung": "punishment", "flamme": "flame", "unsauberkeit": "impurity",
    "anrufung": "invocation", "fronarbeit": "corvée labour", "krummstab": "staff crook", "hohlmaß": "measure",
    "flasche": "bottle flask", "schemel": "stool", "beruhigung": "calming", "entweihung": "desecration",
    "kompensation": "compensation", "substitut": "substitute", "eile": "haste", "person": "person",
    "durchgang": "passage", "eingang": "entrance", "pfahl": "stake pole", "gericht": "dish court", "merkmal": "mark",
    "wachstum": "growth", "tassenhalter": "cup-holder", "schmuck": "jewellery ornament", "löffel": "spoon",
    "handlung": "act action", "schrein": "shrine", "truppen": "troops army", "feuerholz": "firewood",
    "weihrauch": "incense", "teppich": "carpet rug", "schöpfer": "creator", "verlauf": "course",
    "zeit": "time period", "jahr": "year", "versehen": "provide", "bekleiden": "clothe dress", "kleiden": "clothe dress",
    "nähern": "approach", "verschließen": "lock close", "zurückkehren": "return", "zurück": "back", "umwenden": "turn",
    "verneigen": "bow", "schilfrohr": "reed", "verhalten": "behave", "aufbrechen": "break set out", "ausgießen": "pour",
    "rösten": "roast", "backen": "bake", "braten": "roast fry", "kauen": "chew", "schlucken": "swallow",
    "atmen": "breathe", "riechen": "smell", "weinen": "weep cry", "lachen": "laugh", "kratzen": "scratch",
    "melken": "milk", "mästen": "fatten", "säen": "sow", "rauben": "rob plunder", "fesseln": "fetter bind",
    "zerreißen": "tear rend", "biegen": "bend", "beugen": "bend bow", "flechten": "plait weave", "spinnen": "spin",
    "kämmen": "comb card", "scheren": "shear", "glänzen": "shine gleam", "leuchten": "shine", "brüllen": "roar",
    "wachen": "watch wake", "erwachen": "awake wake", "aufwachen": "wake", "warten": "wait", "bewachen": "guard watch",
    "schützen": "protect", "helfen": "help", "verbieten": "forbid", "erlauben": "allow", "zeigen": "show",
    "verstecken": "hide", "kaufen": "buy", "verkaufen": "sell", "zahlen": "pay", "bezahlen": "pay", "leihen": "lend",
    "besiegen": "defeat conquer", "vernichten": "destroy annihilate", "verwüsten": "devastate", "verletzen": "injure",
    "heilen": "heal", "pressen": "press", "zusammenpressen": "press",
    "hinaufgehen": "go up ascend climb", "hinabgehen": "go down descend", "hinaufsteigen": "climb ascend mount",
    "steigen": "climb mount", "besteigen": "mount", "kriechen": "crawl creep", "schwimmen": "swim",
    "fliegen": "fly", "rennen": "run", "eintreten": "enter", "hineingehen": "go in enter", "herauskommen": "come out",
    "hinausgehen": "go out", "herankommen": "approach", "vorbeigehen": "pass", "umgeben": "surround",
    "umkreisen": "circle", "runde": "round circle", "verzehren": "consume", "auslöschen": "extinguish",
    "aufbewahren": "keep store", "bewahren": "keep preserve", "behüten": "guard protect", "versperren": "bar block",
    "abwehren": "ward off", "vertreiben": "drive away expel", "verbannen": "banish", "verschonen": "spare",
    "gedeihen": "thrive prosper", "blühen": "bloom flower", "welken": "wither", "faulen": "rot",
    "trocken": "dry", "nass": "wet", "feucht": "damp wet", "dick": "thick fat", "dünn": "thin", "scharf": "sharp",
    "stumpf": "blunt", "hart": "hard", "weich": "soft", "fest": "firm solid", "schnell": "quick fast swift",
    "langsam": "slow", "eng": "narrow", "tief": "deep", "flach": "flat", "rund": "round", "gerade": "straight",
    "krumm": "crooked bent", "nackt": "naked", "blind": "blind", "taub": "deaf", "lahm": "lame", "krank": "sick ill",
    "gesund": "healthy", "schön": "beautiful", "hässlich": "ugly", "reich": "rich", "arm": "poor arm", "stolz": "proud",
    "wild": "wild", "zahm": "tame", "fremd": "foreign strange", "eigen": "own", "ganz": "whole all", "halb": "half",
    "letzter": "last", "erster": "first", "zweiter": "second", "rechter": "right", "linker": "left", "link": "left",
    "jung": "young", "erwachsen": "adult", "gnädig": "gracious", "heftig": "violent", "furchtbar": "terrible",
    "sauber": "clean", "schmutzig": "dirty", "lebendig": "alive living", "tot": "dead", "wahr": "true", "falsch": "false",
    "gesamt": "whole all entire", "verborgen": "hidden", "offen": "open", "geschlossen": "closed",
    "himmel": "sky heaven", "sonne": "sun", "mond": "moon", "stern": "star", "wind": "wind", "sturm": "storm",
    "schnee": "snow", "eis": "ice", "nebel": "mist fog", "dampf": "steam smoke", "rauch": "smoke", "asche": "ash",
    "glut": "embers", "sand": "sand", "staub": "dust", "lehm": "clay", "ton": "clay", "erde": "earth soil",
    "boden": "ground floor", "acker": "field", "garten": "garden", "wald": "forest wood", "busch": "bush",
    "zweig": "branch twig", "ast": "branch", "wurzel": "root", "blatt": "leaf", "blüte": "blossom flower",
    "frucht": "fruit", "samen": "seed", "korn": "grain corn", "gerste": "barley", "weizen": "wheat", "mehl": "flour meal",
    "grütze": "groats meal", "brotlaib": "loaf bread", "kuchen": "cake", "fleischopfer": "meat offering",
    "opfer": "offering sacrifice", "opfergabe": "offering", "gabe": "gift", "geschenk": "gift present", "lohn": "wage reward",
    "preis": "price", "brautpreis": "bride-price", "schuld": "debt guilt", "strafe": "punishment penalty",
    "gesetz": "law", "eid": "oath", "bund": "bond alliance", "krieg": "war", "heer": "army", "sieg": "victory",
    "beute": "booty spoil", "gefangener": "prisoner captive", "sklave": "slave", "diener": "servant",
    "dienerin": "maidservant", "knecht": "servant", "magd": "maid", "herrin": "mistress lady", "könig": "king",
    "prinz": "prince", "fürst": "prince", "held": "hero", "krieger": "warrior", "hirte": "shepherd herdsman",
    "bauer": "farmer peasant", "schmied": "smith", "koch": "cook", "bäcker": "baker", "sänger": "singer",
    "witwe": "widow", "waise": "orphan", "kind": "child", "knabe": "boy", "mädchen": "girl", "greis": "old man",
    "schwiegervater": "father-in-law", "schwiegersohn": "son-in-law", "enkel": "grandson", "gatte": "husband",
    "gattin": "wife", "ehemann": "husband", "ehefrau": "wife", "braut": "bride", "bräutigam": "bridegroom",
    "nachkomme": "descendant offspring", "geschlecht": "family kin", "familie": "family", "sippe": "clan kin",
    "leib": "body", "körper": "body", "haut": "skin hide", "haar": "hair", "bart": "beard", "stirn": "forehead brow",
    "nase": "nose", "wange": "cheek", "kinn": "chin", "hals": "neck throat", "nacken": "neck", "schulter": "shoulder",
    "brust": "breast chest", "bauch": "belly", "leber": "liver", "niere": "kidney", "lunge": "lung", "darm": "intestine gut",
    "galle": "gall bile", "ferse": "heel", "zehe": "toe", "nagel": "nail", "kralle": "claw", "schwanz": "tail",
    "feder": "feather", "ei": "egg", "nest": "nest", "vogel": "bird", "adler": "eagle", "fisch": "fish", "schlange": "snake serpent",
    "wolf": "wolf", "löwe": "lion", "leopard": "leopard", "bär": "bear", "hirsch": "deer stag", "ziege": "goat",
    "bock": "buck he-goat", "widder": "ram", "lamm": "lamb", "kalb": "calf", "stier": "bull", "ochse": "ox",
    "esel": "donkey ass", "maultier": "mule", "schwein": "pig swine", "ferkel": "piglet", "maus": "mouse",
    "laus": "louse", "fliege": "fly", "biene": "bee", "wurm": "worm", "rad": "wheel", "wagen": "wagon chariot cart",
    "joch": "yoke", "pflug": "plough plow", "beil": "axe", "axt": "axe", "messer": "knife", "schwert": "sword",
    "bogen": "bow", "pfeil": "arrow", "schild": "shield", "helm": "helmet", "seil": "rope", "netz": "net",
    "faden": "thread", "nadel": "needle", "kleid": "garment dress", "gewand": "garment", "mantel": "cloak mantle",
    "gürtel": "belt girdle", "schuh": "shoe", "kopfbedeckung": "headdress", "tür": "door",     "wand": "wall", "zimmer": "room", "kammer": "chamber", "dorf": "village", "stadt": "city town", "burg": "fortress",
    "turm": "tower", "brücke": "bridge", "brunnen": "well", "ofen": "oven kiln", "herd": "hearth", "topf": "pot",
    "kessel": "cauldron kettle", "becher": "cup beaker", "tasse": "cup", "kanne": "jug pitcher", "trog": "trough",
    "tisch": "table", "lampe": "lamp", "kerze": "candle", "spiegel": "mirror", "kamm": "comb", "salbe": "ointment",
    "öl": "oil", "butter": "butter", "käse": "cheese", "fett": "fat", "talg": "tallow", "wachs": "wax",
    "farbe": "colour color", "bild": "image picture", "statue": "statue", "götterstatue": "divine statue",
    "geist": "spirit", "seele": "soul", "traum": "dream", "wunder": "miracle wonder",
    "wort": "word", "rede": "speech", "lied": "song", "laut": "sound", "ruf": "call cry",
    "name": "name", "zahl": "number", "maß": "measure", "gewicht": "weight", "länge": "length", "breite": "width breadth",
    "tiefe": "depth", "mitte": "middle", "rand": "edge rim", "seite": "side", "spitze": "tip point top",
    "anfang": "beginning", "ende": "end", "weg": "road way path", "pfad": "path", "straße": "street road",
    "reise": "journey", "flucht": "flight", "rückkehr": "return", "ankunft": "arrival",
    "gemeinsam": "common together", "gegenseitig": "mutual", "ewig": "eternal", "täglich": "daily",
    "innen": "inside within", "außen": "outside", "oberhalb": "above", "unterhalb": "below", "zusammen": "together",
}

DE_EN_MORE.update({"mitteilen": "inform tell report communicate", "trocknen": "dry", "zusammenfügen": "join fit",
                   "glühen": "glow", "entkommen": "escape flee", "schrecklich": "terrible dreadful"})
for _k, _v in fm.HIT_DE_EN.items():                    # united with the shared table
    DE_EN_MORE[_k] = " ".join(dict.fromkeys((_v + " " + DE_EN_MORE.get(_k, "")).split()))


# irregular English forms in glosses ('coarsely ground meal', 'bound') → the verb
_EN_IRREGULAR = {"ground": "grind", "bound": "bind", "broken": "break", "broke": "break", "born": "bear",
                 "borne": "bear", "spoken": "speak", "spoke": "speak", "sung": "sing", "sang": "sing",
                 "struck": "strike", "thrown": "throw", "threw": "throw", "taken": "take", "took": "take",
                 "given": "give", "gave": "give", "seen": "see", "saw": "see", "known": "know", "knew": "know",
                 "drunk": "drink", "drank": "drink", "eaten": "eat", "ate": "eat", "fallen": "fall", "fell": "fall",
                 "woven": "weave", "wove": "weave", "sewn": "sew", "dead": "die", "went": "go", "gone": "go",
                 "came": "come", "lain": "lie", "lay": "lay", "sat": "sit", "stood": "stand", "led": "lead",
                 "fed": "feed", "held": "hold", "brought": "bring", "bought": "buy", "sought": "seek",
                 "taught": "teach", "thought": "think", "dug": "dig", "spun": "spin", "stuck": "stick",
                 "split": "split", "cut": "cut", "put": "put", "set": "set", "shut": "shut", "burnt": "burn"}


def _stem(w: str) -> str:
    w = w.lower().strip("'’-")
    w = _EN_IRREGULAR.get(w, w)
    for suf, rep in (("ies", "y"), ("ing", ""), ("ied", "y"), ("ed", ""), ("es", ""), ("s", "")):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            w = w[: len(w) - len(suf)] + rep
            break
    return w[:-1] if w.endswith("e") and len(w) > 3 else w


def en_words(text) -> set[str]:
    """English gloss words (stemmed, stopwords off): 'to break, to crush' → {'break', 'crush'}."""
    if isinstance(text, (list, tuple)):
        text = " ; ".join(text)
    text = re.sub(r"\([^)]*\)", " ", (text or "").lower())
    return {_stem(w) for w in re.findall(r"[a-z]+(?:-[a-z]+)?", text) if w not in _EN_STOP and len(w) > 1}


def de_words(gloss: str) -> list[str]:
    """German gloss words: '(her)schicken' → herschicken, schicken; light verbs (machen, sein) dropped
    when the gloss has another word; stopwords and '(u. B.)' off."""
    g = (gloss or "").lower()
    g = re.sub(r"\(([a-zäöüß]+)\)([a-zäöüß]+)", r"\1\2 \2", g)
    ws = [w for w in re.findall(r"[a-zäöüß]+", g) if w not in _DE_STOP and len(w) > 1]
    if len(ws) > 1:
        ws = [w for w in ws if w not in _LIGHT_DE] or ws
    return list(dict.fromkeys(ws))


def tlh_gloss(lemma: str) -> str:
    return lemma.split("@", 1)[1] if "@" in lemma else ""


def tlh_en(lemma: str) -> set[str]:
    """English words for a TLHdig lemma's German gloss (fm.HIT_DE_EN + DE_EN_MORE)."""
    out = set()
    for w in de_words(tlh_gloss(lemma)):
        out |= en_words(DE_EN_MORE.get(w, ""))
    return out


def _de_stem(w: str) -> str:
    for suf in ("en", "ern", "eln", "e", "n"):
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            return w[: len(w) - len(suf)]
    return w


def gloss_agrees(lemma: str, edhil_gloss: str, lex_entries: list[dict]) -> bool:
    """Does the meaning of a lexicon entry agree with the Hittite word? An English word shared by the
    entry's meaning and Kloekhorst's gloss or the TLHdig gloss (translated), or a German word shared by
    the TLHdig gloss and the LIV meaning_de."""
    hit = en_words(edhil_gloss) | tlh_en(lemma)
    de = {_de_stem(w) for w in de_words(tlh_gloss(lemma))}
    for e in lex_entries:
        if hit & en_words(e.get("meaning") or []):
            return True
        if de and de & {_de_stem(w) for w in de_words(re.sub(r"['‘’]", " ", e.get("meaning_de") or ""))}:
            return True
    return False


# ---------------------------------------------------------------- EDHIL headword ↔ TLHdig lemma

_PUA_HEAD = re.compile(r"[\x01-\x1f]")


def edhil_stem_pattern(stem: str) -> re.Pattern | None:
    """An EDHIL headword stem → a regex on the TLHdig damaged key (fm.hit_damaged_key): ḫ/h/w/y/j
    deleted, š → s, marks off, geminates single, a control character (a lost glyph: ḫ, ē, ā, ī, ū, i̯,
    w) an optional vowel. None if the stem has no letter."""
    s = (stem or "").lower().replace("š", "s")
    s = "".join(c for c in unicodedata.normalize("NFD", s) if not unicodedata.combining(c))
    s = re.sub(r"[ḫhwyj]", "", s)
    s = re.sub(r"[^a-z\x01-\x1f]", "", s)
    s = re.sub(r"([a-z])\1+", r"\1", s)
    if not re.search(r"[a-z]", s):
        return None
    rx = "".join("[aeiou]?" if _PUA_HEAD.match(c) else c for c in s)
    return re.compile(rx)


def _skeleton_key(stem: str) -> str:
    """Consonants of a headword stem as the damaged key has them (h/ḫ/w/y/j deleted, geminates single
    within the parts between lost glyphs): the candidate index of EdhilIndex."""
    s = (stem or "").lower().replace("š", "s")
    s = "".join(c for c in unicodedata.normalize("NFD", s) if not unicodedata.combining(c))
    s = re.sub(r"[ḫhwyj]", "", s)
    parts = [re.sub(r"([a-z])\1+", r"\1", re.sub(r"[^a-z]", "", x)) for x in _PUA_HEAD.split(s)]
    return re.sub(r"[aeiou]", "", "".join(parts))


# derivational suffixes after TLHdig's last '=' that are not vowel-initial: causative -nu-, -ya-, imperfective -šk-
_SUFFIXES = frozenset({"nu", "ya", "ye/a", "iye/a", "aye/a", "šk", "ške/a", "iške/a", "ški/a"})


def lemma_keys(lemma: str) -> list[str]:
    """Damaged keys of a TLHdig lemma: each stem (fm.hit_lemma_stems), and, for a segmented lemma, the
    stem without its last segment when that is a short suffix (arr=a- → arr, mem=a- → mem,
    pešš=iye/a- → pešš)."""
    keys = [fm.hit_damaged_key(st) for st in fm.hit_lemma_stems(lemma)]
    base = fm._HIT_MARKS.sub("", lemma.split("@")[0]).strip()
    if "=" in base:
        head, tail = base.rsplit("=", 1)
        t = re.sub(r"[^a-zāēīūšḫ/]", "", tail)
        if len(t) <= 4 and re.match(r"[aeiouāēīū]", t) or t in _SUFFIXES:
            keys += [fm.hit_damaged_key(st) for st in fm.hit_lemma_stems(head)]
    return [k for k in dict.fromkeys(keys) if k]


class EdhilIndex:
    """EDHIL entries by the consonant skeleton of their stems, with each stem's pattern."""

    def __init__(self, entries: list[dict]):
        self.entries = entries
        self.idx: dict[str, list] = collections.defaultdict(list)
        for i, e in enumerate(entries):
            for st in e["stems"]:
                p = edhil_stem_pattern(st)
                if p is None:
                    continue
                self.idx[_skeleton_key(st)].append((i, p))

    def candidates(self, lemma: str) -> list[int]:
        """Indices of the entries one of whose stems matches one of the lemma's keys (lemma_keys)."""
        out = []
        for k in lemma_keys(lemma):
            for i, p in self.idx.get(re.sub(r"[aeiou]", "", k), ()):
                if p.fullmatch(k) and i not in out:
                    out.append(i)
        return out


# ---------------------------------------------------------------- PIE root skeletons

def _tokens(seg: str) -> list[str] | None:
    """A root segment in Kloekhorst's plain-text or the lexicon's notation → skeleton tokens:
    laryngeals H<set> (h1 → H1, h1/3 → H13, H → H123), dorsals K<k|g|gh|*>, dentals T<t|d|dh|*>,
    labials p b bh, resonants r l m n y w, s. Vowels (a e o, length, accent) are dropped (ablaut);
    i/u are y/w; palatal and plain velars fold, a labiovelar is a velar + w. Control characters of the
    text layer: \\x05 y, \\x06 w, a run of \\x02-\\x04 a dorsal of unknown series (K*, or K*h when an h
    follows: an aspirate); anything else → None."""
    s = unicodedata.normalize("NFD", seg)
    s = s.replace("ʰ", "h").replace("ʷ", "w").replace("₁", "1").replace("₂", "2").replace("₃", "3")
    s = "".join(c for c in s if not unicodedata.combining(c))
    out, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        nxt = s[i + 1] if i + 1 < n else ""
        if c == "h" and nxt.isdigit():
            j = i + 2
            ds = {nxt}
            while j + 1 < n and s[j] == "/" and s[j + 1].isdigit():
                ds.add(s[j + 1])
                j += 2
            out.append("H" + "".join(sorted(ds)))
            i = j
            continue
        if c == "H":
            out.append("H123")
            i += 1
            continue
        if c in "aeoāēō":
            i += 1
            continue
        if c in "iy":
            out.append("y")
        elif c in "uw":
            out.append("w")
        elif c in "rlmns":
            out.append(c)
        elif c in "pbtdkg":
            asp = nxt == "h" and not (i + 2 < n and s[i + 2].isdigit())
            cls = "P" if c in "pb" else "T" if c in "td" else "K"
            val = {"p": "p", "b": "b", "t": "t", "d": "d", "k": "k", "g": "g"}[c] + ("h" if asp and c not in "ptk" else "")
            out.append(val if cls == "P" else cls + val)
            i += 2 if asp else 1
            continue
        elif c == "K":
            out.append("K*")
        elif c == "T":
            out.append("T*")
        elif c in "\x02\x03\x04":
            j = i
            while j < n and s[j] in "\x02\x03\x04":
                j += 1
            asp = j < n and s[j] == "h" and not (j + 1 < n and s[j + 1].isdigit())
            out.append("K*h" if asp else "K*")      # *ǵʰih₁- is aspirated: not *ǵeyH-
            j += asp
            i = j
            continue
        elif c == "\x05":
            out.append("y")
        elif c == "\x06":
            out.append("w")
        elif c in "/":
            pass                                # é/ó: vowels either way
        else:
            return None
        i += 1
    return out


def _paren_variants(s: str) -> list[str]:
    return list(dict.fromkeys([re.sub(r"\([^)]*\)", "", s), re.sub(r"[()]", "", s)]))


def root_skeletons(form: str) -> list[tuple]:
    """Kloekhorst's PIE form → skeletons of its root (the first hyphen segment; after a reduplication
    syllable, the second: *mé-molh2- → m l H2). [] for a suffix (*-d), a compound (+) or an enclitic."""
    s = (form or "").strip().lstrip("*")
    if not s or s.startswith(("-", "=")) or "+" in s:
        return []
    out = []
    for v in _paren_variants(s):
        segs = [x for x in v.split("-") if x != ""]
        if not segs:
            continue
        t0 = _tokens(segs[0])
        if t0 is None:
            continue
        if len(t0) == 1 and len(segs) > 1:
            t1 = _tokens(segs[1])
            if t1 and t1[0] == t0[0]:
                t0 = t1                         # reduplication
        if t0 and len(t0) >= 2:
            out.append(tuple(t0))
    return list(dict.fromkeys(out))


def lex_root_skeletons(form: str) -> list[tuple]:
    """A lexicon root form (bʰers-, (s)teg-, h₁ey-) → skeletons."""
    s = (form or "").strip().lstrip("*").rstrip("-")
    out = []
    for v in _paren_variants(s):
        t = _tokens(v.replace("-", ""))
        if t:
            out.append(tuple(t))
    return list(dict.fromkeys(out))


def _tok_ok(a: str, b: str) -> bool:
    if a == b:
        return True
    if a[0] == "H" and b[0] == "H":
        return bool(set(a[1:]) & set(b[1:]))
    if a[0] == b[0] and a[0] in "KT":
        if a[1:] == "*" or b[1:] == "*":
            return True
        if "*h" in (a[1:], b[1:]):              # a lost dorsal glyph + h: an aspirate of unknown series
            return {a[1:], b[1:]} <= {"*h", "gh"}
        return False
    return False


def _coarse(t: tuple) -> tuple:
    return tuple(x[0] if x[0] in "HKT" else x for x in t)


def skeletons_agree(a: tuple, b: tuple) -> bool:
    return len(a) == len(b) and all(_tok_ok(x, y) for x, y in zip(a, b))


class RootIndex:
    """Lexicon roots (kind 'root') by coarse skeleton."""

    def __init__(self, lexicon: list[dict]):
        self.by_id = {e["id"]: e for e in lexicon}
        self.idx: dict[tuple, list] = collections.defaultdict(list)
        for e in lexicon:
            if e.get("kind") != "root":
                continue
            for f in [e["form"], *(e.get("variants") or [])]:
                for sk in lex_root_skeletons(f):
                    self.idx[_coarse(sk)].append((sk, e["id"]))

    def lookup(self, skel: tuple) -> list[str]:
        out = []
        for sk, i in self.idx.get(_coarse(skel), ()):
            if skeletons_agree(skel, sk) and i not in out:
                out.append(i)
        return out


def resolve_root(forms: list[str], lemma: str, edhil_gloss: str, roots: RootIndex,
                 gmap: dict | None = None) -> tuple[frozenset, str] | None:
    """Kloekhorst's PIE forms → (one lexicon root group's ids, the form used), at the root: the root
    skeleton agrees with a lexicon root's AND the meaning agrees (gloss_agrees). None unless exactly one
    root group passes for the first form that has a skeleton match."""
    gmap = gmap or {}
    for f in forms:
        cands = []
        for sk in root_skeletons(f):
            cands += [i for i in roots.lookup(sk) if i not in cands]
        if not cands:
            continue
        ok = [i for i in cands if gloss_agrees(lemma, edhil_gloss, [roots.by_id[i]])]
        groups = {gmap.get(i, i) for i in ok}
        if len(groups) == 1:
            return frozenset(ok), f
        return None                     # skeleton found, meaning disagrees (or several roots agree)
    return None


# ---------------------------------------------------------------- the EDHIL route

def _readable(head: str) -> str:
    return _PUA_HEAD.sub("·", head)


def _with_parents(e: dict, by_id: dict) -> list[dict]:
    """An entry, and its parents when it has no meaning of its own."""
    if e.get("meaning"):
        return [e]
    return [e] + [by_id[p] for p in e.get("parents") or () if p in by_id]


def formation_matches(lemma: str, form: str) -> bool:
    """Do not assign a base formation to a marked TLHdig derivative.

    The EDHIL headword search deliberately strips these suffixes for root
    retrieval. That is not evidence that the derivative inherits its base's
    lexeme. Inflectional endings (including nominal -ant- ergatives) are not
    derivational suffixes here.
    """
    base = lemma.split("@")[0]
    tail = base.rsplit("=", 1)[-1].strip("-") if "=" in base else ""
    key = fm.pie_fuzzy_key(form)
    if tail == "nu":
        return bool(re.search(r"n(?:eu|u)", key))
    if tail in {"išk", "iešk", "anna"}:
        return "sk" in key
    if tail in {"iya", "iya-2", "iye/a", "e/a", "ā(e)"}:
        return bool(re.search(r"i(?:e|o)", key))
    if tail in {"eš", "aḫḫ"}:
        return False  # no reviewed matching PIE formation in this route
    return True


def formation_roots(ids, by_id):
    """Existing root ancestors only; never turn a root-group label into an id."""
    todo, seen, out = list(ids), set(), set()
    while todo:
        i = todo.pop()
        if i in seen or i not in by_id:
            continue
        seen.add(i)
        e = by_id[i]
        if e.get("kind") == "root":
            out.add(i)
        else:
            todo.extend(e.get("parents") or [])
    return frozenset(out)


def same_formation(a, b):
    """Compare complete formations, allowing EDHIL's uncertain dorsal notation.

    Ablaut and middle -r variation do not change the formation; -ti, -t,
    -ei and -to do. Never compare only the initial root segment.
    """
    if fm.pie_fuzzy_key(a) == fm.pie_fuzzy_key(b):
        return True
    for av in _paren_variants(a.lstrip("*")):
        for bv in _paren_variants(b.lstrip("*")):
            at, bt = _tokens(av.replace("-", "")), _tokens(bv.replace("-", ""))
            if at and bt and skeletons_agree(tuple(at), tuple(bt)):
                # Keep the ending's vowels: hi -ei is not a middle -o.
                if fm.pie_fuzzy_key(a)[-2:] == fm.pie_fuzzy_key(b)[-2:]:
                    return True
            if fm.pie_fuzzy_key(b).endswith("tor") and same_formation(a, b[:-1]):
                return True
    return False


def check_formations(recs, lexicon, entries):
    """Apply EDHIL formation evidence to every automatic route, including chains.

    A base's identity can survive a formation mismatch, but its lexeme cannot.
    Unresolved headwords are left to reviewed overrides; damaged forms are not
    silently treated as positive whole-form evidence.
    """
    by_id = {e["id"]: e for e in lexicon}
    index = EdhilIndex(entries)
    out = dict(recs)
    for lemma, rec in recs.items():
        cs = [entries[i] for i in index.candidates(lemma)
              if tlh_en(lemma) & en_words(entries[i]["gloss"])]
        forms = [f for e in cs if not e["doubtful"] and not e["foreign"] for f in e["pie"]]
        ids, notes = set(), []
        for i in rec.ids:
            e = by_id.get(i, {})
            verbal = e.get("pos") == "verb" or any(
                fm.pie_fuzzy_key(s).endswith(("enti", "ent")) for s in e.get("stems", []))
            # A shared plural -enti cannot establish a singular mi/hi formation.
            matches = [f for f in forms if any(same_formation(f, s) for s in
                       [e.get("form", ""), *e.get("variants", [])])]
            mismatch = i.startswith("pie-lex-") and (
                not formation_matches(lemma, e.get("form", "")) or
                (verbal and forms and not matches))
            if not mismatch:
                ids.add(i)
                continue
            ids.update(formation_roots([i], by_id))
            notes.append(f"note:Formation differs from {i}; root only. EDHIL "
                         + ", ".join(e["printed"] or e["page"] for e in cs)
                         + "; formations: " + ", ".join(_readable(f) for f in forms))
        if notes:
            if ids:
                out[lemma] = fm.MapRec(rec.key, rec.word, frozenset(ids), rec.path,
                                      "kloekhorst-root", "low", rec.sources + tuple(notes), rec.gloss)
            else:
                del out[lemma]
    return out


def resolve_form(forms: list[str], lemma: str, edhil_gloss: str, fz: fm.FuzzyPie, by_id: dict,
                 gmap: dict | None = None) -> tuple[frozenset, str] | None:
    """Kloekhorst's PIE forms → (ids, form) by a whole-form match in the lexicon (FuzzyPie, a key of at
    least 4 letters). One lexeme (or the entries of one root group) is taken as it is; a root, or
    homographs of several groups (*kʷer- 'cut' / *kʷer- 'make'), or a short stem (*h₂us-, a tree-path
    stub of *h₂ews- 'draw water'), only for the ids whose meaning (or, without one, their parents')
    agrees (gloss_agrees) and form one group."""
    gmap = gmap or {}
    for f in forms:
        if _PUA_HEAD.search(f):
            continue                    # a lost glyph: the plain key would drop a consonant (*h1orǵ- → *h1or-)
        ids, how = fz.lookup(f)
        if not ids or how != "form" or len(fm.pie_fuzzy_key(f)) < 4:
            continue
        groups = {gmap.get(x, x) for x in ids}
        lexemes = [by_id.get(x, {}) for x in ids]
        stub = len(fm.pie_fuzzy_key(f)) < 5 and all((e.get("form") or "").endswith("-") for e in lexemes)
        if len(groups) == 1 and all(e.get("kind") != "root" for e in lexemes) and not stub:
            accepted = frozenset(ids) if formation_matches(lemma, f) else formation_roots(ids, by_id)
            return (accepted, f) if accepted else None
        ok = {x for x in ids if x in by_id and gloss_agrees(lemma, edhil_gloss, _with_parents(by_id[x], by_id))}
        if ok and len({gmap.get(x, x) for x in ok}) == 1:
            accepted = frozenset(ok) if formation_matches(lemma, f) else formation_roots(ok, by_id)
            return (accepted, f) if accepted else None
        return None
    return None


def _resolve_forms(forms, lemma, e, fz, roots, by_id, gmap):
    r = resolve_form(forms, lemma, e["gloss"], fz, by_id, gmap)
    if r:
        how = "kloekhorst-root" if not formation_matches(lemma, r[1]) else "kloekhorst"
        return r[0], r[1], how
    r = resolve_root(forms, lemma, e["gloss"], roots, gmap)
    if r:
        return r[0], r[1], "kloekhorst-root"
    return None


def resolve_entry(e: dict, lemma: str, fz: fm.FuzzyPie, roots: RootIndex, by_id: dict,
                  gmap: dict | None = None, doubtful: bool = False) -> tuple[frozenset, str, str] | str:
    """An EDHIL entry → (ids, PIE form used, how) or the reason it stays unmapped ('foreign',
    'doubtful', 'no_pie', 'pie_unresolved', 'not_doubtful', 'alternatives_disagree').

    doubtful=True is the low-confidence tier: only entries whose PIE line has a '?' are resolved, by the
    same machinery; when Kloekhorst gives alternatives ('or'), every alternative must resolve and all to
    the same root group, else the entry is skipped. how is then 'kloekhorst-doubtful'."""
    gmap = gmap or {}
    if e["foreign"]:
        return "foreign"
    if not e["pie"]:
        return "no_pie"
    if doubtful:
        if not e["doubtful"]:
            return "not_doubtful"
        res = [_resolve_forms(a, lemma, e, fz, roots, by_id, gmap) for a in e.get("pie_alts") or [e["pie"]]]
        if any(r is None for r in res):
            return "pie_unresolved"
        groups = [frozenset(gmap.get(i, i) for i in r[0]) for r in res]
        if len(set(groups)) != 1:
            return "alternatives_disagree"
        return res[0][0], res[0][1], "kloekhorst-doubtful"
    if e["doubtful"]:
        return "doubtful"
    r = _resolve_forms(e["pie"], lemma, e, fz, roots, by_id, gmap)
    return r if r else "pie_unresolved"


def kloekhorst_hittite(lemmas, lexicon: list[dict], root: Path = ROOT, gmap: dict | None = None,
                       entries: list[dict] | None = None, stats: dict | None = None, doubtful: bool = False) -> dict:
    """TLHdig lemma → MapRec via EDHIL.

    Headword: of the entries whose stem pattern matches a key of the lemma (EdhilIndex), those whose
    English gloss shares a word with the TLHdig gloss (translated: tlh_en). One such entry, or several
    that resolve to the same ids, is used; none, or several that disagree, leave the lemma unmapped.
    PIE (resolve_entry): no line, a '?' on it, or a foreign label → unmapped; a whole-form match in the
    lexicon (resolve_form) → how 'kloekhorst'; else the root (resolve_root: skeleton and meaning) → how
    'kloekhorst-root'. sources: 'headword-unique' (one candidate entry) or 'headword-gloss' (several,
    the gloss chose)."""
    ents = entries if entries is not None else fm.kloekhorst_entries(root)
    ei = EdhilIndex(ents)
    fz = fm.FuzzyPie(lexicon)
    roots = RootIndex(lexicon)
    by_id = {e["id"]: e for e in lexicon}
    gmap = gmap or {}
    st = stats if stats is not None else {}
    bump = lambda k: st.__setitem__(k, st.get(k, 0) + 1)
    out = {}
    for lem in lemmas:
        cs = ei.candidates(lem)
        if not cs:
            bump("no_headword")
            continue
        en = tlh_en(lem)
        agree = [i for i in cs if en & en_words(ents[i]["gloss"])]
        if not agree:
            bump("headword_no_gloss_agreement")
            continue
        res = [resolve_entry(ents[i], lem, fz, roots, by_id, gmap, doubtful) for i in agree]
        ok = [(i, r) for i, r in zip(agree, res) if not isinstance(r, str)]
        if len(agree) > 1 and (len(ok) != len(agree) or len({r[0] for _, r in ok}) != 1):
            bump("headword_ambiguous")
            continue
        if not ok:
            bump(res[0])
            continue
        i, (ids, f, how) = ok[0]
        e = ents[i]
        sel = "unique" if len(cs) == 1 else "gloss"
        bump(how + ":" + sel)
        head = _readable(e["head"])
        out[lem] = fm.MapRec(fm.hit_damaged_key((fm.hit_lemma_stems(lem) or [lem])[0]), head, ids,
                             (f"hit:{lem}", f"kloekhorst:{e['page']}:{head}", f"edhil-page:{e['printed']}",
                              f"ine-pro:{_readable(f)}"),
                             how, "medium" if how == "kloekhorst" else "low",
                             ("kloekhorst", f"headword-{sel}") +
                             ((f"note:EDHIL p. {e['printed']}: base formation {_readable(f)}; "
                               "TLHdig derivative mapped at root only",) if not formation_matches(lem, f) else ()) +
                             ((f"note:EDHIL p. {e['printed']}: PIE line marked "
                                                                   "doubtful by Kloekhorst",) if doubtful else ()),
                             e["gloss"])
    return out


# ---------------------------------------------------------------- the table

def hittite_table(toks, lm: fm.LangMapping, lexicon: list[dict], gmap: dict, root: Path = ROOT,
                  stats: dict | None = None) -> tuple[dict, dict]:
    """(lemma → MapRec, coverage notes) for the TLHdig lemmas: kaikki + lexicon (gloss-checked) first,
    for every lemma but names and clitic chains (an adverb, preverb or pronoun keeps its etymology,
    though it is not a content word); EDHIL second, for content lemmas; where both map a lemma and
    agree, the shared ids are kept."""
    m, recs = fm.corpus_mapping(toks, lm, lemma_keys=fm.hit_tlh_keys, gmap=gmap)
    content = {t.lemma for t in toks if t.content}
    names = {t.lemma for t in toks if t.pos == "name"}
    ok = {l: r for l, r in recs.items()
          if l not in names and not fm.hit_is_clitic_chain(l) and fm.hittite_gloss_ok(l, r)}
    lemmas = sorted(content)
    kh = kloekhorst_hittite(lemmas, lexicon, root, gmap=gmap, stats=stats)
    cont = [t for t in toks if t.content]
    share = lambda d: round(sum(t.lemma in d for t in cont) / max(1, len(cont)), 4)
    cov = {"kaikki_lexicon_raw": share(recs), "kaikki_lexicon_gloss_checked": share(ok),
           "kloekhorst_only": share(kh),
           "kloekhorst_agree_with_kaikki": sum(1 for l in set(kh) & set(ok) if kh[l].ids & ok[l].ids),
           "kloekhorst_disagree_with_kaikki": sum(1 for l in set(kh) & set(ok) if not kh[l].ids & ok[l].ids)}
    final = dict(ok)
    for l, r in kh.items():
        if l not in final:
            final[l] = r
        elif r.ids & final[l].ids:
            fr = final[l]
            final[l] = fm.MapRec(fr.key, fr.word, fr.ids & r.ids, fr.path, fr.how, "high",
                                 fr.sources + ("kloekhorst",), fr.gloss)
    final = check_formations(final, lexicon, fm.kloekhorst_entries(root))
    cov["final"] = share(final)
    return final, cov


def table_rows(recs: dict) -> list[dict]:
    """The rows of data/research/formulas/mapping/hit.jsonl (scripts/formula_search.py write_mapping_tables)."""
    rows = []
    for lem in sorted(recs):
        r = recs[lem]
        rows.append({"corpus": "hit", "lang": "hit", "lemma": lem, "word": r.word, "lex_id": sorted(r.ids),
                     "path": list(r.path), "how": r.how, "confidence": r.confidence, "sources": list(r.sources)})
    return rows


# ---------------------------------------------------------------- the doubtful tier (retrieval only)

DOUBTFUL_TABLE = "data/research/formulas/mapping/hit-doubtful.jsonl"
REVIEWED_DOUBTFUL = "data/research/formulas/hit-reviewed-doubtful.json"


def reviewed_doubtful(lexicon: list[dict], root: Path = ROOT) -> dict:
    """Explicit EDHIL decisions for retrieval only; never ordinary mapping overrides.

    Validate even unused decisions so stale ids and misspelled fields fail regeneration.
    Notes are reviewer paraphrases; no book prose is stored here.
    """
    import json
    p = Path(root) / REVIEWED_DOUBTFUL
    if not p.exists():
        return {}
    known = {e["id"] for e in lexicon}
    out = {}
    fields = {"lemma", "lex_id", "head", "page", "pie", "note"}
    for row in json.loads(p.read_text("utf-8")):
        if set(row) != fields:
            raise ValueError("Invalid reviewed Hittite doubtful fields")
        if any(not isinstance(row[k], str) or not row[k].strip() for k in fields - {"lex_id"}):
            raise ValueError("Reviewed Hittite doubtful evidence must be nonempty text")
        ids = row["lex_id"]
        if not isinstance(ids, list) or not ids or any(not isinstance(i, str) or i not in known for i in ids):
            raise ValueError("Reviewed Hittite doubtful decision needs existing lexicon ids")
        lem = row["lemma"]
        if lem in out:
            raise ValueError(f"Duplicate reviewed Hittite doubtful lemma: {lem}")
        if not re.fullmatch(r"\d+(?:-\d+)?", row["page"]):
            raise ValueError("Reviewed Hittite doubtful decision needs an EDHIL page")
        out[lem] = fm.MapRec(
            fm.hit_damaged_key((fm.hit_lemma_stems(lem) or [lem])[0]), row["head"], frozenset(ids),
            (f"hit:{lem}", f"kloekhorst:reviewed:{row['head']}", f"edhil-page:{row['page']}",
             f"ine-pro:{row['pie']}"), "kloekhorst-doubtful", "low",
            ("kloekhorst", "reviewed-doubtful", f"note:{row['note']}"), "")
    return out


def doubtful_table(toks, lexicon: list[dict], gmap: dict, main: dict, root: Path = ROOT,
                   stats: dict | None = None) -> dict:
    """lemma → MapRec (how 'kloekhorst-doubtful', confidence 'low') for content lemmas that the main
    table does not map and that no override decides, from EDHIL entries whose PIE line Kloekhorst marks
    doubtful (kloekhorst_hittite(doubtful=True)), supplemented by reviewed decisions for notation,
    gloss and derivative-key failures. Written to DOUBTFUL_TABLE, never to hit.jsonl."""
    from . import mapping as mp
    ov = mp.load_overrides(root)
    lemmas = sorted({t.lemma for t in toks if t.content} - set(main))
    lemmas = [l for l in lemmas if not mp.decisions_for("hit", l, ov, root=root)]
    out = kloekhorst_hittite(lemmas, lexicon, root, gmap=gmap, stats=stats, doubtful=True)
    reviewed = reviewed_doubtful(lexicon, root)
    out.update({l: r for l, r in reviewed.items() if l in lemmas})
    return {l: fm.MapRec(r.key, r.word, r.ids, r.path, r.how, "low", r.sources, r.gloss) for l, r in out.items()}


def doubtful_note(row: dict) -> str:
    """'Kloekhorst EDHIL s.v. <head>, p. <page>: PIE <form> (marked doubtful)' for a doubtful-tier row."""
    if "reviewed-doubtful" in row.get("sources", []):
        return next(x.removeprefix("note:") for x in row["sources"] if x.startswith("note:"))
    head = row["path"][1].split(":", 2)[2]
    page = next(x for x in row["path"] if x.startswith("edhil-page:")).split(":", 1)[1]
    return f"Kloekhorst EDHIL s.v. {head}, p. {page}: PIE {row['path'][-1].split(':', 1)[1]} (marked doubtful)"


def read_union_table(root: Path = ROOT, doubtful: bool = True, *, qualifications: dict | None = None) -> dict:
    """lemma → lex ids tuple: hit.jsonl with the mapping errata applied (what the 8c loaders read through
    _table('hit')), plus, if doubtful, the rows of hit-doubtful.jsonl for lemmas the main table leaves
    unmapped and no override decides. For retrieval only (Stage C-S may opt in); the corpus tables and the
    Tier 2 secure check never see the doubtful rows. If supplied, qualifications is populated by lemma
    with the doubtful equations' reader-facing evidence, independently of the retrieval ids."""
    import json
    from . import mapping as mp
    if qualifications is not None:
        qualifications.clear()
    rows = mp.read_table("hit", root)
    out = dict(fm.apply_table_overrides("hit", {r["lemma"]: tuple(r["lex_id"]) for r in rows}, root=root))
    p = Path(root) / DOUBTFUL_TABLE
    if doubtful and p.exists():
        ov = mp.load_overrides(root)
        for line in p.read_text("utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                if r["lemma"] not in out and not mp.decisions_for("hit", r["lemma"], ov, root=root):
                    out[r["lemma"]] = tuple(sorted(r["lex_id"]))
                    if qualifications is not None:
                        qualifications[r["lemma"]] = {
                            "confidence": "low", "source": "Kloekhorst EDHIL",
                            "page": next(x.split(":", 1)[1] for x in r["path"]
                                         if x.startswith("edhil-page:")),
                            "reason": r.get("note") or doubtful_note(r),
                        }
    return out
