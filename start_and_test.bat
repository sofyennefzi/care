@echo off
echo ============================================================
echo           CLINIC APP - Services Fix Verification
echo ============================================================
echo.

echo Step 1: Verifying files...
python verify_fixes.py
echo.

echo Step 2: Starting server...
echo Press Ctrl+C to stop when done testing
echo.
timeout /t 3 /nobreak
python main.py

