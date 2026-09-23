#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/build.pid"
LOG_FILE="$SCRIPT_DIR/build.log"
OVERLEAF_DIR="$SCRIPT_DIR/../overleaf"
SERVER_CE_DIR="$SCRIPT_DIR/../server-ce"

check_running() {
    if [ -f "$PID_FILE" ]; then
        local old_pid
        old_pid=$(cat "$PID_FILE" 2>/dev/null)
        if [ -n "$old_pid" ] && kill -0 "$old_pid" 2>/dev/null; then
            echo "Error: An operation is already running (PID: $old_pid)." >&2
            exit 1
        fi
    fi
}

print_bg_instructions() {
    local action="$1"
    local pid="$2"
    echo "--------------------------------------------------------"
    echo "${action} is now running in the background (PID: ${pid})."
    echo "Logs are being written to: ${LOG_FILE}"
    echo "To view progress in real-time, run:"
    echo "  tail -F ${LOG_FILE}"
    echo "  or: $0 logs"
    echo "To check status, run:"
    echo "  $0 status"
    echo "To stop the process, run:"
    echo "  $0 stop"
    echo "--------------------------------------------------------"
}

ACTION="${1:-}"

case "$ACTION" in
    start)
        check_running

        if [ -d "$OVERLEAF_DIR/.git" ]; then
            echo "Restoring and updating existing Overleaf repository..."
            git -C "$OVERLEAF_DIR" checkout -- .
            git -C "$OVERLEAF_DIR" clean -fd
            git -C "$OVERLEAF_DIR" pull origin main
        else
            echo "Cloning Overleaf repository..."
            git clone -b main https://github.com/overleaf/overleaf "$OVERLEAF_DIR"
        fi

        read -p "Press enter to continue"

        echo "Starting build in the background..."

        set -m
        (
            trap 'rm -f "$PID_FILE"' EXIT INT TERM HUP
            echo "--- Build started at $(date) ---"

            cp -r "$SERVER_CE_DIR/." "$OVERLEAF_DIR/server-ce/"

            set +e
            ( cd "$SERVER_CE_DIR" && make MONOREPO_ROOT="$OVERLEAF_DIR" )
            RESULT=$?
            set -e

            if [ $RESULT -eq 0 ]; then
                echo "Build completed successfully!"
            else
                echo "Build failed with exit code $RESULT."
            fi

            echo "--- Build process finished at $(date) ---"
        ) > "$LOG_FILE" 2>&1 &

        BUILD_PID=$!
        echo "$BUILD_PID" > "$PID_FILE"
        set +m

        print_bg_instructions "Build" "$BUILD_PID"
        ;;

    push)
        check_running

        echo "Starting push in the background..."

        set -m
        (
            trap 'rm -f "$PID_FILE"' EXIT INT TERM HUP
            echo "--- Push started at $(date) ---"

            set +e
            ( cd "$SERVER_CE_DIR" && make push )
            RESULT=$?
            set -e

            if [ $RESULT -eq 0 ]; then
                echo "Push completed successfully!"
            else
                echo "Push failed with exit code $RESULT."
            fi

            echo "--- Push process finished at $(date) ---"
        ) > "$LOG_FILE" 2>&1 &

        PUSH_PID=$!
        echo "$PUSH_PID" > "$PID_FILE"
        set +m

        print_bg_instructions "Push" "$PUSH_PID"
        ;;

    clean)
        rm -f "$PID_FILE" "$LOG_FILE"
        rm -rf "$OVERLEAF_DIR"
        echo "Overleaf repository directory removed."
        ;;

    logs)
        if [ -f "$LOG_FILE" ]; then
            tail -F "$LOG_FILE"
        else
            echo "No log file found ($LOG_FILE)."
        fi
        ;;

    status)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE" 2>/dev/null)
            if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
                echo "Operation is running (PID: $PID)."
                echo
                if command -v pstree >/dev/null 2>&1; then
                    pstree -ap "$PID"
                    echo
                fi
                ps -f --pid "$PID" --ppid "$PID"
            else
                echo "Operation is not running, but stale PID file exists ($PID_FILE)."
            fi
        else
            echo "No operation is running."
        fi
        ;;

    stop)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE" 2>/dev/null)
            PGID=$(ps -o pgid= -p "$PID" 2>/dev/null | tr -d ' ')
            [ -n "$PGID" ] && kill -9 -"$PGID" 2>/dev/null || kill -9 "$PID" 2>/dev/null
            rm -f "$PID_FILE"
            echo "Process stopped (PID: $PID)."
        else
            echo "No PID file found ($PID_FILE)."
        fi
        ;;

    *)
        echo "Usage: $0 {start|push|clean|logs|status|stop}"
        exit 1
        ;;
esac