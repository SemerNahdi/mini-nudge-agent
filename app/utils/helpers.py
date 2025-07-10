import pandas as pd
import json
import os

def load_data(crm_path: str = "data/crm_events.csv", email_path: str = "data/emails.json") -> tuple[pd.DataFrame, list]:
    """Load CRM events and email threads from files."""
    try:
        
        crm_df = pd.read_csv(crm_path, sep=';', thousands=' ')
        
        required_columns = ['deal_id', 'deal_name', 'amount_eur', 'stage', 'last_activity']
        if not all(col in crm_df.columns for col in required_columns):
            missing = [col for col in required_columns if col not in crm_df.columns]
            raise ValueError(f"Missing required columns in CRM data: {missing}")
        
        
        crm_df['amount_eur'] = pd.to_numeric(crm_df['amount_eur'].replace(r'[\s]', '', regex=True), errors='coerce').fillna(0).astype(int)
        crm_df['amount_eur'] = crm_df['amount_eur'].clip(lower=0)  # 
        
        # Load emails
        if not os.path.exists(email_path):
            print(f"Warning: {email_path} not found. Returning empty email list.")
            return crm_df, []
        
        try:
            with open(email_path, 'r') as f:
                emails = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in {email_path}: {e}. Returning empty email list.")
            return crm_df, []
        
        
        if not isinstance(emails, list):
            print(f"Warning: {email_path} is not a list. Returning empty email list.")
            return crm_df, []
        
        valid_emails = []
        for email in emails:
            if not isinstance(email, dict) or 'deal_id' not in email or 'thread' not in email:
                print(f"Warning: Invalid email entry: {email}. Skipping.")
                continue
            valid_emails.append(email)
        
        return crm_df, valid_emails
    except FileNotFoundError as e:
        print(f"Error: Data file not found: {e}")
        raise
    except pd.errors.ParserError as e:
        print(f"Error: Failed to parse CSV file. Ensure it uses semicolons (;) as separators: {e}")
        raise
    except Exception as e:
        print(f"Error loading data: {e}")
        raise

def save_nudges(nudges: list, output_path: str = "out/nudges.json"):
    """Save nudges to output file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(nudges, f, indent=2)