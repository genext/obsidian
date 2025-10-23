## Quick Command Lookup

| Situation | Command | Effect |
|-----------|---------|--------|
| Undo last commit, keep changes staged | `git reset --soft HEAD~1` | Changes ready to commit again |
| Undo last commit, keep changes unstaged | `git reset HEAD~1` | Changes in working directory |
| Undo last commit, discard changes | `git reset --hard HEAD~1` | Changes permanently lost ⚠️ |
| Pushed commit, safe undo | `git revert HEAD` | Creates new commit undoing changes |
| Pushed commit, dangerous undo | `git reset --hard HEAD~1` + `git push --force-with-lease` | Rewrites history ⚠️ |

## Common Scenarios

### Not Pushed Yet

```bash
# Keep changes staged
git reset --soft HEAD~1

# Keep changes unstaged
git reset HEAD~1

# Discard all changes
git reset --hard HEAD~1
```

### Already Pushed

```bash
# Safe method (recommended)
git revert HEAD
git push

# Dangerous method (use with caution)
git reset --hard HEAD~1
git push --force-with-lease
```

## Multiple Commits

### Undo last 3 commits (not pushed)
```bash
git reset --soft HEAD~3    # Keep staged
git reset HEAD~3           # Keep unstaged
git reset --hard HEAD~3    # Discard all
```

### Revert last 3 commits (pushed)
```bash
git revert HEAD~3..HEAD    # Revert last 3 commits
git push
```

## Reset Types Comparison

| Type | `--soft` | `--mixed` (default) | `--hard` |
|------|----------|---------------------|----------|
| Commit History | ✓ Reset | ✓ Reset | ✓ Reset |
| Staging Area | ✗ Keep | ✓ Reset | ✓ Reset |
| Working Directory | ✗ Keep | ✗ Keep | ✓ Reset |

## HEAD Notation Quick Guide

```bash
HEAD      # Current commit
HEAD~1    # 1 commit back
HEAD~2    # 2 commits back
HEAD~3    # 3 commits back

# Alternative notation
HEAD^     # 1 commit back (same as HEAD~1)
HEAD^^    # 2 commits back (same as HEAD~2)
HEAD^^^   # 3 commits back (same as HEAD~3)
```

## When to Use What

### Use `git reset` when:
- ✓ Commits are NOT pushed yet
- ✓ You're working alone on a branch
- ✓ You want to reorganize commits

### Use `git revert` when:
- ✓ Commits are already pushed
- ✓ Working on shared branch
- ✓ Don't want to rewrite history
- ✓ Safety is priority

### Use `git reset --hard` when:
- ⚠️ You're absolutely sure you don't need the changes
- ⚠️ Changes are not pushed OR you're alone on the branch

### Use `--force-with-lease` when:
- ⚠️ You must force push
- ⚠️ You've coordinated with team
- ⚠️ Want to check remote hasn't changed

## Emergency Commands

```bash
# View commit history
git log --oneline

# See what will change before reset
git diff HEAD~1

# View reflog (recover lost commits)
git reflog

# Recover from accidental reset
git reset --hard HEAD@{1}
```

---

**Related Notes:**
- [[Not pushed Commit]]
- [[Already Pushed Commit]]