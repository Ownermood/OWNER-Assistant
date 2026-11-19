#!/usr/bin/env bash
# OWNER Assistant installer: installs system packages + python requirements.
#
#   bash installer.sh                 # inside this repo: just installs deps
#   bash installer.sh --dir=/path     # clone the repo there first (if missing)
#
# Options: --dir=PATH  --branch=NAME  --env-file=FILE  --no-root
# Env:     REPO (git url to clone, default: your fork)

REPO="${REPO:-https://github.com/Ownermood/Ultroid.git}"
BRANCH="${BRANCH:-main}"
CURRENT_DIR="$(pwd)"
ENV_FILE_PATH=".env"
DIR="/root/OWNER-Assistant"

while [ $# -gt 0 ]; do
    case "$1" in
    --dir=*) DIR="${1#*=}" ;;
    --branch=*) BRANCH="${1#*=}" ;;
    --env-file=*) ENV_FILE_PATH="${1#*=}" ;;
    --no-root) NO_ROOT=true ;;
    *)
        echo "Unknown parameter passed: $1"
        exit 1
        ;;
    esac
    shift
done

SUDO=""
if [ "$(id -u)" -ne 0 ] && [ -z "$NO_ROOT" ] && command -v sudo &>/dev/null; then
    SUDO="sudo"
fi

install_system_packages() {
    echo "Installing system packages..."
    if command -v apt-get &>/dev/null && { [ "$(id -u)" -eq 0 ] || [ -n "$SUDO" ]; }; then
        $SUDO apt-get -qq update
        $SUDO apt-get install -qq -y --no-install-recommends \
            python3 python3-pip git ffmpeg mediainfo curl
        $SUDO apt-get install -qq -y neofetch 2>/dev/null || true
    elif command -v pacman &>/dev/null && { [ "$(id -u)" -eq 0 ] || [ -n "$SUDO" ]; }; then
        $SUDO pacman -Sy --noconfirm python python-pip git ffmpeg mediainfo curl
    elif command -v pkg &>/dev/null; then
        # Termux
        pkg install -y python git ffmpeg mediainfo
    else
        for tool in python3 git ffmpeg; do
            command -v "$tool" &>/dev/null || echo "WARNING: '$tool' is not installed."
        done
    fi
}

check_python() {
    if ! command -v python3 &>/dev/null; then
        echo "Python 3.10 or higher is required."
        exit 1
    fi
    if [ "$(python3 -c 'import sys; print(sys.version_info >= (3, 10))')" != "True" ]; then
        echo "Python 3.10 or higher is required."
        exit 1
    fi
}

get_repo() {
    # Already inside the repo (git clone or downloaded zip): use it as is.
    if [ -d "$CURRENT_DIR/pyUltroid" ] && [ -d "$CURRENT_DIR/plugins" ]; then
        DIR="$CURRENT_DIR"
        if [ -d "$DIR/.git" ]; then
            echo "Updating OWNER Assistant..."
            git -C "$DIR" pull -q || echo "git pull failed, continuing with local code."
        fi
        return
    fi
    if [ -d "$DIR/.git" ]; then
        echo "Updating OWNER Assistant in $DIR..."
        git -C "$DIR" pull -q
    elif [ -d "$DIR/pyUltroid" ]; then
        echo "Using existing OWNER Assistant in $DIR"
    else
        echo "Cloning $REPO ($BRANCH) into $DIR..."
        mkdir -p "$(dirname "$DIR")"
        git clone -q -b "$BRANCH" "$REPO" "$DIR" || exit 1
    fi
}

pip_install_file() {
    # install a requirements file line by line, so one broken optional
    # package does not stop the rest from installing
    [ -f "$1" ] || return
    tr -d '\r' <"$1" | grep -vE '^\s*(#|$)' | while read -r pkg; do
        # On Termux, opencv comes from `pkg install opencv-python`; building it
        # with pip takes hours, so skip it when cv2 already works.
        if [ -n "$TERMUX_VERSION" ] && [[ "$pkg" == opencv* ]] && python3 -c "import cv2" 2>/dev/null; then
            continue
        fi
        python3 -m pip install -q --no-cache-dir "$pkg" || echo "  skipped: $pkg"
    done
}

install_requirements() {
    cd "$DIR" || exit 1
    PIP_FLAGS=""
    python3 -m pip install -q --upgrade pip 2>/dev/null || PIP_FLAGS="--break-system-packages"
    export PIP_BREAK_SYSTEM_PACKAGES=1
    echo "Installing requirements..."
    if ! python3 -m pip install -q --no-cache-dir $PIP_FLAGS -r requirements.txt; then
        echo "Some requirements failed, retrying one by one..."
        pip_install_file requirements.txt
        python3 -c "import telethon, decouple, git, aiohttp" || {
            echo "Core requirements could not be installed. Fix the errors above and run again."
            exit 1
        }
    fi
    echo "Installing optional requirements..."
    pip_install_file resources/startup/optional-requirements.txt
    echo "Installing addons requirements..."
    pip_install_file addons/addons.txt
}

install_db_requirements() {
    if [ -n "$MONGO_URI" ]; then
        python3 -m pip install -q "pymongo[srv]"
    elif [ -n "$DATABASE_URL" ]; then
        python3 -m pip install -q psycopg2-binary
    elif [ -n "$REDIS_URI" ] || [ -n "$REDISHOST" ]; then
        python3 -m pip install -q redis hiredis
    fi
}

misc_install() {
    if [ -n "$SETUP_PLAYWRIGHT" ]; then
        python3 -m pip install -q playwright && python3 -m playwright install --with-deps chromium
    fi
    if [ -n "$VCBOT" ]; then
        if [ -d "$DIR/vcbot/.git" ]; then
            git -C "$DIR/vcbot" pull -q
        else
            git clone -q https://github.com/TeamUltroid/VcBot "$DIR/vcbot"
        fi
        python3 -m pip install -q "py-tgcalls" av
    fi
}

main() {
    echo "Starting OWNER Assistant setup..."
    if [ -f "$ENV_FILE_PATH" ]; then
        set -a
        # shellcheck disable=SC1090
        source <(tr -d '\r' <"$ENV_FILE_PATH" | sed -e '/^\s*#/d;/^\s*$/d')
        set +a
    fi
    install_system_packages
    check_python
    get_repo
    if [ -f "$ENV_FILE_PATH" ] && [ "$(realpath "$ENV_FILE_PATH")" != "$(realpath "$DIR/.env" 2>/dev/null)" ]; then
        cp "$ENV_FILE_PATH" "$DIR/.env"
    fi
    install_requirements
    install_db_requirements
    misc_install
    echo ""
    echo "Setup completed. Start the bot with:  cd $DIR && bash startup"
}

main
