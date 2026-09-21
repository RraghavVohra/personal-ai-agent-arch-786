from config import USER_ID
from orchestrator import handle_message
from disclosure import get_disclosure_message
from distress_classifier import DistressTier

EXIT_WORDS = {"exit", "quit", "bye", "bahar"}


def run_chat_loop(user_id: str = USER_ID):
    print(f"Billie: {get_disclosure_message()}\n")

    last_tier = DistressTier.NONE

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBillie: Chalo phir, baad mein baat karte hain. Apna khayal rakhna.")
            break

        if not user_input:
            continue

        if user_input.lower() in EXIT_WORDS:
            print("Billie: Chalo phir, baad mein baat karte hain. Apna khayal rakhna.")
            break

        result = handle_message(
            user_input, is_first_message=False, user_id=user_id,
            previous_tier=last_tier, debug=True,
        )
        print(f"\nBillie: {result['reply']}\n")
        last_tier = result["tier"]


if __name__ == "__main__":
    run_chat_loop()