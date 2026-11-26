# BACKUP MANIFEST

Everything from this project folder is preserved in **two places**: the git
repository, and a GitHub Release for the large binary directories that git
cannot hold (GitHub caps a single git file at 100 MB).

| | Location | Size | What |
|---|---|---|---|
| **1** | `git clone` of this repo | ~44 MB, 343 files | All source, proofs, papers, data, configs, and full history of the 3 nested repos |
| **2** | [Release `backup-2026-11-26`](https://github.com/aaronher1030-glitch/Lean-Formalization-Tax-code-of-the-Philippines/releases/tag/backup-2026-11-26) | ~883 MB | `tools-lean-4.35.0-windows.zip` (857 MB) + `bettergovtarlacph-node_modules.zip` (26 MB) |

## Get it all back on a new machine

```bash
git clone https://github.com/aaronher1030-glitch/Lean-Formalization-Tax-code-of-the-Philippines.git
cd Lean-Formalization-Tax-code-of-the-Philippines

# large directories (needs the GitHub CLI: https://cli.github.com)
gh release download backup-2026-11-26
Expand-Archive tools-lean-4.35.0-windows.zip -DestinationPath tools\lean\dist
Expand-Archive bettergovtarlacph-node_modules.zip -DestinationPath bettergovtarlacph-publish
```

Without `gh`, download both files manually from the Releases page and unzip as above.

## Map of the repository

| Path | Contents |
|---|---|
| `lean/` | Lean 4 formalization of the NIRC: `TaxSchedule`, `Tiers`, `Loopholes`, `Certificate`, `Opt8`, `GovernanceDemo` |
| `tools/` | Python harness, benchmark generators, findings/loophole analysis, figure + docx builders |
| `data/` | NIRC section index, benchmark cases, results, per-engine certificates, LLM raw runs |
| `docs/` | Spec review packet |
| `figures/` | Plots |
| `preview/`, `previews/`, `preview_paper/` | Rendered page previews of the papers |
| `msp/` | MSPR3-2026 abstract submissions, templates, plans |
| `ph-tax-code-lean/` | Self-contained project snapshot: lean, data, paper, docs, tools, CI config |
| `bettergovtarlacph-publish/` | Better Concepcion web project source + built `dist/` |
| `discord-mcp-lite/` | Discord MCP server |
| `_git-bundles/` | Complete git history of the three nested repos (`.bundle` files) + restore guide |
| `*.md` (root) | Papers and research notes: `Verified_Core_Tax_Governance_PH`, `Feasibility_Study_Lean_Governance_PH`, `DEEP_RESEARCH_*`, `REVIEWER_RED_TEAM`, `FINDINGS`, `LOOPHOLE_FINDINGS`, `OVERVIEW_AND_BETTERGOV_PROPOSAL` |
| `*.pdf`, `*.docx` (root) | Rendered versions of the papers |
| `paper-check-page-1[4-6].png` | Page proofs |

## Deliberately not stored (all regenerable in one command)

| Excluded | Why | Rebuild |
|---|---|---|
| `*.olean`, `*.ilean` | Lean build output, derived 1:1 from the committed `.lean` sources | `bash lean/run_demo.sh` |
| `tools/__pycache__/` | Python bytecode cache | automatic |
| `bettergovtarlacph-publish/_edge_profile/` | Local Edge browser profile (cookies/cache) | automatic |
| `bettergovtarlacph-publish/_visual_check/` | Throwaway screenshot scratch | not needed |
| `target/logs/` | Runtime log | not needed |
| `_archives/` | Local staging for the release zips | `gh release download` |

## Integrity checks

```bash
git bundle verify _git-bundles/ph-tax-code-lean.bundle   # history intact
git log --oneline | wc -l                                 # commit count
```
