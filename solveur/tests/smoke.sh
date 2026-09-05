#!/bin/sh
# Test de fumee du binaire : chaque exemple doit rendre un placement (ok: true) en temps borne.
#   ./tests/smoke.sh [chemin/vers/placement]      (defaut : ./build/placement)
set -e
cd "$(dirname "$0")/.."
BIN="${1:-./build/placement}"
[ -x "$BIN" ] || { echo "binaire introuvable : $BIN" >&2; exit 2; }
"$BIN" --version
fail=0
for ex in exemple_stick exemple_groupes exemple_tandems exemple_20_paras; do
  out="$("$BIN" "exemples/$ex.json" --temps 2 --silencieux)" || rc=$?
  if printf '%s' "$out" | grep -q '"ok": true'; then
    echo "ok   $ex"
  else
    echo "FAIL $ex (code ${rc:-0})"; printf '%s\n' "$out" | head -20; fail=1
  fi
done
# entree standard : meme resultat attendu
cat exemples/exemple_stick.json | "$BIN" - --temps 1 --silencieux | grep -q '"ok": true' && echo "ok   stdin" || { echo "FAIL stdin"; fail=1; }
exit $fail
