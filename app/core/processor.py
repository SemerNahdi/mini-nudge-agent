import os
import pandas as pd
from datetime import datetime, timezone
from typing import List, Dict
from statistics import median
from app.core.model import Nudge
from app.utils.helpers import load_data
from dotenv import load_dotenv
load_dotenv()
MIN_IDLE_DAYS = 7
MIN_URGENCY = 250

def calculate_idle_days(last_activity: str, today: datetime) -> float:
    """Calculate idle days since last activity, ignoring time of day."""
    try:
        last_activity_dt = datetime.fromisoformat(last_activity.replace('Z', '+00:00')).date()
        today_dt = today.date()
        if last_activity_dt > today_dt:
            print(f"Warning: last_activity {last_activity} is in the future. Returning 0.")
            return 0
        return (today_dt - last_activity_dt).days
    except ValueError:
        print(f"Invalid timestamp format for last_activity: {last_activity}. Returning 0.")
        return 0

def calculate_reply_speed(thread: List[Dict], your_email: str, client_email: str) -> float:
    """Calculate median reply speed in minutes for client replies to your messages."""
    reply_gaps = []
    for i in range(1, len(thread)):
        prev_sender = thread[i-1].get("from")
        curr_sender = thread[i].get("from")
        if prev_sender == your_email and curr_sender == client_email:
            try:
                time_diff = (datetime.fromisoformat(thread[i]["ts"].replace('Z', '+00:00')) - 
                            datetime.fromisoformat(thread[i-1]["ts"].replace('Z', '+00:00'))).total_seconds() / 60
                if time_diff > 0:
                    reply_gaps.append(time_diff)
            except (ValueError, KeyError) as e:
                print(f"Invalid timestamp or missing key in thread: {thread[i]}. Error: {e}. Skipping.")
                continue
    return median(reply_gaps) if reply_gaps else float('inf')

def process_deals(today: datetime = datetime.now(timezone.utc)) -> List[Nudge]:
    """Process deals and generate nudges for stalled opportunities."""
    from app.core.classifier import detect_tone
    from app.core.generator import generate_nudge
    
    try:
        crm_df, emails = load_data()
    except Exception as e:
        print(f"Error loading data: {e}")
        return []
    
    nudges = []
    your_email = os.getenv("YOUR_EMAIL") 
    
    for _, row in crm_df.iterrows():
        deal_id = row['deal_id']
        if not row['stage'] or not row['deal_name']:
            print(f"Deal {deal_id} skipped: invalid stage or deal_name")
            continue
        idle_days = calculate_idle_days(row['last_activity'], today)
        if idle_days < MIN_IDLE_DAYS:
            print(f"Deal {deal_id} skipped: idle_days={idle_days} < {MIN_IDLE_DAYS}")
            continue
        urgency = idle_days * row['amount_eur']
        if urgency <= MIN_URGENCY:
            print(f"Deal {deal_id} skipped: urgency={urgency} <= {MIN_URGENCY}")
            continue
        
        email_thread = next((e for e in emails if e.get('deal_id') == deal_id), None)
        if not email_thread or not email_thread.get('thread'):
            print(f"No valid email thread for deal {deal_id}. Skipping.")
            continue
        
        # Ensure thread has valid messages
        valid_thread = [msg for msg in email_thread['thread'] if msg.get('to') and msg.get('from') and msg.get('ts')]
        if not valid_thread:
            print(f"No valid messages in thread for deal {deal_id}. Skipping.")
            continue
        
        contact = next((msg['to'] for msg in valid_thread if msg.get('to') != your_email), None)
        if not contact:
            print(f"No valid contact for deal {deal_id}. Skipping.")
            continue
        
        reply_speed = calculate_reply_speed(valid_thread, your_email, contact)
        tone = detect_tone(valid_thread[-1].get('body', '')) if valid_thread else "formal"
        nudge_text = generate_nudge(deal_id, contact, tone, reply_speed, row['deal_name'], row['stage'])
        
        nudges.append(Nudge(
            deal_id=deal_id,
            contact=contact,
            nudge=nudge_text,
            urgency=int(urgency),
            reply_speed=round(reply_speed, 1),
            tone=tone
        ))
    
    return nudges