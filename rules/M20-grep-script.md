## Part C — The grep script (RUN THIS; do not eyeball)

```bash
# Run each grep against the paper's text.

# ── M1: Em-dashes (must return nothing) ──
grep -rn -- '---' ; grep -rn $'—\|–'

# ── M11: PASSIVE VOICE (also runs in the base per-edit gate). Over-catches on purpose. ──
grep -rnoE "\b(is|are|was|were|be|been|being)\s+([a-z]+ed|done|made|shown|given|taken|held|built|drawn|chosen|written|known|found|seen|set|put|sent|kept|met|run|used|based)\b"

# ── M2: Antithesis / negation-as-rhetoric (inspect each; "not" branch matches digit/letter/\macro) ──
grep -rnoE ",? not [0-9A-Za-z\\]|not only .* but|rather than|less .* than|is the point|whatever it is|means nothing|more than just|not in competition with|on one hand|on the other hand"

# ── M3/M4/M8/M9: editorializing, intensifiers, grandiose setups, metaphor filler ──
grep -rnoE "in effect|in a sense|at (its|the) (heart|core)|in essence|\btruly\b|\bgenuinely\b|\bindeed\b|\bin fact\b|precisely because|a testament to|the kind of .* that|exactly the kind|is the point|set(s)? .* apart|no (predecessor|one) .* (made|posed)|the key (insight|idea) is|the (machine|engine) that|draw(s)? .* power from|under the hood|where .* meets"

# ── M6: throat-clearing openers ──
grep -rnE "^(Moreover|Furthermore|Additionally|Notably|Importantly|Indeed|Ultimately|Crucially|In turn|That said)"

# ── M5/M16: banned + pompous words ──
grep -rnoiE "\bnovel\b|\bsignificant\b|\bsubstantial\b|\bimpressive\b|\bpromising\b|\bcomprehensive\b|\brobust\b|\bpowerful\b|\bseamless|\bcrucial\b|\bparadigm\b|\bleverag|\butiliz|\bfinaliz|[a-z]+-oriented\b|\bfactor\b|\bfeature[ds]?\b|\bmeaningful\b|\binsightful\b|\bprestigious\b|\bpossess|\bcontact(s|ed|ing)?\b|\bcurrently\b|\bimpact(s|ed|ing)?\b"

# ── M10: vague-mechanism / futurist hype verbs ──
grep -rnoiE "promises to|stands? to|is poised to|opens the door to|is set to|has the potential to|keeps .* from|stands? in the way|\bunlocks?\b"

# ── M17: fancy / figurative verbs (inspect each; keep only precise domain jargon like "amortize") ──
grep -rnoiE "\b(pit(s|ted|ting)?|dispatch(es|ed|ing)?|chip(s|ped|ping)? (away )?at|marshal(s|led|ling)?|orchestrat(e|es|ed|ing)|wrangl(e|es|ed|ing)|harness(es|ed|ing)?|forge[sd]?|weav(e|es|ed|ing)|delv(e|es|ed|ing) into|usher(s|ed)? in|grappl(e|es|ed|ing) with|anew|afresh)\b"

# ── M18: content-free openers ──
grep -rnE "In this (paper|section), we"

# ── M12: needless words / wordiness ──
grep -rnoE "the fact that|the question (as to |of )?whether|as to whether|in order to|there is no doubt but|the reason .* is because|owing to the fact that|in a [a-z]+ manner|is a (subject|man|woman) (that|who)|in the last analysis|along these lines|in terms of|one of the most"

# ── M13: weak qualifiers ──
grep -rnoiE "\b(rather|very|pretty|little|quite|somewhat|fairly|certainly)\b"

# ── M14: coined adverbs / false ordinals ──
grep -rnoiE "\b(thusly|muchly|overly|firstly|secondly|thirdly)\b|[a-z]+wise\b"

# ── M15: exclamation marks ──
grep -rn "!"

# ── Part B: precision pairs (inspect for wrong member) ──
grep -rnoiE "\bcomprised of\b|\bdata is\b|different than|\bvery unique\b|\bdue to\b|\bless (than )?[0-9]"

# ── Term/decomposition drift (see gate_semantic S8/S9): one name per concept ──
#   (a) For each canonical term in the project_context term-map, show every surface form + location,
#       then converge. Replace the list with the paper's real synonym clusters.
for t in "term A" "term A variant" "term B" "term B variant"; do
  echo "== $t =="; grep -rn "$t" | grep -v '^\s*%'; done
#   (b) Decomposition cardinality: do all the "N <noun>" counts agree across sections?
grep -rnoE "\b(three|four|five|six|seven)\b (stages|concerns|axes|requirements|dimensions|systems)"
```

Report the per-category hit counts in the audit summary. "Clean" means every hit fixed or
justified, with the counts shown.
