# Git Range Notation (..)

## What is Range Notation?

The `..` notation is used to specify a range of commits in Git commands.

## Syntax

**Format:** `A..B`

**Meaning:** "commits reachable from B but NOT reachable from A"

**Important Rules:**
- Start point (A) is **excluded**
- End point (B) is **included**

## Examples

### Example 1: HEAD~2..HEAD

```bash
HEAD~2..HEAD
```

This includes:
- HEAD (included) ✓
- HEAD~1 (included) ✓
- HEAD~2 (excluded - starting point) ✗

**Result:** 2 commits (HEAD~1 and HEAD)

### Example 2: HEAD~3..HEAD

```bash
HEAD~3..HEAD
```

This includes:
- HEAD (included) ✓
- HEAD~1 (included) ✓
- HEAD~2 (included) ✓
- HEAD~3 (excluded - starting point) ✗

**Result:** 3 commits (HEAD~2, HEAD~1, and HEAD)

## Visual Representation

```
HEAD~3 (excluded) -- HEAD~2 (included) -- HEAD~1 (included) -- HEAD (included)
       ^                                                                ^
       |                                                                |
   start point                                                     end point
       ✗                           ✓                    ✓                ✓
```

## Common Use Cases

### Revert multiple commits
```bash
# Revert last 2 commits
git revert HEAD~2..HEAD

# Revert last 3 commits
git revert HEAD~3..HEAD
```

### View commits in a range
```bash
# Show commits between two points
git log HEAD~5..HEAD

# Show commits in a branch not in another
git log main..feature-branch
```

### Compare changes
```bash
# See what changed in last 3 commits
git diff HEAD~3..HEAD
```

## Quick Formula

To revert the last **n** commits:
```bash
git revert HEAD~n..HEAD
```

This will revert **n commits** (not n+1, because the start point is excluded).

---

**Related Notes:**
- [[Git: How to Cancel Commits (Main)]]
- [[Git HEAD]]
- [[Git Commit Hash]]