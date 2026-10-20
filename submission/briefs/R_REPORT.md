# R: written course report (PDF submitted)  -> folder submission/report/
Read submission/briefs/COMMON.md first.
Format: LaTeX article (XeLaTeX), A4, 11pt, two-level numbered sections, about 15-20 pages
plus appendices. Title page with project title, course "Operating Systems", team
placeholders (\newcommand for names/IDs/lecturer so the owner fills them).
Structure: Abstract; 1 Introduction (motivation, problem, RQs, contributions);
2 Background (Linux scheduling and contention, IPC/buffering and AoI, clocks, RTOS/FreeRTOS,
Simplex-style supervision - cite only verified sources already in the repo research notes);
3 System design (architecture, ownership, protocol v1/v2, Linux pipeline, supervisor state
machine, clock sync); 4 Implementation (modules, files, threads, scheduling config, firmware
tasks/ISR/DMA, tools); 5 Evaluation method (rig, profiles, loads, metrics, validity rules
v1/v2, repeats); 6 Results (each experiment: figure/table from data + interpretation + label);
7 Discussion and limitations; 8 Conclusion and future work; References;
Appendix A claim-to-evidence table (claim, commit, config, raw run path, figure);
Appendix B how to reproduce (commands); Appendix C OS-concept mapping to course topics.
Base the text on docs/STAGE_REPORT.md but rewrite as a polished academic report.
