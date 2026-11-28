# -*- coding: utf-8 -*-
"""Replay the BIR Withholding Tax Calculator and compare it with the model.

The BIR publishes exactly one public calculator for tax computation: a
withholding tax calculator for employees earning purely compensation income,
https://web-services.bir.gov.ph/tax_calculator/wt_calculator.html . Its
arithmetic is in wt_calculator.js, transcribed here branch by branch: the five
period tables are TABLES, the branch order and the two dead-end branches are
bir_tax.

Four numbers are recorded for every case:

  bir       the shipped calculator's answer, replayed from that source. It
            computes in binary floating point and rounds half up at the end
            (Math.round(x * 100) / 100), so this replay does too, in the same
            order of operations. That is not sloppiness: two cases below turn
            on the last bit, and rounding the replay exactly would hide it.
  statute   the same period table applied to *total* taxable compensation in
            exact integer centavos, truncating. For the annual table this is
            bracketTax from the verified Lean model, imported below and
            asserted equal on a sweep, so this file holds no third
            implementation of the schedule.
  observed  answers read from the live script in a browser on RETRIEVED, kept
            here so any drift between this transcription and the shipped code
            fails the run instead of passing silently.
  display   the Net Taxable Compensation Income the form itself shows,
            replayed from getTaxableCompensationIncome and
            getNetTaxableCompensationIncome, with its own observed values in
            OBSERVED_DISPLAY. Recorded so that finding C is measured: the
            displayed base can be compared with the figure the branches tax
            instead of being argued from the source.

Period tables are applied to the period's own total taxable compensation. The
annual column is a claim about the Code (§24(A)(2)(a)); the daily, weekly,
semi-monthly and monthly columns are claims about Annex E of RR 11-2018, the
Bureau's own withholding tables. Those four are transcribed below as ANNEX_E
and asserted equal to TABLES row for row, so the comparison with the
regulation is checked on every run instead of being asserted in prose. Two
other publications reprint the same table -- the Bureau's withholding-tax
page, preserved in a court circular, and a Vialto advisory -- and REPRINTS
holds those, so the twenty bases are checked against something other than
the annex file as well.

The annex has two tranches and the regulation sends the other one to Annex
"D", for compensation paid 1 January 2018 to 31 December 2022. That table is
transcribed separately as ANNEX_D. The shipped calculator implements only the
2023 table, so ANNEX_D is applied to no case: it is a second transcription
with its own check, against the 2018 bases the regulation's worked
illustrations print.

The SSS/GSIS/Pag-IBIG box is recorded per case in SSS, but it is not an
argument to bir_tax or statute_tax. That the box changes neither the tax nor
the displayed figure is the measurement (finding C), not an assumption.

Writes data/bir_calculator_check.csv. Deterministic, stdlib only, no network.

    python -X utf8 tools/bir_calculator_check.py
"""

import csv
import sys
from math import floor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_benchmark import bracket_tax  # noqa: E402  the verified schedule

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = DATA / "bir_calculator_check.csv"

SOURCE_PAGE = "https://web-services.bir.gov.ph/tax_calculator/wt_calculator.html"
SOURCE_JS = "https://web-services.bir.gov.ph/tax_calculator/js/wt_calculator.js"
RETRIEVED = "2026-11-28"

# The 90,000 peso ceiling on 13th month pay and other benefits, in centavos.
BENEFITS_CEILING = 90_000_00

# Each period table, ascending: (floor_centavos, base_centavos, rate_percent).
# The shipped code tests the same floors in descending order with `>=`; the
# bases are the cumulative tax at each floor, which is why they are not
# floor * rate / 100. Transcribed from getDailyZero, getWeeklyZero,
# getSemiMonthlyZero, getMonthlyZero and getAnnual.
TABLES = {
    "daily": [
        (685_00, 0, 15),
        (1_096_00, 61_65, 20),
        (2_192_00, 280_85, 25),
        (5_479_00, 1_102_60, 30),
        (21_918_00, 6_034_30, 35),
    ],
    "weekly": [
        (4_808_00, 0, 15),
        (7_692_00, 432_60, 20),
        (15_385_00, 1_971_20, 25),
        (38_462_00, 7_740_45, 30),
        (153_846_00, 42_355_65, 35),
    ],
    "semi_monthly": [
        (10_417_00, 0, 15),
        (16_667_00, 937_50, 20),
        (33_333_00, 4_270_70, 25),
        (83_333_00, 16_770_70, 30),
        (333_333_00, 91_770_70, 35),
    ],
    "monthly": [
        (20_833_00, 0, 15),
        (33_333_00, 1_875_00, 20),
        (66_667_00, 8_541_80, 25),
        (166_667_00, 33_541_80, 30),
        (666_667_00, 183_541_80, 35),
    ],
    "annual": [
        (250_000_00, 0, 15),
        (400_000_00, 22_500_00, 20),
        (800_000_00, 102_500_00, 25),
        (2_000_000_00, 402_500_00, 30),
        (8_000_000_00, 2_202_500_00, 35),
    ],
}

