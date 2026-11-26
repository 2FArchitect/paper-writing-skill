# Rule files (`rules/*.yml`)

One file per rule ID. The Markdown twin (`<ID>-*.md`) is the source the YAML was filled from and
stays until the compile script reads the YAML; nothing in a YAML file is new text, every sentence
has a `source` line.

Top level: rule metadata, then one block per actor. Actor blocks all have the same shape. Any top-level
key that is not a metadata key is an actor; the compiler builds a view for every actor name it finds,
so a new actor is a new key in a rule file, nothing else. An actor that is absent is not shown that
rule and not asked about it; do not write empty actor blocks.

```yaml
id: M5                     # the existing ID
title: Banned adjectives
severity: MAJOR            # only when the source states one (S rules); reviewers grade findings themselves
applies:                   # the rule's scope, only when the source says so; it is the rule's, not an actor's
  sections: [evaluation]   # section kinds: intro, design, evaluation, related-work, abstract, conclusion, ...
  register: []             # craft_reference registers, when a rule is relaxed for one
  venue: []
merged: [CE4]              # IDs whose text now lives in this file (so old findings and question lists still resolve)
source:                    # file:line of every sentence used
  - rules/M5-banned-adjectives.md
exceptions: []             # the rule's own exception clauses; a property of the rule, shared by every actor
grep:                      # shared tool; the author runs it in the audit, the writing reviewer as question M
  - {pattern: '...', flags: i, action: replace, hint: '...'}
grep_hits_only: true       # reviewers are asked this rule only when its greps match the text under review
notes:                     # things noticed, not changed

author:                    # the Claude session writing the paper
  text: >                  # one block of prose, or
  questions: []            #   a list, one question each (checklists)
  why: >
  examples: {good: [], bad: []}
writing:                   # reviewer-writing (how it reads); facts: reviewer-facts; logic: the logic reviewer; ...
```

Metadata keys: `id`, `title`, `severity`, `applies`, `merged`, `source`, `exceptions`, `grep`,
`grep_hits_only`, `notes`. Everything else is an actor.

## One rule, one file

Two texts that check the same thing are one rule, whatever IDs they carried: the check goes in the
file of the rule it checks, under the actor that performs it, and the absorbed ID goes in `merged`
(for example the checklist group CE4 is the reviewer's form of P8, so P8 carries its questions and
`merged: [CE4]`). Texts that are about different things stay separate, even when they are close
(S1 define before use, S3 spell out acronyms, S6 gloss once are three rules). There is no field for
"related"; an overlap is either a merge or nothing.

## Including a rule in a Markdown file

`scripts/expand_includes.py` (run by `setup`) renders a rule where a Markdown file has one of these lines:

```
@../rules/M5-banned-adjectives.yml             the author's block
@../rules/M5-banned-adjectives.yml#writing     one actor's block
@../rules/M5-banned-adjectives.yml#reviewers   every actor except the author, in file order
@@grep-script                                  a bash block of every text grep in rules/ (the Mechanical Gate's Part C)
```

A rule with no block for the requested actor renders nothing. The compiler adds no heading; a file that
wants one writes it on the line above the include. Render order inside a block: text,
`- [ ] question` lines, why, exceptions, examples (`- ✗ bad → ✓ good` pairs when the lists are the same length, otherwise two lines).
The Markdown twins of converted rules were deleted on 2026-11-26; `source` lines that name them point at
git history. `scripts/check_rules.py` validates every file (run it before `setup`).

## How the fields are used

- `text` / `questions` is what the actor reads or is asked. `why`, `exceptions` and `examples` are
  kept as fields rather than folded into the text because each has a second use: `why` can be
  checked for presence (every rule should have one) and dropped from a compact view; `exceptions`
  is printed by the grep script beside each hit; `examples` double as tests for `grep` (every `bad`
  example must match, no `good` example may). The renderer composes them into prose for the actor:
  text, then the why, then exceptions, then examples.
- A rule applies to a section kind for every actor, so `applies` is top level. Two actors with
  different scopes means two rules.
- Which mode shows a rule to the author is not in the rule file: the mode files (`modes/*.md`)
  list rules in order with `@rules/<ID>-*.yml` lines, as they list Markdown fragments. The mode file
  is the only place that decides membership and order.
- The reviewers' questions are not in the mode files: `scripts/review.py` asks each reviewer every rule
  that has its actor block (`facts`, `writing`), filtered by `applies.sections`, one rule per question.
  For the writing reviewer `review.py` runs the rule's
  text greps on the text under review and puts each match (line number, about ten words either side) in the question; with no matches the
  rule is asked without them, or skipped when the rule has `grep_hits_only: true`.
- A project can override a rule: `<project>/.paper-writing/rules/<ID>-*.yml` with the same `id`
  replaces the skill's file for that project (`scripts/review.py` reads them; the install-time mode files do not). A project file with no actor blocks switches the rule
  off. Project-only rules use the same format.
