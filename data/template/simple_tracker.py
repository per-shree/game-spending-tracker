from flask import Flask, render_template_string, request, redirect, url_for, flash, session
import os
import json
import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "gamespendingtrackersecretkey"

# App configuration
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

USERS_FILE = os.path.join(DATA_DIR, "users.json")

# Game categories and platforms
GAME_CATEGORIES = [
    "Mobile Games", "Console Games", "PC Games", "In-App Purchases", 
    "Game Subscriptions", "Gaming Hardware", "Virtual Currency"
]

GAME_PLATFORMS = [
    "Fortnite", "Roblox", "Minecraft", "PUBG Mobile", "Genshin Impact",
    "Call of Duty", "FIFA", "Steam", "Epic Games", "PlayStation", 
    "Xbox", "Nintendo Switch", "App Store", "Google Play", "Other"
]

# Helper functions
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def get_user_file(username):
    return os.path.join(DATA_DIR, f"{username}_data.json")

def load_user_data(username):
    user_file = get_user_file(username)
    if os.path.exists(user_file):
        with open(user_file, 'r') as f:
            return json.load(f)
    return {
        "profile": {
            "name": "",
            "account_balance": 0,
            "monthly_budget": 0,
            "parent_email": "",
            "parent_mode": False,
            "game_spending_limit": 0,
            "child_name": "",
            "is_child_account": False,
            "parent_account": ""
        },
        "transactions": []
    }

def save_user_data(username, data):
    user_file = get_user_file(username)
    with open(user_file, 'w') as f:
        json.dump(data, f, indent=4)

def get_gaming_tip():
    tips = [
        "Set a time limit for gaming sessions to maintain balance.",
        "Look for game bundles and sales to save money on purchases.",
        "Consider subscription services like Game Pass instead of buying individual games.",
        "Avoid impulse purchases of in-game items and cosmetics.",
        "Wait a week before buying a new game to make sure you really want it."
    ]
    
    import random
    return random.choice(tips)

# Add sample data for demonstration
def add_sample_data(username):
    user_data = load_user_data(username)
    
    # Only add sample data if no transactions exist
    if not user_data["transactions"]:
        # Set profile data
        user_data["profile"] = {
            "name": "Sample User",
            "account_balance": 5000.00,
            "monthly_budget": 10000.00,
            "parent_email": "parent@example.com",
            "parent_mode": True,
            "game_spending_limit": 2000.00
        }
        
        # Sample transactions
        now = datetime.datetime.now()
        
        sample_transactions = [
            {
                "id": str(uuid.uuid4()),
                "date": (now - datetime.timedelta(days=20)).isoformat(),
                "amount": 299.00,
                "description": "Minecraft Subscription",
                "game_platform": "Minecraft",
                "game_category": "Game Subscriptions",
                "is_game_purchase": True,
                "approved_by_parent": True
            },
            {
                "id": str(uuid.uuid4()),
                "date": (now - datetime.timedelta(days=15)).isoformat(),
                "amount": 1499.00,
                "description": "Call of Duty: Modern Warfare",
                "game_platform": "PlayStation",
                "game_category": "Console Games",
                "is_game_purchase": True,
                "approved_by_parent": True
            },
            {
                "id": str(uuid.uuid4()),
                "date": (now - datetime.timedelta(days=10)).isoformat(),
                "amount": 799.00,
                "description": "Nintendo Switch Online Subscription",
                "game_platform": "Nintendo Switch",
                "game_category": "Game Subscriptions",
                "is_game_purchase": True,
                "approved_by_parent": True
            },
            {
                "id": str(uuid.uuid4()),
                "date": (now - datetime.timedelta(days=5)).isoformat(),
                "amount": 899.00,
                "description": "FIFA 2023",
                "game_platform": "Xbox",
                "game_category": "Console Games",
                "is_game_purchase": True,
                "approved_by_parent": True
            },
            {
                "id": str(uuid.uuid4()),
                "date": now.isoformat(),
                "amount": 399.00,
                "description": "PUBG Mobile Royal Pass",
                "game_platform": "PUBG Mobile",
                "game_category": "In-App Purchases",
                "is_game_purchase": True,
                "approved_by_parent": False
            }
        ]
        
        user_data["transactions"] = sample_transactions
        save_user_data(username, user_data)
        return True
    
    return False

