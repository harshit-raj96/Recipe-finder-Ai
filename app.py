from flask import Flask, render_template, request ,jsonify
import os
from werkzeug.utils import secure_filename
from PIL import Image
from dotenv import load_dotenv
from google import genai
import base64
import json
import requests
from concurrent.futures import ThreadPoolExecutor
import random



app = Flask(__name__)

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

gemini_client = genai.Client(
    api_key=gemini_api_key
)

UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp"
}

def get_recipe_image(recipe_name):
    # search on  Pexels 
    url = "https://api.pexels.com/v1/search"

    headers = {
        "Authorization": os.getenv("PEXELS_API_KEY")
    }
    params = {
    "query": recipe_name + " finished cooked food dish",
    "per_page": 5
}
  

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=3
        )

        data = response.json()

        if data.get("photos"):
            photo = random.choice(data["photos"])
            return photo["src"]["large"]

            

    except Exception as e:
        print("Pexels error:", e)

    # 2. Pexels me nhi mila to  TheMealDB
    try:
        url = "https://www.themealdb.com/api/json/v1/1/search.php"

        response = requests.get(
            url,
            params={"s": recipe_name},
            timeout=3
        )

        data = response.json()

        if data.get("meals"):
            return data["meals"][0].get("strMealThumb")

    except Exception as e:
        print("TheMealDB error:", e)

    # 3. dono jagh nhi mila to
    return None


# ingrediend image function 

def get_ingredient_image(ingredient_name):

    # 1. Pehle Pexels se real image search karo
    url = "https://api.pexels.com/v1/search"

    headers = {
        "Authorization": os.getenv("PEXELS_API_KEY")
    }

    params = {
        "query": ingredient_name + " ingredient food",
        "per_page": 1
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=3
        )

        data = response.json()

        if data.get("photos"):
            print("Pexels image found:", ingredient_name)

            return data["photos"][0]["src"]["medium"]

    except Exception as e:
        print("Pexels ingredient error:", e)


    # 2. Pexels me image nahi mili
    #    Ab AI image generate karo

    print("Generating AI image:", ingredient_name)

    try:
        result = gemini_client.images.generate(
            model="gpt-image-2",
            prompt=f"""
            Create a realistic food photography image of:

            {ingredient_name}

            Show only the ingredient.
            Clean light background.
            Natural realistic appearance.
            No text.
            No labels.
            No packaging.
            Suitable for a recipe website ingredient card.
            """,
            size="512x512"
        )

        image_base64 = result.data[0].b64_json

        image_bytes = base64.b64decode(image_base64)

        os.makedirs("static/generated_ingredients", exist_ok=True)

        safe_name = secure_filename(
            ingredient_name.lower()
        )

        file_path = os.path.join(
            "static/generated_ingredients",
            safe_name + ".png"
        )

        with open(file_path, "wb") as image_file:
            image_file.write(image_bytes)

        print("AI image created:", ingredient_name)

        return "/" + file_path.replace("\\", "/")

    except Exception as e:
        print("AI ingredient image error:", e)

        return None


def get_step_image(step_title):

    url = "https://api.pexels.com/v1/search"

    headers = {
        "Authorization": os.getenv("PEXELS_API_KEY")
    }

    params = {
        "query": f"{step_title} cooking food",
        "per_page": 1
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=3
    )

    data = response.json()

    if data.get("photos"):
        return data["photos"][0]["src"]["medium"]

    return None


# demo recipe data lena 
with open("app.json", "r", encoding="utf-8") as file:
    DEMO_RECIPE = json.load(file)

# home page
@app.route("/")
def home():
    print(DEMO_RECIPE)
    return render_template("index.html", recipe = DEMO_RECIPE)

