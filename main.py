#run streamlit: streamlit run <file.py>
import re
import cohere
import streamlit as st

from fractions import Fraction
from config import API_KEY_COHERE

try:
    co = cohere.Client(API_KEY_COHERE)
except Exception as e:
    st.error(f"Failed to initialize Cohere client: {e}")
    st.stop()

# Streamlit Configurations
st.set_page_config(page_title="AI Chef de Cuisine", layout="centered", initial_sidebar_state="auto")
st.title("🧑🏻‍🍳 AI Chef de Cuisine! 🤖")
st.subheader("Let me help you create a new recipe!")
st.divider()

# User Inputs
ingredients = st.text_input("📃 Enter a list of ingredients (comma-separated): ").strip()
selected_dish = st.radio("🍽️ Choose a plate: ", options=["Entrée", "Main course", "Dessert", "Drink or Cocktail"])
measurement_system = st.radio("📏 Choose a metric system for measurement: ", options=["Imperial", "Metric"])

# Validation
if ingredients:
    if not re.match(r"^[a-zA-Z, ]+$", ingredients):
        st.error("Please enter a valid list of ingredients, separated by commas.")
        st.stop()

    # Recipe Generation
    prompt = f"Write a recipe with the following ingredients: {ingredients}, served as a {selected_dish}."
    try:
        response = co.generate(
            model='command-r-08-2024',  # Use an appropriate model name
            prompt=prompt,
            max_tokens=500,
            temperature=0.7
        )

        # Extract and Display Recipe
        generated_text = response.generations[0].text.strip()
        lines = generated_text.split("\n")

        def convert_measures(lines, measurement_system):
            if measurement_system == "Metric":
                conversions = {"cup": 240, "teaspoon": 5, "tablespoon": 15, "ounce": 28, "inch": 2.54}
                converted_lines = []

                for line in lines:
                    def convert_fraction(match):
                        try:
                            return str(float(Fraction(match.group(0))))
                        except ValueError:
                            return match.group(0)

                    line = re.sub(r"(\d+/\d+)", convert_fraction, line)

                    for unit, value in conversions.items():
                        line = re.sub(
                            rf"(\d+)\s*{unit}s?",
                            lambda m: f"{int(int(m.group(1)) * value)} ml"
                            if unit in ["cup", "teaspoon", "tablespoon"] else f"{int(int(m.group(1)) * value)} grams",
                            line
                        )
                    converted_lines.append(line)
                return converted_lines
            return lines


        converted_lines = convert_measures(lines, measurement_system)
        recipe_text = "\n".join(converted_lines)

    except Exception as e:
        st.error(f"Failed to generate a recipe: {e}")
else:
    st.warning("Please enter your list of ingredients...")