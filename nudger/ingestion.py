import pandas as pd
import json

def load_crm_data(path: str = "data/crm_events.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df['last_activity'] = pd.to_datetime(df['last_activity'])
    df['amount_eur'] = df['amount_eur'].astype(str).str.replace(" ", "").astype(float)
    return df

def load_email_threads(path: str = "data/emails.json") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
