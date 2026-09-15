from flask import Flask, render_template, request ,jsonify
import os
from werkzeug.utils import secure_filename
from PIL import Image
from dotenv import load_dotenv
from openai import OpenAI
import base64
import json
import requests
from concurrent.futures import ThreadPoolExecutor



app = Flask(__name__)

load_dotenv()
api_key = os.getenv("OPEN_API_KEY")
clint = OpenAI(api_key=api_key)

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
        "query": recipe_name + " food",
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
            return data["photos"][0]["src"]["large"]

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

def get_ingredient_image(ingredient_name):

    ingredient_name = ingredient_name.replace(" ", "_")

    return f"https://www.themealdb.com/images/ingredients/{ingredient_name}.png"

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

# home route
@app.route("/")
def home():
    print(DEMO_RECIPE)
    return render_template("index.html", recipe = DEMO_RECIPE)


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

    result = clint.responses.create(
    model="gpt-5.6-luna",
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                   "text": """
                   Identify the item in this image.

                   If the image contains a food, vegetable, or drink,
                   return only its name.

                   If the image does not contain food, vegetable, or drink,
                   return exactly:

                   NOT_FOOD

                   Do not provide any explanation.
                   """
                },
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{image_data}"
                }
            ]
        }
    ]
)
    ai_result = result.output_text.strip()
    print("AI result:", ai_result)

    if ai_result == "NOT_FOOD":
        return " please upload a food , vegitables, or drink image "

    recipe_result = clint.responses.create(
    model="gpt-5.6-luna",
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": f"""
                 Create a complete recipe using this food:

                 {ai_result}
                 - Choose a suitable recipe for the identified food.
                 - Do not always choose the same recipe for the same food.
                 - If multiple realistic recipes are possible, vary the recipe and cooking 
                 style between requests.
                 - Do not default to pasta or any fixed recipe.
                 - The recipe must be realistic and appropriate for the identified food.

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
                 nutrition
                 variations
                 similar_recipes

                 Rules:

                 - recipe_name must contain the recipe name.
                 - description must contain a short description.
                 - prep_time must contain preparation time.
                 - cook_time must contain cooking time.
                 - difficulty must contain Easy, Medium, or Hard.
                 - servings must contain the serving size.

                 - ingredients must be an array.
                 - Each ingredient must contain:
                 name
                 quantity

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

                 - variations must be an array containing exactly 4 items.
                 - Each variation must contain:
                 name
                 description
                 - Each variation description must be very short and clear.
                 - Keep each variation description between 8 and 15 words.
                 - Describe only the main change or idea of the variation.
                 - Do not give cooking instructions, ingredient quantities, or long explanations.

                 - similar_recipes must be an array contain exactly 5 items.
                 - Each similar recipe must contain:
                   name
                  description

                 Do not add any text outside the JSON.
                 Do not use Markdown.
                 """
                }
            ]
        }
    ]
)
    recipe_text = recipe_result.output_text.strip()
    recipe_data = json.loads(recipe_text)
    


    main_image = get_recipe_image(recipe_data["recipe_name"])
    recipe_data["main_image"] = main_image

    for similar in recipe_data["similar_recipes"]:
        image_url = get_recipe_image(similar["name"])
        similar["image"] = image_url

    for ingredient in recipe_data["ingredients"]:
        image_url = get_ingredient_image(ingredient["name"])
        ingredient["image"] = image_url

    for variation in recipe_data["variations"]:
        image_url = get_recipe_image(variation["name"])
        variation["image"] = image_url    

    with ThreadPoolExecutor(max_workers=5) as executor:
        step_images = executor.map(
        lambda step: get_step_image(step["title"]),
        recipe_data["steps"]
    )

    for step, image_url in zip(recipe_data["steps"], step_images):
        step["image"] = image_url    

   


            

    print(recipe_data)
    print(recipe_data["recipe_name"])
    return render_template("index.html",recipe = recipe_data)
    
    

    
    # return "Image uploaded successfully!"


if __name__ == "__main__":
    app.run(debug=True)