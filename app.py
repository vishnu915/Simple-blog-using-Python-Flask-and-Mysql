from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:vishnu%40123@localhost/blog_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author = db.Column(db.String(50), default='Anonymous')

@app.route('/')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/create_post', methods=['POST'])
def create_post():
    title = request.form['title']
    content = request.form['content']
    author = request.form.get('author', 'Anonymous')
    
    new_post = Post(title=title, content=content, author=author)
    db.session.add(new_post)
    db.session.commit()
    
    # Emit new post to all clients
    socketio.emit('new_post', {
        'id': new_post.id,
        'title': new_post.title,
        'content': new_post.content,
        'author': new_post.author,
        'created_at': new_post.created_at.strftime('%Y-%m-%d %H:%M:%S')
    })
    
    return redirect(url_for('index'))

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)
