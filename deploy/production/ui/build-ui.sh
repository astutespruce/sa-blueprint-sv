#!/bin/bash

echo "Removing previous Gatsby build"
docker-compose run --rm sa-ui-build clean

if docker-compose run --rm sa-ui-build build --prefix-paths; then
    echo "====> Gatsby build succeeded"
    rm -rf /var/www/southatlantic/*
    cp -r ../../../ui/public/* /var/www/southatlantic
else
    echo "====> ERROR: Gatsby build failed"
fi