# Annex "E" of Revenue Regulations No. 11-2018, "Revised Withholding Tax
# Table", as hosted by the Bureau at bir-cdn.bir.gov.ph/local/pdf/Annex E RR
# 11-2018.pdf, read on RETRIEVED. The copy there is the table "Effective
# January 1, 2023 and onwards" -- the second TRAIN tranche, which is the one
# the calculator implements.
#
# Transcribed in the same shape as TABLES, because Annex E writes each band's
# range in whole pesos and its excess "over" the band's first peso:
#
#     P 1,096 - P 2,191    P 61.65 + 20% over P 1,096
#
# so the first peso of the range is the excess floor, and the base is the
# prescribed withholding tax printed above the rate. Annex E's first band
# ("P 685 and below: 0.00") and its second band's "over P 685" meet at 685,
# where 15% of a zero excess is the 0.00 the first band prints.
#
# Annex E publishes four payroll-period tables and no annual one: the annual
# schedule is §24(A)(2)(a) itself, and the statute column above is that.
ANNEX_E = {
    "daily": [
        (685_00, 0, 15),
        (1_096_00, 61_65, 20),
        (2_192_00, 280_85, 25),
        (5_479_00, 1_102_60, 30),
        (21_918_00, 6_034_30, 35),
    ],
    "weekly": [
        (4_808_00, 0, 15),
        (7_692_00, 432_60, 20),
        (15_385_00, 1_971_20, 25),
        (38_462_00, 7_740_45, 30),
        (153_846_00, 42_355_65, 35),
    ],
    "semi_monthly": [
        (10_417_00, 0, 15),
        (16_667_00, 937_50, 20),
        (33_333_00, 4_270_70, 25),
        (83_333_00, 16_770_70, 30),
        (333_333_00, 91_770_70, 35),
    ],
    "monthly": [
        (20_833_00, 0, 15),
        (33_333_00, 1_875_00, 20),
        (66_667_00, 8_541_80, 25),
        (166_667_00, 33_541_80, 30),
        (666_667_00, 183_541_80, 35),
    ],
}

# A second source for the same tables: the body of RR 11-2018 itself, read on
# RETRIEVED from bir-cdn.bir.gov.ph/local/pdf/RR No. 11-2018.pdf. The
# regulation does not reprint the per-period tables -- those are the separate
# annex files -- but it prints three things that can be checked against:
#
#   1. Sec. 2.79(B)(1): Annex "D" governs compensation paid 1 January 2018 to
#      31 December 2022 and Annex "E" compensation paid from 1 January 2023,
#      which is why the copy transcribed above is the 2023-onwards one.
#   2. Sec. 2.79(B)(4), Step 4: "Compute the withholding tax due by adding the
#      tax predetermined in the compensation range as indicated on the column
#      used and the rate of tax on the excess of the total compensation over
#      the minimum of the compensation range." That is base + rate x (amount -
#      floor), the shape of every row of TABLES, and it makes the "over P X"
#      figure the band's floor rather than a separate threshold.
#   3. Sec. 2.79(B)(5)(b) prints the 2023-onwards annual schedule, and the
#      worked illustrations name per-period compensation-range minimums.
#
# What it does *not* print is the 2023 per-period bases, so those rest on the
# annex file alone; rr_text_mismatches() claims only what the body shows.
RR_TEXT_ANNUAL = [
    (250_000_00, 0, 15),
    (400_000_00, 22_500_00, 20),
    (800_000_00, 102_500_00, 25),
    (2_000_000_00, 402_500_00, 30),
    (8_000_000_00, 2_202_500_00, 35),
]

# Compensation-range minimums named in the regulation's own illustrations, by
# period, in centavos. Those illustrations compute 2018 tax, so they carry
# Annex "D" bases and cannot corroborate a 2023 base -- but the per-period
# floors did not move between the tranches, because the P250,000 exemption did
# not, so they do corroborate these. Only floors the body actually prints are
# listed: Illustration 6 names P2,192 daily, 7 names P7,692 weekly, 8 names
# P10,417 semi-monthly, and 9-12 name P20,833, P33,333 and P66,667 monthly.
# The 2018 bases printed beside those floors are the check on ANNEX_D.
RR_TEXT_FLOORS = {
    "daily": {2_192_00},
    "weekly": {7_692_00},
    "semi_monthly": {10_417_00},
    "monthly": {20_833_00, 33_333_00, 66_667_00},
}

