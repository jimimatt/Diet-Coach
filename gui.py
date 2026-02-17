"""Streamlit frontend for the Nutritionist Assistant."""

from pathlib import Path

import streamlit as st

from agent import run_nutritionist_pipeline

st.set_page_config(page_title="Nutritionist Assistant", page_icon="🍽️", layout="wide")

st.title("🍽️ Nutritionist Assistant")

col1, col2 = st.columns(2)

with col1:
    username = st.text_input("Username", placeholder="Enter your name")
    meal_desc = st.text_area(
        "Meal Description",
        placeholder="Describe your meal (e.g., 'Chicken salad with olive oil dressing')",
    )
    dietary_preference = st.selectbox(
        "Dietary Preference",
        options=["non-vegetarian", "vegetarian", "vegan", "gluten-free"],
    )
    submit = st.button("Process Meal", type="primary")

with col2:
    if submit:
        if not username or not meal_desc:
            st.error("Please enter both username and meal description.")
        else:
            with st.spinner("Processing your meal..."):
                result = run_nutritionist_pipeline(username, meal_desc, dietary_preference)

            calories = result.get("calories", "Not available")

            # Map tool names to Mistral connectors
            connector_map = {
                "Web Search": "Web Search",
                "Image Description Generation": "Image Generation",
                "Meal Logging": "Chat Completion",
                "Next Meal Suggestion": "Chat Completion",
            }
            connectors_used = {connector_map[tool] for tool in result["tools_used"] if tool in connector_map}

            # Display results
            st.markdown("## Meal Details")
            st.markdown(f"- **Meal Description:** {meal_desc}")
            st.markdown(f"- **Estimated Calories:** {calories}")

            st.markdown("## Next Meal Suggestion")
            st.markdown(result["next_meal_suggestion"])

            st.markdown("## Tools Used")
            st.markdown(", ".join(result["tools_used"]))

            st.markdown("## Mistral Connectors Used")
            st.markdown(", ".join(sorted(connectors_used)))

            # Display image if valid
            image_path = Path(result["meal_image"])
            if image_path.exists() and image_path.suffix == ".png":
                st.image(str(image_path), caption="Generated Meal Image")
