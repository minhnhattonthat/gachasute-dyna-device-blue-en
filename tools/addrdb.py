"""addrdb.py: the address database (resource file 2, ROM 0x44C754-0x702BB4): Japanese postal codes with their
prefecture, municipality and town names. Parse and repack, byte-exact.

    python -X utf8 tools/addrdb.py            # counts + identity repack check

Layout (docs/re/text.md), all names Shift-JIS, NUL-padded to a fixed width:
  header  4 x u32 LE offsets from the file start: towns (0x10), prefectures, municipalities, end (= file size)
  towns   120701 records of 23 bytes: u32 BE postal code (7 digits), u8 prefecture index, u16 BE municipality
          index, 16-byte town name (empty = the code's catch-all entry); then 5 zero bytes
  prefs   48 x 10 bytes
  cities  3356 x 20 bytes
The file ends with "end\\x1a" + 12 zero bytes like the other resource files (outside the parsed size).
Translation plan (non-blocking question in docs/status.md): Hepburn from Japan Post KEN_ALL readings by postal code.
"""
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROM = ROOT / "rom" / "Gachasute! Dyna Device Blue (Japan).gba"
BASE = 0x44C754
TOWN_LEN, TOWN_NAME = 23, 16
PREF_LEN, CITY_LEN = 10, 20


def unpack(rom, base=BASE):
    """-> dict(towns=[(postal, pref, city, name bytes)], prefs=[bytes], cities=[bytes], tail=bytes)."""
    t, p, c, end = struct.unpack_from("<4I", rom, base)
    n = (p - t) // TOWN_LEN
    towns = []
    for k in range(n):
        a = base + t + k * TOWN_LEN
        postal, pref, city = struct.unpack_from(">IBH", rom, a)
        towns.append((postal, pref, city, rom[a + 7:a + TOWN_LEN].rstrip(b"\0")))
    tail = rom[base + t + n * TOWN_LEN:base + p]
    prefs = [rom[base + p + k:base + p + k + PREF_LEN].rstrip(b"\0") for k in range(0, c - p, PREF_LEN)]
    cities = [rom[base + c + k:base + c + k + CITY_LEN].rstrip(b"\0") for k in range(0, end - c, CITY_LEN)]
    return dict(towns=towns, prefs=prefs, cities=cities, tail=tail)


def _field(name, width):
    if len(name) > width:
        raise ValueError(f"name {name!r} longer than {width} bytes")
    return name + bytes(width - len(name))


def pack(db):
    """-> the file bytes covered by the header (no end marker)."""
    towns = b"".join(struct.pack(">IBH", po, pr, ci) + _field(nm, TOWN_NAME) for po, pr, ci, nm in db["towns"])
    towns += db["tail"]
    prefs = b"".join(_field(x, PREF_LEN) for x in db["prefs"])
    cities = b"".join(_field(x, CITY_LEN) for x in db["cities"])
    t = 0x10
    p = t + len(towns)
    c = p + len(prefs)
    end = c + len(cities)
    return struct.pack("<4I", t, p, c, end) + towns + prefs + cities


def size(rom, base=BASE):
    return struct.unpack_from("<4I", rom, base)[3]


# ---------------------------------------------------------------- English database (decision D20, v1.1)
# The two postal-code lookups (profile form 0x0803B6DC/0x0803B75C, PDA address book 0x08024A6C/0x08024AEC, same
# code) scan 23-byte town records and copy fixed-width SJIS names. The English file keeps the header and the
# scan, with 11-byte records whose name is a u32 pointer, and a new builder (ARM, in the file) that writes
# prefecture, municipality and town into the caller's 64-byte buffer (the field keeps 54 bytes).
# The form draws a field as rows of 13 units (26 bytes), each row in two pieces: 8 units at x 32, 5 units at
# x 160 (seen in game, work/qa/addr). Each piece starts at its own cell, so ASCII (two letters per 16-px cell)
# leaves a gap at every piece end. The builder therefore wraps by words into the pieces CHUNKS: a word that
# does not fit goes to the first later piece it fits (PAD 0x7F, zero-width, up to there); a word longer than any
# piece runs across. At most 52 bytes, then a space (when mid-piece) and PAD to an even length, so the SJIS the
# player types after it stays on even bytes (docs/re/text.md "Address database").
SLOT_END = 0x702BB4             # the file's slot; "end\x1a" + 12 zero bytes follow and stay
EN_REC = 11
STRIDE_AT = (0x03B748, 0x024AD8)                     # adds r2, #0x17 in each scan loop
HOOK_AT = (0x03B798, 0x024B28)                       # adds r6, #4 after the scan found a record
HOOK_RET = (0x0803B866, 0x08024BF6)                  # mov r3, r8 before the field-setter call
SCAN_COUNT = 120702                                  # the scan's count literal (one record past the last)
MAX_LEN = 52
CHUNKS = (0, 16, 26, 42, 52)    # piece starts (and the end): row 1 = 16 + 10 bytes, row 2 the same
TYPE_ROOM = 8                  # bytes left for the player's own SJIS (4 chars) before a record falls back


