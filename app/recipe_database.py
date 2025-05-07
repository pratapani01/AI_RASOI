import pandas as pd
import os

# Load the CSV at app startup
CSV_PATH = os.path.join(os.path.dirname(__file__), "recipes.csv")
recipes_df = pd.read_csv(CSV_PATH)

def find_matching_recipe(input_ingredients: list, threshold: float = 0.6):
    """
    Check if any recipe in the CSV matches input ingredients above threshold.
    Returns: recipe dict or None
    """
    for _, row in recipes_df.iterrows():
        recipe_ingredients = [i.strip().lower() for i in row["Ingredients"].split(",")]
        input_set = set(i.strip().lower() for i in input_ingredients)
        recipe_set = set(recipe_ingredients)

        # Calculate Jaccard similarity
        common = input_set & recipe_set
        union = input_set | recipe_set
        similarity = len(common) / len(union)

        if similarity >= threshold:
            return {
                "name": row["Meal Name"],
                "ingredients": row["Ingredients"],
                "prep_time": row["Prep Time"],
                "cook_time": row["Cooking Time"]
            }

    return None
