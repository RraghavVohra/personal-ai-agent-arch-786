"""
disclosure.py

Purpose: Safety Layer - Safeguard 1 (Disclosure).
Ben-Zion ka pehla safeguard, aur ab California SB 243 (Jan 2026) mein
legally codified: chatbot ko consistently clear rakhna hai ki woh AI
hai, insaan nahi - especially jab relationship deep ho sakta hai
(coach-jaisa dynamic mein yeh risk zyada hai).

Abhi sirf session-start disclosure hai (V1 scope). Periodic reminders
(kuch state laws mein required, jaise har 3 ghante) Step 7
(Orchestrator) ka kaam hoga jab session-tracking exist karegi.
"""

DISCLOSURE_TEXT = (
    "Hey, main Billie hoon - tera AI coach, insaan nahi. "
    "Par jo bhi share karega, poori dhyaan se sunoonga aur yaad rakhoonga."
)


def get_disclosure_message() -> str:
    """
    Session-start pe Orchestrator (Step 7) isko call karega, pehla
    message bhejne se pehle. Function isliye banaya (constant seedha
    return nahi kiya), taaki future mein logic add ho sake (jaise
    periodic-reminder timing) bina call-site badle.
    """
    return DISCLOSURE_TEXT