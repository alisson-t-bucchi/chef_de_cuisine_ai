#run streamlit: streamlit run <file.py>
import re
import cohere
from config import API_KEY
import streamlit as st

co = cohere.Client(API_KEY)

st.title("🧑🏻‍🍳 AI Chef de cuisine! 🤖")
st.title("Help you to create a new recipe!")
st.divider()

ingredients = st.text_input("📃 Enter a list of ingredients: ")

selected_dish = st.radio("🍽️ Choose a plate: ", options=["Entrée", "Main course", "Desert", "Drink or Cocktail"])

measurament_system = st.radio("📏 Choose a metric system for measurament: ", options=["Imperial", "Metric"])

if ingredients:
    prompt = f"Write a recipe with the {ingredients} to served like {selected_dish}."

    try:
        response = co.generate(
            model='command-r-08-2024',
            prompt=prompt,
            max_tokens=500,
            temperature=0.7
        )

        st.divider()
        generated_text = response.generations[0].text.strip()
        lines = generated_text.split("\n")

        st.title(f"📝 Your recipe: ")
        st.text(" ")

        def convert_measures(lines, measurament_system):
            if measurament_system == "Metric":
                conversions = {"cup": 230, "teaspoon": 5, "tablespoon": 14, "ounce": 28, "inch": 25}
                converted_lines = []

                #change fractions to decimals
                for line in lines:
                    line = re.sub(r"(\d+)/(\d+)", lambda m: str(round(int(m.group(1)) / int(m.group(2)))), line)

                    # change units to a correspond values
                    for unit, value in conversions.items():
                        line = re.sub(
                            rf"(\d+)\s*{unit}s?",
                            lambda
                                m: f"{int(int(m.group(1)) * value)} grams" if unit == "inch" else f"{int(int(m.group(1)) * value)} ml",
                            line
                        )
                    converted_lines.append(line)
                return converted_lines
            return lines

        converted_lines = convert_measures(lines, measurament_system)
        for line in converted_lines:
            st.write(line)

    except Exception as e:
        st.error(f"Fail to generate a recipe: {e}")

else:
    st.warning("Please enter your list of ingredients...")