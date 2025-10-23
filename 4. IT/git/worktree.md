# worktree
Physical directory separation replaces logical branch switching. Instead of `git checkout branch` → just `cd directory`. Each directory = different branch, automatically.

## Create worktree
```shell
git worktree add <path> <branch>
```

## List all worktrees
```shell
git worktree list
```

## Remove worktree
```shell
git worktree remove <path>
```

## Clean up deleted worktrees
```shell
git worktree prune
```

## Setup once
```shell
git worktree add ../project-feature feature/new-ui
git worktree add ../project-hotfix hotfix/bug
```

## Daily work - just move between directories
```shell
cd ../project-feature # Auto on feature/new-ui branch
cd ../project-hotfix # Auto on hotfix/bug branch
cd ../project # Back to original branch
```
