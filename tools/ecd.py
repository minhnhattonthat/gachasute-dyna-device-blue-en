"""ecd.py: the game's "ECD\\x01" LZSS container (decompressor at 0x08005680) and a ROM scan.

Header (16 bytes, big-endian u32s): "ECD\\x01", raw_len, in_len, out_len.
Body: raw_len bytes copied verbatim (they bypass the ring), then Okumura LZSS over the remaining in_len - raw_len
bytes: flag byte LSB first, bit 1 = literal byte, bit 0 = match (b1, b2): ring position b1 | (b2 & 0xC0) << 2,
length (b2 & 0x3F) + 3. Ring: 0x400 bytes, zero-filled, first write at 0x3BE (IWRAM 0x03001410 in game).

    python -X utf8 tools/ecd.py scan ROM            # every ECD block: offset, in_len, out_len, payload tag
    python -X utf8 tools/ecd.py dump ROM OFF OUT    # decompress one block
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
    A real LZSS encoder comes with the graphics work (phase 3+)."""
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
    elif len(argv) == 4 and argv[0] == "dump":
        data = open(argv[1], "rb").read()
        open(argv[3], "wb").write(decompress(data, int(argv[2], 16))[0])
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