# Two reprints of the same 2023 table, neither of them the annex file above,
# read on RETRIEVED. They answer the one question the regulation body could
# not: are the twenty per-period *bases* as the Bureau publishes them, or as
# one PDF's text layer rendered them?
#
#   1. The Bureau's withholding-tax page,
#      bir.gov.ph/index.php/tax-information/withholding-tax.html, as
#      print-captured into Annex A of OCA Circular No. 35-2024 (Office of the
#      Court Administrator, 5 February 2024,
#      oca.judiciary.gov.ph/wp-content/uploads/OCA-Circular-No.-35-2024.pdf).
#      The circular adopts "the Revised Withholding Tax Table (Annex A) as
#      required by the Bureau" for monthly salaries; the capture carries the
#      page's own URL and its "EFFECTIVE DATE JANUARY 1, 2023" annual table.
#      The page itself answered 404 when checked on RETRIEVED, so the capture
#      is the surviving copy compared here.
#   2. Vialto Partners, "Philippines | 2024 Year-end reminders on employment
#      taxes", 4 December 2024, which reprints the WTC table "effective
#      January 1, 2023 onwards".
#
# Both print the 2023 ranges with the 2023 bases, and both agree with ANNEX_E
# band for band. That rules out a transcription error in the annex file -- the
# failure the daily table's mangled "P 6,034.00.30" invites -- but not a
# drafting error in the regulation, since every source reprints the same
# table rather than deriving it from Sec. 24(A)(2)(a).
BIR_WT_PAGE_2023 = {
    "daily": [
        (685_00, 0, 15),
        (1_096_00, 61_65, 20),
        (2_192_00, 280_85, 25),
        (5_479_00, 1_102_60, 30),
        (21_918_00, 6_034_30, 35),
    ],
    "weekly": [
        (4_808_00, 0, 15),
        (7_692_00, 432_60, 20),
        (15_385_00, 1_971_20, 25),
        (38_462_00, 7_740_45, 30),
        (153_846_00, 42_355_65, 35),
    ],
    "semi_monthly": [
        (10_417_00, 0, 15),
        (16_667_00, 937_50, 20),
        (33_333_00, 4_270_70, 25),
        (83_333_00, 16_770_70, 30),
        (333_333_00, 91_770_70, 35),
    ],
    "monthly": [
        (20_833_00, 0, 15),
        (33_333_00, 1_875_00, 20),
        (66_667_00, 8_541_80, 25),
        (166_667_00, 33_541_80, 30),
        (666_667_00, 183_541_80, 35),
    ],
}

VIALTO_2023 = {
    "daily": [
        (685_00, 0, 15),
        (1_096_00, 61_65, 20),
        (2_192_00, 280_85, 25),
        (5_479_00, 1_102_60, 30),
        (21_918_00, 6_034_30, 35),
    ],
    "weekly": [
        (4_808_00, 0, 15),
        (7_692_00, 432_60, 20),
        (15_385_00, 1_971_20, 25),
        (38_462_00, 7_740_45, 30),
        (153_846_00, 42_355_65, 35),
    ],
    "semi_monthly": [
        (10_417_00, 0, 15),
        (16_667_00, 937_50, 20),
        (33_333_00, 4_270_70, 25),
        (83_333_00, 16_770_70, 30),
        (333_333_00, 91_770_70, 35),
    ],
    "monthly": [
        (20_833_00, 0, 15),
        (33_333_00, 1_875_00, 20),
        (66_667_00, 8_541_80, 25),
        (166_667_00, 33_541_80, 30),
        (666_667_00, 183_541_80, 35),
    ],
}

REPRINTS = {
    "OCA Circular 35-2024 / BIR withholding-tax page": BIR_WT_PAGE_2023,
    "Vialto 2024 year-end alert": VIALTO_2023,
}

# Annex "D" of the same regulation, "Revised Withholding Tax Table", effective
# 1 January 2018 to 31 December 2022, read on RETRIEVED from
# bir-cdn.bir.gov.ph/local/pdf/Annex D RR 11-2018.pdf. Kept apart from TABLES
# on purpose: the calculator implements the 2023 tranche, so this table is a
# second transcription with its own check, not a table the cases run on.
#
# Same row shape as ANNEX_E -- (floor, tax at the floor, rate above the floor)
# -- so the two tranches can be compared directly.
#
#     P 685 and below      0.00
#     P 685 - P 1,095      0.00  + 20% over P 685
#     P 1,096 - P 2,191    P 82.19 + 25% over P 1,096
#     P 2,192 - P 5,478    P 356.16 + 30% over P 2,192
#     P 5,479 - P 21,917   P 1,342.47 + 32% over P 5,479
#     P 21,918 and above   P 6,602.74 + 35% over P 21,918
#
# The first band's rate is 20%, not the 15% of the 2023 table: the 2018
# schedule exempts the first P250,000 of annual income, so 20% is the first
# rate that bites, and the daily P685 floor is that exemption divided by 264.
ANNEX_D = {
    "daily": [
        (685_00, 0, 20),
        (1_096_00, 82_19, 25),
        (2_192_00, 356_16, 30),
        (5_479_00, 1_342_47, 32),
        (21_918_00, 6_602_74, 35),
    ],
    "weekly": [
        (4_808_00, 0, 20),
        (7_692_00, 576_92, 25),
        (15_385_00, 2_500_00, 30),
        (38_462_00, 9_423_08, 32),
        (153_846_00, 46_346_15, 35),
    ],
    "semi_monthly": [
        (10_417_00, 0, 20),
        (16_667_00, 1_250_00, 25),
        (33_333_00, 5_416_67, 30),
        (83_333_00, 20_416_67, 32),
        (333_333_00, 100_416_67, 35),
    ],
    "monthly": [
        (20_833_00, 0, 20),
        (33_333_00, 2_500_00, 25),
        (66_667_00, 10_833_33, 30),
        (166_667_00, 40_833_33, 32),
        (666_667_00, 200_833_33, 35),
    ],
}

