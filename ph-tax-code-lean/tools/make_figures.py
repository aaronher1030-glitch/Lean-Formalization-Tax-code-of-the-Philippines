# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams["font.family"] = "Calibri"
NAVY, BLUE, GRAY, RED, GREEN = "#1F3864", "#2E5496", "#555F6D", "#A33A3A", "#2F6B3A"


def box(ax, x, y, w, h, title, body, fc, ec, tc="white", bc=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.018",
                                fc=fc, ec=ec, lw=1.4))
    ax.text(x + w / 2, y + h - 0.045, title, ha="center", va="top", fontsize=11.5,
            fontweight="bold", color=tc)
    ax.text(x + w / 2, y + h - 0.115, body, ha="center", va="top", fontsize=9.2,
            color=bc or tc, linespacing=1.35)


def arrow(ax, a, b, color=NAVY, style="-|>", ls="-"):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=style, mutation_scale=16, lw=1.6,
                                 color=color, linestyle=ls))


def architecture():
    fig, ax = plt.subplots(figsize=(10, 5.2), dpi=200)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

    ax.add_patch(FancyBboxPatch((0.47, 0.05), 0.51, 0.9, boxstyle="round,pad=0.01,rounding_size=0.02",
                                fc="#EAF1FB", ec=NAVY, lw=1.2, ls="--"))
    ax.text(0.725, 0.925, "TRUSTED: spec (human review) + checker (Lean proof)", ha="center", va="top",
            fontsize=10, color=NAVY, fontweight="bold")
    ax.add_patch(FancyBboxPatch((0.02, 0.05), 0.42, 0.9, boxstyle="round,pad=0.01,rounding_size=0.02",
                                fc="#F6F6F6", ec="#B0B0B0", lw=1.0, ls="--"))
    ax.text(0.23, 0.925, "UNTRUSTED: any implementation", ha="center", va="top",
            fontsize=10, color=GRAY, fontweight="bold")

    box(ax, 0.05, 0.56, 0.36, 0.28, "Assessment engine",
        "BIR system, spreadsheet,\nvendor software, or an LLM\n(may be buggy or wrong)",
        "#FFFFFF", "#8A8A8A", tc="#222222", bc=GRAY)
    box(ax, 0.05, 0.19, 0.36, 0.28, "Certificate (the explanation)",
        "one line per bracket: base, amount\nincome tax = sum of lines\nsurcharge, interest, total due",
        "#FFFFFF", "#8A8A8A", tc="#222222", bc=GRAY)
    arrow(ax, (0.23, 0.56), (0.23, 0.475), color=GRAY)
    ax.text(0.245, 0.517, "emits", fontsize=9, color=GRAY, va="center")

    box(ax, 0.52, 0.56, 0.42, 0.28, "Statute specification",
        "bracketTax  (TRAIN schedule, 2023+)\nsurcharge 25%,  interest 12% p.a.\nabout 15 lines of Lean",
        NAVY, NAVY)
    box(ax, 0.52, 0.19, 0.42, 0.28, "check  (7 lines)",
        "lines use the statute's brackets?\nevery line's arithmetic correct?\ntotals add up?",
        BLUE, BLUE)
    arrow(ax, (0.73, 0.56), (0.73, 0.475))
    ax.text(0.745, 0.517, "proved: sound + complete", fontsize=9, color=NAVY,
            va="center", fontweight="bold")
    arrow(ax, (0.41, 0.33), (0.52, 0.33), color=GRAY)

    ax.text(0.73, 0.155, "ACCEPT: total = statutory liability", fontsize=9.6, color=GREEN,
            ha="center", va="top", fontweight="bold")
    ax.text(0.73, 0.11, "REJECT: some line or total disagrees", fontsize=9.6, color=RED,
            ha="center", va="top", fontweight="bold")
    fig.savefig("figures/fig1_certificate_architecture.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def bracket_tax(t):
    s = lambda lo, hi: max(0, min(t - lo, hi - lo))
    return (s(25000000, 40000000) * 15 // 100 + s(40000000, 80000000) * 20 // 100
            + s(80000000, 200000000) * 25 // 100 + s(200000000, 800000000) * 30 // 100
            + max(0, t - 800000000) * 35 // 100)


def schedule():
    checked = {0: 0, 10000000: 0, 25000000: 0, 25000001: 0, 30000000: 750000, 40000000: 2250000,
               45000000: 3250000, 50000000: 4250000, 80000000: 10250000, 90000000: 12750000,
               100000000: 15250000, 150000000: 27750000, 200000000: 40250000, 250000000: 55250000,
               400000000: 100250000, 800000000: 220250000, 850000000: 237750000,
               900000000: 255250000, 1000000000: 290250000, 2000000000: 640250000}
    for k, v in checked.items():
        assert bracket_tax(k) == v, (k, v, bracket_tax(k))
    xs = [int(1e7 * (10 ** (i / 400))) for i in range(0, 1201)]
    pts = {k: v for k, v in checked.items() if k > 0}
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.9), dpi=200)
    xa = [x for x in xs if x <= 2000000000]
    a1.plot([x / 1e8 for x in xa], [bracket_tax(x) / 1e8 for x in xa], color=NAVY, lw=1.8)
    a1.scatter([k / 1e8 for k in pts], [v / 1e8 for v in pts.values()], s=22,
               color="white", edgecolor=RED, zorder=3, lw=1.4,
               label="kernel-checked values (19 of 20; income 0 off-axis)")
    a1.set_xscale("log")
    for th in (0.25, 0.4, 0.8, 2, 8):
        a1.axvline(th, color="#C9D2E3", lw=0.8, zorder=0)
        a2.axvline(th, color="#C9D2E3", lw=0.8, zorder=0)
    a1.set_xlabel("Taxable income (million PHP, log scale)"); a1.set_ylabel("Income tax (million PHP)")
    a1.set_title("A. Tax owed under the formal schedule", fontsize=11, color=NAVY, loc="left")
    a1.legend(frameon=False, fontsize=8.6, loc="upper left")
    a2.plot([x / 1e8 for x in xs], [100 * bracket_tax(x) / x for x in xs], color=BLUE, lw=1.8,
            label="effective (average) rate")
    marg = [(0.1, 0.25, 0), (0.25, 0.4, 15), (0.4, 0.8, 20), (0.8, 2, 25), (2, 8, 30), (8, 100, 35)]
    for lo, hi, r in marg:
        a2.hlines(r, lo, hi, color=GRAY, lw=1.1, linestyles="--")
    a2.text(0.105, 31.5, "marginal rate (dashed)", fontsize=8.6, color=GRAY)
    a2.set_xscale("log"); a2.set_xlim(0.1, 100); a2.set_ylim(0, 38)
    a2.set_xlabel("Taxable income (million PHP, log scale)"); a2.set_ylabel("Percent")
    a2.set_title("B. Effective rate stays below the marginal rate", fontsize=11, color=NAVY, loc="left")
    a2.legend(frameon=False, fontsize=9, loc="lower right")
    from matplotlib.ticker import FixedLocator, FixedFormatter, NullLocator
    for a, ticks in ((a1, [0.1, 0.25, 0.4, 0.8, 2, 8, 20]), (a2, [0.1, 0.25, 0.4, 0.8, 2, 8, 20, 100])):
        a.xaxis.set_major_locator(FixedLocator(ticks))
        a.xaxis.set_major_formatter(FixedFormatter([f"{t:g}" for t in ticks]))
        a.xaxis.set_minor_locator(NullLocator())
        a.spines[["top", "right"]].set_visible(False)
        a.tick_params(labelsize=9)
    fig.tight_layout()
    fig.savefig("figures/fig2_schedule.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


architecture()
schedule()
print("ok")
