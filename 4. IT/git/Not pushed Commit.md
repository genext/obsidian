When you haven't pushed your commits to a remote repository, you have three main options using `git reset`.

## Option A: Undo commit, keep changes staged

```bash
git reset --soft HEAD~1
```

**What happens:**
- Moves HEAD back one commit
- Changes from that commit remain **staged** (in the index)
- Ready to commit again immediately

**Use when:**
- You want to modify the commit message
- You want to add more changes to the commit
- You want to split one commit into multiple commits

**Example:**
```bash
# You committed too early
git commit -m "Add feature"

# Undo the commit but keep changes staged
git reset --soft HEAD~1

# Add more changes
echo "more code" >> file.txt
git add file.txt

# Commit everything together
git commit -m "Add complete feature"
```

## Option B: Undo commit, keep changes unstaged

```bash
git reset HEAD~1
# or explicitly
git reset --mixed HEAD~1
```

**What happens:**
- Moves HEAD back one commit
- Changes remain in working directory but are **unstaged**
- This is the default behavior (`--mixed` is optional)

**Use when:**
- You want to reorganize which changes go into which commits
- You want to review changes before re-committing
- You want to selectively stage files

**Example:**
```bash
# You committed multiple files together
git commit -m "Update features"

# Undo commit, changes now unstaged
git reset HEAD~1

# Stage and commit files separately
git add feature1.txt
git commit -m "Add feature 1"

git add feature2.txt
git commit -m "Add feature 2"
```

## Option C: Undo commit, discard all changes

```bash
git reset --hard HEAD~1
```

**What happens:**
- Moves HEAD back one commit
- **Permanently deletes all changes** from that commit
- Working directory is clean

**Use when:**
- You want to completely remove the commit and its changes
- You're certain you don't need those changes

⚠️ **Warning:** This cannot be undone easily! The changes are permanently lost.

**Example:**
```bash
# You made a commit with wrong changes
git commit -m "Experimental feature"

# Completely remove it
git reset --hard HEAD~1

# Everything is gone, back to previous state
```

## Undo Multiple Commits

Replace `HEAD~1` with the number of commits you want to undo:

```bash
# Undo last 3 commits, keep changes staged
git reset --soft HEAD~3

# Undo last 3 commits, keep changes unstaged
git reset HEAD~3

# Undo last 3 commits, discard all changes
git reset --hard HEAD~3
```

Or use the `^` notation:
```bash
# Undo last 3 commits
git reset --soft HEAD^^^
```

## Reset to a Specific Commit

You can also use commit hashes:

```bash
# Find the commit hash you want
git log --oneline

# Reset to that specific commit
git reset --soft a1b2c3d4
git reset a1b2c3d4
git reset --hard a1b2c3d4
```

## Comparison Table

| Command | Commit History | Staging Area | Working Directory |
|---------|---------------|--------------|-------------------|
| `--soft` | Reset | Unchanged | Unchanged |
| `--mixed` (default) | Reset | Reset | Unchanged |
| `--hard` | Reset | Reset | Reset |

---

**Related Notes:**
- [[Git: How to Cancel Commits (Main)]]
- [[Git Cancel Commit - Already Pushed]]
- [[Git HEAD]]
- [[Git Cancel Commit - Quick Reference]]