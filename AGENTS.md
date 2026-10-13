## Agent skills

### Issue tracker

Issues and specs are tracked in GitHub Issues. See `docs/agents/issue-tracker.md`.

### Triage labels

The default five triage labels are used. See `docs/agents/triage-labels.md`.

### Domain docs

ModaMix is a single-context project. See `docs/agents/domain.md`.

### Pull request size

Keep behavior-changing pull requests at or below 400 changed lines, counting additions and deletions, including tests and documentation. Split larger work into independently testable slices.

A pull request may exceed 400 changed lines only when its diff is predominantly behavior-preserving refactoring, file moves, formatting, or generated artifacts. Its description must state the exception and why it could not be split safely.