# features page
@app.route("/features")
def features():
    return render_template("features.html")

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/upload", methods=["POST"])
def upload():

    if "food_image" not in request.files:
        return "No image uploaded "

    image = request.files["food_image"]

    if image.filename == "":
        return "No file selected"

    filename = secure_filename(image.filename)

    extension = filename.rsplit(".", 1)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        return "Invalid image format"

    os.makedirs(
        app.config["UPLOAD_FOLDER"],
        exist_ok=True
    )

    image_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    image.save(image_path)

    img = Image.open(image_path)

    print("image opened successfully")
    print("format", img.format)
    print("size", img.size)

    img.verify()
    print("image is valid")

    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(
            image_file.read()
        ).decode("utf-8")


    try:

       result = gemini_client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[
            "Identify the item in this image. "
            "If the image contains a food, vegetable, or drink, "
            "return only its name. "
            "If the image does not contain food, vegetable, or drink, "
            "return exactly: NOT_FOOD. "
            "Do not provide any explanation.",

            {
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": image_data
                }
            }
        ]
    )

    except Exception as e:
        print("Gemini error:", e)

        return "Sorry! Our AI service is temporarily busy. Please try again after a moment."
  
    ai_result = result.text.strip()
    print("AI result:", ai_result)

    if ai_result == "NOT_FOOD":
        return " please upload a food , vegitables, or drink image "

    recipe_result = gemini_client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents=f"""
     Create a complete recipe using this food:

    {ai_result}

    - Treat the identified food as the main ingredient of the recipe, not as the final dish.
    - Create a proper cooked, ready-to-eat dish using the identified food.
    - The final recipe must be a real dish that a person would normally prepare and eat as a      meal,  side dish, snack, breakfast, or appetizer.
    - Do not make the identified food itself the recipe.
    - Do not return raw ingredients, plain chopped food, plain boiled food, or simple serving   suggestions as the main recipe.
    - For example, if the identified food is tomato, create a proper dish such as tomato soup, tomato curry, tomato rice, tomato chutney, or another realistic tomato-based dish.
    - The recipe should have a clear dish name that sounds like an actual food dish.
   - Choose a suitable recipe for the identified food.
   - Do not always choose the same recipe for the same food.
   - If multiple realistic recipes are possible, vary the recipe and cooking style between requests.
   - Do not default to pasta or any fixed recipe.
    - The recipe must be realistic, appetizing, and appropriate for the identified food.

     Return the answer ONLY as valid JSON.

     The JSON must contain exactly these fields:
     recipe_name
    description
    prep_time
    cook_time
    difficulty
    servings
    ingredients
    steps
    tips
    benefits
    serving_suggestions
    nutrition
    variations
    similar_recipes

- recipe_name must contain the recipe name.
- description must contain a short description.
- prep_time must contain preparation time.
- cook_time must contain cooking time.
- difficulty must contain Easy, Medium, or Hard.
- servings must contain the serving size.

- ingredients must be an array containing exactly 6 items.
- Each ingredient must contain:
  name
  quantity
- Do not provide fewer or more than 6 ingredients.

- steps must be an array.
- Each step must contain:
  title
  description

- tips must be an array of useful cooking tips.
- benefits must be an array of health benefits.

- nutrition must contain:
  calories
  protein
  carbohydrates
  fat
  fiber

  - serving_suggestions must be an array of practical serving suggestions specifically related to the generated recipe.
- Each serving suggestion must describe how, when, or with what the dish can be served.
- Serving suggestions must match the actual recipe and its ingredients.
- Do not provide generic serving suggestions that could apply to every recipe.
- Do not repeat the same serving suggestion multiple times.

- variations must be an array containing exactly 4 items.
- Each variation must be an object containing exactly:
  name
  
- Every variation must remain a variation of the original recipe.
- Every variation must use the same main food as the original recipe.
- Keep the variation within the same dish category.
- Each variation must be a complete prepared dish name.
- Only change one or two aspects such as spice level, cooking method, texture, or one supporting ingredient.
- Keep the main food clearly present in every variation.
- Do not suggest unrelated dishes.
- Do not use abstract names such as "Spicy Heat", "Tomato Rich", "Nutty Crunch", or "Lentil Twist".


- similar_recipes must be an array containing exactly 5 items.
- Each similar recipe must contain:
  name
  description

- Use commonly available ingredients and realistic quantities.
- Cooking steps must be logically ordered and match the ingredients.
- prep_time and cook_time must be realistic for the recipe.
- difficulty must accurately reflect the cooking complexity.
- servings must be realistic for the given ingredient quantities.
- benefits must be specifically related to the main ingredients used in this recipe.
- Do not make exaggerated or guaranteed health claims.
- Nutrition values are approximate estimates.
- nutrition must be reasonably consistent with the ingredients and serving size.
- tips must be practical and specifically useful for this recipe.
- Do not repeat generic tips for every recipe.
- variations must be realistic alternatives for the same main food.
- similar_recipes must be genuinely related to the identified food or recipe.
- Do not generate unrelated recipes just to fill the list.

IMAGE RELEVANCE RULES:

- Every main recipe, variation, and similar recipe represents a different finished dish.
- Each image must visually represent the specific dish name.
- Variation images must represent that specific variation, not the original recipe.
- Similar recipe images must represent the specific similar recipe.
- Prefer realistic photos of fully cooked and served dishes.
- Do not use raw ingredients, ingredient-only photos, abstract food images, or ingredient collages.
- If an exact dish photo is unavailable, use a closely related finished dish photo.
- Never intentionally use the same image for multiple different dishes.

Do not add any text outside the JSON.
Do not use Markdown.
"""
)

    recipe_text = recipe_result.text.strip()
    recipe_data = json.loads(recipe_text)

    with ThreadPoolExecutor(max_workers=10) as executor:

     main_future = executor.submit(
        get_recipe_image,
        recipe_data["recipe_name"]
     )

     similar_futures = [
        executor.submit(get_recipe_image, item["name"])
        for item in recipe_data["similar_recipes"]
     ]

     variation_futures = [
        executor.submit(get_recipe_image, item["name"])
        for item in recipe_data["variations"]
     ]

     ingredient_futures = [
        executor.submit(get_ingredient_image, item["name"])
        for item in recipe_data["ingredients"]
     ]

     step_futures = [
        executor.submit(get_step_image, item["title"])
        for item in recipe_data["steps"]
    ]


    recipe_data["main_image"] = main_future.result()


    for item, future in zip(
     recipe_data["similar_recipes"],
    similar_futures
    ):
     item["image"] = future.result()


    for item, future in zip(
    recipe_data["variations"],
    variation_futures
    ):
     item["image"] = future.result()


    for item, future in zip(
    recipe_data["ingredients"],
    ingredient_futures
    ):
     item["image"] = future.result()


    for item, future in zip(
    recipe_data["steps"],
    step_futures
    ):
     item["image"] = future.result()

   


            

    print(recipe_data)
    print(recipe_data["recipe_name"])
    return render_template("index.html",recipe = recipe_data)
    
    

    
    # return "Image uploaded successfully!"


if __name__ == "__main__":
    app.run(debug=True)