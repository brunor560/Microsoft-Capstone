# Templates

Supplied course templates are kept unchanged in `originals/`, copied from the instructor-provided Templates folder on October 14, 2026. Markdown equivalents in `markdown/` give agents the structure and instructions. Template examples and placeholders are not project facts. Word and PowerPoint exports should keep the original template's styles and fonts.

| Template | Original | Supplied filename | SHA-256 | Markdown equivalent |
| --- | --- | --- | --- | --- |
| Detailed Design Document | [ddd_template.docx](originals/ddd_template.docx) | `Detailed_Design_Doc_Template.docx` | `f2b96e29a76e63fbb33703ac0d3b56b2ec0ec8553be674c5213195e3852e8ca3` | [ddd_template.md](markdown/ddd_template.md) |
| System Requirements Specification | [srs_template.docx](originals/srs_template.docx) | `SRS_Doc_Template.docx` | `361d450569c159d44ddf1b449b5e0d334f2fcc2634c6a4e59c4ccc282c474dbf` | [srs_template.md](markdown/srs_template.md) |
| Status report | [status_report_template.doc](originals/status_report_template.doc) | `StatusReport_Template.doc` | `3e3d3a7092cca18142c0ab22d3bfb4f2d040fa3fa2437a4d1d6e3709b01491ca` | [status_report_template.md](markdown/status_report_template.md) |
| Initial presentation (slides) | [initial_presentation_template.ppt](originals/initial_presentation_template.ppt) | `Week3_PPT_Template.ppt` | `df98b7f9386c78a576d0539417a3a052df36ec60b98c95c3f8f1bcb1583e96f1` | None |
| SRS presentation (slides) | [srs_presentation_template.ppt](originals/srs_presentation_template.ppt) | `SRS_PPT_Template.ppt` | `a2dfd6139a9b3e46d9fd6bc844cc01127f772c11df2920316fcfc8e614f57776` | None |
| Design review presentation (slides) | [design_review_presentation_template.ppt](originals/design_review_presentation_template.ppt) | `DesignReview_PPT_ Template.ppt` | `90401ed332feeae8bba8079ad77f948a0792c0b467e6ee6696fc2ec314105add` | None |
| Final presentation (slides) | [final_presentation_template.ppt](originals/final_presentation_template.ppt) | `Final_PPT_Template.ppt` | `574e4937779408c63f94810539efd739e14c14eeb26279985290742f92bb1bb8` | None |
| Timesheet | Not supplied | | | None |

Notes:

- The four `.ppt` files are binary PowerPoint templates. Only their title slides were identified (for example "Detailed Architectural Review for Senior Project"), so no Markdown equivalents were written. Open the originals in PowerPoint when preparing a presentation.
- The status report as supplied was filled in with a project name, week number, and member list. The Markdown equivalent uses placeholders for those.
- The SRS template's own example content is not carried into the Markdown equivalent.
- The SRS template marks the HLA section "remove after week 5". This matches the course rule in `AGENTS.md` that the HLA belongs in the DDD.
- Team-written change-summary and issue forms were removed in the October 14 consolidation; this folder holds course templates only.

## Adding a template

1. Copy the unchanged original into `originals/` with a descriptive filename and record its supplied name and SHA-256 above.
2. For document templates, add a Markdown equivalent in `markdown/` that keeps headings, required sections, instructional notes, and table fields. Label any adaptation.
3. Check whether current sources need structural changes, and note any gap in `TODO.md` or the matching `todo/` file.
