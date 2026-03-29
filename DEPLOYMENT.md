# DigitalOcean Deployment Guide

This guide explains how to deploy your **EpicChain Telegram Bot** to DigitalOcean.

## Option 1: DigitalOcean App Platform (Recommended)
This is the easiest way to deploy. DigitalOcean will automatically build your Docker container.

1.  **Push your code to GitHub.**
2.  In DigitalOcean, click **Create** -> **Apps**.
3.  Select your GitHub repository.
4.  DigitalOcean will detect the `Dockerfile`.
5.  **Environment Variables:** Add the following secrets from your `.env`:
    - `TELEGRAM_BOT_TOKEN`
    - `GEMINI_API_KEY`
    - `QDRANT_URL`
    - `QDRANT_API_KEY`
6.  **HTTP Port:** Since this is a worker bot (it doesn't have a web server), you don't need to expose any ports.
7.  Deploy!

## Option 2: DigitalOcean Droplet (Docker)
If you prefer a virtual machine:

1.  **Create a Droplet** (Marketplace -> Docker on Ubuntu).
2.  **SSH into your Droplet.**
3.  **Clone your repo:** `git clone <your-repo-url>`
4.  **Create your .env file:** `nano .env` (paste your keys).
5.  **Run with Docker Compose:**
    ```bash
    docker compose up -d --build
    ```

## Maintenance
- **Logs:** Use `docker compose logs -f` to see the bot's activity.
- **Updates:** `git pull` then `docker compose up -d --build` to apply changes.
