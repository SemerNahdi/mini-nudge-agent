import pytest
import pandas as pd
from datetime import datetime, timezone
from statistics import median
from unittest.mock import patch, MagicMock
from app.core.processor import calculate_idle_days, calculate_reply_speed, process_deals
from app.utils.helpers import load_data

# Mock Nudge class
class Nudge:
    def __init__(self, deal_id, contact, nudge, urgency, reply_speed, tone):
        self.deal_id = deal_id
        self.contact = contact
        self.nudge = nudge
        self.urgency = urgency
        self.reply_speed = reply_speed
        self.tone = tone

# Fixture for current date (July 10, 2025, 17:20 UTC)
@pytest.fixture
def today():
    return datetime(2025, 7, 10, 17, 20, tzinfo=timezone.utc)

# Fixture for sample CRM data
@pytest.fixture
def sample_crm_df():
    return pd.DataFrame([
        {
            "deal_id": "OPP-123",
            "stage": "Negotiation",
            "deal_name": "Project Alpha",
            "last_activity": "2025-07-01T12:00:00Z",
            "amount_eur": 5000,
        },
        {
            "deal_id": "OPP-456",
            "stage": "Proposal",
            "deal_name": "Project Beta",
            "last_activity": "2025-06-30T12:00:00Z",
            "amount_eur": 10000,
        },
        {
            "deal_id": "OPP-789",
            "stage": "",  # Invalid stage
            "deal_name": "Project Gamma",
            "last_activity": "2025-07-05T12:00:00Z",
            "amount_eur": 3000,
        },
    ])

# Fixture for sample email data
@pytest.fixture
def sample_emails():
    return [
        {
            "deal_id": "OPP-123",
            "thread": [
                {"from": "ae@nudge.ai", "to": "marie.cfo@acme.com", "ts": "2025-07-01T09:00:00Z", "body": "Hello 😊"},
                {"from": "marie.cfo@acme.com", "to": "ae@nudge.ai", "ts": "2025-07-01T09:45:00Z", "body": "Hi back 😎"},
            ],
        },
        {
            "deal_id": "OPP-456",
            "thread": [
                {"from": "ae@nudge.ai", "to": "marie.cfo@acme.com", "ts": "2025-06-30T09:00:00Z", "body": "Proposal"},
            ],
        },
        {
            "deal_id": "OPP-999",  # No matching deal
            "thread": [
                {"from": "ae@nudge.ai", "to": "marie.cfo@acme.com", "ts": "2025-07-01T09:00:00Z", "body": "Test"},
            ],
        },
    ]

# Tests for calculate_idle_days
@pytest.mark.parametrize(
    "last_activity, expected_days",
    [
        ("2025-07-01T12:00:00Z", 9),
        ("2025-06-25T12:05:00Z", 15),
        ("2025-07-10T12:00:00Z", 0),
        ("2025-07-09T23:59:59Z", 1),
        ("2024-07-10T12:00:00Z", 365),
        ("2025-07-15T12:00:00Z", 0),
        ("invalid", 0),
    ],
    ids=[
        "valid_past_date_9_days",
        "valid_past_date_15_days",
        "same_day",
        "yesterday",
        "one_year_ago",
        "future_date",
        "invalid_timestamp",
    ],
)
def test_calculate_idle_days(today, last_activity, expected_days):
    assert calculate_idle_days(last_activity, today) == expected_days

# Tests for calculate_reply_speed
@pytest.mark.parametrize(
    "thread, expected_speed",
    [
        (
            [
                {"from": "ae@nudge.ai", "to": "marie.cfo@acme.com", "ts": "2025-07-10T09:00:00Z"},
                {"from": "marie.cfo@acme.com", "to": "ae@nudge.ai", "ts": "2025-07-10T09:45:00Z"},
            ],
            45.0,
        ),
        (
            [
                {"from": "ae@nudge.ai", "to": "marie.cfo@acme.com", "ts": "2025-07-10T09:00:00Z"},
                {"from": "marie.cfo@acme.com", "to": "ae@nudge.ai", "ts": "2025-07-10T09:30:00Z"},
                {"from": "ae@nudge.ai", "to": "marie.cfo@acme.com", "ts": "2025-07-10T10:00:00Z"},
                {"from": "marie.cfo@acme.com", "to": "ae@nudge.ai", "ts": "2025-07-10T11:00:00Z"},
            ],
            45.0,
        ),
        (
            [
                {"from": "ae@nudge.ai", "to": "marie.cfo@acme.com", "ts": "2025-07-10T09:00:00Z"},
            ],
            float('inf'),
        ),
        (
            [
                {"from": "ae@nudge.ai", "to": "marie.cfo@acme.com", "ts": "2025-07-10T09:00:00Z"},
                {"from": "marie.cfo@acme.com", "to": "ae@nudge.ai", "ts": "invalid"},
            ],
            float('inf'),
        ),
        (
            [
                {"from": "ae@nudge.ai", "to": "marie.cfo@acme.com", "ts": "2025-07-10T09:00:00Z"},
                {"from": "marie.cfo@acme.com", "to": "ae@nudge.ai"},
            ],
            float('inf'),
        ),
        (
            [
                {"from": "ae@nudge.ai", "to": "marie.cfo@acme.com", "ts": "2025-07-10T09:45:00Z"},
                {"from": "marie.cfo@acme.com", "to": "ae@nudge.ai", "ts": "2025-07-10T09:00:00Z"},
            ],
            float('inf'),
        ),
        (
            [
                {"from": "ae@nudge.ai", "to": "marie.cfo@acme.com", "ts": "2025-07-10T09:00:00Z"},
                {"from": "marie.cfo@acme.com", "to": "ae@nudge.ai", "ts": "2025-07-10T09:00:00Z"},
            ],
            float('inf'),
        ),
    ],
    ids=[
        "single_reply_45min",
        "multiple_replies_median_45min",
        "single_message_no_reply",
        "invalid_timestamp",
        "missing_keys",
        "out_of_order_timestamps",
        "same_timestamp",
    ],
)
def test_calculate_reply_speed(thread, expected_speed):
    assert calculate_reply_speed(thread, "ae@nudge.ai", "marie.cfo@acme.com") == expected_speed

# Test process_deals
@patch("app.utils.helpers.load_data")
@patch("app.core.processor.os.getenv")
@patch("app.core.classifier.detect_tone")
@patch("app.core.generator.generate_nudge")
def test_process_deals(
    mock_generate_nudge,
    mock_detect_tone,
    mock_getenv,
    mock_load_data,
    today,
    sample_crm_df,
    sample_emails,
):
    mock_getenv.return_value = "ae@nudge.ai"
    mock_load_data.return_value = (sample_crm_df, sample_emails)
    mock_detect_tone.return_value = "casual"  # Match emoji edge case
    mock_generate_nudge.return_value = "Follow up with marie.cfo@acme.com"
    
    with patch("app.core.processor.MIN_IDLE_DAYS", 5), patch("app.core.processor.MIN_URGENCY", 1000):
        nudges = process_deals(today)
    
    assert len(nudges) == 2, "Expected 2 nudges got instead " + str(len(nudges))
    assert nudges[0].deal_id == "OPP-123", f"Expected deal_id 'OPP-123', got {nudges[0].deal_id}"
    assert nudges[0].contact == "marie.cfo@acme.com", f"Expected contact 'marie.cfo@acme.com', got {nudges[0].contact}"
    assert nudges[0].nudge == "Follow up with marie.cfo@acme.com"
    assert nudges[0].urgency == 45000  # 9 * 5000
    assert nudges[0].reply_speed == 45.0
    assert nudges[0].tone == "casual"
    assert nudges[1].deal_id == "OPP-456"
    assert nudges[1].contact == "marie.cfo@acme.com"
    assert nudges[1].nudge == "Follow up with marie.cfo@acme.com"
    assert nudges[1].urgency == 100000  # 10 * 10000
    assert nudges[1].reply_speed == float('inf')
    assert nudges[1].tone == "casual"

