"""addr_en.py: romanize the address database (tools/addrdb.py) into script/addr_*.tsv, which the build packs.

    <venv>/python -X utf8 tools/addr_en.py [--stats]

Needs the cached sources in work/addr/src/ (docs/re/text.md "Address database", decision D20):
  posuto_2026.11.0.db, posuto_0.1.10.json.gz  Japan Post KEN_ALL with kana readings (PyPI package posuto; Japan Post
                                              itself 404s outside Japan). Keyed by postal code.
  wikidata_dissolved.csv, wikidata_current.csv  municipality kana (P1814): the game's 2002 data names ~1800
                                              municipalities merged away since.
and, for the last fallback only, fugashi + unidic-lite (a venv: they are not in the repo's requirements).

Every output row says where its reading came from (column `src`), so the weak ones (unidic) can be reviewed:
  addr_pref.tsv  idx  jp  en
  addr_city.tsv  idx  jp  kana  en  src
  addr_town.tsv  pref  city  jp  kana  en  src     (one row per distinct (pref, city, town); empty town = no row)
English: Hepburn without macrons (Tokyo, Chuo), municipality suffix kept (-shi -ku -cho/-machi -mura/-son), the
county (-gun) dropped, a designated city's -shi dropped before its ward (Sapporo Chuo-ku).
"""
import argparse
import csv
import gzip
import json
import re
import sqlite3
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import addrdb  # noqa: E402

SRC = ROOT / "work" / "addr" / "src"
LONG_WORD = 15                  # a romanized word longer than the form's right-hand chunks (15 bytes) gets split


def break_long(w):
    """A word still longer than LONG_WORD: break it at the syllable boundary (after a vowel, or a syllabic n)
    nearest its middle, the second part capitalized; recursively."""
    if len(w) <= LONG_WORD:
        return w
    best = None
    for i in range(3, len(w) - 2):
        a, b = w[i - 1], w[i]
        if b == "-" or a == "-" or a == "'":
            continue
        ok = a in "aeiou" and b not in "aeiou" or (a == "n" and b not in "aeiouy'")
        if ok and w[i:i + 2] not in ("n'",):
            score = max(i, len(w) - i)
            if best is None or score < best[0]:
                best = (score, i)
    if best is None:
        return w
    i = best[1]
    return break_long(w[:i]) + " " + break_long(w[i].upper() + w[i + 1:])
OUT = ROOT / "script"

# ---------------------------------------------------------------- Hepburn
_K = {}
for row in """
ア a,イ i,ウ u,エ e,オ o,カ ka,キ ki,ク ku,ケ ke,コ ko,サ sa,シ shi,ス su,セ se,ソ so,タ ta,チ chi,ツ tsu,テ te,ト to,
ナ na,ニ ni,ヌ nu,ネ ne,ノ no,ハ ha,ヒ hi,フ fu,ヘ he,ホ ho,マ ma,ミ mi,ム mu,メ me,モ mo,ヤ ya,ユ yu,ヨ yo,
ラ ra,リ ri,ル ru,レ re,ロ ro,ワ wa,ヰ i,ヱ e,ヲ o,ガ ga,ギ gi,グ gu,ゲ ge,ゴ go,ザ za,ジ ji,ズ zu,ゼ ze,ゾ zo,
ダ da,ヂ ji,ヅ zu,デ de,ド do,バ ba,ビ bi,ブ bu,ベ be,ボ bo,パ pa,ピ pi,プ pu,ペ pe,ポ po,ヴ vu,
ァ a,ィ i,ゥ u,ェ e,ォ o,ヮ wa,ヵ ka,ヶ ke
""".replace("\n", "").split(","):
    if row.strip():
        k, v = row.split()
        _K[k] = v
_YOON = {"ャ": "a", "ュ": "u", "ョ": "o"}
_SMALL_V = {"ァ": "a", "ィ": "i", "ゥ": "u", "ェ": "e", "ォ": "o"}


