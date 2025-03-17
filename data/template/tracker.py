from flask import Flask, render_template_string, request, redirect, session, flash
import os
import json
import datetime
import uuid

app = Flask(__name__)
app.secret_key = "gamespendingtracker"

# Create data directory
if not os.path.exists('data'):
    os.makedirs('data')

# Game categories and platforms
GAME_CATEGORIES = ["Mobile Games", "Console Games", "PC Games", "In-App Purchases", "Game Subscriptions"]
GAME_PLATFORMS = ["Fortnite", "Minecraft", "PlayStation", "Xbox", "Nintendo Switch", "Steam", "Other"]

# User data functions
def save_user(username, password):
    with open(f'data/{username}.json', 'w') as f:
        data = {
            "password": password,
            "profile": {
                "name": username,
                "balance": 5000,
                "budget": 2000,
                "limit": 1000,
                "is_parent": True
            },
            "transactions": []
        }
        json.dump(data, f)
    return data

def load_user(username):
    try:
        with open(f'data/{username}.json', 'r') as f:
            return json.load(f)
    except:
        return None

def save_transaction(username, data):
    user_data = load_user(username)
    user_data["transactions"].append(data)
    with open(f'data/{username}.json', 'w') as f:
        json.dump(user_data, f)

def add_sample_data(username):
    user_data = load_user(username)
    if not user_data["transactions"]:
        now = datetime.datetime.now()
        transactions = [
            {
                "id": str(uuid.uuid4()),
                "date": (now - datetime.timedelta(days=15)).strftime("%Y-%m-%d"),
                "amount": 599,
                "description": "Minecraft Subscription",
                "platform": "Minecraft",
                "category": "Game Subscriptions",
                "approved": True
            },
            {
                "id": str(uuid.uuid4()),
                "date": (now - datetime.timedelta(days=10)).strftime("%Y-%m-%d"),
                "amount": 1499,
                "description": "PlayStation Game",
                "platform": "PlayStation",
                "category": "Console Games",
                "approved": True
            },
            {
                "id": str(uuid.uuid4()),
                "date": now.strftime("%Y-%m-%d"),
                "amount": 399,
                "description": "Fortnite V-Bucks",
                "platform": "Fortnite",
                "category": "In-App Purchases",
                "approved": False
            }
        ]
        user_data["transactions"] = transactions
        with open(f'data/{username}.json', 'w') as f:
            json.dump(user_data, f)
        return True
    return False

