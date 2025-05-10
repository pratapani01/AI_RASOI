import gradio as gr
import time
import sys
from app.recipe_generator import generate_recipe
from app.nutrition_lookup import get_nutrition_data
from app.voice_input import transcribe_audio
# from app.image_input import detect_ingredients_from_image
from app.database import save_recipe  # ✅ Added import
from app.image_input import detect_dish_from_image

spice_levels = ["Mild", "Medium", "Spicy", "Extra Spicy"]
regional_styles = ["North Indian", "South Indian", "East Indian", "West Indian"]
meal_types = ["Breakfast", "Lunch", "Snacks", "Dinner"]

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

    # ✅ Save recipe to database
    save_recipe(", ".join(ingredients), spice, region, meal, recipe)

    return nutrition_info + f"\n\nTotal Estimated Calories: {round(total_calories)} kcal", recipe

def process_text_input(text, spice, region, meal):
    ingredients = [x.strip() for x in text.split(",") if x.strip()]
    return handle_ingredients(ingredients, spice, region, meal)


  # update import

def process_image_input(image, spice, region, meal):
    dish_name = detect_dish_from_image(image)
    if dish_name.startswith("Error"):
        return dish_name, ""
    
    recipe = generate_recipe(dish_name, spice, region, meal)
    return f"Detected Dish: {dish_name}", recipe


def type_effect(recipe_text):
    lines = recipe_text.split("\n")
    result = ""
    for line in lines:
        result += line + "\n"
        yield result
        time.sleep(0.1)

