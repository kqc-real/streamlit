#!/usr/bin/env bash
set -euo pipefail

# mc_test_app/deploy.sh – Subtree Deploy der mc_test_app direkt auf main ohne Force-Push
# Usage: ./mc_test_app/deploy.sh [remote]
# Default remote: github
# Voraussetzungen: Arbeitsbaum sauber, Branch main lokal aktuell.

REMOTE="${1:-github}"
AUTO_FF=0
if [ "${2:-}" = "--auto-ff" ]; then
  AUTO_FF=1
fi
PREFIX_DIR="mc_test_app"
TMP_BRANCH="deploy-mc-test"
TARGET_BRANCH="main"

err() { echo "[ERROR] $*" >&2; exit 1; }
info() { echo "[INFO] $*"; }

command -v git >/dev/null 2>&1 || err "git nicht gefunden"
[ -d "$PREFIX_DIR" ] || err "Verzeichnis $PREFIX_DIR fehlt"
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || err "Kein Git-Repository"
if ! git remote get-url "$REMOTE" >/dev/null 2>&1; then
  if [ "$REMOTE" != "origin" ] && git remote get-url origin >/dev/null 2>&1; then
    info "Remote '$REMOTE' nicht gefunden – falle zurück auf 'origin'"
    REMOTE="origin"
  else
    err "Remote $REMOTE nicht konfiguriert"
  fi
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  err "Arbeitsbaum oder Staging Area nicht leer – bitte committen oder stashen"
fi

if ! git show-ref --verify --quiet "refs/heads/$TARGET_BRANCH"; then
  err "Lokaler Branch '$TARGET_BRANCH' fehlt"
fi

info "Fetch vom Remote ($REMOTE)..."
git fetch "$REMOTE" "$TARGET_BRANCH"

LOCAL_HASH=$(git rev-parse "$TARGET_BRANCH")
REMOTE_HASH=$(git rev-parse "refs/remotes/$REMOTE/$TARGET_BRANCH" || echo none)
if [ "$REMOTE_HASH" != "none" ] && [ "$LOCAL_HASH" != "$REMOTE_HASH" ]; then
  if [ $AUTO_FF -eq 1 ]; then
    # Prüfen ob lokaler nur hinterher hängt (lokaler Commit ist Vorfahr des Remote)
    if git merge-base --is-ancestor "$LOCAL_HASH" "$REMOTE_HASH"; then
      info "Lokaler Branch hinter Remote – führe Fast-Forward Pull aus (--auto-ff)."
      git pull --ff-only "$REMOTE" "$TARGET_BRANCH"
      LOCAL_HASH=$(git rev-parse "$TARGET_BRANCH")
      if [ "$LOCAL_HASH" != "$REMOTE_HASH" ]; then
        err "Fast-Forward Pull hat Hash nicht angeglichen – Abbruch."
      fi
    else
      err "Divergenz (lokal nicht Vorfahr). Manuelles Rebase/Merge nötig oder ohne --auto-ff kein Deploy."
    fi
  else
    err "Lokaler $TARGET_BRANCH ($LOCAL_HASH) != Remote ($REMOTE_HASH). Bitte zuerst synchronisieren (git pull) oder --auto-ff nutzen."
  fi
fi

if git show-ref --verify --quiet "refs/heads/$TMP_BRANCH"; then
  info "Lösche existierenden temporären Branch $TMP_BRANCH"
  git branch -D "$TMP_BRANCH"
fi

info "Erzeuge Subtree Split für $PREFIX_DIR ..."
SPLIT_HASH=$(git subtree split --prefix "$PREFIX_DIR" -b "$TMP_BRANCH")
info "Split Hash: $SPLIT_HASH"

# Falls der zuletzt deployte Commit (REMOTE_HASH) identisch mit dem neuen Subtree-Split ist,
# wurden innerhalb von mc_test_app/ keine Änderungen vorgenommen → Deployment überspringen.
if [ "$REMOTE_HASH" = "$SPLIT_HASH" ]; then
  info "Keine Änderungen im Subtree $PREFIX_DIR seit letztem Deployment – überspringe Push."
  git branch -D "$TMP_BRANCH"
  exit 0
fi

info "Push auf $REMOTE/$TARGET_BRANCH (ohne --force) ..."
git push "$REMOTE" "$TMP_BRANCH:$TARGET_BRANCH"

info "Aufräumen: Lösche temporären Branch"
git branch -D "$TMP_BRANCH"

info "Fertig. Deployment aktualisiert."
