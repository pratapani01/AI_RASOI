from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms.base import LLM
from dotenv import load_dotenv
from typing import Optional, List
import google.generativeai as genai
import os

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Custom Gemini Wrapper for LangChain
class GeminiLLM(LLM):
    model_name: str = "models/gemini-1.5-flash-latest"
    api_key: str = GOOGLE_API_KEY

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        try:
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API Error: {str(e)}")

    @property
    def _llm_type(self) -> str:
        return "gemini"


# Initialize Gemini LLM
llm = GeminiLLM()

# Prompt Template
template = """
You are an Indian chef AI. Suggest a healthy recipe using the following details:

Ingredients:
{ingredients}
Spice Level: {spice_level}
Regional Style: {regional_style}
Meal Type: {meal_type}

Return the output in this format:
1. Recipe Name:
2. Ingredients Needed:
3. Step-by-Step Instructions:
4. Estimated Calories:
5. Cuisine Type:
6. Dietary Info:
7. Recommended Meals for the Day:
"""

prompt = PromptTemplate(
    input_variables=["ingredients", "spice_level", "regional_style", "meal_type"],
    template=template
)

# LangChain Chain Setup
recipe_chain = LLMChain(
    llm=llm,
    prompt=prompt
)

def generate_recipe(ingredients_text, spice_level="Medium", regional_style="North Indian", meal_type="Lunch"):
    """
    Generate a recipe based on provided ingredients string and preferences.
    """
    try:
        result = recipe_chain.run({
            "ingredients": ingredients_text,
            "spice_level": spice_level,
            "regional_style": regional_style,
            "meal_type": meal_type
        })
        return result
    except Exception as e:
        return f"Error generating recipe: {str(e)}"
