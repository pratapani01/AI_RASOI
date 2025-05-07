import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("SPOONACULAR_API_KEY")

def get_nutrition_data(ingredient_name):
    """
    Uses Spoonacular API to fetch nutrition data for a given ingredient string.
    Example input: "100g paneer"
    Returns: Dict with name, calories, unit or error message
    """
    url = "https://api.spoonacular.com/recipes/parseIngredients"
    params = {
        "ingredientList": ingredient_name,
        "servings": 1,
        "apiKey": API_KEY
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        response = requests.post(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data:
                item = data[0]
                nutrients = item.get("nutrition", {}).get("nutrients", [])
                calories = next((n for n in nutrients if n["name"] == "Calories"), None)
                return {
                    "name": item.get("name", ingredient_name),
                    "calories": calories.get("amount", 0) if calories else 0,
                    "unit": calories.get("unit", "kcal") if calories else "kcal"
                }
            else:
                return {"error": "No nutrition data found."}
        else:
            return {"error": f"API error: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}
