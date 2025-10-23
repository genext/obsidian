## What is a Commit Hash?

Every commit in Git has a unique identifier called a commit hash (or SHA). It's a 40-character hexadecimal string that looks like this:

```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
```

## Using Commit Hashes

You can use commit hashes to reference specific commits in Git commands:

```bash
# View a specific commit
git show a1b2c3d4

# Reset to a specific commit
git reset a1b2c3d4

# Revert a specific commit
git revert a1b2c3d4
```

## Short vs Full Hash

You don't need to use the full 40-character hash. Git allows you to use a shortened version (usually 7-8 characters) as long as it's unique in your repository:

```bash
# These are equivalent if unique:
git show a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
git show a1b2c3d4
```

## Finding Commit Hashes

### View commit history with hashes
```bash
# Full view
git log

# Compact view (short hash + commit message)
git log --oneline

# Last 5 commits
git log --oneline -5
```

### Example output
```bash
$ git log --oneline
a1b2c3d (HEAD -> main) Fix bug in user authentication
e4f5g6h Add user profile page
i7j8k9l Update dependencies
```

## When to Use Commit Hash vs HEAD Notation

- **Use HEAD notation** (`HEAD~1`, `HEAD~2`): When referencing commits relative to your current position
- **Use commit hash**: When you need to reference a specific commit that might not be near HEAD

---

**Related Notes:**
- [[Git: How to Cancel Commits (Main)]]
- [[Git HEAD]]
- [[Git Range Notation]]