def launch_interface():
    custom_css = """
* {
    font-family: 'Georgia', serif !important;
}
textarea, input, select, button, label {
    font-size: 20px !important;
}
button {
    background-color: #e65100 !important;
    color: white !important;
    border-radius: 10px !important;
    padding: 8px 16px !important;
    font-weight: bold;
    width: auto !important;
    max-width: 200px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 40px;
    max-height: 50px;
}
button svg {
    width: 20px;
    height: 20px;
    fill: currentcolor;
}
.gr-tab-label {
    background-color: #ccc !important;
    color: black !important;
    font-size: 18px !important;
    border-radius: 5px !important;
}
.footer {
    display: none;
}
.settings-btn {
    position: fixed;
    top: 10px;
    right: 10px;
    background-color: transparent;
    border: none;
    font-size: 30px;
    cursor: pointer;
    z-index: 999;
}
footer {
    display: none !important;
}
.my_footer {
    text-align: center;
    font-size: 16px;
    padding-top: 30px;
    color: #555;
}
.my_footer a {
    text-decoration: none;
    color: #555;
    transition: color 0.3s ease;
}
.my_footer a:hover {
    color: #ff6600;
}
.my_footer .social-icons {
    display: flex;
    justify-content: center;
    gap: 20px;
    padding-top: 10px;
}
.my_footer .social-icons img {
    width: 20px;
    height: 20px;
    transition: transform 0.3s ease;
}
.my_footer .social-icons img:hover {
    transform: scale(1.2);
}
"""

    with gr.Blocks(css=custom_css) as demo:
        gr.Markdown("<h2 style='text-align: center; font-size: 40px;'>TadkaGPT</h2>")
        gr.Markdown("<h2 style='text-align: center; font-size: 30px;'>👩‍🍳 AI Rasoi: Recipe GPT with a Desi Twist</h2>")

        with gr.Tabs():
            with gr.Tab("Text"):
                text_input = gr.Textbox(label="🧾 Enter ingredients (comma-separated)/dish for recipe", lines=3)
                spice_dropdown_t = gr.Dropdown(spice_levels, label="🌶️ Spice Level", value="Medium")
                region_dropdown_t = gr.Dropdown(regional_styles, label="🌍 Regional Style", value="North Indian")
                meal_dropdown_t = gr.Dropdown(meal_types, label="🍴 Meal Type", value="Lunch")
                text_submit = gr.Button("Generate")

                status_box = gr.Textbox(label="", visible=False, interactive=False, show_copy_button=False)
                text_nutrition = gr.Textbox(label="🧪 Nutrition Summary", lines=6, visible=False)
                text_recipe = gr.Textbox(label="🍽️ Suggested Recipe", lines=20, max_lines=70, autoscroll=False, show_copy_button=True, visible=False)
                

                def on_click_text_generate(text, spice, region, meal):
                    return (
                        gr.update(value="🔄 Generating recipe based on your ingredients...", visible=True),
                        gr.update(visible=False),
                        gr.update(visible=False)
                    )

                def on_done_text_generate(text, spice, region, meal):
                    ingredients = [x.strip() for x in text.split(",") if x.strip()]
                    nutrition, recipe = handle_ingredients(ingredients, spice, region, meal)
                    return (
                        gr.update(value="", visible=True),
                        gr.update(value=nutrition, visible=True),
                        gr.update(value=recipe, visible=True)
                    )

                text_submit.click(
                    on_click_text_generate,
                    inputs=[text_input, spice_dropdown_t, region_dropdown_t, meal_dropdown_t],
                    outputs=[status_box, text_nutrition, text_recipe],
                    queue=True
                ).then(
                    on_done_text_generate,
                    inputs=[text_input, spice_dropdown_t, region_dropdown_t, meal_dropdown_t],
                    outputs=[status_box, text_nutrition, text_recipe],
                )

            with gr.Tab("Voice"):
                voice_button = gr.Button("🎤 Record")
                voice_textbox = gr.Textbox(label="🗣️ Spoken Ingredients", interactive=True, placeholder="Speak now...", lines=3, max_lines=50)
                recording_text = gr.Textbox(label="📣 Status", value="", interactive=False)

                spice_dropdown_v = gr.Dropdown(spice_levels, label="🌶️ Spice Level", value="Medium")
                region_dropdown_v = gr.Dropdown(regional_styles, label="🌍 Regional Style", value="North Indian")
                meal_dropdown_v = gr.Dropdown(meal_types, label="🍴 Meal Type", value="Lunch")
                generate_button = gr.Button("Generate")

                status_box_v = gr.Textbox(label="", visible=False, interactive=False, show_copy_button=False)
                voice_nutrition = gr.Textbox(label="🧪 Nutrition Summary", lines=6, visible=False)
                voice_recipe = gr.Textbox(label="🍽️ Suggested Recipe", lines=20, max_lines=70, autoscroll=False, show_copy_button=True, visible=False)

                def update_voice_input():
                    status_text = "⏺️ Recording... Speak now (10 seconds)"
                    text = transcribe_audio()
                    status_text = "✅ Recording completed"
                    return text, status_text

                def on_click_voice_generate(spice, region, meal, text):
                    return (
                        gr.update(value="🔄 Generating recipe based on your ingredients...", visible=True),
                        gr.update(visible=False),
                        gr.update(visible=False)
                    )

                def on_done_voice_generate(spice, region, meal, text):
                    nutrition, recipe = process_text_input(text, spice, region, meal)
                    return (
                        gr.update(value="", visible=True),
                        gr.update(value=nutrition, visible=True),
                        gr.update(value=recipe, visible=True)
                )

                voice_button.click(update_voice_input, outputs=[voice_textbox, recording_text])

                generate_button.click(
                    on_click_voice_generate,
                    inputs=[spice_dropdown_v, region_dropdown_v, meal_dropdown_v, voice_textbox],
                    outputs=[status_box_v, voice_nutrition, voice_recipe],
                    queue=True
                ).then(
                    on_done_voice_generate,
                    inputs=[spice_dropdown_v, region_dropdown_v, meal_dropdown_v, voice_textbox],
                    outputs=[status_box_v, voice_nutrition, voice_recipe],
                )

            with gr.Tab("Image"):
                image_input = gr.Image(type="filepath", label="🖼️ Upload Image of Ingredients")
                spice_dropdown_i = gr.Dropdown(spice_levels, label="🌶️ Spice Level", value="Medium")
                region_dropdown_i = gr.Dropdown(regional_styles, label="🌍 Regional Style", value="North Indian")
                meal_dropdown_i = gr.Dropdown(meal_types, label="🍴 Meal Type", value="Lunch")
                image_submit = gr.Button("Generate")
                image_nutrition = gr.Textbox(label="🧪 Nutrition Summary", lines=6)
                image_recipe = gr.Textbox(label="🍽️ Suggested Recipe", lines=20, max_lines=70, autoscroll=False, show_copy_button=True)
                image_submit.click(
                    process_image_input,
                    inputs=[image_input, spice_dropdown_i, region_dropdown_i, meal_dropdown_i],
                    outputs=[image_nutrition, image_recipe],
                )

        gr.HTML("""
            <div class='settings-btn' onclick="window.location.href='http://127.0.0.1:7860/?view=settings'">
                ⚙️
            </div>
            <div class='my_footer' id="footer-settings">
                <p>© 2025 Team <b>RUNTIME TERROR</b>. All rights reserved.</p>
                <div style="display: flex; justify-content: center; gap: 40px; padding-top: 10px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <a href="https://www.instagram.com/pratap.ani.01/" target="_blank">
                            <img src="https://cdn-icons-png.flaticon.com/24/2111/2111463.png" alt="Instagram" width="20" height="20" />
                        </a>
                        <a href="https://www.linkedin.com/in/animesh-pratap-singh-1977ba29a/" target="_blank">
                            <img src="https://cdn-icons-png.flaticon.com/24/174/174857.png" alt="LinkedIn" width="20" height="20" />
                        </a>
                    </div>
                </div>
            </div>
        """)

        gr.Markdown("<p style='text-align: center; font-size: 16px;'>Made with ❤️ by Team Runtime Terror</p>")

    demo.launch(share=True)
if __name__ == "__main__":
    launch_interface()