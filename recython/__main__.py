from __future__ import annotations

import sys

from recython.cli import main


def run() -> None:
    raise SystemExit(main(sys.argv[1:]))


if __name__ == "__main__":
    run()
