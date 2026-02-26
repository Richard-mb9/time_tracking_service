export PYTHONPATH="$(pwd)/src"

if [ $# -ne 0 ]; then
    exec "$@"
else
    chmod +x ./update_database.sh
    ./update_database.sh
    exec alembic revision --autogenerate --version-path=src/infra/migrations
fi