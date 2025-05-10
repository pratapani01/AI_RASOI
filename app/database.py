# app/database.py

import os
from datetime import datetime

def save_recipe(ingredients, spice, region, meal, recipe_text):
    # Ensure the folder exists
    save_folder = "saved_recipes"
    os.makedirs(save_folder, exist_ok=True)

    # Create unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"recipe_{timestamp}.txt"
    file_path = os.path.join(save_folder, file_name)

    # Save the recipe to a text file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("Ingredients: " + ingredients + "\n")
        f.write("Spice Level: " + spice + "\n")
        f.write("Region: " + region + "\n")
        f.write("Meal Type: " + meal + "\n\n")
        f.write("Recipe:\n" + recipe_text.strip())

    print(f"✅ Recipe saved to: {file_path}")

def fetch_all_recipes():
    recipes = []
    folder = "saved_recipes"
    if not os.path.exists(folder):
        return recipes

    for filename in os.listdir(folder):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
                if len(lines) >= 5:
                    recipe = {
                        "ingredients": lines[0].replace("Ingredients: ", ""),
                        "spice": lines[1].replace("Spice Level: ", ""),
                        "region": lines[2].replace("Region: ", ""),
                        "meal": lines[3].replace("Meal Type: ", ""),
                        "recipe": "\n".join(lines[5:])  # skip the empty line and header
                    }
                    recipes.append(recipe)
    return recipes
