import os
import shutil
from app import app, Post, About

# Configuration
DEST_DIR = 'docs'
BASE_URL = 'https://your-github-username.github.io/your-repo-name/'

def get_all_pages():
    """Manually collect all public URLs."""
    pages = []
    with app.app_context():
        # --- DEBUGGING START ---
        print("\n--- Checking Database Posts ---")
        all_posts = Post.query.all()
        if not all_posts:
            print("No posts found in the database.")
        else:
            for p in all_posts:
                print(f"  - Found Post: '{p.title}' (Is Draft: {p.is_draft})")
        print("-----------------------------\n")
        # --- DEBUGGING END ---

        # Static pages
        pages.append('/')
        pages.append('/about')

        # Post pages
        posts = Post.query.filter_by(is_draft=False).all()
        for post in posts:
            pages.append(f'/post/{post.slug}')

        # Tag pages
        tags = set()
        for post in posts:
            if post.tags:
                for tag in post.tags.split(','):
                    tags.add(tag.strip())
        for tag in tags:
            pages.append(f'/tag/{tag}')
            
    return pages

def build_site():
    """Generates the static site."""
    # Clean destination directory
    if os.path.exists(DEST_DIR):
        shutil.rmtree(DEST_DIR)
    os.makedirs(DEST_DIR)

    # Copy static files
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    shutil.copytree(static_dir, os.path.join(DEST_DIR, 'static'))

    # Generate HTML pages
    pages = get_all_pages()
    client = app.test_client()

    for page_url in pages:
        print(f"Building {page_url}...")
        try:
            response = client.get(page_url)
            if response.status_code != 200:
                print(f"  [!] Warning: Received status code {response.status_code} for {page_url}")
                continue

            # Determine the output path
            if page_url == '/':
                path = os.path.join(DEST_DIR, 'index.html')
            else:
                # Create a directory for the page
                dir_path = os.path.join(DEST_DIR, page_url.lstrip('/'))
                os.makedirs(dir_path, exist_ok=True)
                path = os.path.join(dir_path, 'index.html')
            
            with open(path, 'wb') as f:
                f.write(response.data)

        except Exception as e:
            print(f"  [X] Error building {page_url}: {e}")

    print("\nBuild complete.")
    print(f"Static site generated in '{DEST_DIR}/' directory.")

if __name__ == '__main__':
    build_site()