def _units(kana):
    """Katakana -> list of romaji syllables (strings) and passthrough chars."""
    out = []
    i = 0
    while i < len(kana):
        c = kana[i]
        n = kana[i + 1] if i + 1 < len(kana) else ""
        if c in _K and n in _YOON:
            base = _K[c]
            if base in ("shi", "chi", "ji"):
                out.append(base[:-1] + _YOON[n])
            else:
                out.append(base[:-1] + "y" + _YOON[n])
            i += 2
            continue
        if c in _K and n in _SMALL_V and c not in _SMALL_V:
            base = _K[c]
            special = {("フ", "ァ"): "fa", ("フ", "ィ"): "fi", ("フ", "ェ"): "fe", ("フ", "ォ"): "fo",
                       ("テ", "ィ"): "ti", ("デ", "ィ"): "di", ("ウ", "ィ"): "wi", ("ウ", "ェ"): "we",
                       ("ウ", "ォ"): "wo", ("シ", "ェ"): "she", ("チ", "ェ"): "che", ("ジ", "ェ"): "je",
                       ("ヴ", "ァ"): "va", ("ヴ", "ィ"): "vi", ("ヴ", "ェ"): "ve", ("ヴ", "ォ"): "vo"}
            if (c, n) in special:
                out.append(special[(c, n)])
                i += 2
                continue
            out.append(base[:-1] + _SMALL_V[n])
            i += 2
            continue
        out.append(_K.get(c, c))
        i += 1
    return out


def hepburn(kana):
    """Katakana reading -> lowercase Hepburn without macrons: ou/oo/uu long vowels collapse (one lengthener per
    syllable), ー dropped, ッ doubles (tch), ン = n (n' before a vowel or y)."""
    kana = unicodedata.normalize("NFKC", kana)
    units = _units(kana)
    res = []
    prev_long = False
    gem = False
    for k, u in enumerate(units):
        if u == "|":                     # morpheme boundary from ou_hint: no long-vowel merge across it
            prev_long = True
            continue
        if u == "ー":
            prev_long = True
            continue
        if u == "ッ":
            gem = True
            continue
        if u == "ン":
            nxt = next((x for x in units[k + 1:] if x not in ("ー",)), "")
            res.append("n'" if nxt[:1] in ("a", "i", "u", "e", "o", "y") else "n")
            prev_long = False
            continue
        if not re.match(r"[a-z]", u):
            res.append(u)
            prev_long = False
            gem = False
            continue
        last = res[-1] if res else ""
        if not prev_long and not gem and last and re.match(r"[a-z]", last[-1:]):
            if u == "u" and last[-1] in "ou":
                prev_long = True
                continue
            if u == "o" and last[-1] == "o":
                prev_long = True
                continue
        if gem:
            res.append(("t" if u.startswith("ch") else u[0]))
            gem = False
        res.append(u)
        prev_long = False
    s = "".join(res)
    return s


# kanji whose reading starts with ウ: after an o-row kana (丸の内 マルノウチ, 堀之内, 野上 ノウエ?) that ウ starts
# the next word and is no long vowel; the rest of each reading must follow it in the kana
U_KANJI = {"内": "チ", "上": "エ", "浦": "ラ", "海": "ミ", "牛": "シ", "梅": "メ", "瓜": "リ", "馬": "マ",
           "魚": "オ", "臼": "ス", "歌": "タ", "氏": "ジ", "打": "チ", "植": "エ", "埋": "メ", "姥": "バ"}
O_ROW = "オコソトノホモヨロゴゾドボポョォ"


def ou_hint(kanji, kana):
    """Mark ウ that starts a ウ-initial kanji's reading after an o-row kana (マルノ|ウチ) for hepburn."""
    for k, rest in U_KANJI.items():
        if k not in kanji:
            continue
        i = kana.find("ウ" + rest, 1)
        while i > 0:
            if kana[i - 1] in O_ROW:
                kana = kana[:i] + "|" + kana[i:]
                i += 1
            i = kana.find("ウ" + rest, i + 1)
    return kana


def title(s):
    """'nishikagura3sen' style -> word-capitalized; a digit run gets a space before and a hyphen after."""
    s = re.sub(r"(?<=[a-z'])(\d)", r" \1", s)
    s = re.sub(r"(\d)(?=[a-z])", r"\1-", s)
    s = s.replace("・", " ").replace("－", "-").replace("、", " ")
    s = re.sub(r"\s+", " ", s).strip()
    out = []
    for w in s.split(" "):
        out.append(w[:1].upper() + w[1:])
    return " ".join(out)


