from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
import os


load_dotenv()

def generate_nudge(deal_id: str, contact: str, tone: str, reply_speed: float, deal_name: str, stage: str) -> str:
    """Generate a nudge using OpenAI GPT-3.5-Turbo."""
    if not all([deal_id, contact, tone, deal_name, stage]):
        print(f"Invalid input for deal {deal_id}. Missing required fields.")
        return f"Hi {contact}, shall we reconnect on the {deal_name} {stage.lower()}? Please suggest a time."
    
    
    original_env = os.environ.copy()
    os.environ.pop("HTTP_PROXY", None)
    os.environ.pop("HTTPS_PROXY", None)
    
    # Initialize OpenAI client with default HTTP client
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    except Exception as e:
        print(f"Failed to initialize OpenAI client for deal {deal_id}: {e}")
        os.environ.update(original_env)
        return f"Hi {contact}, shall we reconnect on the {deal_name} {stage.lower()}? Please suggest a time."
    
    system_prompt = (
            "You are a smart sales assistant helping a salesperson revive a stalled deal. "
            "Generate a clear, concise, and polite nudge message (no more than 25 words) "
            "to send to the contact. Tailor the message to the buyer’s communication tone "
            "and reply speed, referencing the deal stage. Avoid generic phrases and encourage a next step."
        )
    user_prompt = (
            f"Deal Name: {deal_name}\n"
            f"Stage: {stage}\n"
            f"Contact Name: {contact}\n"
            f"Buyer Tone: {tone}\n"
            f"Buyer Reply Speed: {reply_speed:.0f} minutes\n\n"
            "Please write a polite, concise nudge message to re-engage the contact and move the deal forward."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=50,
            temperature=0.7
        )
        os.environ.update(original_env)
        return response.choices[0].message.content.strip()
    except OpenAIError as e:
        print(f"OpenAI API error for deal {deal_id}: {e}")
        os.environ.update(original_env)
        return f"Hi {contact}, shall we reconnect on the {deal_name} {stage.lower()}? Please suggest a time."
    except Exception as e:
        print(f"Unexpected error generating nudge for deal {deal_id}: {e}")
        os.environ.update(original_env)
        return f"Hi {contact}, shall we reconnect on the {deal_name} {stage.lower()}? Please suggest a time."