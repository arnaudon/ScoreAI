#!/bin/bash
# Install Docker
sudo apt-get update
sudo apt-get -y upgrade
sudo apt-get install -y docker.io docker-compose git

# Clone your repo (or use a deployment key)
git clone https://github.com/arnaudon/ScoreAI.git
cd ScoreAI

# Start the app
sudo docker-compose up -d
