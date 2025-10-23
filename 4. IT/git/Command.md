## Initialize source directory
```shell
echo "# repotest" >> README.md
git init # make .git directory
git add README.md
git commit -m "first commit"
git branch -M main  # -M은 현 브랜치명을 바꿔준다.
git remote add origin https://github.com/genext/repo_name.git
git push -u origin main
```
- 하지만 이미 ".git" 디렉토리가 있을 경우, ".git"을 먼저 삭제하고 초기화 실행.

## 인증방법
github은 비밀번호 인증을 더는 사용하지 않는다.

두 가지 인증 방법이 있지만 굳이 사용하지 않아도 개인 PC서는 잘 된다. 회사에서 보안 정책 상 쓰기는 한다.

### access token
github에서 access token을 만들어서 매번 로그인할 때마다 사용. -> 불편!!

### ssh
```shell
ssh-keygen -t ed25519 -C "your-email@example.com"
```
-t 옵션에 rsa 등 다른 것도 있지만 ed25519가 가장 최근 것.

## Repository copy
```shell
git clone http_url
```

## configure
```shell
git config --[global|local] user.name "your name here"
git config --[global|local] user.email "your email here"

git config --[global|local] --list
```

## status
```shell
git status
```

## working directory -> staging area
```shell
# current directory files
git add .

# for all files and folders
git add -A

# a specific file
git add file
```

## stash area
```shell
git stash

git stash pop

git stash clear
```

## staging area -> Local Repository
```shell
git commit -m "my commit message"
```

## compare
```shell
git diff
```

## local -> central Repository
```shell
git push origin master

git push origin otherBranch
```

## log
```shell
git log
```

## branch
```shell
git branch # list all branches

# make a new branch
git branch myBranch

git checkout myBranch # switch branch

# make a new branch and switch to it in one command
git checkout -b myBranch

# delete a branch
git branch -d myBranch

git checkout master # switch back to master
```

## merge/rebase after working on a branch
choose one of 2 ways

### merge: writing in master branch
```shell
git checkout master
git merge myBranch
```

### rebase: merges the branch with the master in a serial fashion.
```shell
git checkout master
git rebase myBranch
```

### push -f or push --without-lease?
한 브랜치에 여러 개발자가 같이 작업할 경우에 --force를 쓰면 위험.

## cherry-pick: commit를 원래 목적지가 아닌 다른 브랜치에 했을 때 원래 목적지로 옮기기
git log -> 잘못 올린 commit hash 찾기

Before you run `git push --force`, please make sure:
- You're on the right branch
- No one else has pushed changes to that branch since your commit
- You have necessary permissions for force push

```shell
# Switch to the correct branch where you want the commit
git checkout correct-branch

# Cherry-pick the specific commit
git cherry-pick 897cb22dabbe54744f1d23daaf3ac53653d8377b

# If you want to remove it from the wrong branch:
git checkout wrong-branch
git reset --hard HEAD~1
git push --force
```
