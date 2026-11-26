## How the author runs a section review

This is the independent review stage of the paper-writing skill (`red_team_protocol.md`) as the
review script runs it. Two reviewer agents, `~/.claude/agents/reviewer-facts.md` and
`~/.claude/agents/reviewer-writing.md`, are asked the skill's and the project's rules one question at
a time by `${CLAUDE_SKILL_DIR}/scripts/review.py` (see "Question IDs"). The agent files say what a reviewer checks, how
it treats your replies, and what the severities mean; this file says what you, the author, do. The
skill's files are in `${CLAUDE_SKILL_DIR}/`, which `review.py` reads.

Terms. A "pass" is one run of both reviewers over the same text with their question lists (together
on Sonnet, one after the other on Opus). A "pair" is the two reviewers of one pass. A "round" is one pass by a fresh pair plus its re-checks.

### Where this differs from the skill

The skill's protocol expects a reviewer spawned with a prompt. Here:

- Reviewers report problems, never fixes. The protocol says the author decides the fix, but
  `SKILL.md`'s "Review / critique this draft" mode gives a rewrite with each finding; not here.
- Reviewers get nothing a reader would not have: no controlling idea, `project_context.md`,
  decisions log, term list, notes, or earlier findings and decisions. Fresh reviewers are not sent the points earlier reviewers accepted.
- You may decline a finding with a reply the reviewer can check in the article, or with the user's
  preference (see "When to involve the user"). The skill's author "fixes every finding"
  (`red_team_protocol.md`; `loop_mode.md` step 4).

### Before a pass

1. Check the text yourself: run `gate_mechanical.md` Part C and fix every unjustified hit, then read
   the section against the author's recurring errors. The recurring errors
   are: widening the user's narrow statement into a broad rule; claiming beyond the evidence
   (unscoped absence claims, one view as "disputed", a pattern stated as "for each"), judged by what
   a fresh reader will conclude; facts or assumptions not from a file, including numbers, defaults,
   section numbers and metadata; weak verification (checking an agent's quotes against its own
   files, trusting a check that could not fail); material that does not serve the argument;
   unreadable phrasing or exact detail where a generalisation belongs; clutter; and fixing a false
   general claim by narrowing its subject until the counterexample falls outside it instead of
   writing what is true across the data. This check applies to every fix too.
2. Rebuild the paper, so the review copy is current.

### Launch a pass

Run both reviewers in parallel, in the background (section 4 shown). On Opus, run them one at a
time.

    python3 ${CLAUDE_SKILL_DIR}/scripts/review.py --project "${CLAUDE_PROJECT_DIR}" \
      --agent reviewer-facts --section 4 --kind evaluation
    python3 ${CLAUDE_SKILL_DIR}/scripts/review.py --project "${CLAUDE_PROJECT_DIR}" \
      --agent reviewer-writing --section 4 --kind evaluation

Sonnet at high effort is the default (`--model`, `--effort`). Reports go to `notes/review-reports/`,
one per reviewer, appended after every answer; the session ID in a report is what `--resume` takes.
Keep notes in `notes/`. The review copy shows figures as rendered images; never offer a figure's data in its
place.

On a new review, `--ask "…"` adds your text to the opening message, for instructions specific to
this review, never for anything a reader would not have. On a resumed review it is your reply (see
"Reply and re-check").

