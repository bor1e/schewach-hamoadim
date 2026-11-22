#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE="$(tr -d '[:space:]' < "$ROOT/VERSION")"
if git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    LATEST_TAG="$(git -C "$ROOT" tag -l 'v*' --sort=-v:refname | head -n 1 || true)"
    if [[ -n "$LATEST_TAG" ]]; then
        BASE="${LATEST_TAG#v}"
    fi
    REV="$(git -C "$ROOT" rev-list --count HEAD 2>/dev/null || echo 0)"
    HASH="$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo "init")"
    DIRTY=""
    if ! git -C "$ROOT" diff --quiet 2>/dev/null; then
        DIRTY="+"
    fi
    echo "${BASE} · r${REV} · ${HASH}${DIRTY}"
else
    echo "${BASE}"
fi
