import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import cloudinary
import cloudinary.uploader

app = Flask(__name__)

# --- CLOUDINARY CONFIG ---
# Get these from your Cloudinary Dashboard
cloudinary.config( 
  cloud_name = "your_cloud_name", 
  api_key = "your_api_key", 
  api_secret = "your_api_secret" 
)

# Configuration - Staying with local SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(500), nullable=False) # Changed from filename to URL
    caption = db.Column(db.String(200))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

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
            # UPLOAD TO CLOUDINARY INSTEAD OF LOCAL FOLDER
            upload_result = cloudinary.uploader.upload(file)
            image_url = upload_result['secure_url'] # This link lasts forever
            
            new_post = Post(image_url=image_url, caption=caption)
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('index'))
            
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