# The 2018 bases the regulation body itself prints, in the illustrations of
# Sec. 2.79(B)(4) that use the withholding tables. Each entry is the tax printed
# on that floor, the marginal rate printed beside it, and the illustration that
# prints them, so a failure names its source rather than "the annex".
#
#   Illustration 6, P2,500 daily:      "Predetermined Tax on P2,192.00 P356.16"
#                                      "+ 30% of the excess"
#   Illustration 7, P9,500 weekly:     "Predetermined Tax on P7,692.00 P576.92"
#                                      "+ 25%"
#   Illustration 8, P15,500 semi:      "Predetermined Tax on P10,417.00 P0"
#                                      "+ 20%"
#   Illustration 9, P165,000 monthly:  "On P66,667.00 P10,833.33" "x 30%"
#   Illustrations 10-12, monthly:      "Tax on P20,833 P0.00" "x 20%",
#                                      "Tax on P33,333 P2,500.00" "x 25%"
#
# Six of the twenty bases, which is what the body prints. Illustration 9's
# prose adds P43,659.89 where its own schedule adds to P41,833.23 (and a
# P103,833 excess where its figures give P103,333); the base is not what it
# fumbles, so only the schedule line is read here.
RR_ILLUSTRATIONS = {
    "daily": {2_192_00: (356_16, 30, "Illustration 6")},
    "weekly": {7_692_00: (576_92, 25, "Illustration 7")},
    "semi_monthly": {10_417_00: (0, 20, "Illustration 8")},
    "monthly": {
        20_833_00: (0, 20, "Illustrations 10-12"),
        33_333_00: (2_500_00, 25, "Illustration 10"),
        66_667_00: (10_833_33, 30, "Illustration 9"),
    },
}


def rr_text_mismatches():
    """Where TABLES disagrees with what the regulation body itself prints."""
    out = []
    if TABLES["annual"] != RR_TEXT_ANNUAL:
        out.append("annual table != RR 11-2018 Sec. 2.79(B)(5)(b) schedule")
    for period, named in RR_TEXT_FLOORS.items():
        known = {row[0] for row in TABLES[period]}
        for floor_c in sorted(named - known):
            out.append(f"{period} {floor_c}: named in RR 11-2018, not a floor here")
    return out


def reprint_mismatches():
    """Bands where TABLES departs from a reprint of the 2023 table.

    Two publications other than the annex file, and both print the twenty
    bases, so a slip in transcribing the annex fails here even though the two
    transcriptions of the annex agree with each other.
    """
    out = []
    for name, tables in REPRINTS.items():
        for period, rows in tables.items():
            if len(rows) != len(TABLES[period]):
                out.append(f"{name}: {period} has {len(rows)} bands, "
                           f"TABLES has {len(TABLES[period])}")
                continue
            for i, (want, row) in enumerate(zip(rows, TABLES[period]), start=1):
                if want != row:
                    out.append(f"{name}: {period} band {i} {row} != reprint {want}")
    return out


def annex_d_mismatches():
    """Where ANNEX_D departs from what RR 11-2018's body prints.

    Two claims. The floors must be TABLES' floors: the P250,000 exemption did
    not move between the tranches, so only bases and rates changed, and a
    mistyped floor would otherwise pass unless an illustration happened to
    name it. And every base and rate an illustration prints must be the one
    transcribed.
    """
    out = []
    for period, rows in ANNEX_D.items():
        got = [row[0] for row in rows]
        want = [row[0] for row in TABLES[period]]
        if got != want:
            out.append(f"{period}: Annex D floors {got} != Annex E floors {want}")
    for period, named in RR_ILLUSTRATIONS.items():
        rows = {row[0]: row for row in ANNEX_D[period]}
        for floor_c, (base_c, rate, cite) in sorted(named.items()):
            row = rows.get(floor_c)
            if row is None:
                out.append(f"{cite}: {period} floor {floor_c} is not in Annex D")
            elif (row[1], row[2]) != (base_c, rate):
                out.append(f"{cite}: Annex D {period} at {floor_c} is "
                           f"{(row[1], row[2])} != printed {(base_c, rate)}")
    return out


