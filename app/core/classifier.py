from transformers import pipeline
from transformers.pipelines import Pipeline
from typing import Optional
import emoji

classifier = None

def init_tone_classifier() -> Optional[Pipeline]:
    try:
        return pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")
    except Exception as e:
        print(f"Warning: Could not load transformer model. {e}")
        return None

# Initialize classifier globally
classifier = init_tone_classifier()

def map_emotion_to_tone(emotion: str) -> str:
    emotion = emotion.strip().lower()

    casual_emotions = {'joy', 'love', 'surprise', 'excitement', 'amusement', 'happiness'}
    formal_emotions = {'anger', 'fear', 'sadness', 'disgust', 'neutral', 'anxiety', 'confusion'}

    if emotion in casual_emotions:
        return "casual"
    elif emotion in formal_emotions:
        return "formal"
    else:
        print(f"[Warning] Unrecognized emotion label: '{emotion}'. Defaulting to 'formal'.")
        return "formal"


def detect_tone(text: str, clf: Optional[Pipeline] = classifier) -> str:
    """Classify email tone as formal or casual using an LLM or fallback heuristic."""
    if not text.strip():   
        return "formal"

    if clf:
        try:
            if len(text.split()) > 512:
                print(f"Warning: Text truncated, length={len(text.split())}")
            result = clf(text, truncation=True)[0]['label']
            return map_emotion_to_tone(result)
        except Exception as e:
            print(f"Model error: {e}")

    # Fallback rule-based classifier
    exclamation_rate = text.count('!') / len(text) * 100 if text else 0
    emoji_count = sum(1 for char in text if char in emoji.EMOJI_DATA)
    if emoji_count >= 2 or exclamation_rate > 2 or any(sig in text.lower() for sig in ["lol", "yo", "hey", "cheers"]):
        return "casual"
    return "formal"