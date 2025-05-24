import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime  # Import datetime for timestamps
import os  # Import os for file handling
from werkzeug.utils import secure_filename  # Import secure_filename for safe file uploads
import random  # Import random for generating random suggestions
import requests  # Already imported
from langchain_ollama import OllamaLLM  # Restore this import

# Initialize Ollama LLM once (reuse for all requests)
llm = OllamaLLM(model="phi3:mini")

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'your_secret_key'

# PostgreSQL Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost/ayush'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Load the dataset
data = pd.read_excel(r'D:\Desktop\project\ayush\ayush\Medical_plants1.xlsx')

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(10), nullable=False, default='draft')  # 'draft' or 'publish'
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref='blogs')  # Relationship to fetch author details
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)  # Timestamp for creation
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)  # Timestamp for updates

@app.route('/')
def index_v2():
    # Fetch the latest blogs (limit to 8)
    latest_blogs = Blog.query.filter_by(status='publish').order_by(Blog.created_at.desc()).limit(8).all()
    return render_template('index_v2.html', blogs=latest_blogs)

@app.route('/search', methods=['GET','POST'])
def search():
    if request.method == 'GET':
        # This renders the search form
        return render_template('search.html')

    if request.method == 'POST':
        # This handles the form submission
        search_term = request.form['search_term']
        search_option = request.form['search_option']

        try:
            # Ensure search term is not empty
            if not search_term:
                return render_template('result.html', results="Please enter a search term.")

            # Determine the search type
            if search_option in ['Botanical Name', 'Common Name(s)']:
                result = data[data[search_option].str.contains(search_term, case=False, na=False)]
                # Display all info for these columns
            elif search_option in ['Medicinal Uses', 'Active Compounds', 'Method of Preparation']:
                result = data[data[search_option].str.contains(search_term, case=False, na=False)]
                # Show specific columns
                result = result[['Botanical Name', 'Common Name(s)', 'Medicinal Uses', 'Active Compounds', 'Method of Preparation']]
            else:
                result = data[data[search_option].str.contains(search_term, case=False, na=False)]
                result = result[['Botanical Name','Common Name(s)', search_option]]

            if result.empty:
                return render_template('result.html', results="No results found.")

            return render_template('result.html', results=result.to_html(index=False))

        except Exception as e:
            print(f"Error: {e}")
            return render_template('result.html', results="An error occurred while processing your request. Please check the console for details.")

@app.route('/search_page')
def search_page():
    # This route will render the search form page (search.html) when clicking 'search' from index_v2
    return render_template('search.html')

@app.route('/explore')
def explore():
    return render_template('explore.html')

# 🆕 New Route for Docs Page
@app.route('/docs')
def docs():
    return render_template('docs.html')

# 🆕 New Route for Ayurveda Page
@app.route('/ayurveda')
def ayurveda_page():
    return render_template('ayurveda.html')  # This will render the Ayurveda page

# 🆕 New Route for Yoga Page
@app.route('/yoga')
def yoga():
    return render_template('yoga.html')  # This will render the Yoga page

# 🆕 New Route for Naturopathy Page
@app.route('/naturopathy')
def naturopath():
    return render_template('naturopathy.html')  

# 🆕 New Route for Unani Page
@app.route('/unani')
def unani():
    return render_template('unani.html')  

# 🆕 New Route for Siddha Page
@app.route('/siddha')
def siddha():
    return render_template('siddha.html')  

# 🆕 New Route for Homeopathy Page
@app.route('/homeopathy')
def homeopathy():
    return render_template('homeopathy.html')  

@app.route('/back_to_home')
def back_to_home():
    # This route will take user back to index_v2.html from result.html
    return render_template('index_v2.html')

