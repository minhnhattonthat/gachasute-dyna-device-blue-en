"""Print the pixel width of each argument as the VWF draws it: python -X utf8 tools/width.py "line one" "line two"."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lint  # noqa: E402

for s in sys.argv[1:]:
    print(lint.line_width(s), s)
