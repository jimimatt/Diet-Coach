# Pipeline logic file
import time
from typing import Any

from tools.image_generation import generate_food_image
from tools.next import estimate_calories, log_meal, suggest_next_meal
from tools.web_search import search_calories


def run_nutritionist_pipeline(username: str, meal_desc: str, dietary_preference: str) -> dict[str, Any]:
    tools_used = set()
    print(f"Searching for calories for: {meal_desc}")
    calories_text = search_calories(meal_desc)
    tools_used.add("Web Search")
    # If web search fails, fall back to estimation
    if calories_text == 0:
        print("Web search failed, falling back to estimation...")
        time.sleep(1)  # Add delay to avoid rate limits
        calories_text = estimate_calories(meal_desc)
        tools_used.add("Calorie Estimation")
    estimated_calories = calories_text
    print(f"Estimated calories: {estimated_calories}")
    print(f"Logging meal for {username}...")
    time.sleep(1)  # Add delay to avoid rate limits
    log_response = log_meal(username, meal_desc, estimated_calories)
    tools_used.add("Meal Logging")
    print("Generating next meal suggestion...")
    time.sleep(1)
    suggestion = suggest_next_meal(estimated_calories, dietary_preference)
    tools_used.add("Next Meal Suggestion")
    print("Generating image description for suggested meal...")
    time.sleep(1)
    meal_image = generate_food_image(suggestion)
    tools_used.add("Image Description Generation")
    return {
        "logged": log_response,
        "calories": estimated_calories,
        "next_meal_suggestion": suggestion,
        "meal_image": meal_image,
        "tools_used": sorted(tools_used),
    }
