# Release Retrospective — 2026-05-10

Session covering the v0.0.3 → v0.0.5 release cycle. Documents what went wrong, why, and how to avoid it.

---

## 1. Two tap directories — root cause of most pain

Having `~/dev/homebrew-tap` and `/opt/homebrew/Library/Taps/sdaas/homebrew-tap/` as separate clones caused repeated divergence problems: we edited the wrong one, the rebase silently reverted the `on_arm`/`on_intel` wheel approach, and CI broke.

**Better approach:** Point `TAP_DIR` in `release.sh` directly at the live tap:
```bash
TAP_DIR="$(brew --repository sdaas/tap)"
```
One repo, one source of truth. The "sync tap at start of release" step we added wouldn't even be needed.

---

## 2. Formula resource list was never verified against pip's dependency resolver

The `annotated-doc` gap existed since fastapi 0.136.1 was added. We only found it when the service crashed at runtime. We then added the import check and brew test smoke test reactively.

**Better approach:** Use `brew update-python-resources` to auto-generate the resource stanzas from pip's resolver:
```bash
brew update-python-resources sdaas/tap/brew-demo
```
This would have caught `annotated-doc` automatically and should be a step in `release.sh` before editing the formula manually.

---

## 3. The rebase was trusted without verification

After `git rebase --continue`, we pushed without checking what actually landed. The rebase silently replaced the `on_arm`/`on_intel` wheel blocks with the sdist, which CI then caught. We spent a full debug cycle on something a one-liner would have caught:
```bash
git diff origin/main HEAD -- Formula/brew-demo.rb
```

**Better approach:** Always verify the diff after a rebase before pushing, especially when there were conflicts.

---

## 4. The import check path bug was a design flaw introduced at creation

We wrote `$(brew --cellar brew-demo)/${VERSION}/libexec/bin/python` — a path that can't exist at the time the check runs (tag isn't pushed yet). The correct form `$(brew --prefix brew-demo)/libexec/bin/python` was obvious in hindsight. This cost a full release attempt.

**Better approach:** Test new `release.sh` steps with a dry run before committing. A simple `ls $(brew --cellar brew-demo)/` at the time would have shown the only installed version is `0.0.3`, not `0.0.5`.

---

## 5. `brew test` was too weak from the start

`brew test` only checked `--version` — which imports nothing, starts nothing, and proves almost nothing. The smoke test (start server, curl `/health`) should have been in the formula from day one. We only added it after the service failed in production.

**Better approach:** When writing a formula for a server, the test block should always include a liveness check. This is a standard practice that should be applied upfront, not as a fix.

---

## 6. The HOMEBREW_NO_ENV_HINTS comment was never validated

The comment claimed the env var suppressed the Xcode warning. It doesn't. No one checked whether the env var actually did what the comment said before it was committed. The Xcode warning kept appearing through multiple releases.

**Better approach:** Comments that describe *why* something suppresses an external tool's behavior should be verified against a real run before committing.

---

## 7. Monitoring GH Actions was reactive

After every push we waited for failure output before debugging. We could have proactively run `gh run watch` immediately after each push and streamed results directly in the session.

**Better approach:** Every `git push` in this project should be followed immediately by:
```bash
gh run watch --repo Sdaas/hello-brew
gh run watch --repo Sdaas/homebrew-tap
```
Failures surface in seconds rather than minutes later through copy-paste.

---

## Summary

| Problem | What happened | Better approach |
|---|---|---|
| Two tap dirs | Repeated edits to wrong repo, rebase regressions | `TAP_DIR=$(brew --repository sdaas/tap)` |
| Missing formula deps | Caught at runtime via service crash | `brew update-python-resources` in release pipeline |
| Rebase not verified | Silently lost wheel approach, broke CI | `git diff origin/main HEAD` before every push after a rebase |
| Import check path | Used `${VERSION}` which doesn't exist yet | Use `brew --prefix` from the start |
| Weak `brew test` | Only checked `--version` | Server smoke test belongs in the formula from day one |
| Wrong comment | `HOMEBREW_NO_ENV_HINTS` claimed to do something it doesn't | Validate externally-facing comments against a real run |
| Reactive CI monitoring | Waited for paste of failure | `gh run watch` immediately after every push |
