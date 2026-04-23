from __future__ import annotations

from semantic_ai_washing.analysis.build_wrds_gvkey_permno_bridge import (
    LinkRow,
    LookupRow,
    choose_link_candidate,
    choose_lookup_candidate,
    is_link_valid_for_filing,
)


def test_is_link_valid_for_filing_respects_date_bounds() -> None:
    link = LinkRow(gvkey='001', permno='10001', permco='20001', linktype='LC', linkprim='P', linkdt='2021-01-01', linkenddt='2022-12-31')
    assert is_link_valid_for_filing(link, '20210115') is True
    assert is_link_valid_for_filing(link, '20230101') is False
    assert is_link_valid_for_filing(link, '20200101') is False


def test_choose_link_candidate_prefers_primary_and_linktype_order() -> None:
    links = [
        LinkRow(gvkey='001', permno='10003', permco='20003', linktype='LS', linkprim='C', linkdt='2020-01-01', linkenddt=''),
        LinkRow(gvkey='001', permno='10002', permco='20002', linktype='LU', linkprim='C', linkdt='2020-01-01', linkenddt=''),
        LinkRow(gvkey='001', permno='10001', permco='20001', linktype='LC', linkprim='P', linkdt='2020-01-01', linkenddt=''),
    ]
    chosen, count = choose_link_candidate(links, '20210401')
    assert chosen is not None
    assert chosen.permno == '10001'
    assert count == 3


def test_choose_lookup_candidate_filters_blank_permnos_and_uses_dates() -> None:
    links = [
        LookupRow(gvkey='018561', cik='0001576169', permno='', permco='', tic='BNFT', conm='BENEFITFOCUS INC', linkdt='2010-01-01', linkenddt='2013-09-17'),
        LookupRow(gvkey='018561', cik='0001576169', permno='14149', permco='54550', tic='BNFT', conm='BENEFITFOCUS INC', linkdt='2013-09-18', linkenddt='2023-01-31'),
    ]
    chosen, count = choose_lookup_candidate(links, '20210310')
    assert chosen is not None
    assert chosen.permno == '14149'
    assert count == 1
