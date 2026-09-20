"""
mood_manager.py

Story: mood_detector.py (LLM classification) aur mood_log.py (storage)
ko wire karta hai — ek hi call se detect + log dono ho jaate hain.
"""

from mood_detector import detect_mood
from mood_log import log_mood


def detect_and_log_mood(user_message: str, timestamp: str = None) -> dict:
    """
    timestamp: optional override — sirf testing ke liye. Production
    mein hamesha None (current time use hoga).
    """
    result = detect_mood(user_message)
    row_id = log_mood(
        emotion=result.emotion.value,
        intensity=result.intensity,
        topic=result.topic.value,  # Enum ko string mein convert, DB storage ke liye
        source_message=user_message,
        timestamp=timestamp,
    )
    return {
        "id": row_id,
        "emotion": result.emotion.value,
        "intensity": result.intensity,
        "topic": result.topic.value,
        "reasoning": result.reasoning,
    }