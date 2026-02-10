#!/bin/bash
set -xe

# כתובת ה-Repo מוזרקת מה-Workflow של GitHub Actions (ע"י sed)
REPO_URL="__REPO_URL__"
APP_DIR="/opt/devops-notes-api"

export DEBIAN_FRONTEND=noninteractive

apt-get update -y
apt-get install -y python3 python3-venv git

mkdir -p /opt
cd /opt

if [ -d "$APP_DIR/.git" ]; then
  cd "$APP_DIR"
  git pull
else
  git clone "$REPO_URL" "$APP_DIR"
  cd "$APP_DIR"
fi

# Ubuntu 24.04 (PEP 668) – חובה להשתמש ב-venv
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

export APP_PORT=8000
nohup python app.py > /var/log/devops-notes-api.log 2>&1 &