# Test process_deals with load_data error
@patch("app.utils.helpers.load_data")
@patch("app.core.processor.os.getenv")
def test_process_deals_load_data_error(mock_getenv, mock_load_data, today):
    mock_getenv.return_value = "ae@nudge.ai"
    mock_load_data.side_effect = Exception("File not found")
    nudges = process_deals(today)
    assert nudges == [], "Expected empty list when load_data raises an exception"

# Test process_deals with invalid thread
@patch("app.utils.helpers.load_data")
@patch("app.core.processor.os.getenv")
@patch("app.core.classifier.detect_tone")
@patch("app.core.generator.generate_nudge")
def test_process_deals_invalid_thread(
    mock_generate_nudge,
    mock_detect_tone,
    mock_getenv,
    mock_load_data,
    today,
    sample_crm_df,
):
    mock_getenv.return_value = "ae@nudge.ai"
    invalid_emails = [
        {"deal_id": "OPP-123", "thread": [{}]},  # Missing to/from/ts
        {"deal_id": "OPP-456", "thread": []},  # Empty thread
    ]
    mock_load_data.return_value = (sample_crm_df, invalid_emails)
    mock_detect_tone.return_value = "casual"
    mock_generate_nudge.return_value = "Follow up"
    
    with patch("app.core.processor.MIN_IDLE_DAYS", 5), patch("app.core.processor.MIN_URGENCY", 1000):
        nudges = process_deals(today)
    
    assert len(nudges) == 0, "Expected no nudges for invalid threads"

# Test process_deals with low urgency
@patch("app.utils.helpers.load_data")
@patch("app.core.processor.os.getenv")
@patch("app.core.classifier.detect_tone")
@patch("app.core.generator.generate_nudge")
def test_process_deals_low_urgency(
    mock_generate_nudge,
    mock_detect_tone,
    mock_getenv,
    mock_load_data,
    today,
):
    mock_getenv.return_value = "ae@nudge.ai"
    low_urgency_df = pd.DataFrame([
        {
            "deal_id": "OPP-123",
            "stage": "Negotiation",
            "deal_name": "Project Alpha",
            "last_activity": "2025-07-10T12:00:00Z",  # 0 days
            "amount_eur": 5000,
        },
        {
            "deal_id": "OPP-456",
            "stage": "Proposal",
            "deal_name": "Project Beta",
            "last_activity": "2025-07-01T12:00:00Z",  # 9 days
            "amount_eur": 10,  # urgency = 9 * 10 = 90
        },
    ])
    emails = [
        {
            "deal_id": "OPP-123",
            "thread": [
                {"from": "ae@nudge.ai", "to": "marie.cfo@acme.com", "ts": "2025-07-10T09:00:00Z", "body": "Hello 😊"},
                {"from": "marie.cfo@acme.com", "to": "ae@nudge.ai", "ts": "2025-07-10T09:45:00Z", "body": "Hi back 😎"},
            ],
        },
        {
            "deal_id": "OPP-456",
            "thread": [
                {"from": "ae@nudge.ai", "to": "marie.cfo@acme.com", "ts": "2025-07-01T09:00:00Z", "body": "Proposal"},
                {"from": "marie.cfo@acme.com", "to": "ae@nudge.ai", "ts": "2025-07-01T09:45:00Z", "body": "Thanks"},
            ],
        },
    ]
    mock_load_data.return_value = (low_urgency_df, emails)
    mock_detect_tone.return_value = "casual"
    mock_generate_nudge.return_value = "Follow up"
    
    with patch("app.core.processor.MIN_IDLE_DAYS", 5), patch("app.core.processor.MIN_URGENCY", 1000):
        nudges = process_deals(today)
    
    assert len(nudges) == 0, "Expected no nudges for low urgency or idle days"