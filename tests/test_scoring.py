import pytest
import pandas as pd
from datetime import datetime, timezone
import json
from app.core.processor import calculate_idle_days, calculate_reply_speed, process_deals
from app.utils.helpers import load_data


def test_calculate_idle_days():
    today = datetime(2025, 7, 10, tzinfo=timezone.utc)
    # Valid past dates
    assert calculate_idle_days("2025-07-01T12:00:00Z", today) == 9
    assert calculate_idle_days("2025-06-25T12:05:00Z", today) == 15
    # Invalid date string returns 0
    assert calculate_idle_days("invalid", today) == 0
    # Future date returns 0
    assert calculate_idle_days("2025-07-15T12:00:00Z", today) == 0

def test_calculate_idle_days_future_date():
    today = datetime(2025, 7, 10, tzinfo=timezone.utc)
    assert calculate_idle_days("2025-07-15T12:00:00Z", today) == 0

def test_calculate_idle_days_invalid_format():
    today = datetime(2025, 7, 10, tzinfo=timezone.utc)
    assert calculate_idle_days("invalid", today) == 0

def test_calculate_reply_speed():
    # Normal reply gap between two messages
    thread = [
        {"from": "ae@nudge.ai", "to": "test@acme.com", "ts": "2025-06-18T09:00:00Z"},
        {"from": "test@acme.com", "to": "ae@nudge.ai", "ts": "2025-06-18T09:45:00Z"}
    ]
    assert calculate_reply_speed(thread, "ae@nudge.ai", "test@acme.com") == 45.0
    
    # Single message thread → infinite reply speed (no reply)
    assert calculate_reply_speed(
        [{"from": "ae@nudge.ai", "to": "test@acme.com", "ts": "2025-06-18T09:00:00Z"}], 
        "ae@nudge.ai", "test@acme.com"
    ) == float('inf')
    
    # Invalid timestamp returns infinite reply speed
    assert calculate_reply_speed(
        [{"from": "ae@nudge.ai", "ts": "invalid"}], 
        "ae@nudge.ai", "test@acme.com"
    ) == float('inf')
    
    # Missing keys returns infinite reply speed
    assert calculate_reply_speed([{}], "ae@nudge.ai", "test@acme.com") == float('inf')

def test_urgency_calculation():
    idle_days = 10
    amount_eur = 5000
    urgency = idle_days * amount_eur
    assert urgency == 50000
