from zerodha_auth import ensure_session
from config import ENTRY_POLICY

_order_queue = []  # queued on session failure

def place_market(symbol:str, qty:int, side:str):
    # Manual token policy: ensure_session validates existing token (no auto-refresh)
    try:
        ensure_session()
    except Exception as e:
        # Queue and let caller decide to flush later
        _order_queue.append({'symbol':symbol,'qty':qty,'side':side,'policy':ENTRY_POLICY})
        return {'status':'queued','error':str(e)}
    print(f"[PAPER] ORDER {side} {symbol} x{qty} {ENTRY_POLICY['product']} {ENTRY_POLICY['order_type']}")
    return {'status':'ok','order_id':'paper-1','avg':'market'}

def flush_queue():
    placed=0
    failed=0
    tmp=list(_order_queue)
    _order_queue.clear()
    for it in tmp:
        try:
            ensure_session()
            print(f"[PAPER][FLUSH] {it['side']} {it['symbol']} x{it['qty']}")
            placed+=1
        except Exception:
            failed+=1
            _order_queue.append(it)
    return {'placed':placed,'failed':failed,'remaining':len(_order_queue)}
