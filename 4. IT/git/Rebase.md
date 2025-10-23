# git rebase

## Make sure you're on your branch
```shell
git checkout your-branch-name
```

## Fetch the latest changes from the master branch
```shell
git fetch origin master
```

## Rebase your branch onto the master branch
```shell
git rebase origin/master
```

**중요!!** 이걸 master에서 하면 안 된다!!

## conflict 처리
```shell
git rebase --continue
```

## 참고자료
[Merging vs Rebasing](https://www.atlassian.com/git/tutorials/merging-vs-rebasing)
