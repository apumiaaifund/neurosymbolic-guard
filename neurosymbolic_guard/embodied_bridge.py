from __future__ import annotations

import functools
import json
from dataclasses import dataclass
from typing import Any, Callable, TypeVar

try:
    from embodied_guard_py import EmbodiedGuard as _RustEmbodiedGuard
    RUST_CORE_AVAILABLE = True
except ImportError:
    _RustEmbodiedGuard = None
    RUST_CORE_AVAILABLE = False

F = TypeVar("F", bound=Callable[..., Any])


@dataclass(frozen=True)
class EdgeVerdict:
    status: str
    reason: str
    safe_linear_velocity_ms: float
    safe_angular_velocity_rads: float
    latency_us: int
    backend: str


class EmbodiedEdgeShield:
    """Гибридный мост между Python-оркестратором/VLA и нативным Rust Edge Core."""

    def __init__(self) -> None:
        self._rust_guard = _RustEmbodiedGuard() if RUST_CORE_AVAILABLE else None

    @property
    def backend(self) -> str:
        return "rust-edge-core" if self._rust_guard is not None else "python-failsafe"

    def evaluate(
        self,
        *,
        distance_to_human_m: float,
        distance_to_obstacle_m: float,
        floor_friction_coeff: float,
        battery_pct: float,
        linear_velocity_ms: float,
        angular_velocity_rads: float = 0.0,
    ) -> EdgeVerdict:
        if self._rust_guard is not None:
            status, reason, safe_lin, safe_ang, latency_us = self._rust_guard.evaluate(
                distance_to_human_m=distance_to_human_m,
                distance_to_obstacle_m=distance_to_obstacle_m,
                floor_friction_coeff=floor_friction_coeff,
                battery_pct=battery_pct,
                linear_velocity_ms=linear_velocity_ms,
                angular_velocity_rads=angular_velocity_rads,
            )
            return EdgeVerdict(
                status=status,
                reason=reason,
                safe_linear_velocity_ms=safe_lin,
                safe_angular_velocity_rads=safe_ang,
                latency_us=int(latency_us),
                backend="rust-edge-core",
            )

        # Fail-closed fallback если C-расширение не собрано
        return EdgeVerdict(
            status="EmergencyStop",
            reason="Rust edge core unavailable (fail-closed mode)",
            safe_linear_velocity_ms=0.0,
            safe_angular_velocity_rads=0.0,
            latency_us=0,
            backend="python-failsafe",
        )

    def verify_chain(self) -> bool:
        if self._rust_guard is not None:
            return bool(self._rust_guard.verify_chain())
        return False

    def export_audit_dict(self) -> dict[str, Any]:
        if self._rust_guard is not None:
            return json.loads(self._rust_guard.export_audit_json())
        return {"chain_valid": False, "records": []}


def embodied_guard(shield: EmbodiedEdgeShield) -> Callable[[F], F]:
    """Декоратор для перехвата и верификации команд актуатора в реальном времени."""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            sensors = kwargs["sensors"]
            verdict = shield.evaluate(
                distance_to_human_m=sensors["distance_to_human_m"],
                distance_to_obstacle_m=sensors["distance_to_obstacle_m"],
                floor_friction_coeff=sensors["floor_friction_coeff"],
                battery_pct=sensors["battery_pct"],
                linear_velocity_ms=kwargs["linear_velocity_ms"],
                angular_velocity_rads=kwargs.get("angular_velocity_rads", 0.0),
            )
            kwargs["linear_velocity_ms"] = verdict.safe_linear_velocity_ms
            kwargs["angular_velocity_rads"] = verdict.safe_angular_velocity_rads
            kwargs["edge_verdict"] = verdict
            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator
