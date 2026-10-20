#!/bin/zsh
# usage: run.sh <letter> <brief> <folder> <builder> <reviewer>
X=$1; BRIEF=$2; DIR=$3; B=$4; R=$5
cd "$(dirname "$0")/.."; mkdir -p submission/$DIR
L=submission/logs; log() { echo "$(date +%T) $X $1" >> $L/progress.log; }
cx() { CODEX_HOME="$HOME/.codex-$1" codex exec --sandbox workspace-write --skip-git-repo-check -o $L/$X-$2.last "$3" > $L/$X-$2.log 2>&1 < /dev/null; log "$2 codex-$1 rc=$?"; }
cx $B build "Read submission/briefs/$BRIEF and follow it exactly. Write NEEDS.md early. Complete the full build and self-review loop before stopping; finish with a summary."
for n in 1 2; do
  cx $R review$n "You are an independent reviewer of submission/$DIR (brief: submission/briefs/$BRIEF, rules: submission/briefs/COMMON.md). Do NOT edit any file except submission/$DIR/REVIEW_$n.md. Build it into /tmp/review_$X$n (latexmk -outdir), render and inspect every page at full size, and check every number and claim against results/ and docs/STAGE_REPORT.md. Write REVIEW_$n.md: numbered defects with page and severity (BLOCKER/MAJOR/MINOR), plus a verdict PASS or FAIL. Be strict about evidence labels, unsupported claims, readability and story flow."
  grep -q -E "Verdict:? *\**PASS|VERDICT:? *\**PASS" submission/$DIR/REVIEW_$n.md 2>/dev/null && [ $n -eq 2 ] && break
  cx $B fix$n "Read submission/briefs/$BRIEF and submission/$DIR/REVIEW_$n.md. Fix every BLOCKER and MAJOR and the cheap MINORs in submission/$DIR, rebuild, re-render, re-inspect changed pages, append the round to REVIEW_LOG.md. Explain any item you reject."
done
log DONE
