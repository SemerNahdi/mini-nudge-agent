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
        "You're a smart sales assistant writing Slack-style nudges to help a salesperson revive stalled B2B deals."
        "Your job is to suggest the next best step to revive a stalled deal by suggesting an action message. "
        "Keep the output concise, actionable, and tailored . "
        "Always write in under 25 words. Avoid greetings, fluff, or full emails. "
        "Just suggest the next step like a sales note Slack message."
        "Reference the deal stage, propose a specific next step, and avoid generic phrases like 'follow up' or 'checking in'."
    )

    user_prompt = (
        f"Deal: {deal_name}\n"
        f"Stage: {stage}\n"
        f"Contact: {contact}\n"
        f"Buyer Tone: {tone}\n"
        f"Buyer Reply Speed: {reply_speed:.0f} minutes\n\n"
        "Write a short, polite nedge message (UNDER 25 WORDS) to re-engage the contact and move the deal forward."
        "referencing the deal stage, and proposing a clear next step."
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