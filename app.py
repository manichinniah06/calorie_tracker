import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
import datetime
import math
import heapq
import random

# --- App & Database Setup ---
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'diet.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'
db = SQLAlchemy(app)

# --- 1. FOOD KNOWLEDGE BASE (With High-Protein Veg Options) ---
FOOD_KB = {
    # --- BREAKFAST ---
    "Masala Dosa (1 pc)": {"calories": 350, "protein": 6, "carbs": 45, "fat": 14, "type": "breakfast", "diet": "veg"},
    "Idly (2 pcs) + Sambar": {"calories": 200, "protein": 8, "carbs": 35, "fat": 2, "type": "breakfast", "diet": "veg"},
    "Poha with Peanuts": {"calories": 270, "protein": 8, "carbs": 40, "fat": 10, "type": "breakfast", "diet": "veg"},
    "Paneer Paratha + Curd": {"calories": 380, "protein": 14, "carbs": 35, "fat": 18, "type": "breakfast", "diet": "veg"},
    "Moong Dal Chilla (2 pcs)": {"calories": 250, "protein": 14, "carbs": 30, "fat": 6, "type": "breakfast", "diet": "veg"},
    "Boiled Eggs (3)": {"calories": 230, "protein": 18, "carbs": 2, "fat": 15, "type": "breakfast", "diet": "non-veg"},
    "Omelette (3 eggs)": {"calories": 300, "protein": 20, "carbs": 2, "fat": 22, "type": "breakfast", "diet": "non-veg"},

    # --- MAINS (High Protein Veg Added) ---
    "Soya Chunks Masala": {"calories": 280, "protein": 25, "carbs": 15, "fat": 10, "type": "main", "diet": "veg"},
    "Paneer Bhurji + 2 Chapati": {"calories": 420, "protein": 22, "carbs": 35, "fat": 20, "type": "main", "diet": "veg"},
    "Grilled Tofu Salad": {"calories": 250, "protein": 20, "carbs": 10, "fat": 12, "type": "main", "diet": "veg"},
    "Rajma Chawal": {"calories": 400, "protein": 14, "carbs": 60, "fat": 10, "type": "main", "diet": "veg"},
    "Dal Tadka + Rice": {"calories": 350, "protein": 12, "carbs": 55, "fat": 8, "type": "main", "diet": "veg"},
    "Palak Paneer + Roti": {"calories": 380, "protein": 18, "carbs": 35, "fat": 20, "type": "main", "diet": "veg"},
    "Chole Masala + Rice": {"calories": 450, "protein": 14, "carbs": 65, "fat": 14, "type": "main", "diet": "veg"},
    
    # --- NON-VEG MAINS ---
    "Grilled Chicken Breast": {"calories": 200, "protein": 40, "carbs": 0, "fat": 4, "type": "main", "diet": "non-veg"},
    "Chicken Curry + Rice": {"calories": 450, "protein": 30, "carbs": 50, "fat": 15, "type": "main", "diet": "non-veg"},
    "Fish Curry + Rice": {"calories": 400, "protein": 28, "carbs": 50, "fat": 12, "type": "main", "diet": "non-veg"},
    "Chicken Biryani": {"calories": 500, "protein": 25, "carbs": 60, "fat": 18, "type": "main", "diet": "non-veg"},

    # --- SNACKS (Protein Boosters) ---
    "Whey Protein Shake": {"calories": 120, "protein": 24, "carbs": 3, "fat": 1, "type": "snack", "diet": "veg"},
    "Greek Yogurt": {"calories": 100, "protein": 10, "carbs": 4, "fat": 0, "type": "snack", "diet": "veg"},
    "Roasted Chana (50g)": {"calories": 180, "protein": 10, "carbs": 30, "fat": 3, "type": "snack", "diet": "veg"},
    "Masala Chai": {"calories": 100, "protein": 3, "carbs": 15, "fat": 3, "type": "snack", "diet": "veg"},
    "Apple": {"calories": 95, "protein": 0.5, "carbs": 25, "fat": 0.3, "type": "snack", "diet": "veg"},
    "Banana": {"calories": 105, "protein": 1.3, "carbs": 27, "fat": 0.3, "type": "snack", "diet": "veg"},
}

# --- Database Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    height = db.Column(db.Float, default=170)
    weight = db.Column(db.Float, default=70)
    age = db.Column(db.Integer, default=25)
    gender = db.Column(db.String(10), default='male')
    activity = db.Column(db.Float, default=1.2)
    preference = db.Column(db.String(20), default='Non-Vegetarian')
    
    tdee = db.Column(db.Float, default=2000)
    protein_goal = db.Column(db.Float, default=150)
    carbs_goal = db.Column(db.Float, default=250)
    fat_goal = db.Column(db.Float, default=65)

class FoodLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.date.today)
    food_name = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Float, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    carbs = db.Column(db.Float, nullable=False)
    fat = db.Column(db.Float, nullable=False)

class WeightLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.date.today)
    weight = db.Column(db.Float, nullable=False)

# --- Logic ---
def calculate_goals(user):
    if user.weight is None or user.height is None: return
    if user.gender == 'male':
        bmr = (10 * user.weight) + (6.25 * user.height) - (5 * user.age) + 5
    else:
        bmr = (10 * user.weight) + (6.25 * user.height) - (5 * user.age) - 161
    user.tdee = round(bmr * user.activity)
    user.protein_goal = round((user.tdee * 0.30) / 4)
    user.carbs_goal = round((user.tdee * 0.40) / 4)
    user.fat_goal = round((user.tdee * 0.30) / 9)

# --- 2. FIXED A* PLANNER ---
class AStarPlanner:
    def __init__(self, kb, t_cal, t_pro, t_carb, t_fat, user_pref):
        self.foods = []
        self.t_cal = t_cal
        self.t_pro = t_pro
        self.t_carb = t_carb
        self.t_fat = t_fat
        
        self.max_items = 8 # INCREASED: Allow more items to hit high protein
        self.cal_tolerance = 200
        
        # Filter KB
        for name, data in kb.items():
            if user_pref == "Vegetarian" and data['diet'] == "non-veg":
                continue
            self.foods.append((name, data))

    def heuristic(self, c_cal, c_pro, c_carb, c_fat):
        """
        Super-weighted Heuristic.
        Protein diff is multiplied by 20 to force the AI to care about it.
        """
        d_cal = abs(self.t_cal - c_cal)
        d_pro = abs(self.t_pro - c_pro) * 20  # HUGE Priority on Protein
        d_carb = abs(self.t_carb - c_carb) * 2
        d_fat = abs(self.t_fat - c_fat) * 4
        
        return d_cal + d_pro + d_carb + d_fat

    def solve(self):
        # (f, g, cal, pro, carb, fat, items_list)
        pq = []
        heapq.heappush(pq, (self.heuristic(0, 0, 0, 0), 0, 0, 0, 0, 0, []))
        visited = set()

        while pq:
            f, g, cal, pro, carb, fat, items = heapq.heappop(pq)

            # Goal Check: Protein must be close (within 15g)
            cal_ok = abs(self.t_cal - cal) <= self.cal_tolerance
            pro_ok = abs(self.t_pro - pro) <= 15 
            
            if cal_ok and pro_ok:
                return items

            if len(items) >= self.max_items: continue
            if cal > self.t_cal + self.cal_tolerance: continue

            state_sig = (int(cal/20), int(pro/5), tuple(sorted(items)))
            if state_sig in visited: continue
            visited.add(state_sig)

            # Shuffle for variety
            random.shuffle(self.foods)

            for name, data in self.foods:
                current_count = items.count(name)
                ftype = data['type']
                
                # --- Realism Constraints ---
                if current_count >= 1 and ftype == 'main': continue # No repeat mains
                if current_count >= 2: continue # No item > 2 times
                
                # Allow multiple "snacks" if they are protein shakes
                if ftype == 'snack' and 'Protein' in name and current_count >= 2: continue

                new_cal = cal + data['calories']
                new_pro = pro + data['protein']
                new_carb = carb + data['carbs']
                new_fat = fat + data['fat']
                new_items = items + [name]
                
                new_g = g + 1
                new_f = new_g + self.heuristic(new_cal, new_pro, new_carb, new_fat)
                
                heapq.heappush(pq, (new_f, new_g, new_cal, new_pro, new_carb, new_fat, new_items))
        
        return None

def organize_meal_plan(item_names):
    if not item_names: return {}
    plan = {"Breakfast": [], "Lunch": [], "Dinner": [], "Snacks": []}
    mains = []
    
    for name in item_names:
        ftype = FOOD_KB[name]['type']
        if ftype == 'breakfast': plan['Breakfast'].append(name)
        elif ftype == 'snack': plan['Snacks'].append(name)
        else: mains.append(name)

    for i, food in enumerate(mains):
        if i % 2 == 0: plan['Lunch'].append(food)
        else: plan['Dinner'].append(food)
            
    return plan