# Configure upload folder
UPLOAD_FOLDER = os.path.join(app.static_folder, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the uploads folder exists
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['email'] = user.email  # Store the user's email in the session
            flash('Login successful!', 'success')
            return redirect(url_for('index_v2'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
            return redirect(url_for('signup'))
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Signup successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index_v2'))

@app.route('/blogs', methods=['GET', 'POST'])
def blogs():
    if 'user_id' not in session:
        flash('Please log in to manage blogs.', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        status = request.form.get('status', 'draft').strip()
        image_url = None

        # Validate required fields
        if not title or not content:
            flash('Title and content are required to create a blog.', 'danger')
            return redirect(url_for('blogs'))

        # Handle file upload
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                image_url = url_for('static', filename=f'uploads/{filename}')  # Save the URL of the uploaded file

        # Create a new blog entry
        new_blog = Blog(
            title=title,
            content=content,
            image_url=image_url,
            status=status,
            author_id=session['user_id'],
            created_at=datetime.utcnow()
        )
        db.session.add(new_blog)
        db.session.commit()
        flash('Blog created successfully!', 'success')
        return redirect(url_for('blogs'))
    
    # Fetch all blogs with status 'publish'
    published_blogs = Blog.query.filter_by(status='publish').all()
    years = sorted({blog.created_at.year for blog in published_blogs if blog.created_at}, reverse=True)  # Extract unique years
    return render_template('blogs.html', blogs=published_blogs, years=years)

@app.route('/blog/<int:blog_id>', methods=['GET', 'POST'])
def blog_detail(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    if blog.status == 'draft' and ('user_id' not in session or blog.author_id != session['user_id']):
        flash('You are not authorized to view this blog.', 'danger')
        return redirect(url_for('index_v2'))
    if request.method == 'POST' and 'user_id' in session and blog.author_id == session['user_id']:
        blog.title = request.form['title']
        blog.content = request.form['content']
        blog.image_url = request.form['image_url']
        blog.status = request.form['status']
        blog.updated_at = datetime.utcnow()  # Update the timestamp
        db.session.commit()
        flash('Blog updated successfully!', 'success')
        return redirect(url_for('blogs'))
    author_email = User.query.get(blog.author_id).email  # Fetch the author's email using author_id
    return render_template('blog_detail.html', blog=blog, author_email=author_email)

@app.route('/delete_blog/<int:blog_id>')
def delete_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    if 'user_id' in session and blog.author_id == session['user_id']:
        db.session.delete(blog)
        db.session.commit()
        flash('Blog deleted successfully!', 'success')
    else:
        flash('You are not authorized to delete this blog.', 'danger')
    return redirect(url_for('blogs'))

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        flash('Please log in to change your password.', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        user = User.query.get(session['user_id'])

        if not check_password_hash(user.password, current_password):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('change_password'))

        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return redirect(url_for('change_password'))

        user.password = generate_password_hash(new_password)
        db.session.commit()
        flash('Password changed successfully!', 'success')
        return redirect(url_for('index_v2'))

    return render_template('change_password.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Please log in to view your profile.', 'danger')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    user_blogs = Blog.query.filter_by(author_id=session['user_id']).all()
    return render_template('profile.html', user=user, blogs=user_blogs)

@app.route('/title_suggestions')
def title_suggestions():
    query = request.args.get('query', '').lower()

    # Expanded list of Ayurveda and medicine-related suggestions
    suggestions_pool = [
    "10 Essential Homeopathy Remedies to Keep at Home",
    "A Beginner's Guide to Siddha Medicine",
    "A Holistic Approach to Respiratory Health",
    "Ancient Ayurvedic Wisdom for Modern Illness",
    "Ancient Secrets of Natural Healing",
    "Ayurveda and Fertility Support",
    "Ayurveda and Skin Care",
    "Ayurveda for Digestive Health",
    "Ayurveda for Mental Clarity",
    "Ayurveda for Weight Management",
    "Ayurveda in Everyday Cooking",
    "Ayurveda in Women's Health",
    "Ayurveda vs. Modern Medicine: A Comparison",
    "Ayurvedic Approaches to Allergies",
    "Ayurvedic Beauty Secrets",
    "Ayurvedic Daily Routine (Dinacharya)",
    "Ayurvedic Detoxification Techniques",
    "Ayurvedic Diet for Better Health",
    "Ayurvedic First Aid Essentials",
    "Ayurvedic Lifestyle Tips for Busy People",
    "Ayurvedic Practices for Modern Living",
    "Ayurvedic Remedies for Anxiety",
    "Ayurvedic Solutions for Stress Relief",
    "Ayurvedic Superfoods You Should Be Eating",
    "Ayurvedic Tips for Seasonal Changes",
    "Ayurvedic Treatments for Joint Pain",
    "Balancing the Mind, Body, and Spirit",
    "Boosting Immunity Naturally",
    "Combining Ayurveda and Aromatherapy",
    "Combining Unani and Ayurveda for Holistic Health",
    "Creating a Balanced Ayurvedic Lifestyle",
    "Detoxifying with Ayurvedic Herbs",
    "Differences Between Homeopathy and Naturopathy",
    "Exploring the World of Herbal Medicine",
    "Exploring Unani Medicine and Its Benefits",
    "Healing Through Nature's Pharmacy",
    "Herbal Remedies for Common Ailments",
    "Herbal Teas for Wellness",
    "Holistic Approaches to Medicine",
    "Home Remedies Backed by Ayurveda",
    "Homeopathy for Allergies and Asthma",
    "Homeopathy for Children's Health",
    "Homeopathy for Everyday Ailments",
    "How Ayurveda Treats Chronic Illnesses",
    "How Naturopathy Addresses Lifestyle Diseases",
    "How Siddha Medicine Balances the Five Elements",
    "Integrating Ayurveda into Daily Routines",
    "Integrative Medicine: Bridging East and West",
    "Mindful Living Through Ayurveda",
    "Natural Remedies for a Healthy Life",
    "Naturopathy for Hormonal Imbalance",
    "Naturopathy for Weight Loss and Detox",
    "Panchakarma: Deep Detox the Ayurvedic Way",
    "Principles of Unani Healing and Diagnosis",
    "Siddha Treatments for Skin Disorders",
    "Spiritual Dimensions of Ayurvedic Healing",
    "Sustainable Living with Naturopathy",
    "The Benefits of Yoga and Ayurveda",
    "The Connection Between Ayurveda and Yoga",
    "The Future of Herbal Medicine",
    "The Healing Power of Ayurveda",
    "The Healing Power of Yoga for the Mind",
    "The History of Ayurvedic Medicine",
    "The History of Homeopathy in India",
    "The Importance of Doshas in Ayurveda",
    "The Philosophy of Ayurveda",
    "The Power of Medicinal Spices",
    "The Role of Ayurveda in Mental Health",
    "The Role of Ayurveda in Preventive Health",
    "The Role of Ayurveda in Women's Health",
    "The Role of Herbs in Modern Medicine",
    "The Science Behind Ayurveda",
    "Top 10 Ayurvedic Herbs You Should Know",
    "Top Ayurvedic Books to Start With",
    "Top Homeopathy Books for Practitioners",
    "Traditional Yoga Practices for Holistic Health",
    "Understanding Ayurvedic Body Types (Prakriti)",
    "Unani Medicine for Digestive Health",
    "Using Ayurveda for Better Sleep",
    "What Western Medicine Can Learn from Ayurveda",
    "Yoga for Anxiety and Mental Peace",
    "Yoga for Digestive Wellness",
    "Yoga for Hormonal Balance",
    "Yoga for Immune System Support",
    "Yoga for Pain Relief and Flexibility"
]  

    # Filter suggestions based on the query
    filtered_suggestions = [s for s in suggestions_pool if query in s.lower()]
    
    # Prioritize suggestions that start with the query
    prioritized_suggestions = [s for s in filtered_suggestions if s.lower().startswith(query)]
    remaining_suggestions = [s for s in filtered_suggestions if not s.lower().startswith(query)]

    # Combine prioritized and remaining suggestions
    final_suggestions = prioritized_suggestions + remaining_suggestions

    # If no query is provided, return a random subset of suggestions
    if not query:
        final_suggestions = random.sample(suggestions_pool, min(len(suggestions_pool), 10))

    # Limit the number of suggestions to 10
    return jsonify(final_suggestions[:10])

@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_query = request.json.get('message', '').strip()
    if not user_query:
        return jsonify({'response': "Please enter a query."})

    system_prompt = (
        "You are an expert in medicinal plants and yoga. "
        "When a user asks about a health issue (e.g., headache), respond with remedies using medicinal plants. "
        "If yoga is relevant, suggest yoga positions or practices. "
        "If no plant or yoga remedy is known, reply: 'Sorry, I couldn't find a plant-based remedy for that.' "
        "Do not mention yoga unless it is relevant to the remedy."
    )

    try:
        # Combine system prompt and user query for the LLM
        prompt = f"{system_prompt}\nUser: {user_query}\nAssistant:"
        reply = llm.invoke(prompt)
        if not reply or not reply.strip():
            reply = "Sorry, I couldn't find a plant-based remedy for that."
    except Exception as e:
        print(f"Ollama/LangChain error: {e}")
        # Detect memory or connection errors and give user-friendly message
        if "actively refused" in str(e) or "Failed to establish a new connection" in str(e):
            reply = "Sorry, the AI server is not running. Please start Ollama by running 'ollama serve' in your terminal."
        elif "system memory" in str(e) or "out of memory" in str(e):
            reply = "Sorry, this model requires more RAM than is available. Please use a smaller model or add more memory."
        else:
            reply = "Sorry, there was an error processing your request."

    return jsonify({'response': reply})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created if they do not exist
        print("Database tables created.")
    app.run(port=5000, debug=True)
