import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# --- CONFIGURATION (UPDATED FOR PERSISTENCE) ---
# Check if running on Render by looking for the RENDER environment variable
if os.environ.get('RENDER'):
    # Path to the Render Persistent Disk mount point
    base_dir = "/data"
else:
    # Use local folder when working on your computer
    base_dir = os.path.abspath(os.path.dirname(__file__))

# Setup paths for database and images
db_path = os.path.join(base_dir, 'database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['UPLOAD_FOLDER'] = os.path.join(base_dir, 'uploads')

# Create the uploads folder immediately if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)

# 1. DATABASE MODEL
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_filename = db.Column(db.String(100), nullable=False)
    caption = db.Column(db.String(200))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

# 2. INITIALIZE DATABASE
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
            # Save file to the persistent disk folder
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            
            # Save reference in the database
            new_post = Post(image_filename=file.filename, caption=caption)
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('index'))
            
    return render_template('upload.html')

# 5. THE IMAGE SERVING ROUTE (NEW)
# Since images are now outside the 'static' folder, we need this to show them
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
