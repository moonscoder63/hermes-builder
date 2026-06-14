#!/usr/bin/env python3
"""rubik per-tenant skills bridge: env HERMES_SKILLS_DISABLED → config.yaml.

rubik-platform (apply-skills) шлёт DISABLED-список скиллов в формате
`<category>/<name>` (effectiveDisabledSkills), handler пишет его в env
HERMES_SKILLS_DISABLED. Агент же читает `config.yaml: skills.disabled`, НЕ env.
Этот скрипт (cont-init, на каждый старт контейнера) транслирует env → config,
используя собственную машинерию агента (load_config/save_disabled_skills из
hermes_cli — сохраняет формат config'а через ruamel).

Семантика env HERMES_SKILLS_DISABLED:
  - не задан (None)  → rubik не применял → НЕ трогаем (дефолт агента)
  - "-"              → rubik явно «ничего не отключать» → disabled = []
  - "a/b,c/d"        → отключить эти скиллы
Имена `<category>/<name>` совпадают 1:1 с путями скиллов агента (skills/<cat>/<name>).
Лишние (несуществующие у агента) — безвредны (агент игнорирует unknown disabled).
"""
import os
import sys


def main() -> int:
    raw = os.environ.get("HERMES_SKILLS_DISABLED")
    if raw is None:
        return 0  # rubik не настраивал skills → оставляем дефолт агента
    items = set() if raw.strip() == "-" else {s for s in raw.split(",") if s.strip()}

    try:
        from hermes_cli.config import load_config
        from hermes_cli.skills_config import save_disabled_skills
    except Exception as e:  # noqa: BLE001
        print(f"[rubik-skills] import failed (non-fatal): {e}", file=sys.stderr)
        return 0

    try:
        cfg = load_config()
        save_disabled_skills(cfg, items)  # config["skills"]["disabled"] = sorted(items); save_config
    except Exception as e:  # noqa: BLE001
        print(f"[rubik-skills] apply failed (non-fatal): {e}", file=sys.stderr)
        return 0

    print(f"[rubik-skills] disabled={len(items)} skills applied to config.yaml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
