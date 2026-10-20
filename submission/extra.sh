#!/bin/zsh
# usage: extra.sh <letter> <brief> <folder> <builder> <reviewer> <round>
X=$1; BRIEF=$2; DIR=$3; B=$4; R=$5; n=$6
cd "$(dirname "$0")/.."; L=submission/logs; log() { echo "$(date +%T) $X $1" >> $L/progress.log; }
cx() { for t in 1 2 3; do CODEX_HOME="$HOME/.codex-$1" codex exec --sandbox workspace-write --skip-git-repo-check -o $L/$X-$2.last "$3" > $L/$X-$2.log 2>&1 < /dev/null; rc=$?; grep -q "at capacity" $L/$X-$2.log && { sleep 60; continue; }; break; done; log "$2 codex-$1 rc=$rc"; }
cx $R review$n "You are an independent reviewer of submission/$DIR (brief: submission/briefs/$BRIEF, rules: submission/briefs/COMMON.md). Do NOT edit any file except submission/$DIR/REVIEW_$n.md. Build it into /tmp/review_$X$n (latexmk -outdir), render and inspect every page at full size, and check every number and claim against results/ and docs/STAGE_REPORT.md. Write REVIEW_$n.md: numbered defects with page and severity (BLOCKER/MAJOR/MINOR), plus a line 'Verdict: PASS' or 'Verdict: FAIL'."
grep -q -E "Verdict:? *\**PASS" submission/$DIR/REVIEW_$n.md || cx $B fix$n "Read submission/briefs/$BRIEF and submission/$DIR/REVIEW_$n.md. Fix every BLOCKER and MAJOR and the cheap MINORs in submission/$DIR, rebuild, re-render, re-inspect changed pages, append the round to REVIEW_LOG.md."
log "EXTRA$n DONE"
