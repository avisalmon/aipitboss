@echo off
REM Script to set up Git hooks for Windows environments
echo Setting up Git hooks for Windows...

REM Create a pre-commit.bat file in the hooks directory
echo @echo off > .git\hooks\pre-commit.bat
echo echo Running tests before commit... >> .git\hooks\pre-commit.bat
echo. >> .git\hooks\pre-commit.bat
echo REM Store current directory >> .git\hooks\pre-commit.bat
echo set "CURRENT_DIR=%%CD%%" >> .git\hooks\pre-commit.bat
echo. >> .git\hooks\pre-commit.bat
echo REM Navigate to project root >> .git\hooks\pre-commit.bat
echo cd /d "%%~dp0..\..\" >> .git\hooks\pre-commit.bat
echo. >> .git\hooks\pre-commit.bat
echo python -m pytest -v tests/ -k "not live" >> .git\hooks\pre-commit.bat
echo. >> .git\hooks\pre-commit.bat
echo if %%ERRORLEVEL%% neq 0 ( >> .git\hooks\pre-commit.bat
echo     echo COMMIT FAILED: Tests failed. Please fix the failing tests before committing. >> .git\hooks\pre-commit.bat
echo     cd /d "%%CURRENT_DIR%%" >> .git\hooks\pre-commit.bat
echo     exit /b 1 >> .git\hooks\pre-commit.bat
echo ) >> .git\hooks\pre-commit.bat
echo. >> .git\hooks\pre-commit.bat
echo echo All tests passed. Proceeding with commit. >> .git\hooks\pre-commit.bat
echo. >> .git\hooks\pre-commit.bat
echo cd /d "%%CURRENT_DIR%%" >> .git\hooks\pre-commit.bat
echo exit /b 0 >> .git\hooks\pre-commit.bat

REM Create a pre-commit file that Git will call
echo @echo off > .git\hooks\pre-commit
echo REM This is a wrapper that calls pre-commit.bat >> .git\hooks\pre-commit
echo call "%%~dp0pre-commit.bat" >> .git\hooks\pre-commit
echo exit /b %%ERRORLEVEL%% >> .git\hooks\pre-commit

echo Hooks set up successfully. When you commit, tests will run automatically.
echo.
echo If you encounter issues with the pre-commit hook, you can:
echo 1. Use 'git commit --no-verify -m "your message"' to bypass the hook
echo 2. Run tests manually with 'python -m pytest -v tests/ -k "not live"'
echo. 