def builder_asm(prefs, cities):
    """ARM source of the builder (prefs / cities: ROM addresses of the u32 pointer tables).
    In: r6 = the record the scan found, sp = the caller's zeroed 64-byte buffer. Clobbers r0-r5, r7, lr."""
    return f"""
entry1: ldr r7, ={HOOK_RET[0] | 1:#x}
        b common
entry2: ldr r7, ={HOOK_RET[1] | 1:#x}
common: ldrb r0, [r6, #4]
        ldrb r1, [r6, #5]
        ldrb r2, [r6, #6]
        orr r1, r2, r1, lsl #8
        ldrb r2, [r6, #7]
        ldrb r3, [r6, #8]
        orr r2, r2, r3, lsl #8
        ldrb r3, [r6, #9]
        orr r2, r2, r3, lsl #16
        ldrb r3, [r6, #10]
        orr r2, r2, r3, lsl #24
        ldr r3, ={prefs:#x}
        ldr r0, [r3, r0, lsl #2]
        ldr r3, ={cities:#x}
        ldr r1, [r3, r1, lsl #2]
        mov r5, sp                  @ r5 = buffer (stays), r4 = write pointer
        push {{r9, r10, r11}}
        mov r4, r5
        mov r9, r1
        mov r10, r2
        mov r3, r0
        bl part
        mov r3, r9
        bl part
        mov r3, r10
        bl part
        sub r0, r4, r5
        cmp r0, #{MAX_LEN}
        bhs even
        cmp r0, #0                  @ a space before the player's text unless at a piece start
        cmpne r0, #{CHUNKS[1]}
        cmpne r0, #{CHUNKS[2]}
        cmpne r0, #{CHUNKS[3]}
        movne r1, #0x20
        strbne r1, [r4], #1
even:   sub r0, r4, r5
        tst r0, #1
        movne r1, #0x7f
        strbne r1, [r4], #1
        mov r1, #0
        strb r1, [r4]
        pop {{r9, r10, r11}}
        bx r7

part:   mov r11, lr                 @ r3 = string or 0: emit its words
        cmp r3, #0
        bxeq r11
ploop:  ldrb r0, [r3]
        cmp r0, #0
        bxeq r11
        cmp r0, #0x20
        addeq r3, r3, #1
        beq ploop
        mov r1, #0
mlen:   ldrb r0, [r3, r1]
        cmp r0, #0
        cmpne r0, #0x20
        addne r1, r1, #1
        bne mlen
        bl word
        b ploop

word:   sub r2, r4, r5              @ r3 = word, r1 = its length; returns r3 past it
        cmp r2, #{MAX_LEN}
        addhs r3, r3, r1
        bxhs lr
        mov r6, #{CHUNKS[0]}        @ r6 = this piece's start, r12 = its end
        mov r12, #{CHUNKS[1]}
        cmp r2, #{CHUNKS[1]}
        movhs r6, #{CHUNKS[1]}
        movhs r12, #{CHUNKS[2]}
        cmp r2, #{CHUNKS[2]}
        movhs r6, #{CHUNKS[2]}
        movhs r12, #{CHUNKS[3]}
        cmp r2, #{CHUNKS[3]}
        movhs r6, #{CHUNKS[3]}
        movhs r12, #{CHUNKS[4]}
        subs r6, r2, r6
        movne r6, #1                @ separator space unless at a piece start
        add r0, r2, r6
        add r0, r0, r1
        cmp r0, r12
        bhi nofit
        cmp r6, #0
        movne r0, #0x20
        strbne r0, [r4], #1
        b copy
nofit:  cmp r12, #{MAX_LEN}         @ r12 = a later piece's start: the first one the word fits
        bhs split
        mov r0, #{CHUNKS[2]}
        cmp r12, #{CHUNKS[2]}
        movhs r0, #{CHUNKS[3]}
        cmp r12, #{CHUNKS[3]}
        movhs r0, #{CHUNKS[4]}      @ r0 = that piece's end
        add r2, r12, r1
        cmp r2, r0
        movhi r12, r0
        bhi nofit
        add r12, r5, r12
        mov r0, #0x7f
padl:   cmp r4, r12
        strblo r0, [r4], #1
        blo padl
        b copy
split:  cmp r6, #0
        beq copy
        sub r2, r4, r5
        add r2, r2, #1
        cmp r2, #{MAX_LEN}
        movlo r0, #0x20
        strblo r0, [r4], #1
copy:   add r12, r5, #{MAX_LEN}
cl:     cmp r1, #0
        bxeq lr
        ldrb r0, [r3], #1
        sub r1, r1, #1
        cmp r4, r12
        strblo r0, [r4], #1
        b cl
        .ltorg
"""