# ---------------------------------------------------------------- sources
def load_posuto():
    recs = []
    for (d,) in sqlite3.connect(SRC / "posuto_2026.11.0.db").execute("select data from postal_data"):
        recs.append(json.loads(d))
    old = json.load(gzip.open(SRC / "posuto_0.1.10.json.gz", "rt", encoding="utf8"))
    recs += list(old.values())
    return recs


def load_wikidata():
    """-> {name: [(district or '', kana, end)]} for dissolved + current municipalities (kana as katakana)."""
    res = defaultdict(list)
    for fn, dis in (("wikidata_dissolved.csv", True), ("wikidata_current.csv", False),
                    ("wikidata_extra.csv", False)):
        if not (SRC / fn).exists():
            continue
        with open(SRC / fn, encoding="utf8") as f:
            for r in csv.DictReader(f):
                if not r.get("kana") or not r.get("ja"):
                    continue
                kana = "".join(chr(ord(c) + 0x60) if "ぁ" <= c <= "ゖ" else c for c in r["kana"])
                res[r["ja"]].append((r.get("inja", ""), kana, r.get("end", "") if dis else "9999"))
    return res


NUMS = str.maketrans("０１２３４５６７８９", "0123456789")
OLD_FORMS = str.maketrans("條嶋澤﨑邊邉濱瀨冨萬龍舘", "条島沢崎辺辺浜瀬富万竜館")
KNUM = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}


def norm(s):
    """Spelling variants that differ between the 2002 data and today's: digits, ケ/ヶ, 之/の."""
    s = s.translate(NUMS).translate(OLD_FORMS).replace("ヶ", "ケ").replace("ｹ", "ケ").replace("之", "の")

    def k2n(m):
        t = m.group(0)
        if t == "十":
            return "10"
        if t.startswith("十"):
            return str(10 + KNUM[t[1]])
        if len(t) == 2 and t[1] == "十":
            return str(KNUM[t[0]] * 10)
        if len(t) == 3 and t[1] == "十":
            return str(KNUM[t[0]] * 10 + KNUM[t[2]])
        return str(KNUM[t]) if len(t) == 1 else t
    return re.sub(r"[一二三四五六七八九]?十[一二三四五六七八九]?|[一二三四五六七八九](?=[条線丁号区番])", k2n, s)


SUFFIX = {"市": ("シ", "shi"), "区": ("ク", "ku")}


def split_county(c):
    """'美馬郡貞光町' -> ('美馬郡', '貞光町'); a town or village only, at the first 郡 that has a name before it
    (郡上郡八幡町; 蒲郡市 and 大和郡山市 are cities); Tokyo's island towns drop their island (大島大島町)."""
    if c[-1:] in "町村":
        for i in range(1, len(c) - 1):
            if c[i] == "郡":
                return c[:i + 1], c[i + 1:]
        m = re.match(r"(.+?(?:諸島|島))(.+[町村])$", c)
        if m and m.group(2).startswith(m.group(1).replace("諸島", "")[:2]):
            return m.group(1), m.group(2)
    return "", c


def muni_suffix(kanji, kana):
    """-> (stem kana, suffix romaji) for one municipality (no county)."""
    last = kanji[-1:]
    if last in SUFFIX and kana.endswith(SUFFIX[last][0]):
        return kana[:-len(SUFFIX[last][0])], SUFFIX[last][1]
    if last == "町":
        for k, r in (("チョウ", "cho"), ("マチ", "machi")):
            if kana.endswith(k):
                return kana[:-len(k)], r
    if last == "村":
        for k, r in (("ムラ", "mura"), ("ソン", "son")):
            if kana.endswith(k):
                return kana[:-len(k)], r
    return kana, ""


def muni_en(kanji, kana):
    stem, suf = muni_suffix(kanji, kana)
    s = title(hepburn(ou_hint(kanji, stem)))
    return f"{s}-{suf}" if suf else s


def town_en(kanji, kana):
    """A town (大字/町名): a final 町 or 村 read as a suffix gets a hyphen like a municipality (Oshima-cho)."""
    if kanji[-1:] in ("町", "村") and len(kanji) > 1:
        stem, suf = muni_suffix(kanji, kana)
        if suf and stem:
            return f"{title(hepburn(ou_hint(kanji, stem)))}-{suf}"
    return title(hepburn(ou_hint(kanji, kana)))


