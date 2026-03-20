Prepare and ship the current changes to GitHub.

Steps:
1. Run `git status` and `git diff` to review what changed
2. Group changes by logical unit (don't mix unrelated changes in one commit)
3. For each group, create a commit following Conventional Commits:
   - `feat:` new feature
   - `fix:` bug fix
   - `chore:` build/config/tooling
   - `docs:` documentation only
   - Scope in parentheses when useful: `feat(mcp-server):`, `feat(engine):`
4. Push to `origin master`
5. Report the commit(s) created and the GitHub URL

Rules:
- Never commit: `*.db`, `*.env`, model files (`*.bin`, `*.safetensors`), `node_modules/`, `__pycache__/`
- Keep commit messages under 72 chars for the subject line
- Add `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>` to every commit
