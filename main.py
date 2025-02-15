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

st.set_page_config(page_title="AI Chef de Cuisine", layout="centered", initial_sidebar_state="auto")
st.title("🧑🏻‍🍳 AI Chef de Cuisine! 🤖")
st.subheader("Let me help you create a new recipe!")
st.divider()

ingredients = st.text_input("📃 Enter a list of ingredients (comma-separated): ").strip()
selected_dish = st.radio("🍽️ Choose a plate: ", options=["Entrée", "Main course", "Dessert", "Drink or Cocktail"])
language_chosen = st.radio("🌍 Choose a language: ", options=["English", "French", "Portugues", "Spanish"])
measurement_system = st.radio("📏 If your recipe is in English, choose a metric measurement: ", options=["Imperial", "Metric"])

if ingredients:
    if not re.match(r"^[a-zA-Z0-9,\- ]+$", ingredients):
        st.error("Please enter a valid list of ingredients, separated by commas.")
        st.stop()

    # prompt
    prompt = (
        f"You are a culinary assistant specialized in {language_chosen} cuisine. "
        f"Generate a detailed recipe in {language_chosen} using the following ingredients: {ingredients}, "
        f"served as a {selected_dish}. Ensure the instructions are clear and precise."
    )

    try:
        response = co.generate(
            model="command-r-08-2024",
            prompt=prompt,
            max_tokens=500,
            temperature=1.0
        )

        generated_text = response.generations[0].text.strip()
        lines = generated_text.split("\n")

        def convert_measures(lines, measurement_system):
            if measurement_system == "Metric":
                conversions = {
                    "cup": (240, "ml"),
                    "teaspoon": (5, "ml"),
                    "tablespoon": (15, "ml"),
                    "ounce": (28, "g"),
                    "inch": (2.54, "cm")
                }
                converted_lines = []

                for line in lines:
                    # fractions conversion (ex: "1/2" -> "0.5")
                    def convert_fraction(match):
                        try:
                            return str(float(Fraction(match.group(0))))
                        except ValueError:
                            return match.group(0)

                    line = re.sub(r"(\d+/\d+)", convert_fraction, line)

                    # unit conversions
                    for unit, (value, new_unit) in conversions.items():
                        pattern = rf"(\d+)\s*{unit}s?"
                        line = re.sub(
                            pattern,
                            lambda m: f"{int(m.group(1)) * value} {new_unit}",
                            line
                        )

                    converted_lines.append(line)

                return converted_lines
            return lines

        converted_lines = convert_measures(lines, measurement_system)
        recipe_text = "\n".join(converted_lines)

        st.text_area("Generated Recipe:", value=recipe_text, height=300)

    except Exception as e:
        st.error(f"Failed to generate a recipe: {e}")
else:
    st.warning("Please enter your list of ingredients...")

