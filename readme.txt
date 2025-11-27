# AI Diet & Calorie Tracker (Project 22AIE201)

This project is a model-based intelligent agent for personalized diet management. It is a multi-page web application built with Flask.

The agent calculates custom calorie and protein goals (TDEE) based on a user's biometrics, stores all data in an SQLite database, and uses a backtracking AI algorithm to generate complete meal routines that meet the user's remaining nutritional targets.

## 🚀 Features

* **Personalized Goal Calculation:** Automatically calculates TDEE (Total Daily Energy Expenditure) and protein goals using the Mifflin-St Jeor formula based on the user's profile (height, weight, age, gender, and activity level).
* **Dynamic Dashboard:** Features real-time progress bars for daily calorie and protein intake.
* **Persistent Progress Tracking:** Uses an SQLite database (`diet.db`) to save the user's profile, daily food logs, and long-term weight history.
* **AI Meal Planner:** Uses a backtracking (state-space search) algorithm to find and recommend an optimal combination of foods from the knowledge base that satisfies the user's *remaining* nutritional targets.
* **Multi-Page Interface:** A clean, separate, multi-page application for:
    * **Dashboard:** View daily progress and log weight.
    * **Profile:** Set and update your personal biometrics.
    * **Log Food:** Add food items to your daily log.
    * **AI Meal Plan:** Get an AI-generated meal routine.

## 💻 Technology Stack

* **Backend:** Flask
* **Database:** Flask-SQLAlchemy, SQLite
* **Frontend:** HTML, CSS, JavaScript
* **Core Logic:** Python 3

## 🛠️ Installation & Setup

Follow these steps to set up and run the application.

### 1. Prerequisites
* Python 3.10+
* `pip` (Python package installer)

### 2. Setup Instructions

1.  **Navigate to the project directory** (the folder containing `app.py`).

2.  **Create a virtual environment** to keep dependencies clean.
    ```bash
    py -m venv venv
    ```

3.  **Activate the virtual environment.**
    ```bash
    .\venv\Scripts\activate
    ```
    *(Your terminal prompt should now show `(venv)`)*

4.  **Install the required packages.**
    ```bash
    pip install Flask Flask-SQLAlchemy
    ```

5.  **Initialize the Database**
    This is a **critical one-time step**. It creates the `diet.db` file and all the necessary tables (`user`, `food_log`, etc.).
    ```bash
    py -m flask init-db
    ```
    *(You should see a message: "Initialized the database and created tables.")*

## ▶️ How to Run the Application

1.  Make sure your virtual environment is still active.
2.  Run the Flask application:
    ```bash
    py -m flask run
    ```
3.  Open your web browser and go to:
    **`http://127.0.0.1:5000`**

## 📓 Application Workflow (How to Use)

1.  **Go to the Profile page FIRST.** The app will not work correctly until you set your goals.
2.  Enter your height, weight, age, and activity level. Click "Save Profile". The agent will calculate your personalized TDEE and protein goals.
3.  **Go to the Log Food page.** Select food items from the dropdown to add them to your daily log.
4.  **Go to the Dashboard.** Watch your progress bars update. You can also log your weight on this page to update your profile.
5.  **Go to the AI Meal Plan page.** Click the "Generate AI Meal Routine" button. The agent will run the backtracking algorithm to find a combination of foods that fits your *remaining* calorie and protein goals for the day.