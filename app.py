#from flask import Flask, render_template, request, redirect, url_for, session, flash, g
#import sqlite3, hashlib, os, json
#from datetime import datetime
#from functools import wraps

#app = Flask(__name__)
#app.config['DEBUG'] = True 
#app.secret_key = 'nh-engineering-secret-2024-nagpur'
#DATABASE = os.path.join(os.path.dirname(__file__), 'nh_engineering.db')*/
#DATABASE = '/tmp/nh_engineering.db'



from flask import Flask, render_template, request, redirect, url_for, session, flash, g
import sqlite3, hashlib, os, json
from datetime import datetime
from functools import wraps

# Fix paths for Vercel
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)
app.config['DEBUG'] = True 
app.secret_key = 'nh-engineering-secret-2024-nagpur'
DATABASE = '/tmp/nh_engineering.db'
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
        # Seed products if empty
        count = db.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if count == 0:
            products = [
                # ── FLOUR MILL ──────────────────────────────────────────
                ('Commercial Flour Mill Plant (Atta Chakki Plant)', 'Flour Mill',
                 'High-capacity commercial wheat flour mill plant built for consistent output and reliability. Suitable for medium to large milling operations across towns and cities. Designed for processing wheat into fine atta with minimal power consumption.',
                 json.dumps({'Material':'Mild Steel','Capacity':'40-100 Ton/Day','Operation':'Semi-Automatic','Voltage':'220-380V','Phase':'Three Phase','Power':'1-5 HP','Finishing':'Powder Coated'}), ''),

                ('Fully Automatic Roller Flour Mill Plant', 'Flour Mill',
                 'Fully automated roller flour milling solution with minimal human intervention. Ideal for high-volume industrial wheat processing. Features precision roller grinding for consistent flour quality and high extraction rates.',
                 json.dumps({'Material':'Mild Steel','Capacity':'>100 Ton/Day','Operation':'Fully Automatic','Voltage':'220-380V','Motor Speed':'1400 RPM','Phase':'Three Phase','Finishing':'Powder Coated'}), ''),

                ('Mini Flour Mill Plant', 'Flour Mill',
                 'Compact and affordable flour mill plant for small-scale operations, village-level businesses, and rural entrepreneurs. Easy to install, operate, and maintain with low power requirement.',
                 json.dumps({'Material':'Mild Steel','Operation':'Semi-Automatic','Capacity':'10-40 Ton/Day','Phase':'Three Phase','Motor Speed':'800-1400 RPM','Power':'1-3 HP'}), ''),

                ('Maize / Corn Flour Mill Plant', 'Flour Mill',
                 'Specialized flour milling plant for processing maize and corn into fine flour. Used for producing corn flour, maize atta, and animal feed grade flour. Robust construction for continuous operation.',
                 json.dumps({'Raw Material':'Maize / Corn','Capacity':'20-80 Ton/Day','Operation':'Semi-Automatic','Phase':'Three Phase','Voltage':'220-380V','Material':'Mild Steel'}), ''),

                ('Millet Flour Mill Plant', 'Flour Mill',
                 'Multi-purpose millet processing plant capable of handling jowar, bajra, ragi, and other millets. Growing demand from health food sector makes this a profitable investment. Low maintenance, high throughput.',
                 json.dumps({'Raw Material':'Jowar / Bajra / Ragi','Capacity':'20-60 Ton/Day','Operation':'Semi-Automatic','Phase':'Three Phase','Voltage':'220-380V','Material':'Mild Steel'}), ''),

                # ── RICE MILL ───────────────────────────────────────────
                ('Fully Automatic Rice Mill Plant', 'Rice Mill',
                 'End-to-end automated rice milling plant from paddy cleaning to polished rice output. Features multiple stages including pre-cleaner, husker, separator, whitener, and grader. Low maintenance, high output with excellent head rice recovery.',
                 json.dumps({'Operation':'Fully Automatic','Capacity':'2-10 Ton/Hour','Power Source':'Electric','Phase':'Three Phase','Stages':'Cleaning, Husking, Separating, Whitening, Grading','Material':'Mild Steel'}), ''),

                ('Commercial Rice Mill Plant', 'Rice Mill',
                 'Designed for commercial paddy processing with high throughput and excellent grain quality. Semi-automatic operation allows skilled operators to maximize output. Suitable for medium-scale rice mills across Maharashtra and Central India.',
                 json.dumps({'Operation':'Semi-Automatic','Capacity':'1-5 Ton/Hour','Power Source':'Electric','Phase':'Three Phase','Material':'Mild Steel','Finishing':'Powder Coated'}), ''),

                # ── DAL MILL ────────────────────────────────────────────
                ('Dal Mill Plant (Multi Purpose)', 'Dal Mill',
                 'Versatile multi-purpose dal processing plant capable of handling urad, moong, masoor, chana, toor, and other pulses. Complete turnkey solution from raw pulse cleaning to finished split dal. Ideal for processors handling multiple pulse varieties.',
                 json.dumps({'Raw Material':'Urad, Moong, Masoor, Chana, Toor','Capacity':'5-50 Ton/Day','Operation':'Semi-Automatic','Phase':'Three Phase','Voltage':'220-380V','Material':'Mild Steel'}), ''),

                ('Green Gram Processing Plant (Moong)', 'Dal Mill',
                 'Specialized processing plant for green gram (moong). Produces whole moong, moong dal (split), and moong fara (dehusked). High yield extraction with minimal breakage. Popular among traders in Vidarbha and Marathwada regions.',
                 json.dumps({'Raw Material':'Green Gram (Moong)','Output':'Moong Dal / Moong Fara','Capacity':'5-30 Ton/Day','Operation':'Semi-Automatic','Phase':'Three Phase','Material':'Mild Steel'}), ''),

                ('Chickpeas & Peas Processing Plant (Chana/Matar)', 'Dal Mill',
                 'Dedicated plant for processing chana (chickpeas) and matar (peas) into besan-grade splits and whole dal. Features efficient dehusking and splitting mechanism for high-quality output suitable for retail and wholesale markets.',
                 json.dumps({'Raw Material':'Chana / Matar','Output':'Chana Dal / Besan Grade','Capacity':'5-40 Ton/Day','Operation':'Semi-Automatic','Phase':'Three Phase','Material':'Mild Steel'}), ''),

                ('Pigeon Pea Processing Plant (Toor Dal)', 'Dal Mill',
                 'High-efficiency toor (arhar) dal processing plant. One of the most consumed pulses in India — toor dal processing is a highly profitable business. Our plant ensures maximum yield with minimal waste and consistent quality output.',
                 json.dumps({'Raw Material':'Toor / Arhar','Output':'Toor Dal (Split)','Capacity':'5-50 Ton/Day','Operation':'Semi-Automatic','Phase':'Three Phase','Material':'Mild Steel'}), ''),

                ('Black Gram Processing Plant (Urad Dal)', 'Dal Mill',
                 'Specialized urad dal processing plant for producing whole urad, urad dal, and urad gota. Essential for papad and snack food manufacturers. High extraction ratio ensures maximum profitability per ton of raw material.',
                 json.dumps({'Raw Material':'Black Gram (Urad)','Output':'Urad Dal / Urad Gota','Capacity':'5-40 Ton/Day','Operation':'Semi-Automatic','Phase':'Three Phase','Material':'Mild Steel'}), ''),

                ('Red Lentil Processing Plant (Masoor Dal)', 'Dal Mill',
                 'Processing plant dedicated to masoor (red lentil) dal production. Masoor is one of the fastest-growing pulse categories in domestic and export markets. Plant includes cleaning, dehusking, splitting, and grading sections.',
                 json.dumps({'Raw Material':'Masoor (Red Lentil)','Output':'Masoor Dal (Split)','Capacity':'5-30 Ton/Day','Operation':'Semi-Automatic','Phase':'Three Phase','Material':'Mild Steel'}), ''),

                # ── PREFABRICATED SHED ──────────────────────────────────
                ('Industrial Prefabricated Shed', 'Prefabricated Shed',
                 'Robust and durable prefabricated steel sheds for industrial use. Fast installation, weather-resistant structure engineered for heavy machinery, manufacturing units, and workshops. Available in custom sizes with optional mezzanine floors.',
                 json.dumps({'Type':'Industrial','Structure':'Steel Frame','Roofing':'Color Coated Sheets','Customizable':'Yes','Installation':'Quick Assembly','Foundation':'RCC as per soil report'}), ''),

                ('Warehouse Prefabricated Shed', 'Prefabricated Shed',
                 'Large-span warehouse sheds designed for maximum storage space with optimal load-bearing capacity. Suitable for logistics, cold storage support structures, grain storage, and e-commerce warehouses. Column-free interior available.',
                 json.dumps({'Type':'Warehouse / Storage','Span':'Up to 30m column-free','Roofing':'Color Coated Sheets','Wall Cladding':'Optional','Customizable':'Yes','Installation':'4-8 weeks'}), ''),

                ('Factory & Commercial Prefabricated Shed', 'Prefabricated Shed',
                 'Purpose-built prefabricated sheds for factories, showrooms, and commercial establishments. Combines speed of construction with architectural flexibility. Lower cost than conventional construction with better longevity.',
                 json.dumps({'Type':'Factory / Commercial','Structure':'Steel Frame + Cladding','Customizable':'Yes','Finish':'Painted / Galvanized','Installation':'Quick Assembly','Certifications':'As per IS standards'}), ''),

                # ── CLEANING & SORTING ──────────────────────────────────
                ('Sorter / Sortex Cleaning Plant', 'Cleaning & Sorting',
                 'Advanced optical and mechanical sorting and cleaning plant for grains, pulses, and spices. Removes foreign materials, damaged grains, discolored seeds, and impurities to produce market-grade cleaned commodity.',
                 json.dumps({'Application':'Grains, Pulses, Spices','Technology':'Mechanical + Optical','Capacity':'2-20 Ton/Hour','Phase':'Three Phase','Material':'Mild Steel','Output':'Market Grade Clean Commodity'}), ''),

                ('Grader Cleaning Plant', 'Cleaning & Sorting',
                 'Precision grading and cleaning plant that separates commodities by size, weight, and quality. Essential for export-quality grain and pulse processing. Produces uniform grade output for premium market pricing.',
                 json.dumps({'Application':'Grains, Pulses','Function':'Size & Weight Grading','Capacity':'2-15 Ton/Hour','Phase':'Three Phase','Material':'Mild Steel','Output':'Uniform Grade Commodity'}), ''),

                ('Cleaning & Polishing Plant', 'Cleaning & Sorting',
                 'Combined cleaning and surface polishing plant for rice, dal, and spices. Produces shiny, market-ready product with improved shelf life and consumer appeal. Used by leading rice and dal processors across Central India.',
                 json.dumps({'Application':'Rice, Dal, Spices','Function':'Cleaning + Polishing','Capacity':'1-10 Ton/Hour','Phase':'Three Phase','Material':'Mild Steel','Output':'Polished Market-Ready Product'}), ''),
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

# Initialize DB on every startup (works with Gunicorn + local)
init_db()

if __name__ == '__main__':
    app.run(debug=True, port=5050)