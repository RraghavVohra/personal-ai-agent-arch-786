"""
decay.py

Story: Yeh module Ebbinghaus forgetting-curve formula implement karta
hai — confidence time ke saath exponentially decay hota hai jab tak
memory reinforce (re-confirm) na ho. Pure math function hai — koi DB,
koi LLM, koi side-effect nahi. Add/search pipeline baad mein isko
import karke actual memory_meta rows pe apply karega.
"""

import math
from datetime import datetime, timezone
from config import DECAY_STABILITY_HOURS


def calculate_decayed_confidence(base_confidence: float, last_reinforced_at: datetime, now: datetime = None) -> float:
    """
    Ebbinghaus forgetting curve: confidence(t) = base_confidence * e^(-t/S)

    - base_confidence: confidence value AS OF last_reinforced_at (jo
      memory_meta mein stored hai reinforcement ke turant baad)
    - last_reinforced_at: last reinforcement ka timestamp (retrieval
      boost ya full CONFIRMS reset)
    - now: current time (default utcnow — lekin parameter isliye hai
      taaki tests "time beetne" ko simulate kar sakein, bina actually
      wait kiye)
    - S (stability): DECAY_STABILITY_HOURS se config.py se aata hai
    """
    if now is None:
        now = datetime.now(timezone.utc)

    elapsed_hours = (now - last_reinforced_at).total_seconds() / 3600
    if elapsed_hours < 0:
        # Why: safety guard — clock skew ya galat timestamp order se
        # elapsed negative aa jaaye toh confidence ko base se zyada
        # mat hone do
        elapsed_hours = 0

    return base_confidence * math.exp(-elapsed_hours / DECAY_STABILITY_HOURS)