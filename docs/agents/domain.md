# Domain Docs

How engineering skills should consume ModaMix domain documentation while exploring the codebase.

## Before exploring, read these

- `GLOSSARY.md` at the repository root, or `GLOSSARY-MAP.md` if one exists.
- ADRs in `docs/adr/` that affect the area being changed.

If a file does not exist, proceed silently. The domain-modeling skill creates glossary entries and ADRs only when a term or qualifying decision has been resolved.

## File structure

ModaMix is a single-context repository. Its domain language lives in root `GLOSSARY.md`; cross-cutting architectural decisions belong in `docs/adr/` when needed.

## Use the glossary vocabulary

Use the canonical terms from `GLOSSARY.md` in issues, specifications, tests, and design discussions. Flag contradictions with existing ADRs rather than silently overriding them.
