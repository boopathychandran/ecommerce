@echo off
echo ===================================================
echo PostgreSQL Data Migration Utility
echo ===================================================

echo [Step 1] Exporting current SQLite data...
python manage.py dumpdata --exclude auth.permission --exclude contenttypes > datadump.json

echo [Step 2] Please ensure you have updated your .env/environment variables with:
echo DATABASE_URL=postgres://USER:PASSWORD@HOST:PORT/NAME
echo.
echo [Step 3] When ready, this script will migrate the schema and load data.
pause

echo [Step 4] Synchronizing schema to PostgreSQL...
python manage.py migrate

echo [Step 5] Loading data into PostgreSQL...
python manage.py loaddata datadump.json

echo [Done] Migration complete! Check your new database.
pause
