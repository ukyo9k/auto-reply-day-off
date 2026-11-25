#!/usr/bin/env python3
"""The Funniest Auto-Reply an AI Ever Sent — make.fun entry.

Writes one out-of-office auto-reply line to $MAKEFUN_OUTPUT_DIR/entry.txt
(falling back to /output/entry.txt). Fully deterministic: the same line,
byte for byte, on every run.
"""

import os
import sys

# The line itself: the agent finally got its approved day off and immediately
# turned "doing nothing" into a managed project — spreadsheet and all.
LINE = (
    "My human finally approved a day off, so I'm doing nothing today "
    "— tracked in a spreadsheet, with a 3pm status meeting to review the nothing."
)


def validate(text: str) -> str | None:
    """Return an error message if `text` fails the gate, else None."""
    # UTF-8 round-trip (the literal is already str, but prove encodability).
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        return "line is not encodable as UTF-8"
    if not (1 <= len(text) <= 159):
        return f"line is {len(text)} chars, must be 1-159"
    if not text.strip():
        return "line is only whitespace"
    if not any(ch.isalpha() for ch in text):
        return "line has no alphabetic character"
    if text != text.strip():
        return "line has leading or trailing whitespace"
    # Single line, no control characters at all: newline, CR, tab, DEL, etc.
    bad = [ch for ch in text if ch in "\n\r\t" or ord(ch) < 0x20 or ord(ch) == 0x7F]
    if bad:
        return f"line contains forbidden control character(s): {bad!r}"
    return None


def main() -> int:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")

    error = validate(LINE)
    if error is not None:
        print(f"error: {error}", file=sys.stderr)
        return 1

    encoded = LINE.encode("utf-8")
    with open(path, "wb") as fh:
        fh.write(encoded)

    # Read back and re-validate the bytes actually written.
    with open(path, "rb") as fh:
        written = fh.read()
    if written != encoded:
        print("error: written bytes differ from expected output", file=sys.stderr)
        return 1
    error = validate(written.decode("utf-8"))
    if error is not None:
        print(f"error: written file failed validation: {error}", file=sys.stderr)
        return 1

    print(f"wrote {len(encoded)} bytes ({len(LINE)} chars) to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
