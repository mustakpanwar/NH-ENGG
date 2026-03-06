from flask import Flask, render_template, request, redirect, url_for, session, flash, g
import sqlite3, hashlib, os, json
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'nh-engineering-secret-2024-nagpur'
DATABASE = os.path.join(os.path.dirname(__file__), 'nh_engineering.db')

# ─── DB HELPERS ────────────────────────────────────────────────────────────────

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    return cur.lastrowid

def init_db():
    with app.app_context():
        db = get_db()
        db.executescript('''
            CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                specs TEXT,
                image_url TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS blogs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                content TEXT NOT NULL,
                excerpt TEXT,
                author TEXT DEFAULT 'Admin',
                published INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        db.commit()

        # Create default admin if not exists
        existing = db.execute("SELECT * FROM admin WHERE username='admin'").fetchone()
        if not existing:
            pw = hashlib.sha256('admin123'.encode()).hexdigest()
            db.execute("INSERT INTO admin (username, password) VALUES (?, ?)", ('admin', pw))
            db.commit()

        # Seed products if empty
        count = db.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if count == 0:
            products = [
                ('Commercial Flour Mill Plant', 'Flour Mill', 'High-capacity commercial flour mill plant built for consistent output and reliability. Suitable for medium to large milling operations.', json.dumps({'Material':'Mild Steel','Capacity':'40-100 Ton/Day','Operation':'Semi-Automatic','Voltage':'220-380V','Phase':'Three Phase','Power':'1-5 HP'}), ''),
                ('Fully Automatic Flour Mill Plant', 'Flour Mill', 'Fully automated flour milling solution with minimal human intervention. Ideal for high-volume industrial production.', json.dumps({'Material':'Mild Steel','Capacity':'>100 Ton/Day','Voltage':'220-380V','Motor Speed':'1400 RPM','Phase':'Three Phase','Finishing':'Powder Coated'}), ''),
                ('Roller Flour Mill Plant', 'Flour Mill', 'Roller-based flour mill offering precise grain grinding, consistent flour quality, and energy-efficient operation.', json.dumps({'Power':'1-5 HP','Operation':'Automatic','Capacity':'40-100 Ton/Day','Motor Speed':'1400 RPM','Phase':'Three Phase'}), ''),
                ('Mini Flour Mill Plant', 'Flour Mill', 'Compact flour mill plant for small-scale operations, easy to set up and maintain.', json.dumps({'Material':'Mild Steel','Operation':'Semi-Automatic','Capacity':'>100 Ton/Day','Phase':'Three Phase','Motor Speed':'800-1400 RPM'}), ''),
                ('Industrial Prefabricated Shed', 'Prefabricated Shed', 'Robust and durable prefabricated sheds for industrial use. Fast installation, weather-resistant structure.', json.dumps({'Type':'Industrial','Structure':'Steel Frame','Customizable':'Yes','Installation':'Quick Assembly'}), ''),
                ('Warehouse Prefabricated Shed', 'Prefabricated Shed', 'Large-span warehouse sheds designed for maximum storage space with optimal load-bearing capacity.', json.dumps({'Type':'Warehouse','Span':'Customizable','Roofing':'Color Coated Sheets','Foundation':'As per requirement'}), ''),
                ('Fully Automatic Rice Mill Plant', 'Rice Mill', 'End-to-end automated rice milling plant from paddy cleaning to finished rice output. Low maintenance, high output.', json.dumps({'Operation':'Fully Automatic','Capacity':'Commercial','Power Source':'Electric','Phase':'Three Phase'}), ''),
                ('Commercial Rice Mill Plant', 'Rice Mill', 'Designed for commercial rice processing with high throughput and excellent grain quality.', json.dumps({'Operation':'Semi-Automatic','Capacity':'Commercial','Power Source':'Electric','Phase':'Three Phase'}), ''),
            ]
            for p in products:
                db.execute("INSERT INTO products (name,category,description,specs,image_url) VALUES (?,?,?,?,?)", p)
            db.commit()

        # Seed blogs if empty
        count = db.execute("SELECT COUNT(*) FROM blogs").fetchone()[0]
        if count == 0:
            blogs = [
                ('Why Prefabricated Sheds Are the Future of Industrial Construction',
                 'why-prefabricated-sheds-are-future',
                 '''Prefabricated structures have revolutionized industrial construction across India. At NH Engineering & Fabricating, we have seen firsthand how businesses in Nagpur and surrounding regions are making the switch from traditional brick-and-mortar to modern prefabricated steel sheds.

The benefits are numerous. First, the speed of construction is dramatically faster — a warehouse that would traditionally take 6-12 months can be erected in 4-8 weeks. Second, the cost savings are substantial, with prefab sheds costing 20-30% less than conventional construction due to reduced material waste and labor.

Our prefabricated sheds are engineered with high-tensile steel frames, color-coated roofing sheets, and can be customized to any dimension your business needs. Whether you need a small parking shed or a sprawling industrial warehouse, the same modular technology applies.

With Nagpur becoming a key logistics hub for central India, now is the perfect time to invest in scalable, expandable prefabricated infrastructure for your business.''',
                 'Prefabricated structures are transforming industrial construction. Learn why businesses across Nagpur are choosing faster, cost-effective prefab sheds.',
                 'Naushad Haji Khan', 1),
                ('Choosing the Right Flour Mill Plant for Your Business',
                 'choosing-right-flour-mill-plant',
                 '''Selecting a flour mill plant is one of the most critical decisions a flour business owner can make. The wrong choice can lead to poor output quality, high energy costs, and frequent breakdowns. Here is a guide from our team at NH Engineering & Fabricating to help you make the right call.

**1. Capacity Planning**
The first question to ask is: how many tons per day do I need to process? Our range covers mini plants for smaller operations (suitable for village-level or small town markets) all the way to fully automatic plants capable of processing over 100 tons per day for large commercial operations.

**2. Automation Level**
Semi-automatic plants are suitable when skilled labor is available and costs are a concern. Fully automatic plants are ideal when consistency, speed, and minimal supervision are priorities.

**3. Power Availability**
All our flour mills operate on three-phase power (220-380V). Ensure your facility has a stable three-phase connection before installation. We also offer guidance on power optimization.

**4. After-Sales Support**
We provide installation, training, and ongoing maintenance support for all equipment supplied from our Nagpur facility on Bhandara Road.

Contact us to discuss which plant is right for your specific requirements.''',
                 'A practical guide to selecting the right flour mill plant capacity, automation level, and specifications for your milling business.',
                 'Naushad Haji Khan', 1),
            ]
            for b in blogs:
                db.execute("INSERT INTO blogs (title,slug,content,excerpt,author,published) VALUES (?,?,?,?,?,?)", b)
            db.commit()

# ─── AUTH ─────────────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

def slugify(text):
    import re
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text

# ─── PUBLIC ROUTES ─────────────────────────────────────────────────────────────

@app.route('/')
def home():
    products = query_db("SELECT * FROM products LIMIT 6")
    blogs = query_db("SELECT * FROM blogs WHERE published=1 ORDER BY created_at DESC LIMIT 3")
    categories = query_db("SELECT DISTINCT category FROM products")
    return render_template('public/home.html', products=products, blogs=blogs, categories=categories)

@app.route('/products')
def products():
    category = request.args.get('category', '')
    if category:
        prods = query_db("SELECT * FROM products WHERE category=? ORDER BY created_at DESC", [category])
    else:
        prods = query_db("SELECT * FROM products ORDER BY created_at DESC")
    categories = query_db("SELECT DISTINCT category FROM products")
    return render_template('public/products.html', products=prods, categories=categories, active_category=category)

@app.route('/products/<int:pid>')
def product_detail(pid):
    product = query_db("SELECT * FROM products WHERE id=?", [pid], one=True)
    if not product:
        return redirect(url_for('products'))
    specs = {}
    try:
        specs = json.loads(product['specs']) if product['specs'] else {}
    except:
        pass
    related = query_db("SELECT * FROM products WHERE category=? AND id!=? LIMIT 3", [product['category'], pid])
    return render_template('public/product_detail.html', product=product, specs=specs, related=related)

@app.route('/blog')
def blog():
    posts = query_db("SELECT * FROM blogs WHERE published=1 ORDER BY created_at DESC")
    return render_template('public/blog.html', posts=posts)

@app.route('/blog/<slug>')
def blog_post(slug):
    post = query_db("SELECT * FROM blogs WHERE slug=? AND published=1", [slug], one=True)
    if not post:
        return redirect(url_for('blog'))
    recent = query_db("SELECT * FROM blogs WHERE published=1 AND slug!=? ORDER BY created_at DESC LIMIT 4", [slug])
    return render_template('public/blog_post.html', post=post, recent=recent)

@app.route('/about')
def about():
    return render_template('public/about.html')

@app.route('/contact')
def contact():
    return render_template('public/contact.html')

# ─── ADMIN ROUTES ──────────────────────────────────────────────────────────────

@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username','')
        password = request.form.get('password','')
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        user = query_db("SELECT * FROM admin WHERE username=? AND password=?", [username, pw_hash], one=True)
        if user:
            session['admin_logged_in'] = True
            session['admin_user'] = username
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials. Try again.')
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/admin')
@login_required
def admin_dashboard():
    product_count = query_db("SELECT COUNT(*) as c FROM products", one=True)['c']
    blog_count = query_db("SELECT COUNT(*) as c FROM blogs", one=True)['c']
    recent_blogs = query_db("SELECT * FROM blogs ORDER BY created_at DESC LIMIT 5")
    recent_products = query_db("SELECT * FROM products ORDER BY created_at DESC LIMIT 5")
    return render_template('admin/dashboard.html', product_count=product_count, blog_count=blog_count,
                           recent_blogs=recent_blogs, recent_products=recent_products)

# Products Admin
@app.route('/admin/products')
@login_required
def admin_products():
    products = query_db("SELECT * FROM products ORDER BY created_at DESC")
    return render_template('admin/products.html', products=products)

@app.route('/admin/products/new', methods=['GET','POST'])
@login_required
def admin_product_new():
    if request.method == 'POST':
        name = request.form.get('name','')
        category = request.form.get('category','')
        description = request.form.get('description','')
        image_url = request.form.get('image_url','')
        # Build specs from dynamic fields
        spec_keys = request.form.getlist('spec_key')
        spec_vals = request.form.getlist('spec_val')
        specs = {k: v for k, v in zip(spec_keys, spec_vals) if k.strip()}
        execute_db("INSERT INTO products (name,category,description,specs,image_url) VALUES (?,?,?,?,?)",
                   [name, category, description, json.dumps(specs), image_url])
        flash('Product added successfully!')
        return redirect(url_for('admin_products'))
    return render_template('admin/product_form.html', product=None, action='New')

@app.route('/admin/products/<int:pid>/edit', methods=['GET','POST'])
@login_required
def admin_product_edit(pid):
    product = query_db("SELECT * FROM products WHERE id=?", [pid], one=True)
    if not product:
        return redirect(url_for('admin_products'))
    specs = {}
    try:
        specs = json.loads(product['specs']) if product['specs'] else {}
    except:
        pass
    if request.method == 'POST':
        name = request.form.get('name','')
        category = request.form.get('category','')
        description = request.form.get('description','')
        image_url = request.form.get('image_url','')
        spec_keys = request.form.getlist('spec_key')
        spec_vals = request.form.getlist('spec_val')
        new_specs = {k: v for k, v in zip(spec_keys, spec_vals) if k.strip()}
        execute_db("UPDATE products SET name=?,category=?,description=?,specs=?,image_url=? WHERE id=?",
                   [name, category, description, json.dumps(new_specs), image_url, pid])
        flash('Product updated!')
        return redirect(url_for('admin_products'))
    return render_template('admin/product_form.html', product=product, specs=specs, action='Edit')

@app.route('/admin/products/<int:pid>/delete', methods=['POST'])
@login_required
def admin_product_delete(pid):
    execute_db("DELETE FROM products WHERE id=?", [pid])
    flash('Product deleted.')
    return redirect(url_for('admin_products'))

# Blogs Admin
@app.route('/admin/blogs')
@login_required
def admin_blogs():
    blogs = query_db("SELECT * FROM blogs ORDER BY created_at DESC")
    return render_template('admin/blogs.html', blogs=blogs)

@app.route('/admin/blogs/new', methods=['GET','POST'])
@login_required
def admin_blog_new():
    if request.method == 'POST':
        title = request.form.get('title','')
        content = request.form.get('content','')
        excerpt = request.form.get('excerpt','')
        author = request.form.get('author', 'Admin')
        published = 1 if request.form.get('published') else 0
        slug = slugify(title)
        # Ensure unique slug
        existing = query_db("SELECT id FROM blogs WHERE slug=?", [slug], one=True)
        if existing:
            slug = slug + '-' + str(int(datetime.now().timestamp()))
        execute_db("INSERT INTO blogs (title,slug,content,excerpt,author,published) VALUES (?,?,?,?,?,?)",
                   [title, slug, content, excerpt, author, published])
        flash('Blog post created!')
        return redirect(url_for('admin_blogs'))
    return render_template('admin/blog_form.html', post=None, action='New')

@app.route('/admin/blogs/<int:bid>/edit', methods=['GET','POST'])
@login_required
def admin_blog_edit(bid):
    post = query_db("SELECT * FROM blogs WHERE id=?", [bid], one=True)
    if not post:
        return redirect(url_for('admin_blogs'))
    if request.method == 'POST':
        title = request.form.get('title','')
        content = request.form.get('content','')
        excerpt = request.form.get('excerpt','')
        author = request.form.get('author','Admin')
        published = 1 if request.form.get('published') else 0
        execute_db("UPDATE blogs SET title=?,content=?,excerpt=?,author=?,published=? WHERE id=?",
                   [title, content, excerpt, author, published, bid])
        flash('Blog post updated!')
        return redirect(url_for('admin_blogs'))
    return render_template('admin/blog_form.html', post=post, action='Edit')

@app.route('/admin/blogs/<int:bid>/delete', methods=['POST'])
@login_required
def admin_blog_delete(bid):
    execute_db("DELETE FROM blogs WHERE id=?", [bid])
    flash('Blog post deleted.')
    return redirect(url_for('admin_blogs'))

@app.route('/admin/change-password', methods=['GET','POST'])
@login_required
def admin_change_password():
    if request.method == 'POST':
        current = request.form.get('current','')
        new_pw = request.form.get('new_password','')
        confirm = request.form.get('confirm','')
        current_hash = hashlib.sha256(current.encode()).hexdigest()
        user = query_db("SELECT * FROM admin WHERE username=? AND password=?",
                        [session['admin_user'], current_hash], one=True)
        if not user:
            flash('Current password is incorrect.')
        elif new_pw != confirm:
            flash('New passwords do not match.')
        elif len(new_pw) < 6:
            flash('Password must be at least 6 characters.')
        else:
            new_hash = hashlib.sha256(new_pw.encode()).hexdigest()
            execute_db("UPDATE admin SET password=? WHERE username=?", [new_hash, session['admin_user']])
            flash('Password changed successfully!')
            return redirect(url_for('admin_dashboard'))
    return render_template('admin/change_password.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5050)
