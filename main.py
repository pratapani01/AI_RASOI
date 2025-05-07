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

    recipe = generate_recipe(", ".join(ingredients), spice, region, meal)
    return nutrition_info + f"\n\nTotal Estimated Calories: {round(total_calories)} kcal", recipe

def launch_interface():
    custom_css = """
    * {
        font-family: 'Georgia', serif !important;
    }
    textarea, input, select, button, label {
        font-size: 20px !important;
    }
    button {
        background-color: orange !important;
        color: white !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        font-weight: bold;
    }
    .gr-tab-label {
        background-color: #ccc !important;
        color: black !important;
        font-size: 18px !important;
        border-radius: 5px !important;
    }
    .footer {
        text-align: center;
        font-size: 16px;
        padding-top: 30px;
        color: #555;
    }
    """

    with gr.Blocks(css=custom_css) as demo:
        gr.Markdown("<h2 style='text-align: center; font-size: 40px;'>TadkaGPT</h2>")
        gr.Markdown("<h2 style='text-align: center; font-size: 30px;'>👩‍🍳 AI Rasoi: Recipe GPT with a Desi Twist</h2>")

        with gr.Tabs():
            with gr.Tab("Text"):
                text_input = gr.Textbox(label="🧾 Enter ingredients (comma-separated)", lines=3)
                spice_dropdown_t = gr.Dropdown(spice_levels, label="🌶️ Spice Level", value="Medium")
                region_dropdown_t = gr.Dropdown(regional_styles, label="🌍 Regional Style", value="North Indian")
                meal_dropdown_t = gr.Dropdown(meal_types, label="🍴 Meal Type", value="Lunch")
                text_submit = gr.Button("Generate")
                text_nutrition = gr.Textbox(label="🧪 Nutrition Summary", lines=6)
                text_recipe = gr.Textbox(label="🍽️ Suggested Recipe", lines=20, max_lines=30, autoscroll=False, show_copy_button=True)
                text_submit.click(
                    process_text_input,
                    inputs=[text_input, spice_dropdown_t, region_dropdown_t, meal_dropdown_t],
                    outputs=[text_nutrition, text_recipe],
                )

            with gr.Tab("Voice"):
                voice_button = gr.Button("🎤 Record Voice")
                voice_textbox = gr.Textbox(label="🗣️ Spoken Ingredients", interactive=True, placeholder="Speak now...", lines=3, max_lines=50)
                recording_text = gr.Textbox(label="📣 Status", value="", interactive=False)

                spice_dropdown_v = gr.Dropdown(spice_levels, label="🌶️ Spice Level", value="Medium")
                region_dropdown_v = gr.Dropdown(regional_styles, label="🌍 Regional Style", value="North Indian")
                meal_dropdown_v = gr.Dropdown(meal_types, label="🍴 Meal Type", value="Lunch")
                generate_button = gr.Button("Generate")
                voice_nutrition = gr.Textbox(label="🧪 Nutrition Summary", lines=6)
                voice_recipe = gr.Textbox(label="🍽️ Suggested Recipe", lines=10, max_lines=30, autoscroll=False, show_copy_button=True)

                def update_voice_input():
                    status_text = "⏺️ Recording... Speak now (10 seconds)"
                    text = transcribe_audio()
                    print("Transcribed Text:", text)
                    status_text = "✅ Recording completed"
                    return text, status_text

                def process_voice_input(spice, region, meal, text):
                    return process_text_input(text, spice, region, meal)

                voice_button.click(update_voice_input, outputs=[voice_textbox, recording_text])
                
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

        
        gr.HTML("""
        <div class='footer'>
            <p>© 2025 Team <b>RUNTIME TERROR</b>. All rights reserved.</p>
            <div style="display: flex; justify-content: center; gap: 40px; padding-top: 10px;">
                <div>
                    <p><b>Animesh</b></p>
                    <a href="https://www.instagram.com/pratap.ani.01/" target="_blank" style="margin-right:10px;">
                        <img src="https://cdn-icons-png.flaticon.com/24/2111/2111463.png" alt="Instagram" />
                    </a>
                    <a href="https://www.linkedin.com/in/animesh-pratap-singh-1977ba29a/" target="_blank">
                        <img src="https://cdn-icons-png.flaticon.com/24/174/174857.png" alt="LinkedIn" />
                    </a>
                </div>
                <div>
                    <p><b>Aditi</b></p>
                    <a href="https://www.instagram.com/_aadu_128/" target="_blank" style="margin-right:10px;">
                        <img src="https://cdn-icons-png.flaticon.com/24/2111/2111463.png" alt="Instagram" />
                    </a>
                    <a href="https://www.linkedin.com/in/aditi-jaiswal-02678629b/" target="_blank">
                        <img src="https://cdn-icons-png.flaticon.com/24/174/174857.png" alt="LinkedIn" />
                    </a>
                </div>
                <div>
                    <p><b>Anish</b></p>
                    <a href="https://www.instagram.com/anish_sinha91/" target="_blank" style="margin-right:10px;">
                        <img src="https://cdn-icons-png.flaticon.com/24/2111/2111463.png" alt="Instagram" />
                    </a>
                    <a href="https://www.linkedin.com/in/anish-kumar-b9b934363/" target="_blank">
                        <img src="https://cdn-icons-png.flaticon.com/24/174/174857.png" alt="LinkedIn" />
                    </a>
                </div>
                <div>
                    <p><b>Aditya</b></p>
                    <a href="https://instagram.com/harshit" target="_blank" style="margin-right:10px;">
                        <img src="https://cdn-icons-png.flaticon.com/24/2111/2111463.png" alt="Instagram" />
                    </a>
                    <a href="https://www.linkedin.com/in/aditiya-raj-srivastav-3447112a0/" target="_blank">
                        <img src="https://cdn-icons-png.flaticon.com/24/174/174857.png" alt="LinkedIn" />
                    </a>
                </div>
            </div>
        </div>
        """)

    demo.launch()

if __name__ == "__main__":
    launch_interface()
