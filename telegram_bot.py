import os
import requests

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN_EXPIRY')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID_EXPIRY')
API = f"https://api.telegram.org/bot{TOKEN}/sendMessage" if TOKEN else None

def _send_text(text: str):
    if not (TOKEN and CHAT_ID and API):
        print('TG (mock):', text)
        return
    try:
        requests.post(API, json={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except Exception as e:
        print('TG error:', e)

def send(msg: str) -> None:
    _send_text(msg)

def send_entry(ctx: dict) -> None:
    symbol = ctx.get('symbol','NIFTY')
    side = ctx.get('side','CE')
    strike = ctx.get('strike',0)
    fut = ctx.get('fut',0.0)
    order = ctx.get('order',{})
    arrow = '🔺' if side=='CE' else '🔻'
    text = (
        f"🚀 {symbol} {('CALL' if side=='CE' else 'PUT')} Trade Alert\n"
        f"Futures Price: {fut:,.2f}\n"
        f"Strike: {strike:,} {side}\n"
        f"Entry: {order.get('avg','market')}\n"
        f"Order ID: {order.get('order_id','paper')}\n"
        f"Reason: {arrow} Momentum + OI skew confirm"
    )
    _send_text(text)

def send_exit(ctx: dict) -> None:
    _send_text(f"🚪 EXIT {ctx}")

def send_warn(msg: str) -> None:
    _send_text(f"⚠️ {msg}")
