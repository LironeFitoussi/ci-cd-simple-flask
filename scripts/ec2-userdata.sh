#!/bin/bash
set -xe

# כתובת ה-Repo מוזרקת מה-Workflow של GitHub Actions (ע"י sed)
REPO_URL="__REPO_URL__"
APP_DIR="/opt/devops-notes-api"

export DEBIAN_FRONTEND=noninteractive

apt-get update -y
apt-get install -y python3 python3-pip git

mkdir -p /opt
cd /opt

if [ -d "$APP_DIR/.git" ]; then
  cd "$APP_DIR"
  git pull
else
  git clone "$REPO_URL" "$APP_DIR"
  cd "$APP_DIR"
fi

pip3 install -r requirements.txt

export APP_PORT=8000
nohup python3 app.py > /var/log/devops-notes-api.log 2>&1 &

