import sys
from collections import Counter


def main() -> int:
    counts: Counter[str] = Counter()
    for line in sys.stdin:
        counts.update(line.lower().split())
    for word, n in counts.most_common(10):
        print(f"{n:6d}  {word}")
    if not counts:
        print("no input", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
