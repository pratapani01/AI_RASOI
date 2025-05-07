import gradio as gr
from app.recipe_generator import generate_recipe
from app.nutrition_lookup import get_nutrition_data
from app.voice_input import transcribe_audio
from app.image_input import detect_ingredients_from_image

spice_levels = ["Mild", "Medium", "Spicy", "Extra Spicy"]
regional_styles = ["North Indian", "South Indian", "East Indian", "West Indian"]
meal_types = ["Breakfast", "Lunch", "Snacks", "Dinner"]

def process_text_input(text, spice, region, meal):
    ingredients = [x.strip() for x in text.split(",") if x.strip()]
    return handle_ingredients(ingredients, spice, region, meal)

def process_image_input(image, spice, region, meal):
    ingredients = detect_ingredients_from_image(image)
    return handle_ingredients(ingredients, spice, region, meal)

def handle_ingredients(ingredients, spice, region, meal):
    # Nutrition Info
    nutrition_info = "\n".join(
        [
            f"{result['name'].title()}: {result['calories']} {result['unit']}"
            if "error" not in (result := get_nutrition_data(item))
            else f"{item}: {result['error']}"
            for item in ingredients
        ]
    )
    total_calories = sum(
        result['calories']
        for item in ingredients
        if "error" not in (result := get_nutrition_data(item))
    )

    # Recipe
    recipe = generate_recipe(", ".join(ingredients), spice, region, meal)

    return nutrition_info + f"\n\nTotal Estimated Calories: {round(total_calories)} kcal", recipe

def launch_interface():
    with gr.Blocks() as demo:
        gr.Markdown("<h2 style='text-align: center; font-size: 30px; font-family: Georgia, serif; font-weight: bold;'>👩‍🍳 AI Rasoi: Recipe GPT with a Desi Twist</h2>")

        with gr.Tabs():
            with gr.Tab("Text"):
                text_input = gr.Textbox(label="🧾 Enter ingredients (comma-separated)")
                spice_dropdown_t = gr.Dropdown(spice_levels, label="🌶️ Spice Level", value="Medium")
                region_dropdown_t = gr.Dropdown(regional_styles, label="🌍 Regional Style", value="North Indian")
                meal_dropdown_t = gr.Dropdown(meal_types, label="🍴 Meal Type", value="Lunch")
                text_submit = gr.Button("Generate")
                text_nutrition = gr.Textbox(label="🧪 Nutrition Summary", lines=6)
                text_recipe = gr.Textbox(label="🍽️ Suggested Recipe", lines=10, max_lines=30, autoscroll=False, show_copy_button=True)
                text_submit.click(
                    process_text_input,
                    inputs=[text_input, spice_dropdown_t, region_dropdown_t, meal_dropdown_t],
                    outputs=[text_nutrition, text_recipe],
                )

            with gr.Tab("Voice"):
                voice_button = gr.Button("🎤 Record Voice")
                voice_textbox = gr.Textbox(label="🗣️ Spoken Ingredients", interactive=True, placeholder="Speak now...", lines=10, max_lines=50)
                recording_text = gr.Textbox(label="📣 Status", value="", interactive=False)

                # Arrange status above the spice dropdown
                spice_dropdown_v = gr.Dropdown(spice_levels, label="🌶️ Spice Level", value="Medium")
                region_dropdown_v = gr.Dropdown(regional_styles, label="🌍 Regional Style", value="North Indian")
                meal_dropdown_v = gr.Dropdown(meal_types, label="🍴 Meal Type", value="Lunch")

                # Move "Generate" button above spice dropdown
                generate_button = gr.Button("Generate")
                voice_nutrition = gr.Textbox(label="🧪 Nutrition Summary", lines=6)
                voice_recipe = gr.Textbox(label="🍽️ Suggested Recipe", lines=10, max_lines=30, autoscroll=False, show_copy_button=True)

                # Function to start recording and update status
                def update_voice_input():
                    # Set initial recording status
                    status_text = "⏺️ Recording... Speak now (10 seconds)"
                    
                    # Transcribe audio and update status once complete
                    text = transcribe_audio()  # Transcribe the voice input
                    
                    # Debugging: Print the raw transcription result
                    print("Transcribed Text:", text)  # You can check the console for this output

                    status_text = "✅ Recording completed"
                    return text, status_text

                # Function to process the generated recipe after voice input
                def process_voice_input(spice, region, meal, text):
                    return process_text_input(text, spice, region, meal)

                voice_button.click(
                    update_voice_input,
                    outputs=[voice_textbox, recording_text],
                )

                generate_button.click(
                    process_voice_input,
                    inputs=[spice_dropdown_v, region_dropdown_v, meal_dropdown_v, voice_textbox],
                    outputs=[voice_nutrition, voice_recipe],
                )

            with gr.Tab("Image"):
                image_input = gr.Image(type="filepath", label="🖼️ Upload Image of Ingredients")
                spice_dropdown_i = gr.Dropdown(spice_levels, label="🌶️ Spice Level", value="Medium")
                region_dropdown_i = gr.Dropdown(regional_styles, label="🌍 Regional Style", value="North Indian")
                meal_dropdown_i = gr.Dropdown(meal_types, label="🍴 Meal Type", value="Lunch")
                image_submit = gr.Button("Generate")
                image_nutrition = gr.Textbox(label="🧪 Nutrition Summary", lines=6)
                image_recipe = gr.Textbox(label="🍽️ Suggested Recipe", lines=10, max_lines=30, autoscroll=False, show_copy_button=True)
                image_submit.click(
                    process_image_input,
                    inputs=[image_input, spice_dropdown_i, region_dropdown_i, meal_dropdown_i],
                    outputs=[image_nutrition, image_recipe],
                )

    demo.launch()


if __name__ == "__main__":
    launch_interface()
