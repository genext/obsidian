## Overview

Force pushing allows you to overwrite remote history, even when it would normally be rejected. There are multiple ways to force push in Git, each with different use cases.

## Basic Force Push Methods

### Method 1: Using `--force` flag
```bash
git push --force origin main
# or shorthand
git push -f origin main
```

**What it does:**
- Overwrites remote branch completely
- Ignores any conflicts or non-fast-forward issues
- Most common and explicit method

### Method 2: Using `+` prefix
```bash
git push origin +main
```

**What it does:**
- Same as `--force` but uses different syntax
- The `+` before the branch name means "force this ref"
- More concise syntax

### Method 3: Using `+HEAD`
```bash
git push origin +HEAD
```

**What it does:**
- Force pushes your current HEAD to the remote
- Pushes to the tracking branch of your current branch
- Useful when you don't want to type the branch name

**Example:**
```bash
# You're on feature-branch
git push origin +HEAD
# This force pushes to origin/feature-branch
```

## Safer Force Push: `--force-with-lease`

```bash
git push --force-with-lease origin main
```

**What it does:**
- Force pushes BUT checks if remote has changed since you last fetched
- Fails if someone else pushed to the remote after your last fetch
- Prevents accidentally overwriting others' work

**Why it's safer:**
- Protects against race conditions
- Won't overwrite work you haven't seen yet
- Still allows force push when safe

**Comparison:**
```bash
# Dangerous - always overwrites
git push --force origin main

# Safer - checks remote first
git push --force-with-lease origin main
```

## Advanced: Selective Force Push

You can force push specific branches while letting others fail normally:

```bash
# Force push main, but let feature fail if not fast-forward
git push origin +main feature-branch
```

This is useful when:
- You want to force push one branch but be careful with others
- Running batch push operations
- Automating deployments

## Force Push with Lease Syntax Variations

### Standard syntax
```bash
git push --force-with-lease origin main
```

### With specific expected value
```bash
git push --force-with-lease=main:a1b2c3d origin main
```

**What it does:**
- Only pushes if remote `main` is at commit `a1b2c3d`
- Even more precise than standard `--force-with-lease`
- Useful in automated systems

## Comparison Table

| Syntax | Force Level | Safety Check | Use Case |
|--------|-------------|--------------|----------|
| `--force` / `-f` | Strong | None | When you know what you're doing |
| `+ref` | Strong | None | Scripting, selective force |
| `+HEAD` | Strong | None | Quick force push current branch |
| `--force-with-lease` | Conditional | Checks remote | Safer force push (recommended) |
| `--force-with-lease=ref:expected` | Conditional | Precise check | Automated systems |

## Common Use Cases

### Use Case 1: Amending pushed commit
```bash
# You already pushed a commit
git push origin main

# You realize you need to amend it
git commit --amend

# Force push the amended commit
git push --force-with-lease origin main
```

### Use Case 2: Rebasing pushed branch
```bash
# You pushed feature branch
git push origin feature-branch

# You rebase it on latest main
git rebase main

# Force push the rebased branch
git push --force-with-lease origin feature-branch
```

### Use Case 3: Quick force push current branch
```bash
# Instead of typing the full branch name
git push origin +HEAD

# Equivalent to
git push --force origin $(git branch --show-current)
```

### Use Case 4: Resetting pushed commits
```bash
# Reset local branch
git reset --hard HEAD~3

# Force push to remote
git push --force-with-lease origin main
```

## Safety Best Practices

### ✅ Do:
1. Use `--force-with-lease` instead of `--force`
2. Communicate with team before force pushing shared branches
3. Force push to feature branches you own
4. Double-check which branch you're pushing to

```bash
# Good practices
git push --force-with-lease origin my-feature-branch
git branch  # Check current branch first
git push --force-with-lease origin +HEAD
```

### ❌ Don't:
1. Force push to main/production without team agreement
2. Force push to branches others are actively working on
3. Use `--force` when `--force-with-lease` would work
4. Force push without checking what you're overwriting

```bash
# Dangerous practices
git push --force origin main  # Without checking
git push origin +main +develop +feature  # Force pushing multiple shared branches
```

## When Force Push is Necessary

### Legitimate reasons:
1. **Amending commits** - Fixed typo in commit message or code
2. **Rebasing** - Keeping feature branch up to date with main
3. **Squashing commits** - Cleaning up commit history before merge
4. **Removing sensitive data** - Accidentally committed passwords/keys
5. **Interactive rebase** - Reorganizing commit history

### Example: Removing sensitive data
```bash
# Remove file from all history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch secrets.txt" \
  --prune-empty --tag-name-filter cat -- --all

# Force push to overwrite remote history
git push --force-with-lease --all
```

## Recovering from Force Push Issues

### If you force pushed by mistake:
```bash
# Find the commit you want to restore
git reflog

# Reset to that commit
git reset --hard a1b2c3d

# Force push again to restore
git push --force-with-lease origin main
```

### If someone else force pushed:
```bash
# Save your work
git stash

# Fetch latest state
git fetch origin

# Reset to remote
git reset --hard origin/main

# Restore your work
git stash pop
```

## Alternative: Avoid Force Push

Sometimes you can avoid force push entirely:

### Instead of amending pushed commit:
```bash
# Don't amend and force push
git commit --amend
git push --force

# Create a new fix commit instead
git commit -m "Fix typo from previous commit"
git push
```

### Instead of rebasing:
```bash
# Don't rebase and force push
git rebase main
git push --force

# Merge instead
git merge main
git push
```

**Trade-off:** Cleaner history (force push) vs. safer workflow (no force push)

---

**Related Notes:**
[[Already Pushed Commit]]