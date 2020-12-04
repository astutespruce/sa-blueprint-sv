#!/bin/bash

echo "Removing previous Gatsby build"
docker-compose run --rm sa-ui-build clean

if docker-compose run --rm sa-ui-build build; then
    echo "====> Gatsby build succeeded"
    rm -rf /var/www/sa/*
    cp -r ./public/* /var/www/sa
else
    echo "====> ERROR: Gatsby build failed"
fi
