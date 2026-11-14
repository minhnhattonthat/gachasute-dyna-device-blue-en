"""lz77.py: GBA BIOS LZ77 (type 0x10) decompress/compress, and a ROM scan for blocks that pointers reach.

    python -X utf8 tools/lz77.py scan ROM [--min 32]       # list pointer-referenced LZ77 blocks: offset, sizes
    python -X utf8 tools/lz77.py dump ROM OFFSET OUT.bin   # decompress one block

decompress(data, off) -> (bytes, compressed_length). compress(raw) -> bytes (BIOS-compatible, greedy)."""
import struct
import sys


def decompress(data, off=0):
    if data[off] != 0x10:
        raise ValueError("not LZ77 type 0x10")
    size = data[off + 1] | data[off + 2] << 8 | data[off + 3] << 16
    out = bytearray()
    p = off + 4
    while len(out) < size:
        flags = data[p]
        p += 1
        for bit in range(8):
            if len(out) >= size:
                break
            if flags & (0x80 >> bit):
                b1, b2 = data[p], data[p + 1]
                p += 2
                length = (b1 >> 4) + 3
                disp = ((b1 & 0xF) << 8 | b2) + 1
                if disp > len(out):
                    raise ValueError("back-reference before start")
                for _ in range(length):
                    out.append(out[-disp])
            else:
                out.append(data[p])
                p += 1
    return bytes(out[:size]), p - off


def compress(raw):
    out = bytearray([0x10, len(raw) & 0xFF, len(raw) >> 8 & 0xFF, len(raw) >> 16 & 0xFF])
    i = 0
    n = len(raw)
    while i < n:
        flag_pos = len(out)
        out.append(0)
        flags = 0
        for bit in range(8):
            if i >= n:
                break
            best_len, best_disp = 0, 0
            # disp >= 2 keeps VRAM-safe (16-bit writes) output, as the BIOS VRAM variant needs
            for disp in range(2, min(i, 0x1000) + 1):
                length = 0
                while length < 18 and i + length < n and raw[i + length] == raw[i + length - disp]:
                    length += 1
                if length > best_len:
                    best_len, best_disp = length, disp
                    if length == 18:
                        break
            if best_len >= 3:
                flags |= 0x80 >> bit
                v = (best_len - 3) << 12 | (best_disp - 1)
                out += bytes([v >> 8, v & 0xFF])
                i += best_len
            else:
                out.append(raw[i])
                i += 1
        out[flag_pos] = flags
    while len(out) % 4:
        out.append(0)
    return bytes(out)


def scan(data, min_size=32):
    targets = set()
    for i in range(0, len(data) - 3, 4):
        v = struct.unpack_from("<I", data, i)[0]
        if 0x08000000 <= v < 0x08000000 + len(data):
            targets.add(v - 0x08000000)
    found = []
    for t in sorted(targets):
        if data[t] != 0x10:
            continue
        size = data[t + 1] | data[t + 2] << 8 | data[t + 3] << 16
        if size < min_size or size > 0x40000:
            continue
        try:
            raw, clen = decompress(data, t)
        except (ValueError, IndexError):
            continue
        found.append((t, clen, len(raw)))
    return found


def main(argv):
    if len(argv) >= 2 and argv[0] == "scan":
        data = open(argv[1], "rb").read()
        mn = int(argv[argv.index("--min") + 1]) if "--min" in argv else 32
        for t, clen, size in scan(data, mn):
            print(f"{t:07X} clen={clen:6X} size={size:6X}")
    elif len(argv) == 4 and argv[0] == "dump":
        data = open(argv[1], "rb").read()
        raw, _ = decompress(data, int(argv[2], 16))
        open(argv[3], "wb").write(raw)
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
