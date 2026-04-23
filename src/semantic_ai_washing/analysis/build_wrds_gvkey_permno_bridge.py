"""Build a filing-level WRDS bridge from gvkey to permno/permco using CCM link history."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import date, datetime, timezone
import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
import psycopg2

DEFAULT_SPINE = "data/interim/market/filing_event_spine_v1.csv"
DEFAULT_OUTPUT = "data/interim/market/filing_wrds_bridge_v1.csv"
DEFAULT_REPORT = "reports/analysis/filing_wrds_bridge_v1.json"
DEFAULT_UNMATCHED = "reports/analysis/filing_wrds_bridge_unmatched_v1.csv"
DEFAULT_DOTENV = ".env"
DEFAULT_ALLOWED_LINKTYPES = ("LC", "LU", "LS")
DEFAULT_ALLOWED_LINKPRIM = ("P", "C")
OUTPUT_COLUMNS = [
    "filing_id",
    "source_filename",
    "cik",
    "filing_date",
    "gvkey",
    "permno",
    "permco",
    "linktype",
    "linkprim",
    "linkdt",
    "linkenddt",
    "wrds_bridge_status",
    "valid_candidate_count",
]


@dataclass(frozen=True)
class LinkRow:
    gvkey: str
    permno: str
    permco: str
    linktype: str
    linkprim: str
    linkdt: str
    linkenddt: str


@dataclass(frozen=True)
class LookupRow:
    gvkey: str
    cik: str
    permno: str
    permco: str
    tic: str
    conm: str
    linkdt: str
    linkenddt: str


def load_spine(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [dict(row) for row in reader]


def _parse_date(value: str) -> date | None:
    text = str(value or "").strip()
    if not text:
        return None
    for fmt in ("%Y%m%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def _link_priority(link: LinkRow) -> tuple[int, int, str, str]:
    prim_rank = {"P": 0, "C": 1}
    type_rank = {"LC": 0, "LU": 1, "LS": 2}
    start = link.linkdt or "9999-12-31"
    return (
        prim_rank.get(link.linkprim, 9),
        type_rank.get(link.linktype, 9),
        start,
        link.permno,
    )


def is_link_valid_for_filing(link: LinkRow, filing_date: str) -> bool:
    filing = _parse_date(filing_date)
    if filing is None:
        return False
    start = _parse_date(link.linkdt)
    end = _parse_date(link.linkenddt)
    if start and filing < start:
        return False
    if end and filing > end:
        return False
    return True


def choose_link_candidate(links: list[LinkRow], filing_date: str) -> tuple[LinkRow | None, int]:
    valid = [link for link in links if is_link_valid_for_filing(link, filing_date)]
    if not valid:
        return None, 0
    valid_sorted = sorted(valid, key=_link_priority)
    return valid_sorted[0], len(valid)


def _lookup_priority(link: LookupRow) -> tuple[str, str]:
    start = link.linkdt or "9999-12-31"
    return (start, link.permno)


def choose_lookup_candidate(links: list[LookupRow], filing_date: str) -> tuple[LookupRow | None, int]:
    valid = [
        link
        for link in links
        if link.permno and is_link_valid_for_filing(
            LinkRow(
                gvkey=link.gvkey,
                permno=link.permno,
                permco=link.permco,
                linktype="",
                linkprim="",
                linkdt=link.linkdt,
                linkenddt=link.linkenddt,
            ),
            filing_date,
        )
    ]
    if not valid:
        return None, 0
    valid_sorted = sorted(valid, key=_lookup_priority)
    return valid_sorted[0], len(valid)


def load_credentials(dotenv_path: str | Path) -> dict[str, str]:
    load_dotenv(dotenv_path, override=False)
    return {
        "user": os.getenv("WRDS_USER", ""),
        "password": os.getenv("WRDS_PASS", ""),
        "host": os.getenv("WRDS_DB_HOST", ""),
        "port": os.getenv("WRDS_DB_PORT", ""),
    }


def fetch_link_rows(
    gvkeys: list[str],
    *,
    dotenv_path: str | Path,
    allowed_linktypes: tuple[str, ...],
    allowed_linkprim: tuple[str, ...],
) -> dict[str, list[LinkRow]]:
    creds = load_credentials(dotenv_path)
    if not all(creds.values()):
        raise RuntimeError("WRDS credentials are missing from the environment/.env")
    conn = psycopg2.connect(
        dbname="wrds",
        user=creds["user"],
        password=creds["password"],
        host=creds["host"],
        port=int(creds["port"]),
        connect_timeout=15,
    )
    try:
        placeholders = ",".join(["%s"] * len(gvkeys))
        query = f"""
            select
                gvkey,
                lpermno,
                lpermco,
                linktype,
                linkprim,
                linkdt,
                linkenddt
            from crsp.ccmxpf_lnkhist
            where gvkey in ({placeholders})
              and linktype = any(%s)
              and linkprim = any(%s)
        """
        with conn.cursor() as cursor:
            cursor.execute(query, [*gvkeys, list(allowed_linktypes), list(allowed_linkprim)])
            rows = cursor.fetchall()
    finally:
        conn.close()

    links: dict[str, list[LinkRow]] = {}
    for gvkey, lpermno, lpermco, linktype, linkprim, linkdt, linkenddt in rows:
        record = LinkRow(
            gvkey=str(gvkey or "").strip(),
            permno=str(lpermno or "").strip(),
            permco=str(lpermco or "").strip(),
            linktype=str(linktype or "").strip(),
            linkprim=str(linkprim or "").strip(),
            linkdt=str(linkdt or "").strip(),
            linkenddt=str(linkenddt or "").strip(),
        )
        links.setdefault(record.gvkey, []).append(record)
    return links


def fetch_lookup_rows(
    *,
    dotenv_path: str | Path,
    ciks: list[str],
) -> dict[str, list[LookupRow]]:
    creds = load_credentials(dotenv_path)
    if not all(creds.values()):
        raise RuntimeError("WRDS credentials are missing from the environment/.env")
    conn = psycopg2.connect(
        dbname="wrds",
        user=creds["user"],
        password=creds["password"],
        host=creds["host"],
        port=int(creds["port"]),
        connect_timeout=15,
    )
    try:
        placeholders = ",".join(["%s"] * len(ciks))
        query = f"""
            select
                gvkey,
                cik,
                lpermno,
                lpermco,
                tic,
                conm,
                linkdt,
                linkenddt
            from crsp.ccm_lookup
            where cik in ({placeholders})
        """
        with conn.cursor() as cursor:
            cursor.execute(query, ciks)
            rows = cursor.fetchall()
    finally:
        conn.close()

    lookup: dict[str, list[LookupRow]] = {}
    for gvkey, cik, lpermno, lpermco, tic, conm, linkdt, linkenddt in rows:
        record = LookupRow(
            gvkey=str(gvkey or "").strip(),
            cik=str(cik or "").strip().zfill(10),
            permno=str(lpermno or "").strip(),
            permco=str(lpermco or "").strip(),
            tic=str(tic or "").strip(),
            conm=str(conm or "").strip(),
            linkdt=str(linkdt or "").strip(),
            linkenddt=str(linkenddt or "").strip(),
        )
        lookup.setdefault(record.cik, []).append(record)
    return lookup


def build_wrds_bridge(
    spine_path: str = DEFAULT_SPINE,
    *,
    dotenv_path: str = DEFAULT_DOTENV,
    allowed_linktypes: tuple[str, ...] = DEFAULT_ALLOWED_LINKTYPES,
    allowed_linkprim: tuple[str, ...] = DEFAULT_ALLOWED_LINKPRIM,
) -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, Any]]:
    spine_rows = load_spine(spine_path)
    gvkeys = sorted({row.get("gvkey", "").strip() for row in spine_rows if row.get("gvkey", "").strip()})
    ciks = sorted({row.get("cik", "").strip() for row in spine_rows if row.get("cik", "").strip()})
    link_lookup = fetch_link_rows(
        gvkeys,
        dotenv_path=dotenv_path,
        allowed_linktypes=allowed_linktypes,
        allowed_linkprim=allowed_linkprim,
    ) if gvkeys else {}
    cik_lookup = fetch_lookup_rows(
        dotenv_path=dotenv_path,
        ciks=ciks,
    ) if ciks else {}

    output_rows: list[dict[str, str]] = []
    unmatched_rows: list[dict[str, str]] = []
    status_counts: dict[str, int] = {}

    for row in spine_rows:
        gvkey = row.get("gvkey", "").strip()
        status = ""
        chosen: LinkRow | None = None
        chosen_lookup: LookupRow | None = None
        valid_count = 0
        if not gvkey:
            status = "missing_gvkey"
        else:
            chosen, valid_count = choose_link_candidate(link_lookup.get(gvkey, []), row.get("filing_date", ""))
            if chosen is None:
                status = "no_valid_link"
            elif valid_count > 1:
                status = "resolved_multiple_valid_links"
            else:
                status = "matched"

        if status in {"missing_gvkey", "no_valid_link"}:
            chosen_lookup, lookup_valid_count = choose_lookup_candidate(
                cik_lookup.get(row.get("cik", "").strip(), []),
                row.get("filing_date", ""),
            )
            if chosen_lookup is not None:
                valid_count = lookup_valid_count
                status = "matched_via_ccm_lookup_fallback"

        bridge_row = {
            "filing_id": row.get("filing_id", ""),
            "source_filename": row.get("source_filename", ""),
            "cik": row.get("cik", ""),
            "filing_date": row.get("filing_date", ""),
            "gvkey": chosen_lookup.gvkey if chosen_lookup else gvkey,
            "permno": chosen_lookup.permno if chosen_lookup else (chosen.permno if chosen else ""),
            "permco": chosen_lookup.permco if chosen_lookup else (chosen.permco if chosen else ""),
            "linktype": chosen.linktype if chosen else "",
            "linkprim": chosen.linkprim if chosen else "",
            "linkdt": chosen_lookup.linkdt if chosen_lookup else (chosen.linkdt if chosen else ""),
            "linkenddt": chosen_lookup.linkenddt if chosen_lookup else (chosen.linkenddt if chosen else ""),
            "wrds_bridge_status": status,
            "valid_candidate_count": str(valid_count),
        }
        output_rows.append(bridge_row)
        status_counts[status] = status_counts.get(status, 0) + 1
        if status not in {"matched", "matched_via_ccm_lookup_fallback"}:
            unmatched_rows.append(bridge_row)

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "spine_path": str(Path(spine_path).resolve()),
        "dotenv_path": str(Path(dotenv_path).resolve()),
        "allowed_linktypes": list(allowed_linktypes),
        "allowed_linkprim": list(allowed_linkprim),
        "row_count": len(output_rows),
        "matched_count": status_counts.get("matched", 0) + status_counts.get("matched_via_ccm_lookup_fallback", 0),
        "status_counts": dict(sorted(status_counts.items())),
        "unique_permno_count": len({row['permno'] for row in output_rows if row['permno']}),
        "unique_permco_count": len({row['permco'] for row in output_rows if row['permco']}),
    }
    return output_rows, unmatched_rows, report


def write_csv(path: str | Path, rows: list[dict[str, str]]) -> None:
    resolved = Path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def write_report(path: str | Path, report: dict[str, Any]) -> None:
    resolved = Path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(json.dumps(report, indent=2), encoding='utf-8')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spine', default=DEFAULT_SPINE)
    parser.add_argument('--dotenv', default=DEFAULT_DOTENV)
    parser.add_argument('--output', default=DEFAULT_OUTPUT)
    parser.add_argument('--report', default=DEFAULT_REPORT)
    parser.add_argument('--unmatched-output', default=DEFAULT_UNMATCHED)
    parser.add_argument('--allowed-linktypes', default=','.join(DEFAULT_ALLOWED_LINKTYPES))
    parser.add_argument('--allowed-linkprim', default=','.join(DEFAULT_ALLOWED_LINKPRIM))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows, unmatched, report = build_wrds_bridge(
        spine_path=args.spine,
        dotenv_path=args.dotenv,
        allowed_linktypes=tuple(part.strip() for part in args.allowed_linktypes.split(',') if part.strip()),
        allowed_linkprim=tuple(part.strip() for part in args.allowed_linkprim.split(',') if part.strip()),
    )
    write_csv(args.output, rows)
    write_csv(args.unmatched_output, unmatched)
    write_report(args.report, report)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
