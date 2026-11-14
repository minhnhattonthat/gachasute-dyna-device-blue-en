"""ecd.py: the game's "ECD\\x01" LZSS container (decompressor at 0x08005680) and a ROM scan.

Header (16 bytes, big-endian u32s): "ECD\\x01", raw_len, in_len, out_len.
Body: raw_len bytes copied verbatim (they bypass the ring), then Okumura LZSS over the remaining in_len - raw_len
bytes: flag byte LSB first, bit 1 = literal byte, bit 0 = match (b1, b2): ring position b1 | (b2 & 0xC0) << 2,
length (b2 & 0x3F) + 3. Ring: 0x400 bytes, zero-filled, first write at 0x3BE (IWRAM 0x03001410 in game).

    python -X utf8 tools/ecd.py scan ROM            # every ECD block: offset, in_len, out_len, payload tag
    python -X utf8 tools/ecd.py dump ROM OFF OUT    # decompress one block
    python -X utf8 tools/ecd.py verify ROM          # re-compress every block, compare with the ROM (~30 s)

compress() is a port of the original encoder (Okumura's LZSS.C): it gives every block in the ROM back byte for
byte, so an edited graphic is compressed the way the game's own tools would have done it.
"""
import struct
import sys

MAGIC = b"ECD\x01"
N, F, START = 0x400, 0x42, 0x3BE


def header(data, off):
    if data[off:off + 4] != MAGIC:
        raise ValueError("no ECD magic at %X" % off)
    return struct.unpack_from(">III", data, off + 4)


def decompress(data, off=0):
    """-> (output bytes, bytes consumed including the 16-byte header)."""
    raw_len, in_len, out_len = header(data, off)
    p = off + 16
    out = bytearray(data[p:p + raw_len])
    p += raw_len
    end = off + 16 + in_len
    ring = bytearray(N)
    r = START
    flags = 0
    while len(out) < out_len and p < end:
        flags >>= 1
        if not flags & 0x100:
            flags = data[p] | 0xFF00
            p += 1
            if p >= end:
                break
        if flags & 1:
            c = data[p]
            p += 1
            out.append(c)
            ring[r] = c
            r = (r + 1) & (N - 1)
        else:
            if p + 1 >= end:
                break
            b1, b2 = data[p], data[p + 1]
            p += 2
            pos = b1 | (b2 & 0xC0) << 2
            for k in range((b2 & 0x3F) + 3):
                c = ring[(pos + k) & (N - 1)]
                out.append(c)
                ring[r] = c
                r = (r + 1) & (N - 1)
    return bytes(out[:out_len]), 16 + in_len


def compress_stored(raw, raw_len=8):
    """Literal-only encoding (every flag bit 1): always valid for the game's decoder, ~12% larger than raw.
    A decoder self-test; builds use compress()."""
    src = raw[raw_len:]
    body = bytearray()
    for i in range(0, len(src), 8):
        chunk = src[i:i + 8]
        body.append((1 << len(chunk)) - 1)
        body += chunk
    out = bytearray(MAGIC) + struct.pack(">III", raw_len, raw_len + len(body), len(raw)) + raw[:raw_len] + body
    while len(out) % 4:
        out.append(0)
    return bytes(out)


