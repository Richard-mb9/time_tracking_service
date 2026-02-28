if [ $# -ne 0 ]; then
    exec "$@"
else
    chmod +x ./update_database.sh
    ./update_database.sh
    
    WORKERS="${UVICORN_WORKERS:-1}"
    exec uvicorn main:app --host 0.0.0.0 --port 8083 --app-dir src --workers $WORKERS
fi