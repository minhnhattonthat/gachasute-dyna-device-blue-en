"""postal_route.py: a warp scene line that types a postal code on the profile form (QA of the address lookup).

    python -X utf8 tools/debug/postal_route.py NAME 4070033 [--extra "6 down;30 -;6 a;120 -"] >> scenes.tsv

The form opens with the cursor on the name row: A + B wakes the cursor, Down = postal row, A opens the number pad
(1 2 3 / 4 5 6 / 7 8 9 / * 0 #, cursor on 1), each digit = moves + A, START confirms and runs the lookup.
"""
import argparse

PAD = {str(d): ((d - 1) // 3, (d - 1) % 3) for d in range(1, 10)}
PAD["0"] = (3, 1)


def route(code, extra=""):
    steps = ["10 -", "6 a", "80 -", "6 b", "60 -", "6 down", "30 -", "6 a", "80 -"]
    r, c = 0, 0
    for ch in code:
        tr, tc = PAD[ch]
        while r != tr:
            steps += ["6 down" if tr > r else "6 up", "12 -"]
            r += 1 if tr > r else -1
        while c != tc:
            steps += ["6 right" if tc > c else "6 left", "12 -"]
            c += 1 if tc > c else -1
        steps += ["6 a", "30 -"]
    steps += ["6 start", "120 -"]
    if extra:
        steps += extra.split(";")
    return ";".join(steps)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("code")
    ap.add_argument("--extra", default="")
    ap.add_argument("--hold", type=int, default=1500)
    a = ap.parse_args()
    print(f"{a.name}\tboot\tform|{route(a.code, a.extra)}\t{a.hold}\tprofile form, postal code {a.code}")


if __name__ == "__main__":
    main()
