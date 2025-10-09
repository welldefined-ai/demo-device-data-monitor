# General

## Commit Message Format

- Prefix with sequence number: `<number>-<type>(<optional scope>)<optional !>: <subject>`.
- Type: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `ci`, `build`, `perf`, or `chore`.
- Subject: imperative, ≤50 chars, no period. Example: `5-feat(auth): add OAuth login`.
- Body: explain **what/why** (not how), wrap at 72 chars, use bullets if clearer.
- Add signature if co-authored by AI.
- Optionally add `!` for breaking changes.

## Python

- Package name: `ddms`
- Package manager: `uv`
- Style:
  - Follow PEP 8 (Ruff + mypy).
  - Include type hints.
  - End files with newline.
  - No trailing whitespace.

