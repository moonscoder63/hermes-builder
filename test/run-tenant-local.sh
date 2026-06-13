#!/usr/bin/env bash
# Локальный harness: запускает per-tenant runtime с ТОЧНЫМИ флагами handler'а
# (scripts/orchestrator-handler.sh provision_tenant в rubik-platform), чтобы
# итерировать adapter локально за секунды вместо 30-мин прод-VPS цикла.
#
# Usage: ./run-tenant-local.sh <image> [tenant_id]
#   ./run-tenant-local.sh ghcr.io/moonscoder63/hermes-runtime:stable    # база (repro краша)
#   ./run-tenant-local.sh rubik-tenant:dev                              # adapter
#
# Отличие от прода: НЕТ userns-remap (Docker Desktop) — base-boot ловит здесь,
# userns-perms финально проверяются на live-VPS (T7).
set -u
IMG="${1:?usage: run-tenant-local.sh <image> [tid]}"
TID="${2:-localtest}"
NAME="hermes-${TID}"
# Bind-источник — НЕ на кириллическом пути (Docker Desktop не монтирует пути с
# кириллицей; репо лежит в C:/Проекты/...). Кладём в нейтральный каталог.
DATADIR="/c/Users/vlada/dockerdata/hermes-${TID}"
export MSYS_NO_PATHCONV=1

docker rm -f "$NAME" >/dev/null 2>&1 || true
rm -rf "$DATADIR"; mkdir -p "$DATADIR"; chmod 777 "$DATADIR"  # uid 10000 пишет (на проде — userns+chown)

# Флаги 1:1 как в provision_tenant handler'а (+ env, которые он пишет в .env тенанта).
docker run -d --name "$NAME" \
  --restart no \
  --network bridge \
  --cpus 1.0 --memory 1g --memory-swap 1g --pids-limit 200 \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=50m \
  --tmpfs /run:rw,exec,nosuid,nodev,size=16m,mode=1777 \
  -e S6_READ_ONLY_ROOT=1 \
  --security-opt no-new-privileges \
  --cap-drop ALL \
  -v "${DATADIR}:/data:rw" \
  -e TENANT_ID="${TID}" \
  -e LITELLM_URL="http://host.docker.internal:8899/v1" \
  -e HERMES_DATA_DIR=/data \
  "$IMG" >/dev/null 2>&1
RC=$?
echo "docker run rc=$RC"

sleep 10
echo "=== status ==="
docker ps -a --filter "name=${NAME}" --format "{{.Status}}"
echo "=== logs (tail 30) ==="
docker logs "$NAME" 2>&1 | tail -30
echo "=== /data содержимое (что записал агент) ==="
ls -la "$DATADIR" 2>/dev/null | head
