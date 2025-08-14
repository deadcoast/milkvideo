# TASK

Unify and correct my settings.json to work in CURSOR IDE. im not using vscode. Cursor IDE is very similar, almost identical, but some plugins and or functions wont be available. See example below: Cursor has python and pylance installed, but these config commands that work in vscode do not work in cursor.

- Below is a snippet from settings.json

> "python.languageServer": "Pylance",
> "python.analysis.addImport.exactMatchOnly": true,
> "python.analysis.autoImportCompletions": false,
> "python.analysis.completeFunctionParens": false,
> "python.analysis.autoFormatStrings": true,
> "python.analysis.logLevel": "Error",

---

- `settings.json` versions.

```json
{
    "editor.tabSize": 4,
    "editor.rulers": [
        120
    ],
    "editor.renderWhitespace": "trailing",
    "editor.suggestSelection": "first",
    "editor.formatOnSave": true,
    "editor.defaultFormatter": null,
    "editor.stickyScroll.enabled": false,
    "editor.bracketPairColorization.enabled": false,
    "editor.cursorSmoothCaretAnimation": "on",
    "editor.suggest.preview": true,
    "terminal.integrated.defaultProfile.windows": "Command Prompt",
    "debug.onTaskErrors": "debugAnyway",
    "explorer.compactFolders": false,
    "explorer.confirmDragAndDrop": false,
    "explorer.confirmDelete": false,
    "explorer.copyRelativePathSeparator": "/",
    "files.autoSave": "onFocusChange",
    "files.exclude": {
        "node_modules/**/*": true,
        "**/.classpath": true,
        "**/.project": true,
        "**/.settings": true,
        "**/.factorypath": true,
        "**/__pycache__": true,
        "**/.pytest_cache": true,
        "**/.mypy_cache": true,
        "**/.ruff_cache": true
    },
    "files.associations": {
        "*.pyx": "cython",
        ".clang*": "yaml",
        "*.gpj": "jsonc",
        "*.gvw": "jsonc",
        "*.hpp.in": "cpp"
    },
    "files.insertFinalNewline": true,
    "files.trimFinalNewlines": true,
    "files.trimTrailingWhitespace": true,
    "workbench.startupEditor": "none",
    "workbench.editorAssociations": {
        "*.ipynb": "jupyter-notebook"
    },
    "workbench.colorTheme": "Default Dark+",
    "git.enableSmartCommit": true,
    "git.autofetch": true,
    "git.confirmSync": false,
    "git.openRepositoryInParentFolders": "always",
    "prettier.tabWidth": 4,
    "prettier.singleQuote": true,
    "prettier.jsxSingleQuote": true,
    "prettier.trailingComma": "all",
    "prettier.useEditorConfig": true,
    "prettier.bracketSpacing": false,
    "markdown.validate.enabled": true,
    "[markdown]": {
        "files.trimTrailingWhitespace": false,
        "editor.formatOnSave": false,
        "editor.wordWrap": "wordWrapColumn",
        "editor.wordWrapColumn": 120
    },
    "[yaml]": {
        "editor.formatOnSave": false,
        "editor.defaultFormatter": "redhat.vscode-yaml",
        "editor.wordWrap": "wordWrapColumn",
        "editor.wordWrapColumn": 120
    },
    "[json]": {
        "editor.formatOnSave": false,
        "editor.defaultFormatter": "vscode.json-language-features"
    },
    "[jsonc]": {
        "editor.formatOnSave": false
    },
    "[plaintext]": {
        "editor.wordWrap": "wordWrapColumn",
        "editor.wordWrapColumn": 120
    },
    "[toml]": {
        "editor.wordWrap": "wordWrapColumn",
        "editor.wordWrapColumn": 120,
        "editor.formatOnSave": true
    },
    "better-comments.tags": [
        {
            "tag": "XXX",
            "color": "#F8C471"
        },
        {
            "tag": "WARN",
            "color": "#FF6961"
        },
        {
            "tag": "NOTE",
            "color": "#3498DB"
        },
        {
            "tag": "TODO",
            "color": "#77C3EC"
        }
    ],
    "codesnap.showWindowControls": false,
    "codesnap.shutterAction": "copy",
    "Workspace_Formatter.excludePattern": [
        "**/build",
        "**/.*",
        "**/.vscode",
        "**/html"
    ],
    "remote.WSL.fileWatcher.polling": true,
    "errorLens.delay": 1000,
    "errorLens.enabledDiagnosticLevels": [
        "error",
        "warning"
    ],
    "errorLens.enabled": true,

    // Python settings
    "[python]": {
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnType": true,
        "editor.formatOnPaste": false,
        "editor.formatOnSaveMode": "file",
        "editor.codeActionsOnSave": {
            "source.organizeImports": "explicit",
            "source.fixAll": "explicit"
        },
        "editor.rulers": [120],
        "editor.wordWrapColumn": 120
    },

    // Python Language Server - Pyright
    "python.languageServer": "Cursor Pyright",
    "python.analysis.typeCheckingMode": "basic",
    "python.analysis.diagnosticMode": "workspace",
    "python.analysis.autoSearchPaths": true,
    "python.analysis.extraPaths": ["src"],
    "python.analysis.diagnosticSeverityOverrides": {
        "reportPrivateImportUsage": "warning",
        "reportImportCycles": "warning",
        "reportUnusedImport": "warning",
        "reportUnusedFunction": "warning",
        "reportUnusedVariable": "warning"
    },
    "python.analysis.autoImportCompletions": true,
    "python.analysis.completeFunctionParens": false,
    "python.analysis.inlayHints.functionReturnTypes": true,
    "python.analysis.inlayHints.variableTypes": true,

    // Black formatter
    "black-formatter.args": ["--line-length=120"],
    "black-formatter.importStrategy": "fromEnvironment",

    // isort configuration
    "isort.args": ["--profile=black", "--line-length=120"],
    "isort.check": true,
    "isort.importStrategy": "fromEnvironment",

    // Ruff configuration
    "ruff.enable": true,
    "ruff.nativeServer": "on",
    "ruff.fixAll": true,
    "ruff.lint.enable": true,

    // mypy configuration
    "mypy-type-checker.args": [
        "--ignore-missing-imports",
        "--disallow-untyped-defs",
        "--disallow-incomplete-defs",
        "--check-untyped-defs",
        "--disallow-untyped-decorators",
        "--no-implicit-optional",
        "--warn-redundant-casts",
        "--warn-return-any"
    ],
    "mypy-type-checker.importStrategy": "fromEnvironment",
    "mypy-type-checker.severity": {
        "error": "Error",
        "note": "Information"
    },

    // Sourcery configuration
    "sourcery.token": "",
    "sourcery.enableExtension": true,
    "sourcery.inlineDecorators": true,

    // Docstring settings
    "autoDocstring.generateDocstringOnEnter": true,
    "autoDocstring.quoteStyle": "'''",
    "autoDocstring.docstringFormat": "google",
    "autoDocstring.includeExtendedSummary": false,

    // Jupyter settings
    "jupyter.interactiveWindow.creationMode": "perFile",
    "jupyter.askForKernelRestart": false,
    "jupyter.themeMatplotlibPlots": true,
    "jupyter.logging.level": "error",
    "notebook.formatOnSave.enabled": false,
    "notebook.output.textLineLimit": 20,
    "notebook.compactView": false,
    "notebook.diff.ignoreMetadata": true,
    "notebook.diff.ignoreOutputs": true,

    // Markdown validation for Textual docs
    "markdown.validate.ignoredLinks": [],

    // Editor settings
    "editor.tabSize": 4,
    "editor.rulers": [
        120
    ],
    "editor.renderWhitespace": "trailing",
    "editor.suggestSelection": "first",
    "editor.tabSize": 4,
    "editor.rulers": [
        120
    ],
    "editor.renderWhitespace": "trailing",
    "editor.suggestSelection": "first",
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.stickyScroll.enabled": false,
    "editor.bracketPairColorization.enabled": false,
    "editor.cursorSmoothCaretAnimation": "on",
    "editor.suggest.preview": true,
    "terminal.integrated.defaultProfile.windows": "Command Prompt",
    "debug.onTaskErrors": "debugAnyway",
    "explorer.compactFolders": false,
    "explorer.confirmDragAndDrop": false,
    "explorer.confirmDelete": false,
    "explorer.copyRelativePathSeparator": "/",
    "files.autoSave": "onFocusChange",
    "files.exclude": {
        "node_modules/**/*": true,
        "**/.classpath": true,
        "**/.project": true,
        "**/.settings": true,
        "**/.factorypath": true
    },
    "files.associations": {
        "*.pyx": "cython",
        ".clang*": "yaml",
        "*.gpj": "jsonc",
        "*.gvw": "jsonc",
        "*.hpp.in": "cpp"
    },
    "files.insertFinalNewline": true,
    "files.trimFinalNewlines": true,
    "files.trimTrailingWhitespace": true,
    "workbench.startupEditor": "none",
    "workbench.editorAssociations": {
        "*.ipynb": "jupyter-notebook",
        "*.md": "vscode.markdown.preview.editor",
        "*.svg": "svgPreviewer.customEditor"
    },
    "workbench.colorTheme": "Default Dark+",
    "git.enableSmartCommit": true,
    "git.autofetch": true,
    "git.confirmSync": false,
    "git.openRepositoryInParentFolders": "always",
    "partialDiff.enableTelemetry": false,
    "prettier.tabWidth": 4,
    "prettier.singleQuote": true,
    "prettier.jsxSingleQuote": true,
    "prettier.trailingComma": "all",
    "prettier.useEditorConfig": true,
    "prettier.bracketSpacing": false,
    "markdown.validate.enabled": true,
    "[markdown]": {
        "files.trimTrailingWhitespace": false,
        "editor.formatOnSave": false,
        "editor.defaultFormatter": "yzhang.markdown-all-in-one",
        "editor.wordWrap": "wordWrapColumn",
        "editor.wordWrapColumn": 80
    },
    "[yaml]": {
        "editor.formatOnSave": false,
        "editor.defaultFormatter": "redhat.vscode-yaml",
        "editor.wordWrap": "wordWrapColumn",
        "editor.wordWrapColumn": 80
    },
    "[json]": {
        "editor.formatOnSave": false,
        "editor.defaultFormatter": "vscode.json-language-features"
    },
    "[jsonc]": {
        "editor.formatOnSave": false
    },
    "[plaintext]": {
        "editor.wordWrap": "wordWrapColumn",
        "editor.wordWrapColumn": 120
    },
    "[toml]": {
        "editor.wordWrap": "wordWrapColumn",
        "editor.wordWrapColumn": 80,
        "editor.defaultFormatter": "tamasfe.even-better-toml",
        "editor.formatOnSave": true
    },
    "better-comments.tags": [
        {
            "tag": "XXX",
            "color": "#F8C471"
        },
        {
            "tag": "WARN",
            "color": "#FF6961"
        },
        {
            "tag": "NOTE",
            "color": "#3498DB"
        },
        {
            "tag": "TODO",
            "color": "#77C3EC"
        }
    ],
    "vsintellicode.modify.editor.suggestSelection": "automaticallyOverrodeDefaultValue",
    "codesnap.showWindowControls": false,
    "codesnap.shutterAction": "copy",
    "Workspace_Formatter.excludePattern": [
        "**/build",
        "**/.*",
        "**/.vscode",
        "**/html"
    ],
    "svg.preview.autoOpen": true,
    "remote.WSL.fileWatcher.polling": true,
    "errorLens.delay": 1000,
    "errorLens.enabledDiagnosticLevels": [
        "error",
        "warning"
    ],
    "errorLens.enabled": false,
    "[python]": {
        "editor.formatOnSave": false,
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnType": false
    },
    "python.languageServer": "Pylance",
    "python.analysis.addImport.exactMatchOnly": true,
    "python.analysis.autoImportCompletions": false,
    "python.analysis.completeFunctionParens": false,
    "python.analysis.autoFormatStrings": true,
    "python.analysis.logLevel": "Error",
    "python.createEnvironment.contentButton": "show",
    "python.missingPackage.severity": "Error",
    "mypy-type-checker.importStrategy": "fromEnvironment",
    "black-formatter.importStrategy": "fromEnvironment",
    "isort.check": true,
    "isort.importStrategy": "fromEnvironment",
    "ruff.organizeImports": false,
    "ruff.fixAll": false,
    "autoDocstring.generateDocstringOnEnter": true,
    "autoDocstring.quoteStyle": "'''",
    "notebook.formatOnSave.enabled": false,
    "notebook.output.textLineLimit": 20,
    "notebook.compactView": false,
    "notebook.diff.ignoreMetadata": true,
    "notebook.diff.ignoreOutputs": true,

    // Python settings
    "python.analysis.diagnosticMode": "workspace",
    "python.analysis.typeCheckingMode": "basic",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.fixAll": "explicit",
        "source.organizeImports": "explicit"
    },
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.fixAll.ruff": "explicit",
            "source.organizeImports.ruff": "explicit"
        }
    },
    "files.exclude": {
        "**/.secretFolder": true,
        "**/node_modules": true,
        "someOtherFolder": true
    },
    "python.analysis.extraPaths": [
        "${workspaceFolder}"
    ],
    "ruff.lineLength": 88,
    "ruff.lint.select": ["E", "F", "B", "I", "N", "UP", "ANN", "COM818", "COM819", "RUF"],
    "ruff.configuration": {
        "format": {
            "quote-style": "double",
            "indent-style": "space",
            "skip-magic-trailing-comma": false,
            "line-ending": "auto"
        },
        "lint": {
            "isort": {
                "known-third-party": ["numpy", "pytest"]
            }
        }
    }
}
```
