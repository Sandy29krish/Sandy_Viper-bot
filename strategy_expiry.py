from datetime import datetime, timedelta
from config import AWARENESS, ENTRY_POLICY, TIME_WINDOWS, MARKET
from indicator import compute_1m, compute_3m
from nse_data import fetch_snapshot
from kite_api import place_market
from telegram_bot import send_entry, send_warn
from trade_logger import log
from lot_manager import decide_lots
from learning_engine import log_features
from lot_manager import can_open, register_entry
from config import OPTION_CONFIRM_MIN, OPTION_CONFIRM_MIN_HIGH_VIX, VIX_BANDS, EXIT_PARTIAL_PCT

def _band(strikes, atm, band, side):
    return [s for s in strikes if s.side==side and abs(s.strike-atm)<=band*50]

def pcr(snapshot, band=5):
    ce=sum(s.oi for s in _band(snapshot.strikes, snapshot.atm, band, 'CE'))
    pe=sum(s.oi for s in _band(snapshot.strikes, snapshot.atm, band, 'PE'))
    return (pe/ce) if ce>0 else 0.0

def skew(snapshot, band=2):
    ce=sum(s.oi for s in _band(snapshot.strikes, snapshot.atm, band, 'CE'))
    pe=sum(s.oi for s in _band(snapshot.strikes, snapshot.atm, band, 'PE'))
    return (ce/pe if pe>0 else 0.0, pe/ce if ce>0 else 0.0)

def choose_strike(fut_ltp:float, direction:str, now:datetime)->int:
    hhmm=now.strftime('%H:%M')
    round50=lambda x:int(round(x/50.0)*50)
    ceil50=lambda x:int(((x+49)//50)*50)
    floor50=lambda x:int((x//50)*50)
    if TIME_WINDOWS['morning'][0]<=hhmm<TIME_WINDOWS['morning'][1]:
        return ceil50(fut_ltp) if direction=='BULL' else floor50(fut_ltp)
    if TIME_WINDOWS['midday'][0]<=hhmm<TIME_WINDOWS['midday'][1]:
        return round50(fut_ltp)
    if TIME_WINDOWS['afternoon'][0]<=hhmm<TIME_WINDOWS['afternoon'][1]:
        return floor50(fut_ltp) if direction=='BULL' else ceil50(fut_ltp)
    return -1

# Placeholder for VIX and OI/Vol gates
def get_vix():
    return 15.0

def option_confirm_score(symbol:str)->float:
    # Weighted match of option MA stack, RSI, LR slope, OI/Vol
    # TODO: Implement with real option snapshot features
    return 0.8

def oi_volume_gate(symbol:str)->bool:
    # TODO: Implement PCR/skew/velocity checks using nse_data snapshots
    return True

# Hybrid 1m/3m execution controller (simplified)
_last_entry = {}

def run_once(symbol='NIFTY'):
    now=datetime.utcnow()+timedelta(hours=5,minutes=30)
    hhmm=now.strftime('%H:%M')
    if hhmm>=MARKET['force_exit']:
        send_warn('After force-exit window – manage only'); return
    snap=fetch_snapshot(symbol, 5)
    f1=compute_1m(symbol); f3=compute_3m(symbol)

    # Futures mandatory confirm
    direction='BULL' if f3.price_above_200wma else 'BEAR'
    if f3.lr_slope_3m < AWARENESS['lr_slope_min']:
        send_warn(f"{symbol} gate: lr slope {f3.lr_slope_3m:.2f} < {AWARENESS['lr_slope_min']}"); return

    # OI/Volume confirm
    if not oi_volume_gate(symbol):
        send_warn(f"{symbol} gate: OI/Volume not supportive"); return

    strike=choose_strike(snap.fut_ltp, direction, now)
    if strike<0 or hhmm>='14:00':
        send_warn('No new entries after 14:00'); return

    # Double confirmation (options weighted)
    vix = get_vix()
    thresh = OPTION_CONFIRM_MIN_HIGH_VIX if vix>=VIX_BANDS['high'] else OPTION_CONFIRM_MIN
    opt_score = option_confirm_score(symbol)
    if opt_score < thresh:
        send_warn(f"{symbol} gate: option confirm {opt_score:.2f} < {thresh:.2f}"); return

    side='CE' if direction=='BULL' else 'PE'
    lots=decide_lots(symbol, 0.95)

    # Exposure cap enforcement
    est_premium = 10.0  # TODO: fetch option LTP approx
    exposure = est_premium * lots  # lot size handled inside decide_lots
    if not can_open(symbol, exposure):
        send_warn(f"{symbol}: exposure/trade cap blocks entry"); return

    if ENTRY_POLICY['product']!='MIS' or ENTRY_POLICY['order_type']!='MARKET':
        send_warn('Only MIS + MARKET allowed'); return

    res=place_market(f'{symbol}{strike}{side}', lots, 'BUY')
    register_entry(symbol, exposure)

    send_entry({'symbol':symbol,'side':side,'strike':strike,'fut':snap.fut_ltp,'order':res})
    log({'event':'entry','symbol':symbol,'side':side,'strike':strike,'fut':snap.fut_ltp,'ts':now.isoformat()})
    log_features({'symbol':symbol,'side':side,'strike':strike,'vix':vix,'opt_score':opt_score})