When reviewing the initial Draft 0 of the paper's Introduction, use `--ask` to include a copy of the
paper's planned Section Architecture from project_context.md, as it will need this to know how the
paper will be structured (this is not an exception to the "Reviewers get nothing a reader would not 
have", as the reader of the finished paper WOULD have that information).

### Handle the findings

Wait for both reports and merge them by paragraph before changing anything. The two reviewers often
report on the same paragraph, and fixing one report and then the other makes the text flip-flop.
One decision per paragraph, with every finding on it in view.

For each paragraph with findings, first work out what each finding is really about: read the
paragraph in the compiled article and all the data the finding draws on, not only the slice the
reviewer quoted. Then find out why the passage is there, from the section's notes and
history (its review log and `git log -p`). A finding is usually a task to fix the source of the problem,
not a reason to delete the passage it names.

Then make one decision for the paragraph that keeps the article true and followable while the
passage keeps its job. The usual outcomes, not a closed list:

- A data or method finding takes the triage test once you have read the paragraph and before any
  further investigation or any question to the user: **Does this finding change a printed number by
  more than its stated uncertainty, change a conclusion, or make a printed sentence false? If yes,
  fix it. If no, it is either a limitation sentence or nothing.** In applying it, "no" never means
  a data change, an estimator change, a new flag or a new set of questions for the user, and a
  finding that only
  improves an explanation the article already prints is a "no".
- The text or a value script is wrong: fix the cause; check every number in the fix against the
  script output or source; re-read around it.
- A misreading: clarify, there or where the article sets the point up, or re-arrange the content,
  even moving it to another area of the paper if it helps make the paper better. The clarification
  must land on text that defines the term.
- Not needed: cut it to the cut file and log it with the reason. Whether a passage is needed is what the belonging rules
  ask: `gate_semantic.md` S7 (every paragraph ties to the one thesis) and `gate_semantic.md` S33 (method or validation detail the
  reader does not need to trust the result). Detail a reader needs only to reproduce the work is the
  published package's job; do not write new package text for cut detail.
  Before cutting a passage, read what the next sentence needs from it.
- The finding is wrong and the article shows it: reply (below).

Blindly editing to clear out the findings is the easy way, but it leads to a paper that quickly 
becomes completely unreadable, as small edits are stacked upon small edits without consideration.
RESIST THIS TEMPATATION AT ALL COSTS. Consider each finding carefully to avoid this trap!

A grouping or threshold you introduce must follow from a valid statement, not from where the numbers
fall.

### Reply and re-check

Rebuild, then ask the reviewer that raised the findings to re-read the whole section, not only the
flagged paragraphs, because a fix moves text the finding did not name:

    python3 ${CLAUDE_SKILL_DIR}/scripts/review.py --project "${CLAUDE_PROJECT_DIR}" \
      --agent reviewer-facts --resume <session ID> \
      --report notes/review-reports/<the same report> \
      --ask "I revised §4 and rebuilt. Re-read the whole section in the new review copy …"

Say what changed, by paragraph, and for each declined finding the place in the article that
answers it, or the user's preference that settles it. Never paste changed text, notes or data the
article does not print. If your only argument is one the reader cannot see, the article is
missing something.

Answer the problem found, not the fix hinted at. Argue when you believe you are right and the article shows it. A reviewer that accepts your reply has judged the reply, not the text; the text is still
yours to get right.

A finding that comes back is evidence about the text. One misreading gets a pointer to where the
article makes the point; fresh reviewers repeating a finding means the article does not make the
point well enough, whatever was accepted before. Defending it again will not clear it, and neither
will rewording the same passage again (`USAGE.md`, "Fresh eyes"). Arguing a finding down to MINOR instead of fixing it is the same failure.

### Record

Write each settled decision into the review log of the section the finding concerns,
in the log's existing form, with the facts it rests on, so the next finding on the
same paragraph is checked against the decision instead of re-argued. A finding about another
section's claim goes in that section's log.

After each round, update the section's row in `notes/AUDIT_LEDGER.md` as the skill's `loop_mode.md`
requires: status PENDING, FINDINGS(n) or CLEAN, the grep counts, the last findings, and the rule IDs
each fix addressed. CLEAN needs the closure reviewer's sign-off, not yours. The ledger is what a
later session reads to see where every section stands.

### The loop

Per section: check it yourself, run a pass, handle the findings, and send fixes and replies back to
the reviewers that raised the findings until neither has a CRITICAL or MAJOR open. Then a fresh pair, starting from the
article alone. Repeat until a fresh pair
finds no CRITICAL or MAJOR in its pass, before any re-check. Then the same on Opus (`--model opus`):
if the first Opus pair finds CRITICAL or MAJOR problems, close them and run a second fresh Opus
pair; the section is done when an Opus pair finds none in its pass. A round closes when no CRITICAL
or MAJOR is left open after fixes and replies, not when every finding has been applied.

Two caps, both failure signals, not finish lines: 6 Sonnet rounds, and 2 Opus rounds after the
Sonnet rounds. At either cap, stop and bring the state of the review to the user.

When every section is done, run the closure review S31 requires over the whole article
(`--section all`), with the same process and caps. A per-section review is not asked about
contradictions between sections or a term defined after first use.

If the reviewers replied with critical or major findings, but you decided the findings do not 
require edits to the paper, and the reviewers agree with you, you may consider the round closed.
Any round that applies edits to the paper requires another fresh reviewer.

### When to involve the user

You decide a finding when something checkable settles it: the data, a cited source, the skill's or
journal's rules, or a decision already in a review log. Record it with its reason and
tell the user in one line in your report, so they can veto in batch. Bring it to the user when the
user wanted the passage and nothing
checkable settles the finding, when the fix would change what the article claims or concludes, or
when it would reverse a decision the user recorded. A passage the user did not ask for, with nothing checkable behind it, is
cut and logged; a finding of taste on a supported passage the user did not ask for is yours to
decide. A cut that passes the belonging rules is not a change of claim: cut, log, one line to the
user. When
you bring a question, give the context first: the passage, why it is in the article, the finding, then the options with a
recommendation.

The user's answer is their words, not your summary. The user's words are not turned into rules unless they indicate they should be; a rule made from
them has the exact scope the user stated, not more, and includes the user's reasoning. Never make up
the user's reasoning; if it is not clear from the discussion why the user wants the rule, ask them.

A user preference is a reply, not a question, when the finding is a choice between true wordings or
whether to say something true: tell the reviewer it is the user's preference, and the agent files
let that close the finding. When the finding shows the preferred text is untrue or misleading, bring
it to the user with a recommendation. Check the user's suggestions before acting on them, as
you would a reviewer's.

### Question IDs

Each question is one rule file, `${CLAUDE_SKILL_DIR}/rules/<ID>-*.yml` (format: `rules/SCHEMA.md`),
asked by its ID. A reviewer is asked every rule that has a block for it (`facts` for
reviewer-facts, `writing` for reviewer-writing); a rule whose `applies`
names section kinds is asked only for those kinds (`--kind`). `anything`, always last, asks for any
other problem. `review.py` reads each rule's text from its file at run
time; a reviewer answers a rule that does not fit the section in one line.

The project's own rules are `.paper-writing/rules/*.yml`, in the same format: a file with a skill
rule's `id` replaces that rule for this paper, one with no actor blocks switches it off. What the
project adds to a reviewer's instructions is `.paper-writing/agents/<facts|writing>.md`; when it
exists, `review.py` sends its text in the opening message.

Not asked: S29 and S31, the author's process (one question at a time replaces S29's
lens reviews, giving each rule a reviewer's whole attention in its own turn; the closure review is
S31); A1–A4, which the author checks in the compile log (`gate_artifact.md` Part A).
