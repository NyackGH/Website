import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)
# Place this after your app and db are defined
with app.app_context():
    db.create_all()

# 1. DATABASE MODEL
# This defines what an "Image Post" looks like in our database
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_filename = db.Column(db.String(100), nullable=False)
    caption = db.Column(db.String(200))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

# 2. THE FEED ROUTE
@app.route('/')
def index():
    # Fetches all posts from the database and shows them on the home page
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('index.html', posts=posts)

# 3. THE UPLOAD ROUTE
@app.route('/nyack-upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['image']
        caption = request.form.get('caption')
        
        if file:
            # Save the file to the uploads folder
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            
            # Save the reference in the database
            new_post = Post(image_filename=file.filename, caption=caption)
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('index'))
            
    return render_template('upload.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Creates the database file
    app.run(debug=True)
