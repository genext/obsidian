# Git HEAD

## What is HEAD?

HEAD is a pointer that represents your current position in the Git repository. It typically points to the latest commit on your current branch.

## HEAD Notation

Git provides shorthand notations to reference commits relative to HEAD:

- `HEAD~1` or `HEAD~` - One commit before HEAD (parent commit)
- `HEAD~2` - Two commits before HEAD
- `HEAD~n` - n commits before HEAD
- `HEAD^` - First parent of HEAD (equivalent to `HEAD~1`)
- `HEAD^^` - Grandparent of HEAD (equivalent to `HEAD~2`)
- `HEAD^^^` - Great-grandparent of HEAD (equivalent to `HEAD~3`)

## Difference between `~` and `^`

For linear history (most common case), `~` and `^` are interchangeable:
- `HEAD~1` = `HEAD^`
- `HEAD~2` = `HEAD^^`
- `HEAD~3` = `HEAD^^^`

The difference matters when dealing with **merge commits** (which have multiple parents):
- `^` can specify which parent: `HEAD^1` (first parent), `HEAD^2` (second parent)
- `~` always follows the first parent

## Examples

```bash
# View commit at HEAD
git show HEAD

# View commit one before HEAD
git show HEAD~1
git show HEAD^

# View commit two before HEAD
git show HEAD~2
git show HEAD^^

# View commit three before HEAD
git show HEAD~3
git show HEAD^^^
```

## HEAD 옮기기
commit hash로 옮길 수 있다.
```shell
git checkout commit-hash
# To go back to the last commit
git checkout master(main)
# shorter command
git checkout -
```

---

**Related Notes:**
- [[Git: How to Cancel Commits (Main)]]
- [[Git Commit Hash]]
- [[Git Range Notation]]