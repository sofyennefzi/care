@echo off
REM Run the application

echo Starting Clinic Management System...
echo.

call .venv\Scripts\activate.bat
python main.py
@echo off
REM Setup script for Clinic Management System

echo ================================
echo Clinic Management System Setup
echo ================================
echo.

REM Activate virtual environment
echo [1/5] Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install dependencies (if needed)
echo [2/5] Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Check MySQL connection
echo [3/5] Checking configuration...
echo Please ensure MySQL is running and the database 'clinic_db' exists.
echo Update .env file with your MySQL credentials if needed.
echo.

REM Seed database
echo [4/5] Do you want to seed the database with sample data? (y/n)
set /p seed_choice=
if /i "%seed_choice%"=="y" (
    echo Seeding database...
    python seed.py
)

echo.
echo [5/5] Setup complete!
echo.
echo ================================
echo You can now run the application:
echo     python main.py
echo.
echo Then open: http://localhost:8000
echo Login: admin / admin123
echo ================================
pause

