from typing import Any


PAIN_PHRASES = {
    "english": [
        "pain",
        "hurts",
        "hurt",
        "aching",
        "burning",
        "cramping",
        "uncomfortable",
        "help me",
        "help",
    ],
    "en": [
        "pain",
        "hurts",
        "hurt",
        "aching",
        "burning",
        "cramping",
        "uncomfortable",
        "help me",
        "help",
    ],
    "tamil": [
        "வலி",
        "வலிக்கிறது",
        "வலிக்குது",
        "தாங்க முடியவில்லை",
        "உதவி",
    ],
    "ta": [
        "வலி",
        "வலிக்கிறது",
        "வலிக்குது",
        "தாங்க முடியவில்லை",
        "உதவி",
    ],
    "hindi": [
        "दर्द",
        "दर्द हो रहा है",
        "बहुत दर्द",
        "मदद",
    ],
    "hi": [
        "दर्द",
        "दर्द हो रहा है",
        "बहुत दर्द",
        "मदद",
    ],
}


def detect_pain_phrases(
    text: str,
    language: str | None = None,
) -> dict[str, Any]:
    normalized_text = text.lower().strip()

    matched_phrases: list[str] = []

    phrase_groups = list(PAIN_PHRASES.values())

    if language:
        language_key = language.lower()
        if language_key in PAIN_PHRASES:
            phrase_groups = [PAIN_PHRASES[language_key]]

    for phrases in phrase_groups:
        for phrase in phrases:
            if phrase.lower() in normalized_text:
                if phrase not in matched_phrases:
                    matched_phrases.append(phrase)

    return {
        "pain_phrase_count": len(matched_phrases),
        "matched_phrases": matched_phrases,
        "pain_phrase_score": min(len(matched_phrases) / 3.0, 1.0),
    }
