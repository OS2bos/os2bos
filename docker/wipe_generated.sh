#!/bin/bash

cd "$(dirname "$0")"

echo "----------------------"
echo "Removing static files."
echo "----------------------"
sudo rm -r ../backend/static/*
