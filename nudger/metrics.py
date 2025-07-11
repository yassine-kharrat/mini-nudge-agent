from datetime import datetime
import numpy as np
import re
import emoji

def calculate_idle_days(last_activity: datetime, today: datetime = None) -> int:
    today = today or datetime.utcnow()
    delta = today - last_activity
    return delta.days

def calculate_reply_speed(thread: list[dict]) -> float:
    replies = []
    for i in range(1, len(thread)):
        sender = thread[i]['from']
        receiver = thread[i - 1]['from']
        if sender != receiver:
            t1 = datetime.fromisoformat(thread[i - 1]['ts'].replace("Z", "+00:00"))
            t2 = datetime.fromisoformat(thread[i]['ts'].replace("Z", "+00:00"))
            delta_min = (t2 - t1).total_seconds() / 60
            replies.append(delta_min)
    return round(np.median(replies), 2) if replies else -1

def classify_tone(thread: list[dict]) -> str:
    body_texts = [m.get("body", "") for m in thread if "body" in m]
    full_text = " ".join(body_texts)

    emoji_count = sum(1 for char in full_text if emoji.is_emoji(char))
    exclamation_rate = full_text.count("!") / max(len(full_text), 1)

    if emoji_count >= 2 or exclamation_rate > 0.02:
        return "casual"
    return "formal"