MORPH = {"東": ("ヒガシ", "トウ"), "西": ("ニシ", "サイ"), "南": ("ミナミ", "ナン"), "北": ("キタ", "ホク"),
         "上": ("カミ", "ウエ", "ジョウ"), "中": ("ナカ", "チュウ"), "下": ("シモ", "シタ", "ゲ"), "新": ("シン", "ニイ"),
         "本": ("ホン",), "町": ("マチ", "チョウ"), "村": ("ムラ", "ソン"), "字": ("アザ",), "通": ("ドオリ", "トオリ"),
         "の": ("ノ",), "ノ": ("ノ",), "之": ("ノ",), "ケ": ("ガ", "ケ"), "ヶ": ("ガ", "ケ"), "が": ("ガ",)}


def split_words(kanji, kana, pieces, loose=True, whole=False):
    """Split a long town name into its parts (桃山町長岡越中南 -> 桃山|町|長岡|越中|南) when the parts' readings
    (pieces: place names with their kana; MORPH: one-kanji parts) spell the whole kana exactly.
    -> [(kanji part, kana part)] or None. Fewest parts wins, a one-kanji part costs more than a name."""
    n, m = len(kanji), len(kana)
    best = {(0, 0): (0, None)}
    for i in range(n):
        for (ii, j) in [k for k in list(best) if k[0] == i]:
            cost = best[(ii, j)][0]
            opts = []
            for i2 in range(i + 2, min(n, i + 6) + 1):
                if i == 0 and i2 == n and not whole:
                    continue                # the whole name is no split
                for r in pieces.get(kanji[i:i2], ()):
                    opts.append((i2, r, 2))
            for r in MORPH.get(kanji[i], ()):
                opts.append((i + 1, r, 3))
            for i2, r, c in opts:
                if kana.startswith(r, j):
                    key = (i2, j + len(r))
                    if key not in best or best[key][0] > cost + c:
                        best[key] = (cost + c, (ii, j, kanji[i:i2], r))
    if (n, m) not in best:
        if not loose:
            return None
        # one unknown part at the end (御陵|荒巻町: 御陵 known) or at the start: the known rest fixes the cut
        tails = [(c, i, j) for (i, j), (c, _) in best.items() if 0 < i < n and 0 < j < m]
        if tails:
            c, i, j = min(tails, key=lambda x: (-x[1], x[0], -x[2]))   # the longest known head and reading
            parts = split_words(kanji[:i], kana[:j], pieces, loose=False) or [(kanji[:i], kana[:j])]
            return parts + [(kanji[i:], kana[j:])]
        for i in range(1, n):
            for j in range(1, m):
                rest = split_words(kanji[i:], kana[j:], pieces, loose=False, whole=True)
                if rest:
                    return [(kanji[:i], kana[:j])] + rest
        return None
    parts = []
    key = (n, m)
    while key != (0, 0):
        _, (i, j, k, r) = best[key]
        parts.append((k, r))
        key = (i, j)
    return parts[::-1]


def words_en(parts):
    """Romanize split parts: 町/村 join the word before as a suffix, one-kanji direction/position parts stand
    alone (Momoyama-cho Nagaoka Etchu Minami)."""
    out = []
    glue = False                 # a particle (の, ケ) binds the words on both sides: Marunouchi, Hoshigaoka
    for k, r in parts:
        if k in ("町", "村") and out and not glue:
            suf = {"マチ": "machi", "チョウ": "cho", "ムラ": "mura", "ソン": "son"}.get(r)
            if suf:
                out[-1] += "-" + suf
                continue
        w = town_en(k, r) if len(k) > 1 else hepburn(r)
        if k in ("の", "ノ", "之", "ケ", "ヶ", "が") and out:
            out[-1] += w
            glue = True
            continue
        if glue and out:
            out[-1] += w.lower()
        else:
            out.append(w)
        glue = False
    return title(" ".join(out))


