# rubik-platform per-tenant Hermes runtime — тонкий adapter поверх hermes-agent.
#
# Зачем: оркестратор rubik-platform запускает per-tenant контейнер с hardened
# sandbox (--read-only --cap-drop ALL --no-new-privileges), данные в /data,
# env TELEGRAM_BOT_TOKEN/OPENAI_API_KEY/HERMES_SKILLS_ALLOWED/HERMES_LLM_*.
# Upstream-образ стартует root + s6-setuidgid дропает на hermes (нужны
# CAP_SETGID/SETUID, которых нет под --cap-drop ALL) и хардкодит /opt/data.
#
# Этот overlay (БЕЗ пересборки агента):
#   1. USER 10000 — стартуем сразу как hermes → s6 не дропает привилегии
#      (main-wrapper.drop() и dashboard/run уже гейтят non-root).
#   2. HERMES_HOME=/data + патч хардкода /opt/data в main-wrapper/dashboard →
#      состояние в /data (персистентный mount handler'а), не в анонимном
#      VOLUME /opt/data.
#
# Сборка: docker build -t ghcr.io/moonscoder63/hermes-runtime:stable
#         (вторая build-цель в hermes-builder, см. workflow).
ARG BASE=ghcr.io/moonscoder63/hermes-agent:isolated
FROM ${BASE}

ENV HERMES_HOME=/data

# Патчим хардкод /opt/data → $HERMES_HOME в скриптах, которые задают HOME/cd
# до запуска агента. Остальное состояние уже идёт через HERMES_HOME (аудит Q2).
USER root
RUN set -eu; \
    for f in /opt/hermes/docker/main-wrapper.sh /etc/s6-overlay/s6-rc.d/dashboard/run; do \
      [ -f "$f" ] || continue; \
      sed -i 's#export HOME=/opt/data#export HOME="${HERMES_HOME:-/opt/data}"#g; s#^cd /opt/data#cd "${HERMES_HOME:-/opt/data}"#g' "$f"; \
    done

# Стартуем как hermes (uid 10000) → s6-setuidgid не вызывается (guard'ы non-root).
USER 10000

# ENTRYPOINT наследуется от базы: /init /opt/hermes/docker/main-wrapper.sh
