## Section Checklists

After generating ANY section draft, Claude MUST also read the corresponding structural checklist and run it:

| Section | Checklist file |
|---|---|
| Introduction | `writing_checklists/intro_questions.md` |
| Evaluation | `writing_checklists/evaluation_questions.md` |
| Design / Method | `writing_checklists/design_questions.md` |
| Related Work | `writing_checklists/related_work_questions.md` |

Flag every violation before presenting the draft. Severity levels: CRITICAL (structural — will cause rejection), MAJOR (visible to reviewers), MINOR (polish-level).