def assemble(src, addr):
    from keystone import Ks, KS_ARCH_ARM, KS_MODE_ARM
    code, _ = Ks(KS_ARCH_ARM, KS_MODE_ARM).asm(src, addr)
    return bytes(code)


def built_text(pref, city, town):
    """-> (bytes the builder writes for one record, cut). Python model of builder_asm (tests check them equal on
    real records); cut = a word ran across a chunk or past MAX_LEN."""
    out = bytearray()
    cut = False
    for part in (pref, city, town):
        for w in (part or "").split(" "):
            if not w:
                continue
            w = w.encode("ascii")
            pos = len(out)
            if pos >= MAX_LEN:
                cut = True
                continue
            k = max(i for i in range(4) if CHUNKS[i] <= pos)
            sep = 0 if pos == CHUNKS[k] else 1
            if pos + sep + len(w) <= CHUNKS[k + 1]:
                out += b" " * sep + w
                continue
            later = [i for i in range(k + 1, 4) if CHUNKS[i] + len(w) <= CHUNKS[i + 1]]
            if later:
                out += b"\x7f" * (CHUNKS[later[0]] - pos) + w
                continue
            cut = True
            if sep and pos + 1 < MAX_LEN:
                out += b" "
            out += w[:max(0, MAX_LEN - len(out))]
    if len(out) < MAX_LEN and len(out) not in CHUNKS:
        out += b" "
    if len(out) % 2:
        out += b"\x7f"
    return bytes(out), cut


def short_city(city):
    """The municipality without its type suffix (Nirasaki-shi -> Nirasaki); a ward keeps -ku."""
    return " ".join(re.sub(r"-(shi|cho|machi|mura|son)$", "", w) for w in city.split(" "))


def choose(pref, city, town):
    """-> (variant, text) for one record: 0 = full, 1 = no prefecture, 2 = no prefecture + short municipality;
    the first whose words all fit their chunks and that leaves TYPE_ROOM bytes for the player, else the last."""
    for v, (p, c) in enumerate(((pref, city), ("", city), ("", short_city(city)))):
        text, cut = built_text(p, c, town)
        if not cut and MAX_LEN - len(text) >= TYPE_ROOM:
            return v, text
    return v, text


