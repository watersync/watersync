#!/bin/bash

docker-compose -f docker-compose.local.yml run --rm django sh -c "python manage.py makemigrations && python manage.py migrate"