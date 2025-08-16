#!/usr/bin/env bash
set -euo pipefail

# deploy.sh – Subtree Deploy der mc_test_app direkt auf main ohne Force-Push
# Usage: ./deploy.sh [remote]
# Default remote: github
# Voraussetzungen: Arbeitsbaum sauber, Branch main lokal aktuell.

REMOTE="${1:-github}"
PREFIX_DIR="mc_test_app"
TMP_BRANCH="deploy-mc-test"
TARGET_BRANCH="main"

# --- Helper Functions -------------------------------------------------------
err() { echo "[ERROR] $*" >&2; exit 1; }
info() { echo "[INFO] $*"; }

# --- Preconditions -----------------------------------------------------------
command -v git >/dev/null 2>&1 || err "git nicht gefunden"
[ -d "$PREFIX_DIR" ] || err "Verzeichnis $PREFIX_DIR fehlt"

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || err "Kein Git-Repository"

git remote get-url "$REMOTE" >/dev/null 2>&1 || err "Remote $REMOTE nicht konfiguriert"

# Arbeitsbaum sauber?
if ! git diff --quiet || ! git diff --cached --quiet; then
  err "Arbeitsbaum oder Staging Area nicht leer – bitte committen oder stashen"
fi

# main existiert lokal?
if ! git show-ref --verify --quiet "refs/heads/$TARGET_BRANCH"; then
  err "Lokaler Branch '$TARGET_BRANCH' fehlt"
fi

# Remote Daten holen
info "Fetch vom Remote ($REMOTE)..."
git fetch "$REMOTE" "$TARGET_BRANCH"

# Divergenz prüfen
LOCAL_HASH=$(git rev-parse "$TARGET_BRANCH")
REMOTE_HASH=$(git rev-parse "refs/remotes/$REMOTE/$TARGET_BRANCH" || echo none)
if [ "$REMOTE_HASH" != "none" ] && [ "$LOCAL_HASH" != "$REMOTE_HASH" ]; then
  err "Lokaler $TARGET_BRANCH ($LOCAL_HASH) != Remote ($REMOTE_HASH). Bitte zuerst synchronisieren (git pull)."
fi

# Vorherigen Temp-Branch entfernen falls vorhanden
if git show-ref --verify --quiet "refs/heads/$TMP_BRANCH"; then
  info "Lösche existierenden temporären Branch $TMP_BRANCH"
  git branch -D "$TMP_BRANCH"
fi

info "Erzeuge Subtree Split für $PREFIX_DIR ..."
SPLIT_HASH=$(git subtree split --prefix "$PREFIX_DIR" -b "$TMP_BRANCH")
info "Split Hash: $SPLIT_HASH"

info "Push auf $REMOTE/$TARGET_BRANCH (ohne --force) ..."
git push "$REMOTE" "$TMP_BRANCH:$TARGET_BRANCH"

info "Aufräumen: Lösche temporären Branch"
git branch -D "$TMP_BRANCH"

info "Fertig. Deployment-Branch '$TARGET_BRANCH' aktualisiert."
