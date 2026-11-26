#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
LEAN="${LEAN:-../tools/lean/dist/lean-4.35.0-windows/bin/lean.exe}"
export LEAN_PATH="$(pwd -W 2>/dev/null || pwd)"
"$LEAN" -o TaxSchedule.olean TaxSchedule.lean
"$LEAN" TaxScheduleChecks.lean
"$LEAN" -o GovernanceDemo.olean GovernanceDemo.lean
"$LEAN" -o Certificate.olean Certificate.lean
"$LEAN" -o Tiers.olean Tiers.lean
"$LEAN" -o Opt8.olean Opt8.lean
"$LEAN" Loopholes.lean
