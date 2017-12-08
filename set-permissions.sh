#!/usr/bin/env bash

sudo setfacl -R -m u:`whoami`:rwX .
sudo setfacl -dR -m u:`whoami`:rwX .
