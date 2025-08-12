from strategy_expiry import run_once
if __name__=='__main__':
    for s in ('NIFTY','BANKNIFTY','FINNIFTY','MIDCPNIFTY'):
        run_once(s)