def annex_d_drift():
    """Annex D bands whose base is not the tax accumulated at their floor.

    The arithmetic that holds to the centavo on Annex E does not hold on Annex
    D, and that is a measurement rather than an oversight: the 2018 bases were
    annualised and rounded (the daily P82.19 against 20% of P411), while the
    2023 table was generated from the annual schedule in one step and is exact.
    So this function reports the drift instead of being a check, and is why
    ANNEX_D is checked against the illustrations.
    """
    out = []
    for period, rows in ANNEX_D.items():
        for i in range(1, len(rows)):
            floor_c, base_c, _ = rows[i]
            prev_floor, prev_base, prev_rate = rows[i - 1]
            cumulative = prev_base + (floor_c - prev_floor) * prev_rate // 100
            if cumulative != base_c:
                out.append((period, floor_c, base_c, cumulative - base_c))
    return out


def annex_e_mismatches():
    """Bands where TABLES departs from the transcribed Annex E.

    This compares two transcriptions, so on its own it catches an edit to one
    of them and nothing more; base_errors() is the half that recomputes.
    """
    out = []
    for period, rows in ANNEX_E.items():
        if len(TABLES[period]) != len(rows):
            out.append(f"{period}: {len(TABLES[period])} bands, Annex E has {len(rows)}")
            continue
        for i, (row, want) in enumerate(zip(TABLES[period], rows), start=1):
            if row != want:
                out.append(f"{period} band {i}: {row} != Annex E {want}")
    return out


def base_errors():
    """Bands whose prescribed base is not the tax accumulated at its floor.

    Recomputed from the band below, at that band's rate, in exact centavos and
    truncating. A mistyped base fails this even if ANNEX_E was mistyped the
    same way.
    """
    out = []
    for period, rows in ANNEX_E.items():
        for i in range(1, len(rows)):
            floor_c, base_c, _ = rows[i]
            prev_floor, prev_base, prev_rate = rows[i - 1]
            cumulative = prev_base + (floor_c - prev_floor) * prev_rate // 100
            if cumulative != base_c:
                out.append(f"{period} base {base_c} at {floor_c}: "
                           f"accumulated {cumulative}")
    return out


def band(table, amount_centavos):
    """Highest floor at or below the amount, as the shipped `>=` chain does."""
    chosen = table[0]
    for row in table:
        if amount_centavos >= row[0]:
            chosen = row
    return chosen


def taxable_benefits(benefits_nt):
    """13th month and other benefits above the ceiling are taxable."""
    return max(0, benefits_nt - BENEFITS_CEILING)


def bir_tax(period, regular, supp=0, benefits_nt=0):
    """The shipped calculator's answer, in centavos.

    Two behaviours here are not stylistic; they are what the branches do.

    1. `getDailyZero` ends with

           else if (wtTaxableCompensationIncome >= 0)
           { wtTotalTaxWithheld = ((wtTaxableCompensationIncome - 0) + wtSupplementary); }

       -- no rate and no base, so for taxable regular pay below the first
       floor it returns the income itself. The other four period functions
       return 0 in the same branch.

    2. The bracket is chosen on regular compensation alone, then supplementary
       is added to that bracket's excess:

           (((wtTaxableCompensationIncome - floor) + wtSupplementary) * rate) + base

       so supplementary is taxed at regular pay's marginal rate even when the
       total crosses a bracket, and is dropped entirely when regular pay is
       below the first floor.

    The arithmetic is done in pesos floats in the source's order of operations,
    so that the last-bit cases round the way the page rounds them.
    """
    table = TABLES[period]
    supp_total = supp + taxable_benefits(benefits_nt)
    supp_p = supp_total / 100

    if regular < table[0][0]:
        if period == "daily":
            return int(floor((regular / 100 + supp_p) * 100 + 0.5))
        return 0

    floor_c, base_c, rate = band(table, regular)
    excess = (regular / 100 - floor_c / 100) + supp_p
    value = excess * (rate / 100) + base_c / 100
    return int(floor(value * 100 + 0.5))


def display_net_taxable(period, regular, supp=0, benefits_nt=0, sss=0):
    """The Net Taxable Compensation Income the form displays, in centavos.

    Transcribed from getTaxableCompensationIncome and
    getNetTaxableCompensationIncome. getPayrollPeriod() returns 1 for annual
    and 12, 24, 66 or 264 for the payroll periods, so its `< 4` test is true
    only for annual -- the opposite of what the names suggest:

      * annual: taxable = total compensation, with no SSS subtracted, and the
        annual display branch returns it unchanged;
      * payroll periods: taxable = total - SSS, and then the non-annual
        display branch adds SSS straight back.

    Either way the displayed figure is total compensation: the SSS box never
    reaches the screen. That is the measured half of finding C.
    """
    total_p = regular / 100 + supp / 100 + taxable_benefits(benefits_nt) / 100
    if period == "annual":
        taxable_p = total_p
    else:
        taxable_p = total_p - sss / 100
    net_p = taxable_p if period == "annual" else taxable_p + sss / 100
    return max(0, int(floor(net_p * 100 + 0.5)))


