if [ $# -ne 0 ]; then
    exec "$@"
else
    chmod +x ./update_database.sh
    ./update_database.sh
    exec uvicorn main:app --host 0.0.0.0 --port 8081 --app-dir src --workers 2
fi