#!/usr/bin/env bash
# Builder/reviewer loop for the slide deck, using several Codex accounts.
# Usage: slides/review_loop.sh [max_rounds]   (run from the repo root, on the Mac)
# Builder and reviewer always use different accounts; an account that hits its usage limit is skipped.
set -u
cd "$(git rev-parse --show-toplevel)"
MAX=${1:-4}
ACCOUNTS=(d e f g a b c i)
mkdir -p slides/review
log() { echo "[$(date +%H:%M:%S)] $*" | tee -a slides/review/loop.log; }

next_idx=0
run_codex() { # $1 = role, $2 = prompt; tries accounts in rotation until one works
  local role=$1 prompt=$2 tries=0
  while [ $tries -lt ${#ACCOUNTS[@]} ]; do
    local acc=${ACCOUNTS[$next_idx]}; next_idx=$(( (next_idx + 1) % ${#ACCOUNTS[@]} ))
    tries=$((tries + 1))
    [ -d "$HOME/.codex-$acc" ] || continue
    log "$role on account $acc"
    local out; out=$(mktemp)
    CODEX_HOME="$HOME/.codex-$acc" codex exec --sandbox workspace-write --skip-git-repo-check \
      -C "$PWD" "$prompt" </dev/null >"$out" 2>&1
    local rc=$?
    if grep -q 'hit your usage limit' "$out" && ! grep -q 'tokens used' "$out"; then
      log "$role: account $acc out of quota, trying next"; continue
    fi
    cat "$out" >> "slides/review/codex-$role.log"
    [ $rc -eq 0 ] && return 0
    log "$role: account $acc exited $rc, trying next"
  done
  log "$role: no account succeeded"; return 1
}

for n in $(seq 1 "$MAX"); do
  log "=== round $n: builder ==="
  run_codex builder "Read slides/LAYOUT_BRIEF.md and follow it exactly. This is round $n. If slides/review/latest.md exists, fix every defect in it first. Write your changelog to slides/review/builder-round-$n.md." || exit 1
  log "=== round $n: reviewer ==="
  rm -f slides/review/latest.md
  run_codex reviewer "Read slides/REVIEWER_BRIEF.md and follow it exactly. This is round $n; write slides/review/latest.md and slides/review/round-$n.md. Do not edit main.tex." || exit 1
  head -1 slides/review/latest.md 2>/dev/null | tee -a slides/review/loop.log
  git add slides/main.tex slides/review slides/images 2>/dev/null
  git commit -qm "Slides layout pass round $n" && git push -q origin HEAD 2>/dev/null
  if head -1 slides/review/latest.md 2>/dev/null | grep -q 'VERDICT: PASS'; then
    log "PASS after round $n"; exit 0
  fi
done
log "Stopped after $MAX rounds without PASS; see slides/review/latest.md"
