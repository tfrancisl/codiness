import csv
from pathlib import Path


def write_report(rows: list[dict], out_dir: str) -> Path:
    """Write the rows to <out_dir>/report.csv and return the file path."""
    target = Path(out_dir)
    target.mkdir(parents=True, exist_ok=True)
    out_file = target / "report.csv"
    with out_file.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return out_file
