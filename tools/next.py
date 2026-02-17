# Meal suggestions
import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo

from mistralai import SystemMessage, UserMessage

from tools.configs import client

TZ = ZoneInfo(os.getenv("TIMEZONE", "UTC"))


def _get_content_str(content: object) -> str:
    """Extract string content from response, handling various types."""
    if isinstance(content, str):
        return content
    if isinstance(content, list) and content:
        first = content[0]
        if hasattr(first, "text"):
            return str(first.text)
    return str(content) if content else ""


def estimate_calories(meal_desc: str) -> int:
    """Estimate calories in a meal description."""
    try:
        messages = [
            SystemMessage(
                content=(
                    "You are a nutrition expert. Estimate calories in meals. "
                    "Return ONLY a single number representing total calories."
                )
            ),
            UserMessage(content=f"Estimate calories in: {meal_desc}"),
        ]
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=messages,
            temperature=0.1,
            max_tokens=50,
        )
        content = _get_content_str(response.choices[0].message.content)
        numbers = re.findall(r"\d+", content)
        if numbers:
            return int(numbers[0])
        return 0
    except Exception as e:
        print(f"Error during calorie estimation: {e!s}")
        return 0


def log_meal(username: str, meal: str, calories: int | str) -> str:
    """Log a user's meal with calorie count."""
    try:
        timestamp = datetime.now(tz=TZ).isoformat()
        messages = [
            SystemMessage(content="You are a meal logging assistant. Log the user's meal with calories."),
            UserMessage(content=f"Log this meal: {meal} with {calories} calories for user {username} at {timestamp}"),
        ]
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=messages,
            temperature=0.1,
            max_tokens=100,
        )
        return _get_content_str(response.choices[0].message.content).strip()
    except Exception as e:
        print(f"Error during meal logging: {e!s}")
        return f"Logged {meal} ({calories} calories) for {username}"


def suggest_next_meal(calories: int | str, dietary_preference: str) -> str:
    """Suggest a next meal based on calorie intake and dietary preferences."""
    try:
        messages = [
            SystemMessage(
                content=(
                    "You are a nutrition expert. Suggest healthy meals based on calorie intake and dietary preferences."
                )
            ),
            UserMessage(
                content=(
                    f"Suggest a {dietary_preference} meal that would be a good next meal "
                    f"after consuming {calories} calories. Make it specific and appetizing."
                )
            ),
        ]
        response = client.chat.complete(model="mistral-small-latest", messages=messages, temperature=0.7)
        return _get_content_str(response.choices[0].message.content).strip()
    except Exception as e:
        print(f"Error during meal suggestion: {e!s}")
        return "Unable to suggest next meal at this time."
