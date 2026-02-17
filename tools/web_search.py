# Web search tool
import re

from tools.configs import client


def _extract_calories_from_content(content: object) -> int | None:
    """Extract calorie number from content (string or list of chunks)."""
    if isinstance(content, str):
        if numbers := re.findall(r"\d+", content):
            return int(numbers[0])
    elif isinstance(content, list):
        for chunk in content:
            text = getattr(chunk, "text", None)
            if text and (numbers := re.findall(r"\d+", str(text))):
                return int(numbers[0])
    return None


def search_calories(meal_desc: str) -> int:
    """Search for calorie information about a meal using web search."""
    try:
        websearch_agent = client.beta.agents.create(
            model="mistral-medium-latest",
            description="Agent able to search for nutritional information and calorie content of meals",
            name="Nutrition Search Agent",
            instructions=(
                "You have the ability to perform web searches with web_search to find accurate calorie "
                "information. Return ONLY a single number representing total calories."
            ),
            tools=[{"type": "web_search"}],
            completion_args={"temperature": 0.3, "top_p": 0.95},
        )
        response = client.beta.conversations.start(
            agent_id=websearch_agent.id,
            inputs=f"What are the total calories in {meal_desc}?",
        )
        print("Raw response:", response)

        if hasattr(response, "outputs"):
            for output in response.outputs:
                content = getattr(output, "content", None)
                if content and (calories := _extract_calories_from_content(content)):
                    return calories

        print("No calorie information found in web search response")
        return 0
    except Exception as e:
        print(f"Error during web search: {e!s}")
        return 0