def pack_en(db, pref_en, city_en, town_en):
    """-> (file bytes for BASE..SLOT_END, entry1 ROM address, entry2 ROM address).
    pref_en / city_en: lists by index; town_en: {(pref, city, jp bytes): english}. Strings are ASCII."""
    n = len(db["towns"])
    assert SCAN_COUNT == n + 1
    # fallback variants (choose): prefecture index len(prefs) = none; municipality index + len(cities) = short
    npref, ncity = len(pref_en), len(city_en)
    pref_en = list(pref_en) + [""]
    city_en = list(city_en) + [short_city(x) for x in city_en]
    t = 0x10
    p = (t + (n + 1) * EN_REC + 3) & ~3
    c = p + 4 * len(pref_en)
    code_at = (c + 4 * len(city_en) + 3) & ~3
    # the builder first (fixed size: assemble once with dummy table addresses to measure)
    probe = assemble(builder_asm(0x08000000, 0x08000000), 0x08000000)
    pool_at = (code_at + len(probe) + 3) & ~3
    pool = bytearray()
    where = {}

    def ptr(s):
        if not s:
            return 0
        if s not in where:
            raw = s.encode("ascii")
            assert b"%" not in raw and all(0x20 <= x < 0x7F for x in raw), s
            where[s] = 0x08000000 + BASE + pool_at + len(pool)
            pool.extend(raw + b"\0")
        return where[s]

    prefs = [ptr(x) for x in pref_en]
    cities = [ptr(x) for x in city_en]
    recs = bytearray()
    for po, pr, ci, nm in db["towns"]:
        town = town_en.get((pr, ci, nm), "") if nm else ""
        v, _ = choose(pref_en[pr], city_en[ci], town)
        pr2 = npref if v >= 1 else pr
        ci2 = ci + ncity if v == 2 else ci
        recs += struct.pack(">IBH", po, pr2, ci2) + struct.pack("<I", ptr(town))
    recs += bytes(EN_REC)                             # the record the scan reads past the last one
    end = pool_at + len(pool)
    if BASE + end > SLOT_END:
        raise ValueError(f"English address file {end:#x} bytes does not fit its slot ({SLOT_END - BASE:#x})")
    code = assemble(builder_asm(0x08000000 + BASE + p, 0x08000000 + BASE + c), 0x08000000 + BASE + code_at)
    assert len(code) == len(probe)
    blob = bytearray(SLOT_END - BASE)
    blob[0:16] = struct.pack("<4I", t, p, c, end)
    blob[t:t + len(recs)] = recs
    blob[p:p + 4 * len(prefs)] = struct.pack(f"<{len(prefs)}I", *prefs)
    blob[c:c + 4 * len(cities)] = struct.pack(f"<{len(cities)}I", *cities)
    blob[code_at:code_at + len(code)] = code
    blob[pool_at:end] = pool
    entry1 = 0x08000000 + BASE + code_at
    return bytes(blob), entry1, entry1 + 8


def load_en(root=ROOT):
    """script/addr_*.tsv -> (pref_en list, city_en list, {(pref, city, jp bytes): en})."""
    import csv

    def rows(name):
        with open(root / "script" / name, encoding="utf8") as f:
            return list(csv.DictReader(f, delimiter="\t"))
    pref = [r["en"] for r in sorted(rows("addr_pref.tsv"), key=lambda r: int(r["idx"]))]
    city = [r["en"] for r in sorted(rows("addr_city.tsv"), key=lambda r: int(r["idx"]))]
    town = {(int(r["pref"]), int(r["city"]), r["jp"].encode("cp932")): r["en"] for r in rows("addr_town.tsv")}
    return pref, city, town


def apply_en(rom, out, log=None):
    """Write the English address file, the two hooks and the two scan strides into `out`."""
    import romwrite
    db = unpack(rom)
    blob, e1, e2 = pack_en(db, *load_en())
    romwrite.put(log, out, BASE, blob, "address database (English, tools/addrdb.py)")
    for at, entry in zip(HOOK_AT, (e1, e2)):
        assert rom[at:at + 2] == b"\x04\x36", hex(at)            # adds r6, #4
        romwrite.put(log, out, at, b"\x00\x48\x00\x47" + struct.pack("<I", entry), "address lookup hook")
    for at in STRIDE_AT:
        assert rom[at:at + 2] == b"\x17\x32", hex(at)            # adds r2, #0x17
        romwrite.put(log, out, at, bytes([EN_REC, 0x32]), "address scan stride")
    return len(blob)


def main():
    rom = ROM.read_bytes()
    db = unpack(rom)
    same = pack(db) == rom[BASE:BASE + size(rom)]
    names = {x[3] for x in db["towns"]}
    print(f"{len(db['towns'])} towns ({len(names)} distinct names), {len(db['prefs'])} prefectures, "
          f"{len(db['cities'])} municipalities; repack {'identical' if same else 'DIFFERENT'}")
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main())
