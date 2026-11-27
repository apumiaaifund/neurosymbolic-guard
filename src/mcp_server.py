from __future__ import annotations

import hashlib
import json
import sys
from decimal import Decimal, getcontext
from typing import Any

getcontext().prec = 28


def verify_zero_float(lhs: str, rhs: str) -> dict[str, Any]:
    a, b = Decimal(lhs), Decimal(rhs)
    ok = a == b
    h = hashlib.sha256(f"{a}|{b}|{ok}".encode()).hexdigest()
    return {"passed": ok, "lhs": str(a), "rhs": str(b), "sha256": h}


def handle_request(req: dict[str, Any]) -> dict[str, Any]:
    rid = req.get("id")
    m = req.get("method", "")
    if m == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": rid,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "apumia-mcp-verifier", "version": "1.0.0"},
            },
        }
    if m == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": rid,
            "result": {
                "tools": [
                    {
                        "name": "verify_zero_float",
                        "description": "Deterministic Decimal verifier",
                        "inputSchema": {
                            "type": "object",
                            "properties": {"lhs": {"type": "string"}, "rhs": {"type": "string"}},
                            "required": ["lhs", "rhs"],
                        },
                    }
                ]
            },
        }
    if m == "tools/call":
        args = (req.get("params") or {}).get("arguments") or {}
        res = verify_zero_float(str(args.get("lhs", "0")), str(args.get("rhs", "0")))
        return {
            "jsonrpc": "2.0",
            "id": rid,
            "result": {"content": [{"type": "text", "text": json.dumps(res)}], "isError": False},
        }
    return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": "Method not found"}}


def main() -> None:
    for line in sys.stdin:
        if line.strip():
            sys.stdout.write(json.dumps(handle_request(json.loads(line))) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
