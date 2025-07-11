import openai
from datetime import datetime
import os
import json
import numpy as np
import pandas as pd
from nudger.metrics import calculate_reply_speed, classify_tone
import openai

def calculate_urgency(idle_days: int, amount: float) -> float:
    return idle_days * amount

def should_nudge(idle_days: int, urgency: float) -> bool:
    return idle_days >= 7 and urgency > 250

def format_thread(thread: list[dict]) -> str:
    formatted = []
    for msg in thread:
        sender = msg.get("from", "Unknown")
        body = msg.get("body", "").strip()
        formatted.append(f"{sender}:\n{body}")
    return "\n\n".join(formatted)

def build_prompt(idle_days, stage, reply_speed, tone, thread):
    return f"""
        The following deal is idle for {idle_days} days, and the buyer is responding at a rate of {reply_speed} minutes on average. 
        The tone of the emails is {tone}. The current deal stage is {stage}.
        Here is the email thread:
        ---
        {thread}
        ---
        Please suggest a short, actionable nudge like a next step to help the sales team.
        The suggestion should not exceed 25 words.
    """

def call_openai(user_prompt: str, model: str = "gpt-3.5-turbo") -> str:
    
    api_key = os.getenv("OPENAI_API_KEY")
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a virtual assistant that generates actionable follow-up nudges for sales teams based on CRM data."},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=60,
        temperature=0.9,
    )
    return response.choices[0].message.content.strip()

def generate_nudges(crm_data: pd.DataFrame, email_data: list) -> list:
    nudges = []

    for deal in crm_data.itertuples():
        deal_id = deal.deal_id
        amount = deal.amount_eur
        last_activity = deal.last_activity
        stage = deal.stage


        thread = next((item['thread'] for item in email_data if item['deal_id'] == deal_id), None)
        if not thread:
            continue

        idle_days = (datetime.today() - last_activity).days
        reply_speed = calculate_reply_speed(thread)
        tone = classify_tone(thread)
        urgency = calculate_urgency(idle_days, amount)

        if should_nudge(idle_days, urgency):
            full_thread = format_thread(thread)
            prompt = build_prompt(idle_days, stage, reply_speed, tone, full_thread)
            nudge = call_openai(prompt)

            nudges.append({
                "deal_id": deal_id,
                "contact": thread[-1]["from"],
                "nudge": nudge,
                "urgency": urgency,
                "reply_speed": reply_speed,
                "tone": tone
            })
    print(f"\n--- Prompt for deal {deal_id} ---\n{prompt}\n-------------------------------\n")

    return nudges

def write_nudges_to_file(nudges: list, output_path: str = "out/nudges.json"):
    """Write the generated nudges to a JSON file."""
    with open(output_path, 'w') as file:
        json.dump(nudges, file, indent=4)
