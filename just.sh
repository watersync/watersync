#!/bin/bash

docker-compose -f docker-compose.local.yml run --rm django sh -c "cd watersync && sudo python ../manage.py $*"