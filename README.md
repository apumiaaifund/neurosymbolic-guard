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



## 🚀 Quickstart для внешних инженеров (3 способа протестировать свои данные)

Сторонние инженеры и команды безопасности могут прогнать свои датасеты, JSON-контракты или телеметрию без передачи данных на внешние серверы:

### 1. Через веб-песочницу (без установки кода, за 10 секунд)
Откройте **[Live Safety Sandbox](https://github.io)**, выберите нужные модули в **Конструкторе решения**, загрузите локальный `.json` / `.csv` файл (или вставьте свой JSON) и нажмите **«Собрать конвейер и проверить данные»**. Все вычисления выполняются локально в браузере (Zero-Trust).

### 2. Через Python SDK в своём коде или `pytest`
```bash
pip install git+https://github.com
```
```python
from neurosymbolic_guard.robotics_adapters import RoboticsProtocolGuard, Ros2Twist

guard = RoboticsProtocolGuard()
safe_twist, verdict = guard.filter_ros2_twist(
    Ros2Twist(linear_x=2.4, angular_z=0.1),
    distance_to_human_m=1.2,
    distance_to_obstacle_m=3.5,
    floor_friction_coeff=0.8,
    battery_pct=85.0,
)
print(verdict.status, safe_twist.linear_x)
```

### 3. По сети через локальный REST / WebSocket шлюз
```bash
uvicorn neurosymbolic_guard.telemetry_server:app --port 8080
curl -X POST http://localhost:8080/api/v1/guard/evaluate \
  -H "Content-Type: application/json" \
  -d '{"distance_to_human_m": 1.2, "distance_to_obstacle_m": 3.5, "floor_friction_coeff": 0.8, "battery_pct": 85.0, "linear_velocity_ms": 2.4, "angular_velocity_rads": 0.1}'
```

## Модель Open-Core (Защита IP)
- **Открытый контур (этот репозиторий):** Python SDK (`@embodied_guard`), адаптеры ROS 2 / MAVLink, FastAPI/WebSocket шлюз телеметрии, тесты `pytest` и формат крипто-аудита.
- **Проприетарный контур (`private-core`):** компилируемое Zero-Panic Rust-ядро (`embodied_guard_rs` + `PyO3`) с кинематическими барьерами тормозного пути (`733,859 checks/sec`, `p99 = 1.333 µs`).

## Контакты
**Артем Шамурадов** — Founder & Architect (**Apumia Fund**) | `apumiaaifund@gmail.com` | [@apumiaaifund](https://github.com/apumiaaifund)

---

### 🚀 Что мы можем реализовать для партнёров на основе этого решения (Ниши и сценарии)

- **Корпоративный ИИ и Финтех:** интеграция детерминированного контроля, крипто-аудита и верификации данных в контур заказчика.
- **Промышленность и ИБ:** адаптация модулей под закрытые контуры (On-Premise) с соблюдением требований безопасности.

> **Формат сотрудничества:** запуск пилотного стенда (PoC) за 2–4 недели, лицензирование модуля (On-Premise) или кастомная интеграция под стек заказчика.  
> 📬 **Запросить демонстрацию и расчёт пилота:** [apumiaaifund@gmail.com](mailto:apumiaaifund@gmail.com)

---

### 🚀 Что мы можем реализовать для партнёров (Ниши и сценарии)

- **Корпоративный ИИ и Финтех:** детерминированный контроль, крипто-аудит и верификация данных.
- **Промышленность и ИБ:** адаптация модулей под закрытые контуры (On-Premise).

> 📬 **Запросить демонстрацию и расчёт пилота:** [apumiaaifund@gmail.com](mailto:apumiaaifund@gmail.com)

---

### 🛡️ Верификация качества (Apumia DevSecOps Gate)

> **Статус:** `VERIFIED & PROVEN` | `_synthetic: false` | `preservation: 100.0%` | `verified: true`
