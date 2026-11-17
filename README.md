# 🛡️ APUMIA Guard — NeuroSymbolic & Embodied AI Safety Infrastructure

[![CI — Safety & Robotics Tests](https://github.com/apumiaaifund)](https://github.com/apumiaaifund)


**Детерминированный нейросимволический предохранитель для автономных ИИ-агентов (< 2 мс) и робототехники / VLA-моделей (733,859 проверок/сек, `p99 = 1.333 µs`).**

Гарантирует соблюдение финансовых лимитов, бизнес-правил и физических инвариантов безопасности до выполнения действия — без переобучения нейросетей и без зависимости от GPU.

## Архитектура и производительность
- **Cloud / Enterprise Core (Python + Z3 SMT):** верификация YAML-политик за `1.18–1.42 мс` + крипто-журнал WAL (`HMAC-SHA256`).
- **Edge / Robotics Core (Rust + PyO3 + ROS 2 / MAVLink):** `733,859 checks/sec`, `p50 = 1.167 µs`, `p99 = 1.333 µs` на ARM64, кинематические барьеры тормозного пути, защитная зона человека (`< 2.0 м`) и `EmergencyStop` при `NaN`/`Inf`.
- **Crypto FlightRecorder & Live WebSocket:** непрерывная хеш-цепочка FNV-1a и реальтайм-стриминг вердиктов для службы безопасности.

## Публичные материалы и SDK
- `index.html` / `deck/presentation.html` — интерактивный питч-дек ([Live на GitHub Pages](https://apumiaaifund.github.io/neurosymbolic-guard-demo/)).
- `ONE_PAGER.md` — краткое коммерческое описание для пилотов за 1 день.
- `neurosymbolic_guard/embodied_bridge.py` & `robotics_adapters.py` — декоратор `@embodied_guard` и адаптеры ROS 2 (`Twist`) / MAVLink.
- `neurosymbolic_guard/telemetry_server.py` — FastAPI REST + WebSocket шлюз телеметрии.


## Модель Open-Core (Защита IP)
- **Открытый контур (этот репозиторий):** Python SDK (`@embodied_guard`), адаптеры ROS 2 / MAVLink, FastAPI/WebSocket шлюз телеметрии, тесты `pytest` и формат крипто-аудита.
- **Проприетарный контур (`private-core`):** компилируемое Zero-Panic Rust-ядро (`embodied_guard_rs` + `PyO3`) с кинематическими барьерами тормозного пути (`733,859 checks/sec`, `p99 = 1.333 µs`).

## Контакты
**Артем Шамурадов** — Founder & Architect (**Apumia Fund**) | `apumiaaifund@gmail.com` | [@apumiaaifund](https://github.com/apumiaaifund)
