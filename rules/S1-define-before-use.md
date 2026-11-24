**S1. Define before use (MAJOR).** Every domain term, acronym, artifact, or coined construct is
defined in plain language at first use, before it appears in an argument. A first-time reader in
the venue must be able to follow. For a cross-disciplinary audience, a gloss that is itself jargon
fails — gloss the gloss.
- Check: for each CamelCase / ×-joined / capitalized construct, is there an upstream "is / means /
  defined as" before its first argumentative use?
- Grep aid: `grep -rnoE "[A-Z][a-zA-Z]+×[A-Z][a-zA-Z]+|\b[A-Z][a-z]+[A-Z][a-zA-Z]+\b" sections/*.tex`
  — for each hit, confirm a definition precedes its first argumentative use.
