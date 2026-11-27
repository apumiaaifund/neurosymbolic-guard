from src.mcp_server import handle_request, verify_zero_float


def test_ok() -> None:
    assert verify_zero_float("10.00", "10.00")["passed"] is True
    assert handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize"})["id"] == 1
