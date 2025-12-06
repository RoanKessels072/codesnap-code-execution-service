#!/bin/bash

echo "Building Python Sandbox Image..."
docker build -t codesnap-python-runner ./sandbox_images/python

echo "Building Node.js Sandbox Image..."
docker build -t codesnap-node-runner ./sandbox_images/javascript

echo "Sandbox images ready!"