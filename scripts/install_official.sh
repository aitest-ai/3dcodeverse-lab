#!/usr/bin/env bash
# Install OFFICIAL Harness from the owner's mirrored snapshot (or original upstream).
# This performs third-party package installs; review before executing.
set -euo pipefail

SOURCE_URL="https://github.com/aitest-ai/3dcodeverse-lab.git"
SOURCE_BRANCH="upstream-3dcodeverse"
if [[ "${1:-}" == "--official" ]]; then
  SOURCE_URL="https://github.com/gaoypeng/3dcodeverse.git"
  SOURCE_BRANCH="main"
elif [[ $# -gt 0 ]]; then
  echo "Usage: bash scripts/install_official.sh [--official]" >&2; exit 2
fi

for program in git python3.13 node npm; do
  command -v "$program" >/dev/null 2>&1 || { echo "Missing: $program" >&2; exit 1; }
done
DIR="official-3dcodeverse"
if [[ -e "$DIR" ]]; then
  echo "Refusing to overwrite $DIR; rename or remove it first." >&2; exit 1
fi

git clone --depth 1 --branch "$SOURCE_BRANCH" "$SOURCE_URL" "$DIR"
cd "$DIR"
printf 'Source commit: %s\n' "$(git rev-parse HEAD)"
python3.13 -m venv .venv
source .venv/bin/activate
bash harness/setup.sh
# The doctor's own output should be reviewed for WARN/FAIL; package import success is not sufficient.
3dcodeverse doctor
echo "Harness installation attempted. AI model/CLI credentials are separate; no AI generation run performed."
