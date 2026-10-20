# P: progress and next-steps deck (for the project owner)  -> folder submission/progress/
Read submission/briefs/COMMON.md first.
Audience: the owner, who needs to regain bearings: understand the system as built, the
current state, the tools, and exactly what to do next. Not for the lecturer.
Size: about 25-30 slides, dense but readable, practical.
Contents: 1 one-page system map (what runs where, data/control paths); 2 timeline of what
was built 2026-10-05..13 (branches, PRs, merges: PR #6 release/os-final open, #3-#5
superseded); 3 status board per component: IMPLEMENTED+TESTED (host) / VERIFIED ON RIG /
MEASURED / FLAGGED / NOT DONE; 4 experiments done: what each measured, valid counts,
why runs were flagged (3 A PSU under-voltage, clock-sync RMS under memrate, v2 replay),
what that means; 5 rig: access (Pi over direct Ethernet, no internet, git bundles/wheels),
Nucleo via ST-LINK on the Mac, UART console disabled, logic analyzer; 6 tools catalogue:
every script under tools/, scripts/, analysis/ with one-line purpose and exact command,
where outputs land; 7 known pitfalls (cyclictest policy flags, pkill self-match, PSU,
reading STATE_EVENT reason codes, FREERTOS_REF for worktree builds); 8 open items and next
steps in priority order with a gate for each (rig photo, flash + verify the 11 review
fixes, rerun under v2 rules with a 5 V/5 A PSU, merge PR #6, final submission package);
9 how this leads into the WBR stage (one or two slides, link to the roadmap A-F, no WBR
detail); 10 study pointers (which pages of the long deck and which Obsidian M-lessons
explain each mechanism).
