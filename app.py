from flask import Flask, render_template, request, redirect, url_for, flash, abort, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import markdown
from markdown.extensions import codehilite
import re
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance/blog.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/images'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.template_filter('markdown')
def markdown_filter(text):
    return markdown.markdown(text, extensions=['codehilite', 'fenced_code'])

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    tags = db.Column(db.String(500))
    is_draft = db.Column(db.Boolean, default=False)
    
    def get_tags_list(self):
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []
    
    def get_html_content(self):
        return markdown.markdown(self.content, extensions=['codehilite', 'fenced_code'])

class About(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    post = db.relationship('Post', backref=db.backref('comments', lazy=True))

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(is_draft=False).order_by(Post.date_created.desc()).paginate(
        page=page, per_page=10, error_out=False)
    return render_template('index.html', posts=posts)

@app.route('/post/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    author = request.form['author']
    content = request.form['content']
    comment = Comment(post_id=post.id, author=author, content=content)
    db.session.add(comment)
    db.session.commit()
    flash('Your comment has been submitted!', 'success')
    return redirect(url_for('post_detail', slug=post.slug))

@app.route('/post/<slug>')
def post_detail(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    db.session.refresh(post)
    return render_template('post.html', post=post)

@app.route('/about')
def about():
    about_content = About.query.first()
    if not about_content:
        about_content = About(content="""
# About Me

I am a passionate software developer and technology enthusiast. 
I love creating innovative solutions and sharing knowledge through this blog.

My interests include:
- Web Development
- Machine Learning
- Open Source Software
- System Architecture

Feel free to connect with me through the social links above!
        """)
        db.session.add(about_content)
        db.session.commit()
    
    return render_template('about.html', about=about_content)

@app.route('/tag/<tag_name>')
def posts_by_tag(tag_name):
    posts = Post.query.filter(Post.tags.contains(tag_name)).filter_by(is_draft=False).order_by(Post.date_created.desc()).all()
    return render_template('tag.html', posts=posts, tag_name=tag_name)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == os.environ.get('ADMIN_USERNAME', 'Hemanth') and password == os.environ.get('ADMIN_PASSWORD', '28997479'):
            session['logged_in'] = True
            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    session.pop('logged_in', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin')
@login_required
def admin():
    posts = Post.query.order_by(Post.date_created.desc()).all()
    return render_template('admin/index.html', posts=posts)

@app.route('/admin/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        slug = request.form['slug'] or re.sub(r'[^\w\s-]', '', title.lower()).strip().replace(' ', '-')
        content = request.form['content']
        summary = request.form['summary']
        tags = request.form['tags']
        is_draft = 'is_draft' in request.form
        
        original_slug = slug
        counter = 1
        while Post.query.filter_by(slug=slug).first():
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        post = Post(title=title, slug=slug, content=content, 
                   summary=summary, tags=tags, is_draft=is_draft)
        db.session.add(post)
        db.session.commit()
        
        flash('Post created successfully!', 'success')
        return redirect(url_for('admin'))
    
    return render_template('admin/edit_post.html', post=None)

@app.route('/admin/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    if request.method == 'POST':
        post.title = request.form['title']
        new_slug = request.form['slug'] or re.sub(r'[^\w\s-]', '', post.title.lower()).strip().replace(' ', '-')
        
        if new_slug != post.slug:
            original_slug = new_slug
            counter = 1
            while Post.query.filter_by(slug=new_slug).filter(Post.id != post.id).first():
                new_slug = f"{original_slug}-{counter}"
                counter += 1
            post.slug = new_slug
        
        post.content = request.form['content']
        post.summary = request.form['summary']
        post.tags = request.form['tags']
        post.is_draft = 'is_draft' in request.form
        
        db.session.commit()
        flash(f'Post updated successfully! Last updated at: {post.updated_at}', 'success')
        return redirect(url_for('admin'))
    
    return render_template('admin/edit_post.html', post=post)

@app.route('/admin/about/edit', methods=['GET', 'POST'])
@login_required
def edit_about():
    about = About.query.first()
    if not about:
        about = About(content="")
        db.session.add(about)
        db.session.commit()
    
    if request.method == 'POST':
        about.content = request.form['content']
        about.updated_at = datetime.utcnow()
        db.session.commit()
        flash('About page updated successfully!', 'success')
        return redirect(url_for('about'))
    
    return render_template('admin/edit_about.html', about=about)

@app.route('/admin/debug')
@login_required
def debug_posts():
    posts = Post.query.all()
    debug_info = []
    for post in posts:
        debug_info.append({
            'id': post.id,
            'title': post.title,
            'slug': post.slug,
            'is_draft': post.is_draft,
            'content_length': len(post.content),
            'content_preview': post.content[:100] + '...' if len(post.content) > 100 else post.content
        })
    return f"<pre>{debug_info}</pre>"

@app.route('/admin/publish-all')
@login_required
def publish_all_drafts():
    drafts = Post.query.filter_by(is_draft=True).all()
    for post in drafts:
        post.is_draft = False
    db.session.commit()
    flash(f'Published {len(drafts)} draft posts!', 'success')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)