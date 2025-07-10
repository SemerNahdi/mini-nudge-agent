from app.core.processor import process_deals
from app.utils.helpers import save_nudges

if __name__ == "__main__":
    nudges = process_deals()
    save_nudges([nudge.dict() for nudge in nudges])
    print(f"Generated {len(nudges)} nudges, saved to out/nudges.json")