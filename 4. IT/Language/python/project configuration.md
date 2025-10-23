---
title: Python Project Configuration
---
## old
- `setup.py` for package configuration and dependencies
- `requirements.txt` for listing dependencies
- `setup.cfg` for additional metadata
## new
### toml
- [toml](https://toml.io/en/)
- Standar python configuration file defined in PEP 518 and PEP 621: pyproject.toml 사용
  - Project metadata (name, version, description, authors)
  - Dependencies
  - Build system configuration
  - Tool-specific settings (for linters, formatters, etc.)
```toml
    # Build system - required for packaging
    [build-system]
    requires = ["setuptools>=61.0", "wheel"]
    build-backend = "setuptools.build_meta"

    # Project metadata - the essentials
    [project]
    name = "my-package"
    version = "0.1.0"
    description = "A short description of your package"
    readme = "README.md"
    license = {text = "MIT"}
    authors = [
        {name = "Your Name", email = "your.email@example.com"}
    ]
    requires-python = ">=3.8"

    # Core dependencies
    dependencies = [
        "requests>=2.25.0",
        # Add your main dependencies here
    ]

    # Optional dependencies for development
    [project.optional-dependencies]
    dev = [
        "pytest>=7.0.0",
        "black>=23.0.0",
        "ruff>=0.1.0"
    ]

    # Project URLs
    [project.urls]
    Homepage = "https://github.com/yourusername/your-repo"
    Repository = "https://github.com/yourusername/your-repo"

    # CLI scripts (if you have any)
    [project.scripts]
    # my-cli = "my_package.cli:main"

    # Setuptools-specific configuration
    [tool.setuptools.packages.find]
    where = ["src"]  # Look for packages in src/ directory
    include = ["my_package*"]  # Include packages starting with my_package

    [tool.setuptools.package-data]
    my_package = ["*.txt", "data/*.json"]  # Include additional files

    # Common tool configurations

    # Black code formatter
    [tool.black]
    line-length = 88

    # Ruff linter (replaces flake8, isort, etc.)
    [tool.ruff]
    line-length = 88
    select = ["E", "F", "I"]  # pycodestyle, pyflakes, isort
    ignore = ["E501"]  # line too long (handled by black)

    # Pytest
    [tool.pytest.ini_options]
    testpaths = ["tests"]
    addopts = ["--cov=src", "--cov-report=term-missing"]
```

#### Tools that use pyproject.toml
- **Package managers**: `pip`, `poetry`, `pdm`, `uv`, `hatch`
- **Build tools**: `setuptools`, `hatchling`, `flit`
- **Other tools**: `black`, `ruff`, `pytest`, `mypy`, etc.
#### Creating distribution package with pyproject.toml
```shell
# This creates a .whl file (wheel) that can be installed
python -m build
# Creates: dist/my_package-1.0.0-py3-none-any.whl

# Then pip can install it:
pip install dist/my_package-1.0.0-py3-none-any.whl
```
## virtual environment
- 가상환경 만들려는 디렉토리에서 다음 명령어 실행.
```shell
  python -m venv my_venv_name

  # windows
  venv/Script/activate(.bat)
  # linux
  source venv/bin/activate
```
### powershell에서 activate를 실행하면 에러 날 때가 있음. windows 재설치 후.
```shell
.\venv\Scripts\activate
.\venv\Scripts\activate : File C:\exercise\python\chatGPT\venv\Scripts\Activate.ps1 cannot be loaded because running scripts is disabled on this system. For more in
formation, see about_Execution_Policies at https:/go.microsoft.com/fwlink/?LinkID=135170.
At line:1 char:1
+ .\venv\Scripts\activate
+ ~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : SecurityError: (:) [], PSSecurityException
    + FullyQualifiedErrorId : UnauthorizedAccess
```

- 이건 Execution-Policy 문제로 다음과 같은 옵션을 주면 보안도 유지하면서 실행할 수 있다.
  - ```shell
    Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
    ```
