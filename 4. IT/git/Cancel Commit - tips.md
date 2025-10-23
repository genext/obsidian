# Git Cancel Commit - Tips

## Safety Tips

### 1. Before Using `--hard`
Always double-check that you don't need those changes. Once deleted with `--hard`, they're very difficult to recover.

```bash
# View what will be lost
git diff HEAD~1

# View the commit details
git show HEAD

# Only then proceed if you're sure
git reset --hard HEAD~1
```

### 2. For Shared Branches
Prefer `git revert` over `git reset` + force push. It's safer and won't cause problems for your teammates.

```bash
# Good for shared branches
git revert HEAD

# Dangerous for shared branches
git reset --hard HEAD~1 && git push --force
```

### 3. Check Your Status First
Always review what you're about to undo.

```bash
# See commit history
git log --oneline

# See detailed history
git log

# See last 5 commits
git log --oneline -5
```

### 4. View What Will Change
Before resetting, see what changes you're about to undo.

```bash
# Compare with previous commit
git diff HEAD~1

# Compare with 3 commits back
git diff HEAD~3

# Show what's in the commit
git show HEAD
```

## Best Practices

### 1. Use `--force-with-lease` Instead of `--force`
When you must force push, use `--force-with-lease` to add a safety check.

```bash
# Safer - checks if remote has new changes
git push --force-with-lease

# Less safe - overwrites regardless
git push --force
```

**Why?** `--force-with-lease` fails if someone else pushed to the remote after your last fetch, preventing accidental overwrites.

### 2. Communicate Before Force Pushing
If you must force push to a shared branch:
1. Tell your team first
2. Make sure no one else is working on it
3. Have them pull immediately after

### 3. Work on Feature Branches
When experimenting or unsure:
```bash
# Create a new branch for experiments
git checkout -b experiment

# Make changes, commits, resets freely
# Main branch stays safe
```

### 4. Use Descriptive Commit Messages
Good commit messages help you identify what to undo:
```bash
# Good
git commit -m "Add user authentication feature"

# Bad
git commit -m "fix stuff"
```

## Emergency Recovery

### 1. Use `git reflog`
If you accidentally reset too far, reflog can save you.

```bash
# View all recent HEAD positions
git reflog

# Output example:
# a1b2c3d HEAD@{0}: reset: moving to HEAD~1
# e4f5g6h HEAD@{1}: commit: Add feature
# i7j8k9l HEAD@{2}: commit: Fix bug

# Restore to a previous state
git reset --hard HEAD@{1}
```

### 2. Recovering After Accidental `--hard`
```bash
# View reflog
git reflog

# Find the commit before the reset
# Reset back to it
git reset --hard <commit-hash>
```

**Note:** Reflog only keeps history for about 90 days by default.

### 3. If Someone Force Pushed
```bash
# Save your work first
git stash

# Fetch latest remote state
git fetch origin

# Reset to match remote
git reset --hard origin/main

# Restore your work
git stash pop
```

## Common Mistakes to Avoid

### ❌ Don't: Force push to main/production
```bash
# Very dangerous!
git push --force origin main
```

### ✅ Do: Use revert on main/production
```bash
# Safe for main branches
git revert HEAD
git push origin main
```

### ❌ Don't: Reset without checking what you're undoing
```bash
# Risky - you don't know what you're losing
git reset --hard HEAD~1
```

### ✅ Do: Check first, then reset
```bash
# Safe - you know what you're doing
git log --oneline
git diff HEAD~1
git reset --hard HEAD~1
```

### ❌ Don't: Guess the number of commits to reset
```bash
# You might undo more than intended
git reset --hard HEAD~5
```

### ✅ Do: Check log and count carefully
```bash
# Know exactly what you're undoing
git log --oneline -10
# Count the commits you want to undo
git reset --hard HEAD~3
```

## Workflow Recommendations

### For Solo Projects
You have more freedom but still be careful:
```bash
# Can use reset freely before pushing
git reset --soft HEAD~1

# After pushing, revert is still safer
git revert HEAD
```

### For Team Projects
Always prioritize team safety:
```bash
# Default to revert for shared branches
git revert HEAD

# Only reset + force push if absolutely necessary
# and you've told your team
```

### For Experimenting
Use branches to protect your work:
```bash
# Create experiment branch
git checkout -b try-new-feature

# Try anything, reset freely
git reset --hard HEAD~5

# If it works, merge back
git checkout main
git merge try-new-feature

# If it doesn't work, just delete the branch
git branch -D try-new-feature
```

## Helpful Aliases

Add these to your `~/.gitconfig` for convenience:

```bash
[alias]
    # Undo last commit, keep changes staged
    undo = reset --soft HEAD~1
    
    # Undo last commit, keep changes unstaged
    unstage = reset HEAD~1
    
    # View pretty log
    lg = log --oneline --graph --decorate
    
    # Show what changed in last commit
    last = show HEAD
```

Usage:
```bash
git undo      # Instead of: git reset --soft HEAD~1
git unstage   # Instead of: git reset HEAD~1
git lg        # Pretty commit history
git last      # Show last commit details
```

---

**Related Notes:**
- [[Not pushed Commit]]
- [[Already Pushed Commit]]