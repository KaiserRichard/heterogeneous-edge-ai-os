# Written course report

Submit `main.pdf`. Edit the five cover macros near the top of `main.tex` to fill student names, IDs and lecturer.

From the repository root:

```sh
submission/report/build.sh
```

Requires Python 3, XeLaTeX/latexmk, macOS Swift/PDFKit, Avenir Next and Menlo. The renderer is the shared main-project `slides/render.swift`; Swift's module cache stays inside this folder. No image generation is needed (`image-prompts/NEEDS.md`).

- `main.tex`: A4, 11pt article; 20 main pages and four appendix pages.
- `generate_evidence.py`: read-only extraction of retained summaries/raw records; writes `generated/*.tex` and SHA-256 manifest.
- `generated/source-manifest.json`: exact inputs for result tables.
- `build.log`: last XeLaTeX build output.
- `preview/page-*.png`: full-size rendered review pages.
- `REVIEW_LOG.md`: defects, fixes, final visual and evidence review.

The report preserves v1 measurement scope, v2 missing-evidence limits, excluded hardware runs and the unflashed status of final firmware review fixes. Report generation does not rerun hardware experiments.
