#! /bin/bash
dir=migrations

if [ -d "$dir" ]; then
    flask db downgrade
    rm -rf $dir
    echo 'clear migration!'
fi
echo "init db ..."

flask db init

echo "Migrate db ..."

flask db migrate -m "Create tables"

echo "Update ....."

flask db upgrade