# --- Helper Functions ---
def get_user_data():
    user = db.session.get(User, 1)
    if not user:
        user = User(id=1, height=170.0, weight=70.0, age=25, gender='male', activity=1.2, preference='Non-Vegetarian')
        calculate_goals(user)
        db.session.add(user)
        db.session.commit()
    return user

def get_today_log():
    today = datetime.date.today()
    log = FoodLog.query.filter_by(date=today).all()
    totals = {
        'calories': sum(i.calories for i in log),
        'protein': sum(i.protein for i in log),
        'carbs': sum(i.carbs for i in log),
        'fat': sum(i.fat for i in log)
    }
    return log, totals

# --- Routes ---
@app.route('/')
def dashboard():
    user = get_user_data()
    _, totals = get_today_log()
    weight_history = WeightLog.query.order_by(WeightLog.date.asc()).all()
    today_date = datetime.date.today().strftime('%B %d, %Y')
    return render_template('dashboard.html', user=user, totals=totals, weight_history=weight_history, today_date=today_date)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user = get_user_data()
    if request.method == 'POST':
        user.height = float(request.form['height'])
        user.weight = float(request.form['weight'])
        user.age = int(request.form['age'])
        user.gender = request.form['gender']
        user.activity = float(request.form['activity'])
        user.preference = request.form['preference']
        calculate_goals(user)
        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('profile'))
    return render_template('profile.html', user=user)

@app.route('/log', methods=['GET', 'POST'])
def log():
    user = get_user_data()
    if request.method == 'POST':
        food_name = request.form['food_name']
        data = FOOD_KB[food_name]
        new_log = FoodLog(
            food_name=food_name, calories=data['calories'],
            protein=data['protein'], carbs=data['carbs'], fat=data['fat']
        )
        db.session.add(new_log)
        db.session.commit()
        flash(f'Added {food_name}', 'success')
        return redirect(url_for('log'))
    log_items, totals = get_today_log()
    today_date = datetime.date.today().strftime('%B %d, %Y')
    
    allowed_foods = []
    for name, data in FOOD_KB.items():
        if user.preference == 'Vegetarian' and data['diet'] == 'non-veg':
            continue
        allowed_foods.append(name)
    allowed_foods.sort()

    return render_template('log.html', user=user, food_list=allowed_foods, today_log=log_items, totals=totals, today_date=today_date)

@app.route('/plan')
def plan():
    user = get_user_data()
    _, totals = get_today_log()
    rem_cal = int(user.tdee - totals['calories'])
    rem_pro = int(user.protein_goal - totals['protein'])
    rem_carb = int(user.carbs_goal - totals['carbs'])
    rem_fat = int(user.fat_goal - totals['fat'])
    
    remaining = {'calories': rem_cal, 'protein': rem_pro, 'carbs': rem_carb, 'fat': rem_fat}
    return render_template('plan.html', user=user, remaining=remaining)

@app.route('/api/generate_plan', methods=['POST'])
def api_generate_plan():
    user = get_user_data()
    _, totals = get_today_log()
    
    r_cal = user.tdee - totals['calories']
    r_pro = user.protein_goal - totals['protein']
    r_carb = user.carbs_goal - totals['carbs']
    r_fat = user.fat_goal - totals['fat']
    
    if r_cal <= 50: return jsonify({'error': 'You have hit your calorie goal!'})
    
    planner = AStarPlanner(FOOD_KB, r_cal, r_pro, r_carb, r_fat, user.preference)
    raw_items = planner.solve()
    
    if not raw_items:
        return jsonify({'error': 'Strict Macro goals not met. Try logging a protein source manually first!'})
    
    organized_plan = organize_meal_plan(raw_items)
    
    plan_stats = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0}
    for meal in organized_plan.values():
        for item in meal:
            d = FOOD_KB[item]
            plan_stats['calories'] += d['calories']
            plan_stats['protein'] += d['protein']
            plan_stats['carbs'] += d['carbs']
            plan_stats['fat'] += d['fat']

    return jsonify({'plan': organized_plan, 'stats': plan_stats})

@app.route('/api/log_weight', methods=['POST'])
def api_log_weight():
    try:
        weight = float(request.form['weight'])
        today = datetime.date.today()
        existing = WeightLog.query.filter_by(date=today).first()
        if existing: existing.weight = weight
        else: db.session.add(WeightLog(date=today, weight=weight))
        user = get_user_data()
        user.weight = weight
        calculate_goals(user)
        db.session.commit()
        return jsonify({'success': True})
    except: return jsonify({'success': False})

@app.cli.command("init-db")
def init_db_command():
    with app.app_context():
        db.drop_all()
        db.create_all()
    print("Initialized database.")

if __name__ == '__main__':
    app.run(debug=True)