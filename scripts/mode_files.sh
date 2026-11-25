#!/usr/bin/env bash
# Print the files a /paper-writing session must read, in order.
#
# Usage (from SKILL.md, run by Claude Code while the skill loads):
#   mode_files.sh <project dir> [mode] [step words...]
#
# Only files that exist are listed: the skill's files (modes/ in this script's skill folder) and the
# paper's own additions (<project dir>/.paper-writing/). For draft and rewrite the step is a section
# name; a common other name (results, method, ...) also finds the file for that kind of section.
# Always exits 0: a failing command would stop the whole skill from loading.
# Plain bash 3.2 (the macOS default): no associative arrays.

SKILL="$(cd "$(dirname "$0")/.." 2>/dev/null && pwd)"
MODES_DIR="$SKILL/modes"
MODES="story brainstorm architecture draft rewrite integrate compress submit-check critique respond figure loop"

slug() { printf '%s' "$*" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//'; }

kind_of() {  # other names for the kinds of section the skill has files for
  case "$1" in
    intro|introduction) echo intro ;;
    design|method|methods|methodology|approach|system) echo design ;;
    evaluation|results|experiments|findings) echo evaluation ;;
    related-work|prior-work|background-and-related-work) echo related-work ;;
    *) echo "$1" ;;
  esac
}

main() {
  if [ $# -eq 0 ]; then echo "(mode_files.sh was called without a project folder)"; return; fi
  local project="$1/.paper-writing"; shift
  local mode step; mode="$(slug "$1")"; shift 2>/dev/null; step="$(slug "$*")"

  if [ -z "$mode" ]; then
    echo "No mode was given. Pick one from the table below if the user's request makes it obvious, or ask the user; then invoke this skill again as \`/paper-writing <mode> [step]\`."
    return
  fi
  case " $MODES " in *" $mode "*) ;; *)
    echo "Unknown mode \`$mode\`. Modes: $MODES. Ask the user which one they meant, then invoke this skill again with it."
    return ;; esac
  if { [ "$mode" = draft ] || [ "$mode" = rewrite ]; } && [ -z "$step" ]; then
    echo "\`$mode\` needs a section, for example \`/paper-writing $mode intro\`. Ask the user which section, then invoke this skill again with it."
    return
  fi
  if [ "$mode" = figure ]; then case "$step" in spec|generate|critique) ;; *)
    echo "\`figure\` needs a step: \`spec\`, \`generate\` or \`critique\`. Ask the user which one, then invoke this skill again with it."
    return ;; esac
  fi

  # Names for the step-specific files: the section's own name first, then its kind if different.
  local names="$step" kind
  if [ "$mode" = draft ] || [ "$mode" = rewrite ]; then
    kind="$(kind_of "$step")"; [ "$kind" != "$step" ] && names="$step $kind"
  fi

  local bases="$mode"; [ "$mode" = rewrite ] && bases="draft rewrite"
  local list="$project/global.md" first=1 base n
  for base in $bases; do
    list="$list
$MODES_DIR/$base.md
$project/$base.md"
    if [ "$first" = 1 ]; then case "$base" in draft|architecture) list="$list
$project/venue.md" ;; esac; fi
    first=0
    for n in $names; do list="$list
$MODES_DIR/$base-$n.md"; done        # the skill's section files first,
    for n in $names; do list="$list
$project/$base-$n.md"; done          # then the paper's
  done

  echo "Mode \`$mode\`${step:+, step \`$step\`}. Read these files with the Read tool, in full, in this order:"
  echo
  local i=0 seen="|" f
  while IFS= read -r f; do
    [ -f "$f" ] || continue
    case "$seen" in *"|$f|"*) continue ;; esac
    seen="$seen$f|"; i=$((i + 1)); echo "$i. \`$f\`"
  done <<EOF
$list
EOF
}

main "$@"
exit 0
