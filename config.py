import os
MODE = os.getenv("MODE","paper")
TZ = "Asia/Kolkata"
ENTRY_POLICY = {"product":"MIS","order_type":"MARKET"}
TIME_WINDOWS = {"morning":("09:30","12:00"),"midday":("12:00","13:30"),"afternoon":("13:30","15:00")}

MARKET = {"open":"09:15","close":"15:30","force_exit":"15:15"}
AWARENESS = {"skew_min":1.2,"velocity_z_min":1.5,"lr_slope_min":2.5,"early_entry_sec":120}

VIX_BANDS = {"low":12.0,"mid":16.0,"high":20.0,"extreme":23.0}
INSTRUMENTS = ["NIFTY","BANKNIFTY","FINNIFTY","MIDCPNIFTY"]

# Governance
MAX_TRADES_PER_INSTRUMENT = 2
GLOBAL_EXPOSURE_CAP = 50000  # INR across all instruments

# Option confirmation weight (0..1)
OPTION_CONFIRM_MIN = 0.75  # 70–80% match tolerated
OPTION_CONFIRM_MIN_HIGH_VIX = 0.65

# Strike rules
STRIKE_STEP = {"NIFTY":50,"BANKNIFTY":100,"FINNIFTY":50,"MIDCPNIFTY":25}

# VIX behavior toggles
HIGH_VIX_LOTTERY = True

# Exit thresholds
EXIT_PARTIAL_PCT = 0.33  # ~33%
EXIT_PREMIUM_DROP_FROM_PEAK = 0.10  # 10%
LR_DROP_FRACTION = 0.5  # 50% from peak
RSI_EXIT_FLOOR = 55
