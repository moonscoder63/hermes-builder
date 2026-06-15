#!/usr/bin/env python3
"""rubik per-tenant LLM bridge: env (LiteLLM endpoint + выбранная модель) → config.yaml.

Биллинг-модель rubik-platform: клиент НЕ подключает свой ключ. Он платит токенами
с баланса, а все LLM-вызовы агента роутятся через наш LiteLLM-gateway (OpenAI-
совместимый). Клиент выбирает модель в ЛК (вкладка «Модель») — она работает везде
(Telegram + web-chat), история общая (одна /data state.db).

Механика:
  handler пишет env:
    LITELLM_URL        — base_url нашего gateway (OpenAI-совместимый /v1)
    OPENAI_API_KEY     — per-tenant virtual-key (sk-rubik...), его LiteLLM мапит
                         в user_id → usage_events → debitWallet. Пишется apply-openai-key.
    HERMES_LLM_MODEL   — выбранная клиентом модель (apply-config). "" / не задан → дефолт.
  агент же читает config.yaml: model.base_url / model.default (НЕ env, кроме fallback
  api_key→OPENAI_API_KEY и gate-проверки наличия ключа).

Этот скрипт (cont-init, на каждый старт) транслирует env → config через машинерию
агента (load_config/save_config, ruamel — сохраняет формат). model.base_url имеет
приоритет над provider, поэтому provider не трогаем.

  model.base_url  = LITELLM_URL (или OPENAI_BASE_URL)   — куда роутить
  model.default   = HERMES_LLM_MODEL                    — какую модель звать
  model.api_key   — оставляем "", агент берёт OPENAI_API_KEY из env (gate + ключ)

Non-fatal: любая ошибка логируется, init контейнера не валится.
"""
import os
import sys


def main() -> int:
    base_url = (os.environ.get("LITELLM_URL") or os.environ.get("OPENAI_BASE_URL") or "").strip()
    model = (os.environ.get("HERMES_LLM_MODEL") or "").strip()
    if not base_url and not model:
        return 0  # rubik не настраивал LLM → оставляем дефолт агента

    try:
        from hermes_cli.config import load_config, save_config
    except Exception as e:  # noqa: BLE001
        print(f"[rubik-model] import failed (non-fatal): {e}", file=sys.stderr)
        return 0

    try:
        cfg = load_config()
        m = cfg.get("model")
        if not isinstance(m, dict):
            m = {}
            cfg["model"] = m
        if base_url:
            m["base_url"] = base_url  # OpenAI-совместимый LiteLLM gateway; приоритет над provider
        if model:
            m["default"] = model      # выбор клиента из ЛК
        save_config(cfg)
    except Exception as e:  # noqa: BLE001
        print(f"[rubik-model] apply failed (non-fatal): {e}", file=sys.stderr)
        return 0

    print(f"[rubik-model] base_url={'set' if base_url else 'kept'} model={model or 'kept'} applied to config.yaml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
