from app import app, db, About

# The scraped content from the about page
scraped_about_content = """
K.I.S.S
Keep It Simple & Stupid

---

### ABOUT ME 📤

**THE ALGORITHM OF HEMAN LIFE**

```
while(life.throws_curveballs()) {
    adapt();
    optimize();
    repeat();
}
```

Who am I? The person your CS professor warned you about - someone who treats every data structure like a love story and every algorithm like a potential government reform and fairy tale waiting to be told.

**Current coordinates:** NIT Trichy, first-year M.Tech (in Industrial Automation) student by day attending classes, pretending to understand control systems while my mind wanders to how these same principles could optimize traffic lights in Bengaluru. A digital alchemist by night, converting constitutional articles into neural network weights.

**The backstory in 30 seconds:** Failed UPSC → Strategic pivot → Now building the tools that future administrators will wish they understood. Think of it as a very expensive, very public debugging session.

### MY STACK (EMOTIONAL & TECHNICAL)

*   **Languages I speak:** C++ (fluently arguing with pointers), Python (for when I need things to actually work. lol:) ), Policy-speak (rusty but trying), and Existential Crisis (native).
*   **Current projects:** Teaching machines to think about governance, building A* pathfinding algorithms that work better than most bureaucratic processes, and documenting every failure as a feature.
*   **Debugging philosophy:** Every 'segfault' is a life lesson. Every infinite loop teaches patience. Every successful compilation feels like a small victory against entropy.

### THE CONFESSION

I'm not here to impress you with buzzwords or claim expertise I don't have. I'm here to share the messy, beautiful process of someone trying to bridge two worlds that rarely speak the same language.

I collect interesting problems the way some people collect stamps - except my problems involve optimizing democracy and my solutions involve suspiciously elegant code.

**Connect with me if:** You believe the best systems are invisible to their users, think governance could use better APIs, or just enjoy watching someone learn very complicated things in very public ways.

---

**Currently:** Writing functions that would make Dijkstra proud and policy proposals that would make system efficient.

**Status:** Compiling dreams... 69% complete

You can also find my other domain writings at "RETROSPECT"

If you're here because you found my technical tutorials helpful, welcome. If you're here because my chess-gambit-civil-service story intrigued you, welcome. If you're here because you accidentally clicked a link and stayed out of curiosity, especially welcome.

© Hemanth 2025
"""

with app.app_context():
    about_page = About.query.first()
    if about_page:
        about_page.content = scraped_about_content
    else:
        about_page = About(content=scraped_about_content)
        db.session.add(about_page)
    db.session.commit()

print("About page content updated successfully.")