# Define the base HTML
BASE_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Game Spending Tracker</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    <style>
        .navbar-brand {
            font-weight: bold;
        }
        .app-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .card {
            margin-bottom: 1.5rem;
            box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
        }
        .stats-card {
            text-align: center;
            padding: 1rem;
        }
        .stats-card i {
            font-size: 2rem;
            margin-bottom: 0.5rem;
            color: #6c757d;
        }
        .stats-card .stats-title {
            font-size: 0.875rem;
            color: #6c757d;
        }
        .stats-card .stats-value {
            font-size: 1.5rem;
            font-weight: bold;
        }
        .budget-progress {
            height: 0.5rem;
            margin-top: 0.25rem;
        }
        .tip-card {
            background-color: #f8f9fa;
            border-left: 4px solid #007bff;
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-gamepad me-2"></i>Game Spending Tracker
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    {% if session.username %}
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('dashboard') }}">
                            <i class="fas fa-chart-line me-1"></i>Dashboard
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('game_spending') }}">
                            <i class="fas fa-coins me-1"></i>Record Spending
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('profile') }}">
                            <i class="fas fa-user-cog me-1"></i>Profile
                        </a>
                    </li>
                    {% if session.account_type == 'parent' %}
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('parent_approval') }}">
                            <i class="fas fa-check-circle me-1"></i>Approvals
                        </a>
                    </li>
                    {% endif %}
                    {% endif %}
                </ul>
                <ul class="navbar-nav">
                    {% if session.username %}
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('logout') }}">
                            <i class="fas fa-sign-out-alt me-1"></i>Logout
                        </a>
                    </li>
                    {% else %}
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('login') }}">
                            <i class="fas fa-sign-in-alt me-1"></i>Login
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('register') }}">
                            <i class="fas fa-user-plus me-1"></i>Register
                        </a>
                    </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <div class="container app-container">
        <!-- Flash Messages -->
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                <div class="alert alert-{{ category }}">
                    {{ message }}
                </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <!-- Page Content -->
        {{ content | safe }}
    </div>

    <!-- Footer -->
    <footer class="bg-light py-3 mt-auto">
        <div class="container text-center">
            <p class="text-muted mb-0">
                &copy; 2025 Game Spending Tracker | Developed by Shree Ugale
            </p>
        </div>
    </footer>

    <!-- Bootstrap JS Bundle -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# Routes
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    
    content = '''
    <div class="row justify-content-center">
        <div class="col-md-10">
            <div class="card border-0 rounded-3 shadow-lg overflow-hidden">
                <div class="card-body p-0">
                    <div class="row g-0">
                        <div class="col-md-6 d-none d-md-block">
                            <div class="bg-primary text-white p-5 h-100 d-flex flex-column justify-content-center">
                                <h2 class="fw-bold mb-4">Game Spending Tracker</h2>
                                <p class="lead mb-4">Monitor and control gaming expenses for your family</p>
                                <ul class="list-unstyled mb-4">
                                    <li class="mb-2">
                                        <i class="fas fa-check-circle me-2"></i>Track game purchases
                                    </li>
                                    <li class="mb-2">
                                        <i class="fas fa-check-circle me-2"></i>Set spending limits
                                    </li>
                                    <li class="mb-2">
                                        <i class="fas fa-check-circle me-2"></i>Approve children's purchases
                                    </li>
                                    <li class="mb-2">
                                        <i class="fas fa-check-circle me-2"></i>Visualize spending patterns
                                    </li>
                                </ul>
                                <p>Take control of your family's gaming budget today!</p>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="p-5">
                                <div class="text-center">
                                    <h1 class="h4 text-gray-900 mb-4">Welcome to Game Spending Tracker</h1>
                                </div>
                                <div class="row mt-4">
                                    <div class="col-md-6">
                                        <a href="{{ url_for('login') }}" class="btn btn-primary btn-lg btn-block w-100 mb-3">
                                            <i class="fas fa-sign-in-alt me-2"></i>Login
                                        </a>
                                    </div>
                                    <div class="col-md-6">
                                        <a href="{{ url_for('register') }}" class="btn btn-outline-primary btn-lg btn-block w-100 mb-3">
                                            <i class="fas fa-user-plus me-2"></i>Register
                                        </a>
                                    </div>
                                </div>
                                <hr class="my-4">
                                <div class="text-center">
                                    <h4 class="h5 mb-3">Demo Account</h4>
                                    <p class="small">To explore the app quickly, register a new account and then click "Add Sample Data" from your dashboard.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''
    
    return render_template_string(BASE_HTML, content=content)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        account_type = request.form.get('account_type', 'parent')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))
        
        users = load_users()
        
        if username in users:
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        
        # Create new user
        users[username] = {
            "password_hash": generate_password_hash(password),
            "created_at": datetime.datetime.now().isoformat(),
            "account_type": account_type
        }
        
        # If it's a child account, link to parent
        if account_type == 'child' and 'parent_username' in request.form:
            parent_username = request.form['parent_username']
            if parent_username in users:
                users[username]["parent_username"] = parent_username
                
                # Update child's profile
                user_data = load_user_data(username)
                user_data["profile"]["is_child_account"] = True
                user_data["profile"]["parent_account"] = parent_username
                save_user_data(username, user_data)
                
                # Update parent's profile to note they have a child account
                parent_data = load_user_data(parent_username)
                if "child_accounts" not in parent_data["profile"]:
                    parent_data["profile"]["child_accounts"] = []
                parent_data["profile"]["child_accounts"].append(username)
                save_user_data(parent_username, parent_data)
            else:
                flash('Parent account not found', 'danger')
                return redirect(url_for('register'))
        
        save_users(users)
        
        # Create initial user data
        user_data = load_user_data(username)
        if account_type == 'parent':
            user_data["profile"]["parent_mode"] = True
        save_user_data(username, user_data)
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    content = '''
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card shadow-sm">
                <div class="card-header bg-primary text-white">
                    <h4 class="mb-0"><i class="fas fa-user-plus me-2"></i>Create Account</h4>
                </div>
                <div class="card-body">
                    <form method="POST" action="{{ url_for('register') }}">
                        <div class="mb-3">
                            <label for="username" class="form-label">Username</label>
                            <input type="text" class="form-control" id="username" name="username" required autofocus>
                        </div>
                        <div class="mb-3">
                            <label for="password" class="form-label">Password</label>
                            <input type="password" class="form-control" id="password" name="password" required>
                        </div>
                        <div class="mb-3">
                            <label for="confirm_password" class="form-label">Confirm Password</label>
                            <input type="password" class="form-control" id="confirm_password" name="confirm_password" required>
                        </div>
                        <div class="mb-4">
                            <label class="form-label">Account Type</label>
                            <div class="form-check">
                                <input class="form-check-input" type="radio" name="account_type" id="parent_account" value="parent" checked>
                                <label class="form-check-label" for="parent_account">
                                    Parent Account
                                </label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="radio" name="account_type" id="child_account" value="child">
                                <label class="form-check-label" for="child_account">
                                    Child Account
                                </label>
                            </div>
                        </div>
                        <div id="parent_username_field" class="mb-3 d-none">
                            <label for="parent_username" class="form-label">Parent's Username</label>
                            <input type="text" class="form-control" id="parent_username" name="parent_username">
                            <div class="form-text">Enter the username of the parent account to link to</div>
                        </div>
                        <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-primary">Register</button>
                        </div>
                    </form>
                    <hr>
                    <div class="text-center">
                        <p class="mb-0">Already have an account? <a href="{{ url_for('login') }}">Login here</a></p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Show/hide parent username field based on account type selection
        document.addEventListener('DOMContentLoaded', function() {
            const childAccountRadio = document.getElementById('child_account');
            const parentAccountRadio = document.getElementById('parent_account');
            const parentUsernameField = document.getElementById('parent_username_field');
            
            function updateParentField() {
                if (childAccountRadio.checked) {
                    parentUsernameField.classList.remove('d-none');
                } else {
                    parentUsernameField.classList.add('d-none');
                }
            }
            
            childAccountRadio.addEventListener('change', updateParentField);
            parentAccountRadio.addEventListener('change', updateParentField);
        });
    </script>
    '''
    
    return render_template_string(BASE_HTML, content=content)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        users = load_users()
        
        if username not in users or not check_password_hash(users[username]["password_hash"], password):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        
        session['username'] = username
        # Store account type in session for easy access
        session['account_type'] = users[username].get("account_type", "parent")
        
        return redirect(url_for('dashboard'))
    
    content = '''
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card shadow-sm">
                <div class="card-header bg-primary text-white">
                    <h4 class="mb-0"><i class="fas fa-sign-in-alt me-2"></i>Login</h4>
                </div>
                <div class="card-body">
                    <form method="POST" action="{{ url_for('login') }}">
                        <div class="mb-3">
                            <label for="username" class="form-label">Username</label>
                            <input type="text" class="form-control" id="username" name="username" required autofocus>
                        </div>
                        <div class="mb-3">
                            <label for="password" class="form-label">Password</label>
                            <input type="password" class="form-control" id="password" name="password" required>
                        </div>
                        <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-primary">Login</button>
                        </div>
                    </form>
                    <hr>
                    <div class="text-center">
                        <p class="mb-0">Don't have an account? <a href="{{ url_for('register') }}">Register here</a></p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''
    
    return render_template_string(BASE_HTML, content=content)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('account_type', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user_data = load_user_data(username)
    
    # Get transactions, sorted by date (newest first)
    transactions = sorted(
        user_data["transactions"], 
        key=lambda x: x.get("date", ""), 
        reverse=True
    )
    
    # Calculate spending statistics
    total_spent = sum(t["amount"] for t in user_data["transactions"])
    
    # Monthly spending
    current_month = datetime.datetime.now().strftime("%Y-%m")
    monthly_transactions = [
        t for t in user_data["transactions"] 
        if t["date"].startswith(current_month)
    ]
    monthly_spent = sum(t["amount"] for t in monthly_transactions)
    
    # Budget calculations
    budget = user_data["profile"]["monthly_budget"]
    balance = user_data["profile"]["account_balance"]
    budget_percent = (monthly_spent / budget * 100) if budget > 0 else 0
    
    # Game spending limit
    game_limit = user_data["profile"]["game_spending_limit"]
    
    # Get a gaming tip
    gaming_tip = get_gaming_tip()
    
    is_child = user_data["profile"].get("is_child_account", False)
    
    content = f'''
    <div class="row mb-4">
        <div class="col-md-8">
            <h2>Welcome, {user_data["profile"]["name"] or session["username"]}</h2>
            <p class="text-muted">
                {'Child Account' if is_child else 'Parent Account'}
            </p>
        </div>
        <div class="col-md-4 text-end">
            <a href="{{ url_for('add_sample_data') }}" class="btn btn-outline-primary">
                <i class="fas fa-plus-circle me-1"></i>Add Sample Data
            </a>
        </div>
    </div>

    <!-- Stats Overview -->
    <div class="row mb-4">
        <div class="col-md-3">
            <div class="card stats-card">
                <i class="fas fa-wallet"></i>
                <div class="stats-title">Current Balance</div>
                <div class="stats-value">₹{balance:.2f}</div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card stats-card">
                <i class="fas fa-chart-line"></i>
                <div class="stats-title">Total Spent</div>
                <div class="stats-value">₹{total_spent:.2f}</div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card stats-card">
                <i class="fas fa-calendar-alt"></i>
                <div class="stats-title">Monthly Spent</div>
                <div class="stats-value">₹{monthly_spent:.2f}</div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card stats-card">
                <i class="fas fa-gamepad"></i>
                <div class="stats-title">Game Limit</div>
                <div class="stats-value">₹{game_limit:.2f}</div>
            </div>
        </div>
    </div>

    <!-- Budget Progress -->
    <div class="row mb-4">
        <div class="col-12">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Monthly Budget</h5>
                    <div class="d-flex justify-content-between mb-1">
                        <span>₹{monthly_spent:.2f} spent</span>
                        <span>₹{budget:.2f} budget</span>
                    </div>
                    <div class="progress budget-progress">
                        <div class="progress-bar {'bg-danger' if budget_percent > 80 else 'bg-warning' if budget_percent > 60 else 'bg-success'}" 
                             role="progressbar" 
                             style="width: {budget_percent}%;" 
                             aria-valuenow="{budget_percent}" 
                             aria-valuemin="0" 
                             aria-valuemax="100"></div>
                    </div>
                    <div class="text-end mt-1">
                        <small class="text-muted">{budget_percent:.1f}% of budget used</small>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Main Dashboard Content -->
    <div class="row">
        <!-- Transactions Column -->
        <div class="col-md-12">
            <div class="card mb-4">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5 class="mb-0">Recent Transactions</h5>
                    <a href="{{ url_for('game_spending') }}" class="btn btn-sm btn-primary">
                        <i class="fas fa-plus me-1"></i>Add
                    </a>
                </div>
                <div class="card-body p-0">
    '''
    
    if transactions:
        content += '''
                    <div class="table-responsive">
                        <table class="table table-hover mb-0">
                            <thead class="table-light">
                                <tr>
                                    <th>Date</th>
                                    <th>Description</th>
                                    <th>Platform</th>
                                    <th>Category</th>
                                    <th>Amount</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
        '''
        
        for transaction in transactions[:10]:  # Show only 10 most recent
            date = transaction["date"].split("T")[0]
            approved = transaction.get("approved_by_parent", True)
            status_badge = '<span class="badge bg-success">Approved</span>' if approved else '<span class="badge bg-warning">Pending</span>'
            
            content += f'''
                                <tr>
                                    <td>{date}</td>
                                    <td>{transaction["description"]}</td>
                                    <td>{transaction["game_platform"]}</td>
                                    <td>{transaction["game_category"]}</td>
                                    <td class="fw-bold">₹{transaction["amount"]:.2f}</td>
                                    <td>{status_badge}</td>
                                </tr>
            '''
        
        content += '''
                            </tbody>
                        </table>
                    </div>
        '''
    else:
        content += '''
                    <div class="p-4 text-center">
                        <p class="text-muted">No transactions yet</p>
                        <a href="{{ url_for('game_spending') }}" class="btn btn-sm btn-primary">
                            <i class="fas fa-plus me-1"></i>Add First Transaction
                        </a>
                    </div>
        '''
    
    content += f'''
                </div>
            </div>

            <!-- Gaming Tip -->
            <div class="card tip-card">
                <div class="card-body">
                    <h5 class="card-title"><i class="fas fa-lightbulb me-2 text-warning"></i>Gaming Tip</h5>
                    <p class="card-text">{gaming_tip}</p>
                </div>
            </div>
        </div>
    </div>
    '''
    
    return render_template_string(BASE_HTML, content=content)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user_data = load_user_data(username)
    
    if request.method == 'POST':
        # Update profile
        user_data["profile"]["name"] = request.form['name']
        user_data["profile"]["account_balance"] = float(request.form['account_balance'])
        user_data["profile"]["monthly_budget"]
        user_data["profile"]["monthly_budget"] = float(request.form['monthly_budget'])
        
        # Parent-specific fields
        if not user_data["profile"].get("is_child_account", False):
            user_data["profile"]["parent_mode"] = 'parent_mode' in request.form
            user_data["profile"]["parent_email"] = request.form['parent_email']
            
            # Child name (if parent manages a child's account)
            if 'child_name' in request.form:
                user_data["profile"]["child_name"] = request.form['child_name']
        
        # Game spending limit (can be set for both parent and child accounts)
        try:
            user_data["profile"]["game_spending_limit"] = float(request.form['game_spending_limit'])
        except ValueError:
            user_data["profile"]["game_spending_limit"] = 0
        
        save_user_data(username, user_data)
        flash('Profile updated successfully', 'success')
        return redirect(url_for('dashboard'))
    
    # If this is a child account, get the parent info
    parent_info = None
    if user_data["profile"].get("is_child_account", False) and user_data["profile"].get("parent_account"):
        parent_data = load_user_data(user_data["profile"]["parent_account"])
        parent_info = {
            "username": user_data["profile"]["parent_account"],
            "name": parent_data["profile"].get("name", "Parent")
        }
    
    is_child = user_data["profile"].get("is_child_account", False)
    
    content = '''
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card shadow-sm">
                <div class="card-header bg-primary text-white">
                    <h4 class="mb-0"><i class="fas fa-user-cog me-2"></i>Profile Settings</h4>
                </div>
                <div class="card-body">
                    <form method="POST" action="{{ url_for('profile') }}">
                        <!-- Name -->
                        <div class="mb-3">
                            <label for="name" class="form-label">Full Name</label>
                            <input type="text" class="form-control" id="name" name="name" 
                                   value="{{ profile.name }}" placeholder="Your full name">
                        </div>
                        
                        <!-- Account Balance -->
                        <div class="mb-3">
                            <label for="account_balance" class="form-label">Account Balance (₹)</label>
                            <input type="number" step="0.01" class="form-control" id="account_balance" 
                                   name="account_balance" value="{{ profile.account_balance }}">
                            <div class="form-text">Current amount available to spend on games</div>
                        </div>
                        
                        <!-- Monthly Budget -->
                        <div class="mb-3">
                            <label for="monthly_budget" class="form-label">Monthly Budget (₹)</label>
                            <input type="number" step="0.01" class="form-control" id="monthly_budget" 
                                   name="monthly_budget" value="{{ profile.monthly_budget }}">
                            <div class="form-text">Your target game spending limit per month</div>
                        </div>
                        
                        <!-- Game Spending Limit -->
                        <div class="mb-3">
                            <label for="game_spending_limit" class="form-label">Game Spending Limit (₹)</label>
                            <input type="number" step="0.01" class="form-control" id="game_spending_limit" 
                                   name="game_spending_limit" value="{{ profile.game_spending_limit }}">
                            <div class="form-text">Maximum amount allowed for game purchases per month (0 for no limit)</div>
                        </div>
    '''
    
    if not is_child:
        content += '''
                        <!-- Parent Email (only for parent accounts) -->
                        <div class="mb-3">
                            <label for="parent_email" class="form-label">Parent Email</label>
                            <input type="email" class="form-control" id="parent_email" name="parent_email" 
                                   value="{{ profile.parent_email }}" placeholder="parent@example.com">
                            <div class="form-text">Email for notifications about purchases</div>
                        </div>
                        
                        <!-- Parent Mode Toggle -->
                        <div class="mb-3 form-check">
                            <input type="checkbox" class="form-check-input" id="parent_mode" name="parent_mode" 
                                  {% if profile.parent_mode %}checked{% endif %}>
                            <label class="form-check-label" for="parent_mode">Enable Parent Mode</label>
                            <div class="form-text">When enabled, you'll need to approve game purchases</div>
                        </div>
                        
                        <!-- Child Name (if managing a child account) -->
                        <div class="mb-3">
                            <label for="child_name" class="form-label">Child's Name</label>
                            <input type="text" class="form-control" id="child_name" name="child_name" 
                                   value="{{ profile.child_name }}" placeholder="Child's name">
                            <div class="form-text">If you're managing a child's account, enter their name</div>
                        </div>
        '''
    else:
        content += '''
                        <!-- Parent Info (for child accounts) -->
                        <div class="alert alert-info">
                            <h5><i class="fas fa-info-circle me-2"></i>Parent Account Information</h5>
                            <p class="mb-1">Your account is linked to a parent account:</p>
                            <p class="mb-0"><strong>Username:</strong> {{ parent_info.username }}</p>
                            <p class="mb-0"><strong>Name:</strong> {{ parent_info.name }}</p>
                        </div>
        '''
    
    content += '''
                        <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-save me-2"></i>Save Profile
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
    '''
    
    return render_template_string(BASE_HTML, content=content, profile=user_data["profile"], parent_info=parent_info)

@app.route('/game_spending', methods=['GET', 'POST'])
def game_spending():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user_data = load_user_data(username)
    
    # Check if this is a child account to determine approval flow
    is_child = user_data["profile"].get("is_child_account", False)
    needs_approval = is_child or user_data["profile"].get("parent_mode", False)
    
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            description = request.form['description']
            game_platform = request.form['game_platform']
            game_category = request.form['game_category']
            
            if amount <= 0:
                flash('Amount must be greater than 0', 'danger')
                return redirect(url_for('game_spending'))
            
            # Create game transaction
            transaction = {
                "id": str(uuid.uuid4()),
                "date": datetime.datetime.now().isoformat(),
                "amount": amount,
                "description": description,
                "game_platform": game_platform,
                "game_category": game_category,
                "is_game_purchase": True,
                "approved_by_parent": not needs_approval  # Auto-approve if no approval needed
            }
            
            # Update balance
            user_data["profile"]["account_balance"] -= amount
            
            # Add transaction
            user_data["transactions"].append(transaction)
            save_user_data(username, user_data)
            
            if needs_approval:
                flash('Game purchase added! Waiting for parent approval.', 'info')
            else:
                flash('Game purchase recorded successfully!', 'success')
                
            return redirect(url_for('dashboard'))
        except ValueError:
            flash('Invalid amount', 'danger')
            return redirect(url_for('game_spending'))
    
    content = '''
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card shadow-sm">
                <div class="card-header bg-primary text-white">
                    <h4 class="mb-0"><i class="fas fa-gamepad me-2"></i>Record Game Purchase</h4>
                </div>
                <div class="card-body">
                    <form method="POST" action="{{ url_for('game_spending') }}">
                        <!-- Amount -->
                        <div class="mb-3">
                            <label for="amount" class="form-label">Amount (₹)</label>
                            <input type="number" step="0.01" min="0.01" class="form-control" id="amount" name="amount" required>
                        </div>
                        
                        <!-- Description -->
                        <div class="mb-3">
                            <label for="description" class="form-label">Description</label>
                            <input type="text" class="form-control" id="description" name="description" placeholder="e.g., Minecraft Subscription" required>
                        </div>
                        
                        <div class="row">
                            <!-- Game Platform -->
                            <div class="col-md-6 mb-3">
                                <label for="game_platform" class="form-label">Game Platform</label>
                                <select class="form-select" id="game_platform" name="game_platform" required>
                                    <option value="" disabled selected>Select platform</option>
                                    {% for platform in game_platforms %}
                                    <option value="{{ platform }}">{{ platform }}</option>
                                    {% endfor %}
                                </select>
                            </div>
                            
                            <!-- Game Category -->
                            <div class="col-md-6 mb-3">
                                <label for="game_category" class="form-label">Game Category</label>
                                <select class="form-select" id="game_category" name="game_category" required>
                                    <option value="" disabled selected>Select category</option>
                                    {% for category in game_categories %}
                                    <option value="{{ category }}">{{ category }}</option>
                                    {% endfor %}
                                </select>
                            </div>
                        </div>
    '''
    
    if needs_approval:
        content += '''
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle me-2"></i>
                            This purchase will require parent approval before it's finalized.
                        </div>
        '''
    
    if user_data["profile"]["game_spending_limit"] > 0:
        content += f'''
                        <div class="alert alert-warning">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            Your monthly game spending limit is ₹{user_data["profile"]["game_spending_limit"]:.2f}.
                        </div>
        '''
    
    content += '''
                        <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-save me-2"></i>Record Purchase
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
    '''
    
    return render_template_string(BASE_HTML, content=content, game_categories=GAME_CATEGORIES, game_platforms=GAME_PLATFORMS, profile=user_data["profile"], needs_approval=needs_approval)

@app.route('/parent_approval')
def parent_approval():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user_data = load_user_data(username)
    
    # Only allow access if parent mode is enabled
    if not user_data["profile"].get("parent_mode", False):
        flash('Parent mode is not enabled for this account', 'warning')
        return redirect(url_for('dashboard'))
    
    # Get all pending transactions from own account
    pending_transactions = [
        {
            "username": username,
            "user_display": "Your Account",
            "transaction": t
        }
        for t in user_data["transactions"] 
        if t.get("is_game_purchase", False) and not t.get("approved_by_parent", True)
    ]
    
    # Get pending transactions from child accounts
    if "child_accounts" in user_data["profile"]:
        for child_username in user_data["profile"]["child_accounts"]:
            child_data = load_user_data(child_username)
            child_display = child_data["profile"].get("name", child_username)
            
            child_transactions = [
                {
                    "username": child_username,
                    "user_display": child_display,
                    "transaction": t
                }
                for t in child_data["transactions"] 
                if t.get("is_game_purchase", False) and not t.get("approved_by_parent", True)
            ]
            
            pending_transactions.extend(child_transactions)
    
    content = '''
    <div class="row mb-4">
        <div class="col">
            <h2><i class="fas fa-check-circle me-2"></i>Parent Approval</h2>
            <p class="text-muted">Review and approve game purchases</p>
        </div>
    </div>
    '''
    
    if pending_transactions:
        content += '''
        <div class="row">
            <div class="col">
                <div class="card shadow-sm">
                    <div class="card-header bg-light">
                        <h5 class="mb-0">Pending Approvals</h5>
                    </div>
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-hover mb-0">
                                <thead>
                                    <tr>
                                        <th>Account</th>
                                        <th>Date</th>
                                        <th>Description</th>
                                        <th>Amount</th>
                                        <th>Platform</th>
                                        <th>Category</th>
                                        <th>Action</th>
                                    </tr>
                                </thead>
                                <tbody>
        '''
        
        for item in pending_transactions:
            date = item["transaction"]["date"].split("T")[0]
            content += f'''
                                    <tr>
                                        <td>{item["user_display"]}</td>
                                        <td>{date}</td>
                                        <td>{item["transaction"]["description"]}</td>
                                        <td class="fw-bold">₹{item["transaction"]["amount"]:.2f}</td>
                                        <td>{item["transaction"]["game_platform"]}</td>
                                        <td>{item["transaction"]["game_category"]}</td>
                                        <td>
                                            <div class="btn-group btn-group-sm">
                                                <a href="{{ url_for('approve_transaction', username='{item["username"]}', transaction_id='{item["transaction"]["id"]}') }}" 
                                                   class="btn btn-success" title="Approve">
                                                    <i class="fas fa-check"></i>
                                                </a>
                                                <a href="{{ url_for('deny_transaction', username='{item["username"]}', transaction_id='{item["transaction"]["id"]}') }}" 
                                                   class="btn btn-danger" title="Deny">
                                                    <i class="fas fa-times"></i>
                                                </a>
                                            </div>
                                        </td>
                                    </tr>
            '''
        
        content += '''
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        '''
    else:
        content += '''
        <div class="row">
            <div class="col">
                <div class="card">
                    <div class="card-body text-center p-5">
                        <i class="fas fa-check-circle fa-4x text-success mb-3"></i>
                        <h4>No Pending Approvals</h4>
                        <p class="text-muted">There are no game purchases waiting for your approval at this time.</p>
                        <a href="{{ url_for('dashboard') }}" class="btn btn-primary mt-2">
                            <i class="fas fa-home me-1"></i>Return to Dashboard
                        </a>
                    </div>
                </div>
            </div>
        </div>
        '''
    
    return render_template_string(BASE_HTML, content=content, pending_transactions=pending_transactions)

@app.route('/approve_transaction/<username>/<transaction_id>')
def approve_transaction(username, transaction_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    parent_username = session['username']
    parent_data = load_user_data(parent_username)
    
    # Verify that this user can approve transactions
    if not parent_data["profile"].get("parent_mode", False):
        flash('You do not have permission to approve transactions', 'danger')
        return redirect(url_for('dashboard'))
    
    # Verify that this user is the parent of the child account (if applicable)
    if username != parent_username and (
        "child_accounts" not in parent_data["profile"] or 
        username not in parent_data["profile"]["child_accounts"]
    ):
        flash('You do not have permission to approve this transaction', 'danger')
        return redirect(url_for('dashboard'))
    
    # Load the target user data
    user_data = load_user_data(username)
    
    # Find and approve the transaction
    transaction_found = False
    for transaction in user_data["transactions"]:
        if transaction.get("id") == transaction_id:
            transaction["approved_by_parent"] = True
            transaction_found = True
            flash('Transaction approved', 'success')
            break
    
    if not transaction_found:
        flash('Transaction not found', 'danger')
    else:
        save_user_data(username, user_data)
    
    return redirect(url_for('parent_approval'))

@app.route('/deny_transaction/<username>/<transaction_id>')
def deny_transaction(username, transaction_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    parent_username = session['username']
    parent_data = load_user_data(parent_username)
    
    # Verify that this user can deny transactions
    if not parent_data["profile"].get("parent_mode", False):
        flash('You do not have permission to deny transactions', 'danger')
        return redirect(url_for('dashboard'))
    
    # Verify that this user is the parent of the child account (if applicable)
    if username != parent_username and (
        "child_accounts" not in parent_data["profile"] or 
        username not in parent_data["profile"]["child_accounts"]
    ):
        flash('You do not have permission to deny this transaction', 'danger')
        return redirect(url_for('dashboard'))
    
    # Load the target user data
    user_data = load_user_data(username)
    
    # Find the transaction
    transaction_found = False
    for i, transaction in enumerate(user_data["transactions"]):
        if transaction.get("id") == transaction_id:
            # Refund the amount
            user_data["profile"]["account_balance"] += transaction["amount"]
            # Remove the transaction
            user_data["transactions"].pop(i)
            transaction_found = True
            flash('Transaction denied and amount refunded', 'warning')
            break
    
    if not transaction_found:
        flash('Transaction not found', 'danger')
    else:
        save_user_data(username, user_data)
    
    return redirect(url_for('parent_approval'))

@app.route('/add_sample_data')
def add_sample_data():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    success = add_sample_data(username)
    
    if success:
        flash('Sample data added successfully', 'success')
    else:
        flash('Sample data not added (transactions already exist)', 'info')
    
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)