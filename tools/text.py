"""text.py: the text codec for script/ JSON. Game text is Shift-JIS (cp932) with ASCII control codes inline.

    from text import decode, encode
    s = decode(raw); assert encode(s) == raw

Text form (docs/re/text.md):
  "\\n"         KG   line break (message box)
  "{KP}" "\\n"  KP   wait for a button, new page; decode adds a newline after it for readability, encode accepts
                     "{KP}" with or without that one newline
  "{KN}"        KN   end the message without the usual wait
  "{%sR4}"      %sRn, %dRn, %WdRn, %0WdRn: insert string / number register n (expander 0x0801328C)
  "{%02X}" ...  other printf formats (debug and menu number fields)
  "{%}"         a lone % (script 341: the game's own typo, expanded by luck)
  "{C1}"        C0-C9, colour (menu strings; C0 = back to normal)
  "[XX]"        any byte that is not one of the above: a non-printable ASCII byte, a byte that does not start a
                cp932 pair that maps back to itself, or a literal "{", "}", "[", "]" or "\\".
Plain printable ASCII stays as itself (debug menu romaji, the name-entry keyboard's tb/so/ED markers, English).
decode(encode(s)) == s is not promised for hand-written English (e.g. "{KP}" with no newline); encode(decode(b))
== b holds for every byte string (tests/test_extract.py runs it over every string in the ROM).
"""
import re

FORMAT = re.compile(rb"%(?:s|\d*d)R\d|%0?\d*[dXxs]")
COLOUR = re.compile(rb"C\d")
TOKEN = re.compile(r"\{KP\}\n?|\{KN\}|\{(%[^{}]*)\}|\{(C\d)\}|\[([0-9A-Fa-f]{2})\]|\n")


def _lead(b):
    return 0x81 <= b <= 0x9F or 0xE0 <= b <= 0xFC


def decode(raw):
    out = []
    i, n = 0, len(raw)
    while i < n:
        b = raw[i]
        if _lead(b) and i + 1 < n:
            pair = raw[i:i + 2]
            try:
                ch = pair.decode("cp932")
            except UnicodeDecodeError:
                ch = None
            if ch is not None and len(ch) == 1 and ch.encode("cp932") == pair:
                out.append(ch)
                i += 2
                continue
        if raw.startswith(b"KG", i):
            out.append("\n")
            i += 2
        elif raw.startswith(b"KP", i):
            out.append("{KP}\n")
            i += 2
        elif raw.startswith(b"KN", i):
            out.append("{KN}")
            i += 2
        elif b == 0x25:  # %
            m = FORMAT.match(raw, i)
            tok = m.group().decode() if m else "%"
            out.append("{" + tok + "}")
            i += len(tok)
        elif COLOUR.match(raw, i):
            out.append("{" + raw[i:i + 2].decode() + "}")
            i += 2
        elif 0x20 <= b < 0x7F and b not in b"{}[]\\":
            out.append(chr(b))
            i += 1
        else:
            out.append(f"[{b:02X}]")
            i += 1
    return "".join(out)


def encode(s):
    out = bytearray()
    pos = 0
    for m in TOKEN.finditer(s):
        out += _plain(s[pos:m.start()])
        t = m.group()
        if t == "\n":
            out += b"KG"
        elif t.startswith("{KP}"):
            out += b"KP"
        elif t == "{KN}":
            out += b"KN"
        elif m[1] is not None:
            out += m[1].encode("ascii")
        elif m[2] is not None:
            out += m[2].encode("ascii")
        else:
            out.append(int(m[3], 16))
        pos = m.end()
    out += _plain(s[pos:])
    return bytes(out)


def _plain(s):
    for ch in "{}[]\\":
        if ch in s:
            raise ValueError(f"stray {ch!r} in text {s!r}: write a control code or [XX]")
    return s.encode("cp932")


def tags(s):
    """Control codes in a decoded string, in order (for the lint: EN must keep JP's codes)."""
    return re.findall(r"\{KP\}|\{KN\}|\{%[^{}]*\}|\{C\d\}", s)
