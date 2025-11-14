#!/usr/bin/bash
set -euo pipefail

# =========================================
# Docker Installer for Ubuntu 20.04+/22.04+/24.04+
# Options:
#   --compose-standalone  Install legacy docker-compose to /usr/local/bin
#   --test                Run `docker run hello-world` after install
#   --uninstall           Remove Docker & cleanup
# =========================================

COMPOSE_STANDALONE=0
RUN_TEST=0
DO_UNINSTALL=0

for arg in "$@"; do
  case "$arg" in
    --compose-standalone) COMPOSE_STANDALONE=1 ;;
    --test) RUN_TEST=1 ;;
    --uninstall) DO_UNINSTALL=1 ;;
    *) echo "Unknown option: $arg" >&2; exit 1 ;;
  esac
done

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing command: $1. Installing..." >&2
    sudo apt-get update -y
    sudo apt-get install -y "$1" || true
  }
}

ensure_sudo() {
  if [ "$EUID" -ne 0 ]; then
    if ! command -v sudo >/dev/null 2>&1; then
      echo "Installing sudo..."
      apt-get update -y
      apt-get install -y sudo
    fi
  fi
}

uninstall_docker() {
  echo "==> Uninstalling Docker..."
  sudo systemctl disable --now docker.service docker.socket containerd.service || true
  sudo apt-get remove -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin docker.io || true
  sudo apt-get autoremove -y
  sudo rm -rf /var/lib/docker /var/lib/containerd
  sudo rm -f /etc/apt/sources.list.d/docker.list /etc/apt/keyrings/docker.gpg
  sudo rm -f /usr/local/bin/docker-compose
  echo "==> Docker removed."
}

install_docker_repo() {
  echo "==> Preparing APT dependencies..."
  sudo apt-get update -y
  sudo apt-get install -y ca-certificates curl gnupg lsb-release

  echo "==> Setting up Docker APT repository..."
  sudo install -m 0755 -d /etc/apt/keyrings
  if [ ! -f /etc/apt/keyrings/docker.gpg ]; then
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg
  fi

  UBUNTU_CODENAME="$(lsb_release -cs)"
  REPO_LINE="deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu ${UBUNTU_CODENAME} stable"
  LIST_FILE="/etc/apt/sources.list.d/docker.list"

  if [ ! -f "$LIST_FILE" ] || ! grep -q "download.docker.com" "$LIST_FILE"; then
    echo "$REPO_LINE" | sudo tee "$LIST_FILE" >/dev/null
  fi
}

install_docker_engine() {
  echo "==> Installing Docker Engine & components..."
  sudo apt-get update -y
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

  echo "==> Enabling services..."
  sudo systemctl enable --now containerd.service
  sudo systemctl enable --now docker.service

  echo "==> Docker version:"
  sudo docker --version || true
}

configure_user_group() {
  echo "==> Configuring user group 'docker'..."
  if ! getent group docker >/dev/null; then
    sudo groupadd docker
  fi

  CURRENT_USER="${SUDO_USER:-$USER}"
  if id -nG "$CURRENT_USER" | grep -qw docker; then
    echo "User '$CURRENT_USER' is already in 'docker' group."
  else
    sudo usermod -aG docker "$CURRENT_USER"
    echo "Added '$CURRENT_USER' to 'docker' group."
    echo ">> Bạn cần đăng xuất/đăng nhập lại (hoặc chạy 'newgrp docker') để dùng docker không cần sudo."
  fi
}

install_compose_standalone() {
  echo "==> Installing docker-compose (standalone) to /usr/local/bin/docker-compose ..."
  # Try GitHub API to get latest tag; fallback to fixed version if API blocked
  TMP_TAG="$(curl -fsSL https://api.github.com/repos/docker/compose/releases/latest | grep -oP '"tag_name":\s*"\K[^"]+' || true)"
  if [ -z "$TMP_TAG" ]; then
    TMP_TAG="v2.29.7"
    echo "Could not fetch latest release via API; falling back to $TMP_TAG"
  fi
  URL="https://github.com/docker/compose/releases/download/${TMP_TAG}/docker-compose-$(uname -s)-$(uname -m)"
  sudo curl -L "$URL" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
  /usr/local/bin/docker-compose --version || true
}

run_test_container() {
  echo "==> Running test container (hello-world)..."
  if docker run --rm hello-world; then
    echo ">> Docker works!"
  else
    echo ">> Test failed. Try: sudo docker run hello-world"
  fi
}

print_summary() {
  echo
  echo "========================================="
  echo " Docker installation completed."
  echo "-----------------------------------------"
  echo " docker version: $(docker --version || echo 'reopen your session')"
  echo " compose plugin: $(docker compose version || echo 'docker compose plugin not found')"
  if command -v docker-compose >/dev/null 2>&1; then
    echo " standalone compose: $(docker-compose --version)"
  fi
  echo "-----------------------------------------"
  echo "Tips:"
  echo " - Dùng Docker không cần sudo: đăng xuất/đăng nhập lại, hoặc chạy: newgrp docker"
  echo " - Kiểm tra: docker run hello-world"
  echo " - Compose (plugin): docker compose up -d"
  echo " - Compose (standalone): docker-compose up -d"
  echo "========================================="
}

main() {
  ensure_sudo
  require_cmd curl
  require_cmd gpg || true
  require_cmd lsb-release || true

  if [ "$DO_UNINSTALL" -eq 1 ]; then
    uninstall_docker
    exit 0
  fi

  # Warn if inside WSL (Docker Desktop for Windows is usually recommended)
  if grep -qi microsoft /proc/version 2>/dev/null; then
    echo ">> Detected WSL. Khuyên dùng Docker Desktop (Windows) + integration. Tiếp tục cài trong WSL..."
  fi

  # Remove conflicting old packages (no-op if not installed)
  echo "==> Removing old Docker packages (if any)..."
  sudo apt-get remove -y docker docker-engine docker.io containerd runc || true

  install_docker_repo
  install_docker_engine
  configure_user_group

  if [ "$COMPOSE_STANDALONE" -eq 1 ]; then
    install_compose_standalone
  fi

  if [ "$RUN_TEST" -eq 1 ]; then
    run_test_container
  fi

  print_summary
}

main "$@"