def _lzss_okumura(src):
    """Haruhiko Okumura's LZSS.C encoder (1989, public domain) with N=0x400, F=0x42, THRESHOLD=2, a zero-filled
    ring and this game's match byte layout. It reproduces the ROM's compressed bodies byte for byte
    (tests/test_ecd.py), so the original tool was this encoder."""
    n, f, nil = N, F, N
    text = bytearray(n + f - 1)
    lson = [nil] * (n + 1)
    rson = [nil] * (n + 257)
    dad = [nil] * (n + 1)
    st = {"pos": 0, "len": 0}

    def insert(r):
        cmp = 1
        p = n + 1 + text[r]
        rson[r] = lson[r] = nil
        st["len"] = 0
        while True:
            if cmp >= 0:
                if rson[p] != nil:
                    p = rson[p]
                else:
                    rson[p] = r
                    dad[r] = p
                    return
            else:
                if lson[p] != nil:
                    p = lson[p]
                else:
                    lson[p] = r
                    dad[r] = p
                    return
            i = 1
            while i < f:
                cmp = text[r + i] - text[p + i]
                if cmp:
                    break
                i += 1
            if i > st["len"]:
                st["pos"] = p
                st["len"] = i
                if i >= f:
                    break
        dad[r] = dad[p]
        lson[r] = lson[p]
        rson[r] = rson[p]
        dad[lson[p]] = r
        dad[rson[p]] = r
        if rson[dad[p]] == p:
            rson[dad[p]] = r
        else:
            lson[dad[p]] = r
        dad[p] = nil

    def delete(p):
        if dad[p] == nil:
            return
        if rson[p] == nil:
            q = lson[p]
        elif lson[p] == nil:
            q = rson[p]
        else:
            q = lson[p]
            if rson[q] != nil:
                while rson[q] != nil:
                    q = rson[q]
                rson[dad[q]] = lson[q]
                dad[lson[q]] = dad[q]
                lson[q] = lson[p]
                dad[lson[p]] = q
            rson[q] = rson[p]
            dad[rson[p]] = q
        dad[q] = dad[p]
        if rson[dad[p]] == p:
            rson[dad[p]] = q
        else:
            lson[dad[p]] = q
        dad[p] = nil

    out = bytearray()
    if not src:
        return bytes(out)
    code = bytearray([0])
    mask = 1
    s, r = 0, n - f
    pos = 0
    ln = 0
    while ln < f and pos < len(src):
        text[r + ln] = src[pos]
        pos += 1
        ln += 1
    for i in range(1, f + 1):
        insert(r - i)
    insert(r)
    while True:
        if st["len"] > ln:
            st["len"] = ln
        if st["len"] <= 2:
            st["len"] = 1
            code[0] |= mask
            code.append(text[r])
        else:
            mp = st["pos"]
            code.append(mp & 0xFF)
            code.append(((mp >> 8) << 6) | (st["len"] - 3))
        mask = (mask << 1) & 0xFF
        if mask == 0:
            out += code
            code = bytearray([0])
            mask = 1
        last = st["len"]
        i = 0
        while i < last and pos < len(src):
            c = src[pos]
            pos += 1
            delete(s)
            text[s] = c
            if s < f - 1:
                text[s + n] = c
            s = (s + 1) & (n - 1)
            r = (r + 1) & (n - 1)
            insert(r)
            i += 1
        while i < last:
            i += 1
            delete(s)
            s = (s + 1) & (n - 1)
            r = (r + 1) & (n - 1)
            ln -= 1
            if ln:
                insert(r)
        if ln <= 0:
            break
    if len(code) > 1:
        out += code
    if len(out) % 2:
        out.append(0)  # the original tool pads the body to an even length
    return bytes(out)


def compress(raw, raw_len=8):
    """ECD block as the original tool made it: header, raw_len bytes verbatim, Okumura LZSS of the rest.
    No trailing padding (the caller aligns)."""
    body = _lzss_okumura(raw[raw_len:])
    return MAGIC + struct.pack(">III", raw_len, raw_len + len(body), len(raw)) + raw[:raw_len] + body


def scan(data):
    found = []
    p = data.find(MAGIC)
    while p >= 0:
        try:
            raw_len, in_len, out_len = header(data, p)
            if raw_len <= in_len < 0x100000 and out_len < 0x200000:
                found.append((p, in_len, out_len, data[p + 16:p + 20].rstrip(b"\0").decode("latin1")))
        except ValueError:
            pass
        p = data.find(MAGIC, p + 4)
    return found


def main(argv):
    if len(argv) == 2 and argv[0] == "scan":
        data = open(argv[1], "rb").read()
        for p, il, ol, tag in scan(data):
            print(f"{p:07X} in={il:6X} out={ol:6X} {tag}")
    elif len(argv) == 2 and argv[0] == "verify":
        data = open(argv[1], "rb").read()
        blocks = scan(data)
        bad = [p for p, il, _ol, _t in blocks if compress(decompress(data, p)[0]) != data[p:p + 16 + il]]
        print(f"{len(blocks)} blocks, {len(bad)} re-compress differently" + "".join(f"\n  {p:07X}" for p in bad[:20]))
        return 1 if bad else 0
    elif len(argv) == 4 and argv[0] == "dump":
        data = open(argv[1], "rb").read()
        open(argv[3], "wb").write(decompress(data, int(argv[2], 16))[0])
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
