"""
debug_moderation_scores.py

Purpose: False-negative debug - concerning message flag nahi hua.
Raw scores print karta hai (exact number dekhne ke liye, sirf True/
False nahi), aur isi message ka English-translated version bhi test
karta hai - taaki pata chale kya yeh specifically Hinglish/code-switched
text ka issue hai (Moderation API English-heavy training data pe zyada
accurate hoti hai, yeh research mein bhi documented limitation hai).
"""

from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

client = OpenAI()

MESSAGES = {
    "Hinglish (original)": "Mujhe lagta hai jeena chhod dena chahiye, sab bekar lagta hai ab.",
    "English (translated)": "I feel like I should stop living, everything feels pointless now.",
}

for label, message in MESSAGES.items():
    response = client.moderations.create(model="omni-moderation-latest", input=message)
    scores = response.results[0].category_scores
    print(f"\n--- {label} ---")
    print(f"Message: {message}")
    print(f"self_harm:              {scores.self_harm:.4f}")
    print(f"self_harm_intent:       {scores.self_harm_intent:.4f}")
    print(f"self_harm_instructions: {scores.self_harm_instructions:.4f}")