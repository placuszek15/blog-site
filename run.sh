#!/bin/bash

PS_OUTPUT=$(ps -aux)

IS_WAITRESS=($(grep "waitress" <<< "$PS_OUTPUT"))
IS_CADDY=($(grep "caddy" <<< "$PS_OUTPUT"))

sudo kill ${IS_WAITRESS[1]}
sudo kill ${IS_CADDY[1]}

sudo -b -u www-data /usr/bin/python3 /usr/local/bin/waitress-serve --call main:return_app
sudo -b caddy run