# HTML Templates
BASE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Game Spending Tracker</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    <style>
        .card { margin-bottom: 20px; }
        .navbar-brand { font-weight: bold; }
        .stats-card { text-align: center; padding: 20px; }
        .stats-card i { font-size: 2rem; margin-bottom: 10px; color: #6c757d; }
        .stats-value { font-size: 1.5rem; font-weight: bold; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/"><i class="fas fa-gamepad me-2"></i>Game Spending Tracker</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    {% if session.username %}
                    <li class="nav-item"><a class="nav-link" href="/dashboard"><i class="fas fa-chart-line me-1"></i>Dashboard</a></li>
                    <li class="nav-item"><a class="nav-link" href="/add"><i class="fas fa-coins me-1"></i>Record Spending</a></li>
                    <li class="nav-item"><a class="nav-link" href="/approvals"><i class="fas fa-check-circle me-1"></i>Approvals</a></li>
                    {% endif %}
                </ul>
                <ul class="navbar-nav">
                    {% if session.username %}
                    <li class="nav-item"><a class="nav-link" href="/logout"><i class="fas fa-sign-out-alt me-1"></i>Logout</a></li>
                    {% else %}
                    <li class="nav-item"><a class="nav-link" href="/login"><i class="fas fa-sign-in-alt me-1"></i>Login</a></li>
                    <li class="nav-item"><a class="nav-link" href="/register"><i class="fas fa-user-plus me-1"></i>Register</a></li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <div class="container py-4">
        {% for message in get_flashed_messages() %}
        <div class="alert alert-info">
            {{ message }}
        </div>
        {% endfor %}
        
        {{ content | safe }}
    </div>

    <footer class="bg-light py-3 text-center">
        <p class="text-muted mb-0">&copy; 2025 Game Spending Tracker | Developed by Shree Ugale</p>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# Routes
@app.route('/')
def index():
    if 'username' in session:
        return redirect('/dashboard')
    
    content = """
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card shadow">
                <div class="card-body p-0">
                    <div class="row g-0">
                        <div class="col-md-6 bg-primary text-white p-5">
                            <h2 class="fw-bold mb-4">Game Spending Tracker</h2>
                            <p class="lead mb-4">Monitor and control gaming expenses for your family</p>
                            <ul class="list-unstyled mb-4">
                                <li class="mb-2"><i class="fas fa-check-circle me-2"></i>Track game purchases</li>
                                <li class="mb-2"><i class="fas fa-check-circle me-2"></i>Set spending limits</li>
                                <li class="mb-2"><i class="fas fa-check-circle me-2"></i>Approve children's purchases</li>
                            </ul>
                        </div>
                        <div class="col-md-6 p-5">
                            <h3 class="text-center mb-4">Welcome!</h3>
                            <div class="d-grid gap-2">
                                <a href="/login" class="btn btn-primary btn-lg mb-3"><i class="fas fa-sign-in-alt me-2"></i>Login</a>
                                <a href="/register" class="btn btn-outline-primary btn-lg"><i class="fas fa-user-plus me-2"></i>Register</a>
                            </div>
                            <hr class="my-4">
                            <p class="text-center text-muted small">Register a new account to try the demo.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    return render_template_string(BASE_HTML, content=content)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please provide both username and password')
            return redirect('/register')
        
        if load_user(username):
            flash('Username already exists')
            return redirect('/register')
        
        save_user(username, password)
        flash('Account created successfully! Please login.')
        return redirect('/login')
    
    content = """
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <h4 class="mb-0"><i class="fas fa-user-plus me-2"></i>Create Account</h4>
                </div>
                <div class="card-body">
                    <form method="POST" action="/register">
                        <div class="mb-3">
                            <label for="username" class="form-label">Username</label>
                            <input type="text" class="form-control" id="username" name="username" required>
                        </div>
                        <div class="mb-3">
                            <label for="password" class="form-label">Password</label>
                            <input type="password" class="form-control" id="password" name="password" required>
                        </div>
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary">Register</button>
                        </div>
                    </form>
                    <hr>
                    <p class="text-center mb-0">Already have an account? <a href="/login">Login here</a></p>
                </div>
            </div>
        </div>
    </div>
    """
    return render_template_string(BASE_HTML, content=content)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_data = load_user(username)
        if not user_data or user_data['password'] != password:
            flash('Invalid username or password')
            return redirect('/login')
        
        session['username'] = username
        return redirect('/dashboard')
    
    content = """
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <h4 class="mb-0"><i class="fas fa-sign-in-alt me-2"></i>Login</h4>
                </div>
                <div class="card-body">
                    <form method="POST" action="/login">
                        <div class="mb-3">
                            <label for="username" class="form-label">Username</label>
                            <input type="text" class="form-control" id="username" name="username" required>
                        </div>
                        <div class="mb-3">
                            <label for="password" class="form-label">Password</label>
                            <input type="password" class="form-control" id="password" name="password" required>
                        </div>
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary">Login</button>
                        </div>
                    </form>
                    <hr>
                    <p class="text-center mb-0">Don't have an account? <a href="/register">Register here</a></p>
                </div>
            </div>
        </div>
    </div>
    """
    return render_template_string(BASE_HTML, content=content)

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out')
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/login')
    
    username = session['username']
    user_data = load_user(username)
    
    # Calculate stats
    total_spent = sum(t["amount"] for t in user_data["transactions"])
    approved_spent = sum(t["amount"] for t in user_data["transactions"] if t["approved"])
    pending_count = sum(1 for t in user_data["transactions"] if not t["approved"])
    
    transactions_html = ""
    if user_data["transactions"]:
        transactions_html = """
        <div class="table-responsive">
            <table class="table table-hover">
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
        """
        
        for t in sorted(user_data["transactions"], key=lambda x: x["date"], reverse=True):
            status = '<span class="badge bg-success">Approved</span>' if t["approved"] else '<span class="badge bg-warning">Pending</span>'
            transactions_html += f"""
                <tr>
                    <td>{t["date"]}</td>
                    <td>{t["description"]}</td>
                    <td>{t["platform"]}</td>
                    <td>{t["category"]}</td>
                    <td>₹{t["amount"]}</td>
                    <td>{status}</td>
                </tr>
            """
        
        transactions_html += """
                </tbody>
            </table>
        </div>
        """
    else:
        transactions_html = """
        <div class="text-center p-4">
            <p class="text-muted">No transactions yet</p>
            <a href="/add" class="btn btn-primary"><i class="fas fa-plus me-1"></i>Add First Transaction</a>
        </div>
        """
    
    content = f"""
    <div class="row mb-4">
        <div class="col-md-8">
            <h2>Welcome, {username}</h2>
            <p class="text-muted">Parent Account</p>
        </div>
        <div class="col-md-4 text-end">
            <a href="/sample-data" class="btn btn-outline-primary"><i class="fas fa-plus-circle me-1"></i>Add Sample Data</a>
        </div>
    </div>

    <div class="row mb-4">
        <div class="col-md-4">
            <div class="card stats-card">
                <i class="fas fa-wallet"></i>
                <div>Balance</div>
                <div class="stats-value">₹{user_data["profile"]["balance"]}</div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card stats-card">
                <i class="fas fa-chart-line"></i>
                <div>Total Spent</div>
                <div class="stats-value">₹{total_spent}</div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card stats-card">
                <i class="fas fa-gamepad"></i>
                <div>Game Limit</div>
                <div class="stats-value">₹{user_data["profile"]["limit"]}</div>
            </div>
        </div>
    </div>

    <div class="card mb-4">
        <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Recent Transactions</h5>
            <a href="/add" class="btn btn-sm btn-primary"><i class="fas fa-plus me-1"></i>Add</a>
        </div>
        <div class="card-body p-0">
            {transactions_html}
        </div>
    </div>

    <div class="card bg-light border-primary">
        <div class="card-body">
            <h5 class="card-title"><i class="fas fa-lightbulb text-warning me-2"></i>Gaming Tip</h5>
            <p class="card-text">Consider subscription services like Game Pass instead of buying individual games to save money.</p>
        </div>
    </div>
    """
    
    return render_template_string(BASE_HTML, content=content)

@app.route('/add', methods=['GET', 'POST'])
def add_transaction():
    if 'username' not in session:
        return redirect('/login')
    
    username = session['username']
    user_data = load_user(username)
    
    if request.method == 'POST':
        amount = int(request.form.get('amount', 0))
        description = request.form.get('description', '')
        platform = request.form.get('platform', '')
        category = request.form.get('category', '')
        
        if amount <= 0 or not description or not platform or not category:
            flash('Please fill all fields correctly')
            return redirect('/add')
        
        transaction = {
            "id": str(uuid.uuid4()),
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "amount": amount,
            "description": description,
            "platform": platform,
            "category": category,
            "approved": False
        }
        
        user_data["transactions"].append(transaction)
        user_data["profile"]["balance"] -= amount
        
        with open(f'data/{username}.json', 'w') as f:
            json.dump(user_data, f)
        
        flash('Transaction added successfully! Waiting for approval.')
        return redirect('/dashboard')
    
    platforms_options = ""
    for platform in GAME_PLATFORMS:
        platforms_options += f'<option value="{platform}">{platform}</option>'
    
    categories_options = ""
    for category in GAME_CATEGORIES:
        categories_options += f'<option value="{category}">{category}</option>'
    
    content = f"""
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <h4 class="mb-0"><i class="fas fa-gamepad me-2"></i>Record Game Purchase</h4>
                </div>
                <div class="card-body">
                    <form method="POST" action="/add">
                        <div class="mb-3">
                            <label for="amount" class="form-label">Amount (₹)</label>
                            <input type="number" class="form-control" id="amount" name="amount" required min="1">
                        </div>
                        
                        <div class="mb-3">
                            <label for="description" class="form-label">Description</label>
                            <input type="text" class="form-control" id="description" name="description" required 
                                   placeholder="e.g., Minecraft Subscription">
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="platform" class="form-label">Game Platform</label>
                                <select class="form-select" id="platform" name="platform" required>
                                    <option value="" disabled selected>Select platform</option>
                                    {platforms_options}
                                </select>
                            </div>
                            
                            <div class="col-md-6 mb-3">
                                <label for="category" class="form-label">Game Category</label>
                                <select class="form-select" id="category" name="category" required>
                                    <option value="" disabled selected>Select category</option>
                                    {categories_options}
                                </select>
                            </div>
                        </div>
                        
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle me-2"></i>
                            This purchase will require approval before it's finalized.
                        </div>
                        
                        <div class="alert alert-warning">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            Your monthly game spending limit is ₹{user_data["profile"]["limit"]}.
                        </div>
                        
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-save me-2"></i>Record Purchase
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
    """
    
    return render_template_string(BASE_HTML, content=content)

@app.route('/approvals')
def approvals():
    if 'username' not in session:
        return redirect('/login')
    
    username = session['username']
    user_data = load_user(username)
    
    pending_transactions = [t for t in user_data["transactions"] if not t["approved"]]
    
    if pending_transactions:
        transactions_html = """
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Description</th>
                        <th>Platform</th>
                        <th>Category</th>
                        <th>Amount</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for t in pending_transactions:
            transactions_html += f"""
                <tr>
                    <td>{t["date"]}</td>
                    <td>{t["description"]}</td>
                    <td>{t["platform"]}</td>
                    <td>{t["category"]}</td>
                    <td>₹{t["amount"]}</td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <a href="/approve/{t["id"]}" class="btn btn-success" title="Approve">
                                <i class="fas fa-check"></i>
                            </a>
                            <a href="/deny/{t["id"]}" class="btn btn-danger" title="Deny">
                                <i class="fas fa-times"></i>
                            </a>
                        </div>
                    </td>
                </tr>
            """
        
        transactions_html += """
                </tbody>
            </table>
        </div>
        """
    else:
        transactions_html = """
        <div class="text-center p-5">
            <i class="fas fa-check-circle fa-4x text-success mb-3"></i>
            <h4>No Pending Approvals</h4>
            <p class="text-muted">There are no game purchases waiting for your approval.</p>
            <a href="/dashboard" class="btn btn-primary mt-2">
                <i class="fas fa-home me-1"></i>Return to Dashboard
            </a>
        </div>
        """
    
    content = f"""
    <div class="row mb-4">
        <div class="col">
            <h2><i class="fas fa-check-circle me-2"></i>Parent Approval</h2>
            <p class="text-muted">Review and approve game purchases</p>
        </div>
    </div>

    <div class="card">
        <div class="card-header bg-light">
            <h5 class="mb-0">Pending Approvals</h5>
        </div>
        <div class="card-body p-0">
            {transactions_html}
        </div>
    </div>
    """
    
    return render_template_string(BASE_HTML, content=content)

@app.route('/approve/<transaction_id>')
def approve(transaction_id):
    if 'username' not in session:
        return redirect('/login')
    
    username = session['username']
    user_data = load_user(username)
    
    for t in user_data["transactions"]:
        if t["id"] == transaction_id:
            t["approved"] = True
            break
    
    with open(f'data/{username}.json', 'w') as f:
        json.dump(user_data, f)
    
    flash('Transaction approved')
    return redirect('/approvals')

@app.route('/deny/<transaction_id>')
def deny(transaction_id):
    if 'username' not in session:
        return redirect('/login')
    
    username = session['username']
    user_data = load_user(username)
    
    for i, t in enumerate(user_data["transactions"]):
        if t["id"] == transaction_id:
            # Refund the amount
            user_data["profile"]["balance"] += t["amount"]
            # Remove the transaction
            user_data["transactions"].pop(i)
            break
    
    with open(f'data/{username}.json', 'w') as f:
        json.dump(user_data, f)
    
    flash('Transaction denied and amount refunded')
    return redirect('/approvals')

@app.route('/sample-data')
def sample_data():
    if 'username' not in session:
        return redirect('/login')
    
    username = session['username']
    if add_sample_data(username):
        flash('Sample data added successfully')
    else:
        flash('Sample data not added (transactions already exist)')
    
    return redirect('/dashboard')

if __name__ == '__main__':
    app.run(debug=True)