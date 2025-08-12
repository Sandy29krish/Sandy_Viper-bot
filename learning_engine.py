import json, os, time

LOG_PATH = os.getenv('LEARNING_LOG_PATH','learning_trades.jsonl')

def log_features(features: dict) -> None:
    try:
        with open(LOG_PATH,'a') as f:
            f.write(json.dumps({"ts":int(time.time()), **features})+"\n")
    except Exception:
        pass
