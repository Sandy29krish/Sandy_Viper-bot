from zerodha_auth import ensure_session
from config import ENTRY_POLICY

def place_market(symbol:str, qty:int, side:str):
    # Manual token policy: ensure_session validates existing token (no auto-refresh)
    ensure_session()
    print(f"[PAPER] ORDER {side} {symbol} x{qty} {ENTRY_POLICY['product']} {ENTRY_POLICY['order_type']}")
    return {'status':'ok','order_id':'paper-1','avg':'market'}
