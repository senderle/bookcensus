#!/bin/bash

# wait for mysql to be ready
nc -z db 3306
n=$?
while [ $n -ne 0 ]; do
    sleep 1
    nc -z db 3306
    n=$?
done

python manage.py runserver 0.0.0.0:8000