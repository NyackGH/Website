import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)

# 1. DATABASE MODEL
# DEFINED FIRST: SQLAlchemy needs to see this class before we run create_all()
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_filename = db.Column(db.String(100), nullable=False)
    caption = db.Column(db.String(200))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

# 2. INITIALIZE DATABASE
# MOVED HERE: This creates the tables for the models defined above
with app.app_context():
    db.create_all()

# 3. THE FEED ROUTE
@app.route('/')
def index():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('index.html', posts=posts)

# 4. THE UPLOAD ROUTE
@app.route('/nyack-upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['image']
        caption = request.form.get('caption')
        
        if file:
            # Ensure upload folder exists
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
                
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            
            new_post = Post(image_filename=file.filename, caption=caption)
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('index'))
            
    return render_template('upload.html')

if __name__ == '__main__':
    # On Render, the server (Gunicorn) starts the app. 
    # This block only runs when you test locally.
    app.run(debug=True)