def statute_tax(period, regular, supp=0, benefits_nt=0):
    """The table applied to total taxable compensation, exact, truncating."""
    table = TABLES[period]
    total = regular + supp + taxable_benefits(benefits_nt)
    if total <= table[0][0]:
        return 0
    floor_c, base_c, rate = band(table, total)
    return base_c + (total - floor_c) * rate // 100


# Answers read from the live script on RETRIEVED, in centavos. Produced by
# evaluating the shipped wt_calculator.js against a stub DOM and calling the
# period functions directly, so these are the page's numbers, not ours.
OBSERVED = {
    "daily_zero_600": 600_00,
    "daily_zero_684_99": 684_99,
    "daily_floor_685": 0,
    "daily_over_685": 2_25,
    "daily_zero_with_supp": 1_600_00,
    "daily_bracket_1096": 61_65,
    "daily_top_21918": 6_034_30,
    "weekly_zero_4807_99": 0,
    "weekly_floor_4808": 0,
    "weekly_top_153846": 42_355_65,
    "semi_floor_10417": 0,
    "semi_top_333333": 91_770_70,
    "monthly_zero_20832_99": 0,
    "monthly_floor_20833": 0,
    "monthly_below_floor_with_supp": 0,
    "monthly_39999": 3_208_20,
    "monthly_top_666667": 183_541_80,
    "monthly_30000": 1_375_05,
    "annual_250000": 0,
    "annual_250000_10": 2,
    "annual_400000": 2_250_000,
    "annual_cross_399999_supp100k": 3_749_985,
    "annual_800000": 10_250_000,
    "annual_2M": 40_250_000,
    "annual_8M": 220_250_000,
    "annual_10M": 290_250_000,
    "annual_below_floor_with_supp": 0,
    "annual_ben_90000": 0,
    "annual_ben_95000": 750_00,
    "annual_top_10c": 220_250_003,
}

# The same anti-drift device for the displayed Net Taxable Compensation
# Income: values read from the live form on RETRIEVED, in centavos.
OBSERVED_DISPLAY = {
    "monthly_30000": 3_000_000,
    "monthly_30000_sss_1350": 3_000_000,
    "monthly_28650_sss_reading": 2_865_000,
    "monthly_below_floor_with_supp": 3_000_000,
    "annual_400000": 40_000_000,
    "annual_400k_sss_10k": 40_000_000,
    "annual_390k_net_of_sss": 39_000_000,
    "annual_cross_399999_supp100k": 49_999_900,
    "annual_ben_95000": 25_500_000,
}

# SSS/GSIS/Pag-IBIG contributions entered in the Non-Taxable/Exempt box, in
# centavos, keyed by case. Kept out of bir_tax and statute_tax on purpose:
# that the box changes neither is what finding C measures.
SSS = {
    "monthly_30000_sss_1350": 1_350_00,
    "annual_400k_sss_10k": 10_000_00,
}

