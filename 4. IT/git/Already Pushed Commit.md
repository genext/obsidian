When commits are already pushed to a remote repository, you need to be more careful because other developers might be using those commits.

## Option A: Safe Method - Revert (Recommended)

```bash
git revert HEAD
```

**What happens:**
- Creates a **new commit** that undoes changes from the specified commit
- Preserves history - doesn't rewrite it
- Safe for shared branches
- Others can pull without conflicts

**Why it's safe:**
- Doesn't delete any commits
- Doesn't change existing history
- Team members won't have conflicts when they pull

**Example:**
```bash
# You pushed a buggy commit
git push

# Create a new commit that undoes it
git revert HEAD

# Push the revert commit
git push
```

### Revert Multiple Commits

```bash
# Revert last 2 commits (HEAD~1 and HEAD)
git revert HEAD~2..HEAD

# Revert last 3 commits (HEAD~2, HEAD~1, and HEAD)
git revert HEAD~3..HEAD

# Or list them explicitly
git revert HEAD~2 HEAD~1 HEAD
```

**Understanding the range:**
- `HEAD~2..HEAD` excludes HEAD~2 itself
- See [[Git Range Notation]] for details

### Revert Without Auto-Committing

```bash
# Revert but don't commit yet
git revert -n HEAD

# Make modifications if needed
# Then commit manually
git commit -m "Revert: description"
```

## Option B: Dangerous Method - Reset + Force Push

⚠️ **Use with extreme caution!**

```bash
# 1. Reset local repository
git reset --hard HEAD~1

# 2. Force push to remote
git push --force
# or specifically but less common. be careful.
git push origin +HEAD
# or safer alternative
git push --force-with-lease
```

**What happens:**
- Rewrites history on the remote
- Deletes commits permanently
- Can cause problems for other developers

**Why it's dangerous:**
- Other developers who pulled those commits will have conflicts
- They'll need to reset their local branches
- Lost commits are hard to recover
- Can break team workflows

**When to use this:**
- You're working **alone** on the branch
- You've **coordinated with your team** and everyone agrees
- The commits contain **sensitive data** that must be removed (passwords, API keys, etc.)

**Difference between --force and --force-with-lease:**
- `--force`: Overwrites remote regardless of what's there
- `--force-with-lease`: Checks if remote has changes you don't have locally before force pushing (safer)

**Example:**
```bash
# View commits
git log --oneline

# Reset to remove last commit
git reset --hard HEAD~1

# Force push (be very careful!)
git push --force-with-lease
```

## Option C: Reset to Specific Commit (Local + Remote)

If you want to completely remove multiple commits:

```bash
# 1. Find the commit hash you want to go back to
git log --oneline

# 2. Reset local to that commit
git reset --hard <commit-hash>
# or use HEAD notation
git reset --hard HEAD~3

# 3. Force push to remote
git push --force-with-lease
```

## Choosing the Right Method

| Scenario                        | Recommended Method                              |
| ------------------------------- | ----------------------------------------------- |
| Shared branch with team         | `git revert` ✓                                  |
| Working alone on feature branch | `git reset` + `--force-with-lease` (acceptable) |
| Main/production branch          | `git revert` ✓ (almost always)                  |
| Sensitive data exposed          | `git reset` + `--force` (necessary evil)        |
| Quick bug fix needed            | `git revert` ✓                                  |

## Recovering from Force Push Gone Wrong

If someone on your team force pushed and you're having issues:

```bash
# Save your current work
git stash

# Fetch the latest remote state
git fetch origin

# Reset your branch to match remote
git reset --hard origin/main
# (replace 'main' with your branch name)

# Restore your saved work if needed
git stash pop
```

---

**Related Notes:**
- [[Force Push Syntax]]