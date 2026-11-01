# 🍽️ RecipeAI – AI Powered Recipe Generator

**RecipeAI** is an AI-powered web application that helps users discover delicious recipes from food images. Simply upload a picture of a food item, and RecipeAI uses Artificial Intelligence to identify the food and generate a complete recipe.

Get ingredients, step-by-step cooking instructions, cooking tips, health benefits, nutritional information, recipe variations, and similar recipes — all in one place.

---

## 🖥️ Homepage Preview

![RecipeAI Homepage](screenshots/home.png)

---

## ✨ Features

* 📸 **AI Food Recognition** – Upload a food image and let AI identify the food.
* 🍳 **AI Recipe Generation** – Generate delicious recipes using Google Gemini AI.
* 🥗 **Ingredients List** – Get ingredients with quantities and images.
* 👨‍🍳 **Step-by-Step Instructions** – Follow cooking instructions with images.
* 💡 **Cooking Tips** – Get helpful cooking suggestions.
* ❤️ **Health Benefits** – Explore the benefits of different recipes.
* 🔄 **Recipe Variations** – Discover different ways to prepare the same dish.
* 🍝 **Similar Recipes** – Explore other delicious food options.
* 📊 **Nutrition Information** – View calories, protein, carbohydrates, fat, and fiber.
* 💾 **Save Recipes** – Save your favourite recipes.
* 📱 **Responsive Design** – User-friendly experience across different screen sizes.

---

## 🛠️ Technologies Used

| Technology       | Purpose                |
| ---------------- | ---------------------- |
| Python           | Backend Programming    |
| Flask            | Web Framework          |
| Google Gemini AI | AI Recipe Generation   |
| HTML5            | Website Structure      |
| CSS3             | Website Styling        |
| JavaScript       | Frontend Functionality |
| JSON             | Recipe Data Management |
| Git & GitHub     | Version Control        |

---

## 📂 Project Structure

```text
RecipeAI/
│
├── app.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
│
├── templates/
│   ├── index.html
│   ├── features.html
│   └── about.html
│
├── static/
│   ├── css/
│   ├── js/
│   ├── ingredients/
│   ├── steps/
│   ├── similar/
│   ├── variations/
│   └── what can be made/
│
└── screenshots/
    └── home.png
```

---

## ⚙️ Installation & Setup

Follow these steps to run RecipeAI on your local machine.

### 1. Clone Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Open Project Folder

```bash
cd RecipeAI
```

### 3. Create Virtual Environment

```bash
python -m venv venv
```

### 4. Activate Virtual Environment

**Windows:**

```bash
venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure Gemini API Key

Create a `.env` file in the root directory.

Add your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Get your API key from Google AI Studio:

https://aistudio.google.com/

### 7. Run Application

```bash
python app.py
```

Open your browser:

```text
http://127.0.0.1:5000/
```

---

## 🧠 How RecipeAI Works

1. User uploads an image of a food item.
2. The application processes the uploaded image.
3. Google Gemini AI analyzes the food.
4. AI generates structured recipe information.
5. The backend processes the generated JSON response.
6. Recipe details are displayed on the website with images and cooking instructions.

---

## 🔑 API Configuration

RecipeAI uses the Google Gemini API for AI-powered food recognition and recipe generation.

A valid Gemini API key is required to access AI functionality.

**Security Note:** Never upload your `.env` file or expose your API key publicly. Add `.env` to `.gitignore`.

---

## 🌐 Live Website

🚀 **Explore RecipeAI:**

[![Live Website]()](https://recipe-finder-ai.onrender.com/)

Experience AI-powered recipe generation by uploading a food image!

---

## 🚀 Future Improvements

* Improve AI food recognition accuracy.
* Add more recipe categories.
* Enhance personalized recipe recommendations.
* Add user authentication.
* Improve recipe management.
* Add advanced nutritional analysis.
* Enhance AI-generated recipe suggestions.

---

## 👨‍💻 Developer

**Harshit Raj**

Backend Developer

Interested in Python, Flask, Backend Development, and AI Integration.

---

## 📜 License

This project is developed for educational and development purposes.

---

⭐ If you like RecipeAI, don't forget to give this repository a star!

**Made with ❤️ using Python, Flask & Google Gemini AI.**
