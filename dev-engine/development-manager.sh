#!/data/data/com.termux/files/usr/bin/bash
set -e

DEV="$HOME/corvus-dev"
LIVE="$HOME/corvus"
STAGE="$DEV/staging/corvus"

case "$1" in
  status)
    echo "=== CORVUS DEVELOPMENT MANAGER ==="
    echo "Live: $(git -C "$LIVE" rev-parse --short HEAD)"
    echo "Staging: $(git -C "$STAGE" rev-parse --short HEAD)"

    if [ -n "$(git -C "$LIVE" status --porcelain)" ]; then
      echo "Live tree: DIRTY"
    else
      echo "Live tree: CLEAN"
    fi

    if [ -n "$(git -C "$STAGE" status --porcelain)" ]; then
      echo "Staging tree: DIRTY"
    else
      echo "Staging tree: CLEAN"
    fi

    if ls "$DEV"/changes/current-* >/dev/null 2>&1; then
      echo "Active state: PRESENT"
    else
      echo "Active state: NONE"
    fi
    ;;

  prepare)
    JOB="$2"

    [ -f "$JOB" ] || {
      echo "MANAGER: BLOCKED - job required"
      exit 1
    }

    "$DEV/start-job.sh" "$JOB"
    echo "MANAGER: PREPARE PASS"
    ;;

  test)
    JOB="$2"

    [ -f "$JOB" ] || {
      echo "MANAGER: BLOCKED - job required"
      exit 1
    }

    "$DEV/test-or-rollback.sh" "$JOB"
    echo "MANAGER: TEST PASS"
    ;;

  fingerprint)
    HASH="$("$DEV/candidate-hash.py")"

    [ -n "$(git -C "$STAGE" status --porcelain)" ] || {
      echo "MANAGER: BLOCKED - no candidate"
      exit 27
    }

    printf '%s\n' "$HASH" > "$DEV/changes/current-candidate.sha256"

    echo "CANDIDATE SHA256: $HASH"
    echo "MANAGER: FINGERPRINT PASS"
    ;;

  verify)
    "$DEV/check-candidate-hash.sh"
    echo "MANAGER: VERIFY PASS"
    ;;

  approve)
    JOB="$2"

    [ -f "$JOB" ] || {
      echo "MANAGER: BLOCKED - job required"
      exit 1
    }

    "$DEV/check-candidate-hash.sh"
    "$DEV/approve-candidate.py" "$JOB"
    "$DEV/check-candidate-approval.py" "$JOB"
    "$DEV/set-job-status.py" "$JOB" approved
    "$DEV/update-current-report.sh" approved

    echo "MANAGER: APPROVAL PASS"
    ;;

  promote)
    JOB="$2"

    [ -f "$JOB" ] || {
      echo "MANAGER: BLOCKED - job required"
      exit 1
    }

    "$DEV/promote.py" "$JOB"
    "$DEV/update-current-report.sh" promoted

    echo "MANAGER: PROMOTION PASS"
    ;;

  live-test)
    JOB="$2"

    [ -f "$JOB" ] || {
      echo "MANAGER: BLOCKED - job required"
      exit 1
    }

    "$DEV/check-promotion.py" "$JOB"
    "$DEV/validate-live.sh"

    echo "MANAGER: LIVE TEST PASS"
    ;;

  *)
    echo "Usage: development-manager.sh status|prepare|test|fingerprint|verify|approve|promote|live-test JOB"
    exit 1
    ;;
esac
