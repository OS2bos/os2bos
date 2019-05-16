#!/bin/bash

cd "$(dirname "$0")"

echo "----------------------"
echo "Removing static files."
echo "----------------------"
sudo rm -r ../backend/static/*
echo "--------------------"
echo "Removing migrations."
echo "--------------------"
sudo rm ../backend/*/migrations/0*
