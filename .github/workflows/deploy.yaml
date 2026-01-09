name: Deploy ScoreAI

on:
  push:
    # branches: [ main ] # Deploy whenever you push to main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Deploy to Infomaniak via SSH
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /home/debian/ScoreAI
            git pull origin main
            sudo docker-compose up --build -d
