import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import cloudinary
import cloudinary.uploader

app = Flask(__name__)

# --- 1. CLOUDINARY CONFIG (Now pulling from Render's Secret Variables) ---
cloudinary.config( 
  cloud_name = os.environ.get('CLOUDY_NAME'), 
  api_key = os.environ.get('CLOUDY_KEY'), 
  api_secret = os.environ.get('CLOUDY_SECRET') 
)

# --- 2. DATABASE CONFIG (Works with Neon.tech or Local) ---
# This fix ensures 'postgres://' (Render's old style) works with SQLAlchemy
uri = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- 3. DATABASE MODEL ---
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(500), nullable=False)
    caption = db.Column(db.String(200))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# --- 4. THE ROUTES ---
@app.route('/')
def index():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/nyack-upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['image']
        caption = request.form.get('caption')
        
        if file:
            # Upload image to Cloudinary
            upload_result = cloudinary.uploader.upload(file)
            # Save the link and caption to your Permanent Neon Database
            new_post = Post(image_url=upload_result['secure_url'], caption=caption)
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('index'))
            
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
