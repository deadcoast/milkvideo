# TASK

Review my other two configuration files `launch.json` and `tasks.json`. Correct, enhance, add any additional features for user qol. Avoid adding complicated, frivalous tasks like trying to integrate CI/CD when that is a user pipeline scenario. During your review and implementations, ensure you keep an eye out for any placeholders unfilled, especially path files that may break the project pointing to the wrong place.

---

`launch.json`

```json
{
    "version": "2.0.0",
    "configurations": [
        {
            "name": "PyDebug: Current File",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "args": [],
            "justMyCode": true
        },
        {
            "name": "PyDebug: Main File",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/main.py",
            "console": "integratedTerminal",
            "args": [],
            "justMyCode": true
        }
    ]
}
```

and

`tasks.json`

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Python: Current File",
            "type": "shell",
            "command": "${command:python.interpreterPath} ${file}",
            "args": [],
            "group": "build"
        },
        {
            "label": "Python: Main File",
            "type": "shell",
            "command": "${command:python.interpreterPath} ${workspaceFolder}/main.py",
            "args": [],
            "group": "build"
        },
        {
            "label": "Ruff: Lint All Files",
            "type": "shell",
            "command": "ruff check .",
            "group": "build",
            "problemMatcher": [],
            "detail": "Run Ruff linter on the entire project."
        },
        {
            "label": "Ruff: Fix All Autofixable Issues",
            "type": "shell",
            "command": "ruff check . --fix",
            "group": "build",
            "problemMatcher": [],
            "detail": "Auto-fix fixable issues."
        },
        {
            "label": "Ruff: Format Code",
            "type": "shell",
            "command": "ruff format .",
            "group": "build",
            "problemMatcher": [],
            "detail": "Format code using Ruff."
        },
        {
            "label": "Ruff: Format + Lint + Fix",
            "type": "shell",
            "command": "bash",
            "args": [
                "-c",
                "ruff format . && ruff check . --fix"
            ],
            "group": "build",
            "problemMatcher": [],
            "detail": "Format and fix code."
        }
    ]
}
```
