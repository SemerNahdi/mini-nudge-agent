from app.core.processor import process_deals
from app.utils.helpers import save_nudges

def main():
    nudges = process_deals()
    save_nudges([nudge.model_dump() for nudge in nudges])
    print(f"✅ Generated {len(nudges)} nudges, saved to out/nudges.json")

if __name__ == "__main__":
    main()