def segment(t, dicts, unidic):
    """Read a town name by splitting it into pieces that are whole town names with known readings (the
    prefecture's postal data first, then the whole country); pieces left over go to unidic.
    -> (kana, n pieces from postal data, n pieces from unidic)."""
    n = len(t)
    best = [None] * (n + 1)      # best[i] = (cost, kana, known, guessed) for t[:i]
    best[0] = (0, "", 0, 0)
    for i in range(n):
        if best[i] is None:
            continue
        cost, kana, kn, gu = best[i]
        for j in range(i + 2, n + 1):
            w = t[i:j]
            for d, pen in dicts:
                if w in d:
                    cand = (cost + pen, kana + d[w], kn + 1, gu)
                    if best[j] is None or cand[0] < best[j][0]:
                        best[j] = cand
                    break
        for j in range(i + 1, n + 1):
            cand = (cost + 10 * (j - i), kana + unidic(t[i:j]), kn, gu + 1)
            if best[j] is None or cand[0] < best[j][0]:
                best[j] = cand
    return best[n][1], best[n][2], best[n][3]


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stats", action="store_true")
    a = ap.parse_args()
    db = addrdb.unpack((addrdb.ROM).read_bytes())
    prefs = [x.decode("cp932") for x in db["prefs"]]
    cities = [x.decode("cp932") for x in db["cities"]]
    recs = load_posuto()
    wd = load_wikidata()

    by_code = defaultdict(list)
    city_kana = defaultdict(Counter)
    town_city = defaultdict(Counter)
    town_pref = defaultdict(Counter)
    for r in recs:
        by_code[r["postal_code"]].append(r)
        city_kana[(r["prefecture"], r["city"])][r["city_kana"]] += 1
        nb = norm(r["neighborhood"])
        town_city[(r["prefecture"], r["city"], nb)][r["neighborhood_kana"]] += 1
        town_pref[(r["prefecture"], nb)][r["neighborhood_kana"]] += 1
    pref_dict = defaultdict(dict)
    all_c = defaultdict(Counter)
    for (p, nb), ks in town_pref.items():
        if len(nb) >= 2 and not re.search(r"[（(、・]", nb) and ks:
            k = ks.most_common(1)[0][0]
            if k and not re.search(r"[（(]", k):
                pref_dict[p][nb] = k
                all_c[nb][k] += sum(ks.values())
    all_dict = {nb: ks.most_common(1)[0][0] for nb, ks in all_c.items()}
    pieces = {nb: [k for k, _ in ks.most_common(3)] for nb, ks in all_c.items() if len(nb) <= 6}

    with open(OUT / "addr_town_fix.tsv", encoding="utf8") as f:
        fixes = {r["jp"]: r["kana"] for r in csv.DictReader(f, delimiter="\t")}
    with open(OUT / "addr_city_fix.tsv", encoding="utf8") as f:
        city_fix = {r["jp"]: r["kana"] for r in csv.DictReader(f, delimiter="\t")}
    tagger = None

    def unidic(s):
        nonlocal tagger
        if tagger is None:
            import fugashi
            tagger = fugashi.Tagger()
        return "".join((w.feature.kana or w.surface) if w.feature.kana else w.surface for w in tagger(s))

    # prefectures
    pref_en = []
    for p in prefs:
        if not p:
            pref_en.append("")
            continue
        kana = Counter(r["prefecture_kana"] for r in recs if r["prefecture"] == p).most_common(1)[0][0]
        for suf in ("ト", "フ", "ケン"):
            if p[-1] in "都府県" and kana.endswith(suf):
                kana = kana[:-len(suf)]
                break
        pref_en.append(title(hepburn(kana)))

    # municipalities: a county prefix (…郡) is dropped; a designated city's ward keeps the city without -shi
    def one_muni(pref, name, district=""):
        """-> (kana, en, src) for one municipality name without county (district = its 〜郡, if any)."""
        ks = city_kana.get((pref, name))
        if ks:
            k = ks.most_common(1)[0][0]
            return k, muni_en(name, k), "postal"
        cands = wd.get(name, [])
        if cands:
            # many names repeat across Japan (吉田町, 広瀬町): the same county first, then still existing in 2002
            cands = sorted(cands, key=lambda c: (bool(district) and c[0] == district, c[2] >= "2002"),
                           reverse=True)
            k = cands[0][1]
            return k, muni_en(name, k), "wikidata"
        k = unidic(name)
        return k, muni_en(name, k), "unidic"

    city_rows = []
    for idx, c in enumerate(cities):
        p = None
        # a municipality index belongs to one prefecture: take it from the first town that uses it
        city_rows.append([idx, c, "", "", ""])
    pref_of_city = {}
    city_codes = defaultdict(set)
    for po, pr, ci, nm in db["towns"]:
        pref_of_city.setdefault(ci, prefs[pr])
        city_codes[ci].add(f"{po:07d}")
    for row in city_rows:
        idx, c = row[0], row[1]
        pref = pref_of_city.get(idx, "")
        if not c:
            continue
        full = city_kana.get((pref, c))
        district, name = split_county(c)
        m = re.match(r"(.+?市)(.+区)$", name)
        if m:
            k1, e1, s1 = one_muni(pref, m.group(1))
            stem1, _ = muni_suffix(m.group(1), k1)
            if full:
                fk = full.most_common(1)[0][0]
                wk = fk[len(k1):] if fk.startswith(k1) else None
                if wk:
                    row[2:] = [fk, f"{title(hepburn(stem1))} {muni_en(m.group(2), wk)}", "postal"]
                    continue
            k2, e2, s2 = one_muni(pref, m.group(2))
            row[2:] = [k1 + k2, f"{title(hepburn(stem1))} {e2}", s2 if s1 == "postal" else s1]
            continue
        if full and name != c:
            fk = full.most_common(1)[0][0]
            gun = fk.find("グン")
            if gun > 0:
                k = fk[gun + 2:]
                row[2:] = [k, muni_en(name, k), "postal"]
                continue
        if c in city_fix:
            row[2:] = [city_fix[c], muni_en(name, city_fix[c]), "manual"]
            continue
        k, e, s = one_muni(pref, name, district)
        if s != "postal":
            # a merged-away municipality: today's districts under its postal codes often start with its name
            # (雲南市加茂町…); their common kana prefix checks the wikidata reading (it has typos: 広瀬町
            # ひろせちまち) and replaces a unidic one
            ks = [r["neighborhood_kana"] for code in city_codes[idx] for r in by_code.get(code, [])
                  if norm(r["neighborhood"]).startswith(name) and len(r["neighborhood"]) > len(name)]
            pk = None
            sufs = ("チョウ", "マチ", "ムラ", "ソン", "シ")
            if len(ks) >= 2 and name[-1:] in "町村市":
                pre = lcp(ks) or ""
                stem_w, _ = muni_suffix(name, k)
                rem = pre[len(stem_w):] if stem_w and pre.startswith(stem_w) else None
                sk = next((x for x in sufs if rem is not None and rem.startswith(x)), None)
                if sk:
                    # the reading's stem is confirmed; a unidic suffix (machi/cho guess) takes today's
                    pk = stem_w + sk if s == "unidic" else None
                else:
                    for sk in sufs:
                        at = pre.find(sk, 1)
                        if at > 0:
                            pk = pre[:at + len(sk)]
                            break
            if pk:
                stem_w, _ = muni_suffix(name, k)
                stem_p, _ = muni_suffix(name, pk)
                if s == "unidic" or stem_p != stem_w:
                    k, e, s = pk, muni_en(name, pk), "postal-prefix"
        row[2:] = [k, e, s]

    # towns
    town_rows = {}
    src_count = Counter()
    for po, pr, ci, nm in db["towns"]:
        t = nm.decode("cp932")
        if not t:
            continue
        key = (pr, ci, t)
        if key in town_rows:
            continue
        pref, city = prefs[pr], cities[ci]
        code = f"{po:07d}"
        nt = norm(t)
        kana, src = None, None
        here = by_code.get(code, [])
        hit = [r for r in here if norm(r["neighborhood"]) == nt]
        if hit:
            kana, src = hit[0]["neighborhood_kana"], "postal"
        if kana is None:
            ks = town_city.get((pref, city, nt))
            if ks:
                kana, src = ks.most_common(1)[0][0], "postal-city"
        if kana is None:
            pre = [r for r in here if norm(r["neighborhood"]).startswith(nt)]
            if pre:
                # today's name continues the 2002 one (a truncated or detailed name): cut the reading by the
                # longest common kana prefix of those rows, or take the one row's reading of the same length
                r = pre[0]
                rest = norm(r["neighborhood"])[len(nt):]
                if not rest or rest[0] in "（(":
                    kana, src = re.split(r"[（(]", r["neighborhood_kana"])[0], "postal-prefix"
        if kana is None:
            suf = [r for r in here if norm(r["neighborhood"]).endswith(nt) and norm(r["neighborhood"]) != nt]
            for r in suf:
                head = norm(r["neighborhood"])[:-len(nt)]
                hk = None
                # the head is usually the merged-away municipality's name (吉田町白浦, or 吉田白浦): strip its
                # reading, with the 町/村 suffix's when the head has it
                ck = city_rows[ci][2]
                own = split_county(city)[1]
                if ck and head:
                    stem, _ = muni_suffix(own, ck)
                    if head == own and r["neighborhood_kana"].startswith(ck):
                        hk = ck
                    elif own.startswith(head) and r["neighborhood_kana"].startswith(stem):
                        hk = stem
                        if head == own:
                            # today's prefix may read the old 町/村 differently from the municipality (金木町:
                            # Kanagi-machi as a town, カナギチョウ as today's district name)
                            for sk in ("チョウ", "マチ", "ムラ", "ソン"):
                                if r["neighborhood_kana"][len(stem):].startswith(sk):
                                    hk = stem + sk
                                    break
                if hk is None:
                    sib = [x["neighborhood_kana"] for x in recs_by_head(by_code, here, head)]
                    if len(sib) >= 2:
                        hk = lcp(sib)
                if (hk and r["neighborhood_kana"].startswith(hk) and len(r["neighborhood_kana"]) > len(hk)
                        and r["neighborhood_kana"][len(hk)] not in "ャュョァィゥェォッーン"):
                    kana, src = r["neighborhood_kana"][len(hk):], "postal-suffix"
                    break
        if kana is None:
            ks = town_pref.get((pref, nt))
            if ks:
                kana, src = ks.most_common(1)[0][0], "postal-pref"
        if t in fixes:
            kana, src = fixes[t], "manual"
        if kana is None:
            nt2 = re.sub(r"(.)々", r"\1\1", nt)
            kana, kn, gu = segment(nt2, [(pref_dict[pref], 1), (all_dict, 3)], unidic)
            src = "unidic" if not kn else ("pieces" if not gu else "pieces+unidic")
        kana = re.split(r"[（(]", kana)[0]
        en = town_en(t, kana)
        if any(len(w) > LONG_WORD for w in en.split(" ")):
            parts = split_words(nt, unicodedata.normalize("NFKC", kana), pieces)
            if parts and len(parts) > 1:
                en = words_en(parts)
            en = " ".join(break_long(w) for w in en.split(" "))
        town_rows[key] = [pr, ci, t, kana, en, src]
        src_count[src] += 1

    OUT.mkdir(exist_ok=True)
    with open(OUT / "addr_pref.tsv", "w", encoding="utf8", newline="\n") as f:
        f.write("idx\tjp\ten\n")
        for i, (p, e) in enumerate(zip(prefs, pref_en)):
            f.write(f"{i}\t{p}\t{e}\n")
    with open(OUT / "addr_city.tsv", "w", encoding="utf8", newline="\n") as f:
        f.write("idx\tjp\tkana\ten\tsrc\n")
        for r in city_rows:
            f.write("\t".join(map(str, r)) + "\n")
    with open(OUT / "addr_town.tsv", "w", encoding="utf8", newline="\n") as f:
        f.write("pref\tcity\tjp\tkana\ten\tsrc\n")
        for k in sorted(town_rows):
            f.write("\t".join(map(str, town_rows[k])) + "\n")
    print("cities:", Counter(r[4] for r in city_rows if r[1]))
    print("towns:", src_count)
    return 0


def recs_by_head(by_code, here, head):
    return [r for r in here if r["neighborhood"].startswith(head) and len(r["neighborhood"]) > len(head)]


def lcp(xs):
    s = min(xs)
    t = max(xs)
    n = 0
    while n < len(s) and s[n] == t[n]:
        n += 1
    return s[:n] if n < len(s) else None


if __name__ == "__main__":
    sys.exit(main())