# (case_id, period, regular, supp, benefits_nt, defect, note)
# defect: none | daily_zero_branch | supp_bracket | float
CASES = [
    ("daily_zero_600", "daily", 600_00, 0, 0, "daily_zero_branch",
     "P600/day, below the P685 floor: returns the income"),
    ("daily_zero_684_99", "daily", 684_99, 0, 0, "daily_zero_branch",
     "last centavo below the floor"),
    ("daily_floor_685", "daily", 685_00, 0, 0, "none", "first taxable centavo"),
    ("daily_over_685", "daily", 700_00, 0, 0, "none", "P15 above the floor"),
    ("daily_zero_with_supp", "daily", 600_00, 1_000_00, 0, "daily_zero_branch",
     "same day, P1,000 supplementary"),
    ("daily_bracket_1096", "daily", 1_096_00, 0, 0, "none", "second floor"),
    ("daily_top_21918", "daily", 21_918_00, 0, 0, "none", "top floor"),
    ("weekly_zero_4807_99", "weekly", 4_807_99, 0, 0, "none", "just below floor"),
    ("weekly_floor_4808", "weekly", 4_808_00, 0, 0, "none", "first taxable centavo"),
    ("weekly_top_153846", "weekly", 153_846_00, 0, 0, "none", "top floor"),
    ("semi_floor_10417", "semi_monthly", 10_417_00, 0, 0, "none",
     "first taxable centavo"),
    ("semi_top_333333", "semi_monthly", 333_333_00, 0, 0, "none", "top floor"),
    ("monthly_zero_20832_99", "monthly", 20_832_99, 0, 0, "none",
     "just below floor"),
    ("monthly_floor_20833", "monthly", 20_833_00, 0, 0, "none",
     "first taxable centavo"),
    ("monthly_below_floor_with_supp", "monthly", 20_000_00, 10_000_00, 0,
     "supp_bracket", "regular below floor, P10,000 supplementary: dropped"),
    ("monthly_39999", "monthly", 39_999_00, 0, 0, "none", "inside the 15% band"),
    ("monthly_top_666667", "monthly", 666_667_00, 0, 0, "none", "top floor"),
    ("monthly_30000", "monthly", 30_000_00, 0, 0, "none",
     "P30,000 with the SSS box empty: the baseline, see report"),
    ("annual_250000", "annual", 250_000_00, 0, 0, "none", "P250,000 floor"),
    ("annual_250000_10", "annual", 250_000_10, 0, 0, "float",
     "15% of 10 centavos is 1.5: binary noise rounds it up"),
    ("annual_400000", "annual", 400_000_00, 0, 0, "none", "second floor"),
    ("annual_cross_399999_supp100k", "annual", 399_999_00, 100_000_00, 0,
     "supp_bracket", "total P499,999 crosses into the 20% band"),
    ("annual_800000", "annual", 800_000_00, 0, 0, "none", "third floor"),
    ("annual_2M", "annual", 2_000_000_00, 0, 0, "none", "fourth floor"),
    ("annual_8M", "annual", 8_000_000_00, 0, 0, "none", "top floor"),
    ("annual_10M", "annual", 10_000_000_00, 0, 0, "none", "top band"),
    ("annual_below_floor_with_supp", "annual", 240_000_00, 50_000_00, 0,
     "supp_bracket", "regular below floor, total above it"),
    ("annual_ben_90000", "annual", 250_000_00, 0, 90_000_00, "none",
     "benefits at the ceiling"),
    ("annual_ben_95000", "annual", 250_000_00, 0, 95_000_00, "none",
     "P5,000 of benefits above the ceiling"),
    ("annual_top_10c", "annual", 800_000_010, 0, 0, "float",
     "35% of 10 centavos is 3.5: the same noise rounds it down"),
    ("monthly_30000_sss_1350", "monthly", 30_000_00, 0, 0, "sss_ignored",
     "P1,350 in the SSS box: tax and display both unchanged"),
    ("monthly_28650_sss_reading", "monthly", 28_650_00, 0, 0, "sss_ignored",
     "the same salary entered net of P1,350: P202.50 less tax"),
    ("annual_400k_sss_10k", "annual", 400_000_00, 0, 0, "sss_ignored",
     "P10,000 in the SSS box: tax and display both unchanged"),
    ("annual_390k_net_of_sss", "annual", 390_000_00, 0, 0, "sss_ignored",
     "the same salary entered net of P10,000: P1,500.00 less tax"),
]


