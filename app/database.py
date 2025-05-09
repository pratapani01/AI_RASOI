# app/database.py
import mysql.connector
import os
from datetime import datetime

def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="your_username",
        password="your_password",
        database="recipe_db"
    )

import os
from datetime import datetime

def save_recipe(ingredients, spice, region, meal, recipe_text):
    # Ensure folder exists
    save_folder = "saved_recipes"
    os.makedirs(save_folder, exist_ok=True)

    # Create unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"recipe_{timestamp}.txt"
    file_path = os.path.join(save_folder, file_name)

    # Save the recipe
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("Ingredients: " + ingredients + "\n")
        f.write("Spice Level: " + spice + "\n")
        f.write("Region: " + region + "\n")
        f.write("Meal Type: " + meal + "\n\n")
        f.write("Recipe:\n" + recipe_text.strip())

    print(f"✅ Recipe saved to: {file_path}")
