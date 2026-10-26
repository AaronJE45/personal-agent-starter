# Course support sidebar blueprint

This is a content/configuration blueprint, not an implemented course website.
[sidebar.json](sidebar.json) provides stable IDs for seven modules, 35 lessons,
and the support resources. It does not contain MCQ questions, answers, or learner
records. The course website must supply those and persist progress per account.

## Always visible

- “Continue learning” linking to the current lesson.
- “12 of 35 lessons complete — 34%” (example, not a saved progress record).
- Expandable modules showing complete / in-progress / not-started lesson states.
- Setup guides, build guide, troubleshooting/restart, free-tier/token guide.
- Reference solution for the current module.
- Optional link to the learner's own GitHub repository.

## Completion contract

Opening a lesson sets it in progress. Only a correct end-of-lesson MCQ marks it
complete. Wrong: “Incorrect. Try again.” Correct: “Correct.” Unlimited retries;
no penalty. Reviewing a completed lesson does not remove completion.
A module is complete when its five lessons are complete. Overall percentage is
completed lessons / 35 × 100, rounded for display. Save progress against the site
account; do not infer it from GitHub commits, solution files, or local code.

There is no personalised support, code grader, repository webhook, Actions badge,
or live WhatsApp verification. Project exercises use written expected results
and learner self-checks. Metana handles certificates separately based on course
completion; MCQs do not prove a working submitted project.