def main():
    rows, replay_mismatch, display_mismatch = [], [], []
    for cid, period, regular, supp, ben, defect, note in CASES:
        sss = SSS.get(cid, 0)
        got = bir_tax(period, regular, supp, ben)
        want = statute_tax(period, regular, supp, ben)
        shown = display_net_taxable(period, regular, supp, ben, sss)
        diff = got - want
        if cid in OBSERVED and OBSERVED[cid] != got:
            replay_mismatch.append((cid, OBSERVED[cid], got))
        if cid in OBSERVED_DISPLAY and OBSERVED_DISPLAY[cid] != shown:
            display_mismatch.append((cid, OBSERVED_DISPLAY[cid], shown))
        rows.append({
            "case_id": cid,
            "period": period,
            "regular_centavos": regular,
            "supp_centavos": supp,
            "benefits_nt_centavos": ben,
            "sss_centavos": sss,
            "display_net_taxable_centavos": shown,
            "bir_centavos": got,
            "statute_centavos": want,
            "diff_centavos": diff,
            "verdict": "match" if diff == 0 else ("bir_over" if diff > 0 else "bir_under"),
            "defect": defect,
            "note": note,
        })

    if replay_mismatch:
        for cid, observed, got in replay_mismatch:
            print(f"TRANSCRIPTION DRIFT {cid}: observed={observed} replay={got}")
        sys.exit("bir_tax no longer reproduces the shipped calculator")
    if display_mismatch:
        for cid, observed, shown in display_mismatch:
            print(f"DISPLAY DRIFT {cid}: observed={observed} replay={shown}")
        sys.exit("display_net_taxable no longer reproduces the shipped form")

    # Finding C, measured: for the same salary, filling the SSS box changes
    # neither the displayed net taxable income nor the tax. bir_tax has no
    # SSS argument at all; here the display is checked against the boxless
    # case, so a transcription that starts using SSS fails.
    for cid in SSS:
        _, period, regular, supp, ben, _, _ = next(c for c in CASES if c[0] == cid)
        assert display_net_taxable(period, regular, supp, ben, SSS[cid]) == \
            display_net_taxable(period, regular, supp, ben, 0), cid

    # The annual statute column must be the verified model, not a copy of it.
    # The four payroll-period tables against the regulation, and their bases
    # recomputed from the band below rather than trusted as transcribed.
    annex_problems = annex_e_mismatches() + base_errors() + rr_text_mismatches()
    if annex_problems:
        for p in annex_problems:
            print(f"ANNEX E {p}")
        sys.exit("period tables no longer match RR 11-2018 Annex E")

    # The same twenty bases in two publications that are not the annex file.
    reprint_problems = reprint_mismatches()
    if reprint_problems:
        for p in reprint_problems:
            print(f"REPRINT {p}")
        sys.exit("period tables no longer match the independent reprints")

    # The other tranche, against the regulation body rather than another copy.
    annex_d_problems = annex_d_mismatches()
    if annex_d_problems:
        for p in annex_d_problems:
            print(f"ANNEX D {p}")
        sys.exit("2018 Annex D no longer matches RR 11-2018's illustrations")
    drift = annex_d_drift()

    sweep = (list(range(0, 900_000_00, 7_777)) +
             [250_000_00 - 1, 250_000_00, 250_000_00 + 1,
              400_000_00 - 1, 400_000_00, 400_000_00 + 1,
              800_000_00 - 1, 800_000_00, 800_000_00 + 1,
              2_000_000_00 - 1, 2_000_000_00, 2_000_000_00 + 1,
              8_000_000_00 - 1, 8_000_000_00, 8_000_000_00 + 1,
              25_000_000_00, 900_000_000_00])
    for t in sweep:
        assert statute_tax("annual", t) == bracket_tax(t), t

    DATA.mkdir(exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    matches = [r for r in rows if r["verdict"] == "match"]
    differs = [r for r in rows if r["verdict"] != "match"]
    print(f"cases {len(rows)}  match {len(matches)}  differ {len(differs)}")
    print(f"replay reproduces the live script on {len(OBSERVED)} observed cases")
    print(f"display reproduces the live form on {len(OBSERVED_DISPLAY)} observed cases")
    print(f"annual statute column == bracketTax on {len(sweep)} points")
    print(f"four period tables == RR 11-2018 Annex E on "
          f"{sum(len(r) for r in ANNEX_E.values())} bands, bases recomputed")
    print(f"RR 11-2018 text: annual schedule matches, and "
          f"{sum(len(v) for v in RR_TEXT_FLOORS.values())} illustrated floors "
          f"are floors here")
    print(f"independent reprints of the 2023 table "
          f"({len(REPRINTS)} sources) agree on "
          f"{sum(len(r) for r in BIR_WT_PAGE_2023.values())} bands")
    print(f"2018 Annex D: RR 11-2018's illustrations print "
          f"{sum(len(v) for v in RR_ILLUSTRATIONS.values())} of its bases and "
          f"all match the transcription; floors are Annex E's")
    print(f"2018 Annex D: {len(drift)} of "
          f"{sum(len(r) - 1 for r in ANNEX_D.values())} bases are rounded, "
          f"not the tax accumulated at their floor "
          f"(largest P{max((abs(d) for *_, d in drift), default=0) / 100:.2f})")
    print()
    print(f"{'case':<32}{'period':<14}{'BIR':>14}{'statute':>14}{'diff':>14}")
    for r in differs:
        print(f"{r['case_id']:<32}{r['period']:<14}"
              f"{r['bir_centavos'] / 100:>14,.2f}"
              f"{r['statute_centavos'] / 100:>14,.2f}"
              f"{r['diff_centavos'] / 100:>+14,.2f}")
    print()
    for defect in ("daily_zero_branch", "supp_bracket", "float"):
        rs = [r for r in rows if r["defect"] == defect]
        n_diff = sum(1 for r in rs if r["verdict"] != "match")
        over = max((r["diff_centavos"] for r in rs), default=0)
        under = min((r["diff_centavos"] for r in rs), default=0)
        print(f"{defect:<20} cases {len(rs):>2}  differ {n_diff:>2}  "
              f"worst over {over / 100:>+11,.2f}  worst under {under / 100:>+11,.2f}")

    print()
    print("finding C: the SSS box, the same salary entered two ways")
    for plain, boxed, netted in (
            ("monthly_30000", "monthly_30000_sss_1350", "monthly_28650_sss_reading"),
            ("annual_400000", "annual_400k_sss_10k", "annual_390k_net_of_sss")):
        p = next(r for r in rows if r["case_id"] == plain)
        b = next(r for r in rows if r["case_id"] == boxed)
        n = next(r for r in rows if r["case_id"] == netted)
        print(f"  {plain:<26} no box      "
              f"display {p['display_net_taxable_centavos'] / 100:>12,.2f}  "
              f"tax {p['bir_centavos'] / 100:>11,.2f}")
        print(f"  {boxed:<26} box filled  "
              f"display {b['display_net_taxable_centavos'] / 100:>12,.2f}  "
              f"tax {b['bir_centavos'] / 100:>11,.2f}")
        print(f"  {netted:<26} netted      "
              f"display {n['display_net_taxable_centavos'] / 100:>12,.2f}  "
              f"tax {n['bir_centavos'] / 100:>11,.2f}  "
              f"spread {n['bir_centavos'] / 100 - b['bir_centavos'] / 100:+,.2f}")
    print(f"\nresults -> {OUT}")


if __name__ == "__main__":
    main()
