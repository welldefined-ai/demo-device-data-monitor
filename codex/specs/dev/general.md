# General

## Commit Message Format

- Use `<sequence>-<type>(<optional scope>)<optional !>: <subject>` format (sequence increments per commit).
- Type: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `ci`, `build`, `perf`, or `chore`.
- Subject: imperative, ≤50 chars, no period. Example: `5-feat(auth): add OAuth login`.
- Body: explain **what/why** (not how), wrap at 72 chars, use bullets if clearer.
- Separate subject, body, and signature blocks with a single blank line only.
- Signature (if co-authored by AI), e.g.:
  ```
  🤖 Generated with [Codex CLI](https://github.com/openai/codex)
  Co-authored-by: Codex CLI <cligent@welldefined.ai>
  ```
- Optionally add `!` for breaking changes.

## Python

- Package name: `ddms`
- Package manager: `uv`
- Style:
  - Follow PEP 8 (Ruff + mypy).
  - Include type hints.
  - End files with newline.
  - No trailing whitespace.

