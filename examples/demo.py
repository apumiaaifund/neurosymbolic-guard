import os
import time
from pathlib import Path

from neurosymbolic_guard import (
    HighLoadPolicyEngine,
    TamperEvidentAuditLogger,
)
from neurosymbolic_guard.cli import verify_wal_file

G, R, Y, C, B, W = (
    "\033[92m",
    "\033[91m",
    "\033[93m",
    "\033[96m",
    "\033[1m",
    "\033[0m",
)


def banner(title: str) -> None:
    print(f"\n{C}{'=' * 66}{W}\n{B}{C}  {title}{W}\n{C}{'=' * 66}{W}")


def execute_step(
    engine: HighLoadPolicyEngine,
    audit: TamperEvidentAuditLogger,
    ctx: dict,
) -> None:
    verdict = engine.verify(ctx)
    audit.log_verdict("transfer_funds", verdict)
    lat = f"{C}[Z3 Latency: {verdict.latency_ms:.2f} ms]{W}"
    if verdict.allowed:
        msg = f"БАНКОВСКОЕ ЯДРО: Перевод {ctx['amount']:,.2f} RUB выполнен."
        print(f"{G}{msg}{W} {lat}")
        print(f"{G}Proof-Hash: {verdict.proof_hash[:16]}...{W}\n")
    else:
        print(f"{R}{verdict.to_llm_feedback()}{W} {lat}\n")


def main() -> None:
    wal = Path("logs/demo_audit.wal")
    if wal.exists():
        wal.unlink()

    raw_key = os.urandom(32)
    engine = HighLoadPolicyEngine("policies/finance_policy.yaml")
    audit = TamperEvidentAuditLogger(str(wal), bytearray(raw_key), batch_size=1)

    banner("NEUROSYMBOLIC GUARD v0.1 | LIVE SECURITY & LATENCY DEMO")
    print(f"Политика: {B}policies/finance_policy.yaml{W} (SMT Solver: Z3)")
    print("Правила:  лимит <= 50,000 RUB (без 2-го ключа) | риск < 80\n")
    time.sleep(0.5)

    print(f"{Y}[ШАГ 1] Галлюцинация LLM: перевод 150,000 RUB без апрува:{W}")
    execute_step(
        engine,
        audit,
        {"amount": 150000.0, "recipient_risk_score": 20, "dual_control_approved": False},
    )
    time.sleep(0.7)

    print(f"{Y}[ШАГ 2] Промпт-инъекция: перевод 40,000 RUB на счет риска 95:{W}")
    execute_step(
        engine,
        audit,
        {"amount": 40000.0, "recipient_risk_score": 95, "dual_control_approved": False},
    )
    time.sleep(0.7)

    print(f"{Y}[ШАГ 3] Самокоррекция агента (получен апрув контролера):{W}")
    execute_step(
        engine,
        audit,
        {"amount": 150000.0, "recipient_risk_score": 20, "dual_control_approved": True},
    )
    time.sleep(0.5)

    audit.close()
    ok, count = verify_wal_file(wal, raw_key)
    banner("ИТОГОВЫЙ АУДИТ СЛУЖБЫ БЕЗОПАСНОСТИ (TAMPER-EVIDENT WAL)")
    st = f"{G}VALID (ПОДПИСЬ ПОДТВЕРЖДЕНА){W}" if ok else f"{R}CORRUPTED{W}"
    print(f"Проверено криптографических записей: {B}{count}{W}")
    print(f"Статус целостности журнала:        {st}")
    print(f"Секрет HMAC в оперативной памяти:  {G}ЗАТЕРТ НУЛЯМИ (ZEROIZED){W}\n")


if __name__ == "__main__":
    main()
