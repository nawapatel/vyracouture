"""
Fashion Store - E-Commerce Web Application
Flask + MongoDB backend
"""

import os
import secrets
import hashlib
from datetime import datetime, timezone, timedelta
from functools import wraps

from flask import (
    Flask, render_template, request, jsonify, session,
    redirect, url_for, flash, abort, send_from_directory
)
from flask_cors import CORS
from pymongo import MongoClient, DESCENDING
from bson import ObjectId
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
CORS(app)

# ─── File Upload ──────────────────────────────────────────────────────────────

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# ─── Cloudinary (optional: permanent image hosting) ─────────────────────
# Set these 3 env vars and admin uploads go to Cloudinary's CDN instead of
# the local disk, so images survive Render deploys/restarts. When not
# configured, falls back to local disk storage.
CLOUDINARY_CLOUD = os.getenv('CLOUDINARY_CLOUD_NAME', '').strip()
CLOUDINARY_KEY = os.getenv('CLOUDINARY_API_KEY', '').strip()
CLOUDINARY_SECRET = os.getenv('CLOUDINARY_API_SECRET', '').strip()
CLOUDINARY_FOLDER = 'vyracouture'


def upload_to_cloudinary(filename, mimetype, content):
    """Upload image bytes to Cloudinary. Returns secure URL or None."""
    if not (CLOUDINARY_CLOUD and CLOUDINARY_KEY and CLOUDINARY_SECRET):
        return None
    try:
        import requests
    except ImportError:
        print('[cloudinary] requests not installed; using local disk')
        return None
    try:
        timestamp = str(int(datetime.now(timezone.utc).timestamp()))
        # Cloudinary signature: sorted params joined, secret appended, sha1
        to_sign = f'folder={CLOUDINARY_FOLDER}&timestamp={timestamp}{CLOUDINARY_SECRET}'
        signature = hashlib.sha1(to_sign.encode('utf-8')).hexdigest()
        resp = requests.post(
            f'https://api.cloudinary.com/v1_1/{CLOUDINARY_CLOUD}/image/upload',
            data={
                'api_key': CLOUDINARY_KEY,
                'timestamp': timestamp,
                'folder': CLOUDINARY_FOLDER,
                'signature': signature,
            },
            files={'file': (filename, content, mimetype)},
            timeout=30,
        )
        if resp.status_code == 200:
            return resp.json().get('secure_url')
        print(f'[cloudinary] upload failed ({resp.status_code}): {resp.text[:300]}')
    except Exception as e:
        print(f'[cloudinary] upload error: {e}')
    return None

import werkzeug.utils

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ─── MongoDB ────────────────────────────────────────────────────────────────

MONGO_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'fashion_store')  # explicit: never touches other DBs (e.g. farhaans_farm)
client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

products_collection = db.products
orders_collection = db.orders
users_collection = db.users
collections_collection = db.collections  # category collections like "Dresses", "Linen"
settings_collection = db.settings
cart_collection = db.carts

# Ensure this store's collections exist (own namespace, shared with no one)
try:
    existing = set(db.list_collection_names())
    for name in ('products', 'collections', 'orders', 'users', 'carts', 'settings'):
        if name not in existing:
            db.create_collection(name)
    # Safety indexes
    users_collection.create_index('phone', unique=True)
    orders_collection.create_index('order_id', unique=True)
    products_collection.create_index('slug', unique=True)
    collections_collection.create_index('slug', unique=True)
except Exception as e:
        print(f'[mongo] init warning: {e}')

# ─── Helpers ────────────────────────────────────────────────────────────────

IST = timezone(timedelta(hours=5, minutes=30))

def istnow():
    return datetime.now(IST)

def json_serial(obj):
    if isinstance(obj, (datetime,)):
        return obj.isoformat()
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            if request.is_json:
                return jsonify({'error': 'Login required'}), 401
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_admin'):
            if request.is_json:
                return jsonify({'error': 'Admin access required'}), 403
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated

# ─── Public Routes ──────────────────────────────────────────────────────────

@app.route('/')
def index():
    featured = list(products_collection.find({'is_featured': True}).limit(8))
    new_arrivals = list(products_collection.find({'is_new': True}).limit(8))
    sale_products = list(products_collection.find({'is_sale': True}).limit(8))
    all_collections = list(collections_collection.find({'is_active': True}).sort('sort_order', 1))

    # Group products by collection
    collection_products = {}
    for col in all_collections:
        prods = list(products_collection.find({'collection_slug': col['slug']}).limit(8))
        if prods:
            collection_products[col['slug']] = {
                'name': col['name'],
                'products': prods
            }

    return render_template('index.html',
        featured=featured,
        new_arrivals=new_arrivals,
        sale_products=sale_products,
        collections=all_collections,
        collection_products=collection_products
    )


@app.route('/shop')
@app.route('/shop/<collection_slug>')
def shop(collection_slug=None):
    page = int(request.args.get('page', 1))
    per_page = 24
    sort = request.args.get('sort', 'newest')
    query = {'is_active': True}

    if collection_slug:
        query['collection_slug'] = collection_slug

    # Sorting
    sort_key = {'newest': ('created_at', -1), 'price_low': ('sale_price', 1),
                'price_high': ('sale_price', -1), 'popular': ('sold_count', -1)}
    sort_field, sort_dir = sort_key.get(sort, ('created_at', -1))

    total = products_collection.count_documents(query)
    products = list(products_collection.find(query).sort(sort_field, sort_dir).skip((page-1)*per_page).limit(per_page))
    all_collections = list(collections_collection.find({'is_active': True}).sort('sort_order', 1))

    return render_template('shop.html',
        products=products,
        all_collections=all_collections,
        current_collection=collection_slug,
        current_sort=sort,
        page=page,
        total_pages=(total + per_page - 1) // per_page,
        total_products=total
    )


@app.route('/product/<product_id>')
def product_detail(product_id):
    try:
        product = products_collection.find_one({'_id': ObjectId(product_id)})
    except:
        product = products_collection.find_one({'slug': product_id})

    if not product:
        abort(404)

    # Get related products
    related = list(products_collection.find({
        'collection_slug': product.get('collection_slug'),
        '_id': {'$ne': product['_id']},
        'is_active': True
    }).limit(4))

    return render_template('product_detail.html', product=product, related=related)


@app.route('/cart')
def cart():
    return render_template('cart.html')


@app.route('/account')
def account():
    return render_template('account.html')


@app.route('/checkout')
def checkout_page():
    return render_template('checkout.html')


@app.route('/track-order')
def track_order():
    return render_template('track_order.html')


@app.route('/order-confirmation/<order_id>')
def order_confirmation(order_id):
    order = orders_collection.find_one({'order_id': order_id})
    # Only the owning customer (or an admin) may view it
    if not order:
        return render_template('404.html'), 404
    if not session.get('is_admin') and order.get('user_id') != session.get('user_id'):
        return render_template('404.html'), 404
    return render_template('order_confirmation.html', order=order)


# ─── API: Auth ──────────────────────────────────────────────────────────────

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    phone = data.get('phone', '').strip()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()

    if not phone or not name:
        return jsonify({'error': 'Phone and name required'}), 400

    existing = users_collection.find_one({'phone': phone})
    if existing:
        return jsonify({'error': 'Phone already registered'}), 400

    user = {
        'phone': phone,
        'name': name,
        'email': email,
        'address': '',
        'created_at': istnow(),
        'last_login': istnow(),
        'auth_method': 'phone'
    }
    result = users_collection.insert_one(user)
    session['user_id'] = str(result.inserted_id)
    session['phone'] = phone
    session['logged_in'] = True
    session['user_name'] = name

    return jsonify({'success': True, 'name': name})


@app.route('/api/login-phone', methods=['POST'])
def api_login_phone():
    data = request.json
    phone = data.get('phone', '').strip()

    user = users_collection.find_one({'phone': phone})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    session['user_id'] = str(user['_id'])
    session['phone'] = phone
    session['logged_in'] = True
    session['user_name'] = user.get('name', 'Customer')

    users_collection.update_one({'_id': user['_id']}, {'$set': {'last_login': istnow()}})

    return jsonify({'success': True, 'name': user.get('name', 'Customer')})


@app.route('/api/session')
def api_session():
    if session.get('logged_in'):
        user = None
        if session.get('user_id'):
            try:
                user = users_collection.find_one({'_id': ObjectId(session['user_id'])})
            except:
                pass
        return jsonify({
            'logged_in': True,
            'name': session.get('user_name', 'Customer'),
            'phone': session.get('phone', ''),
            'email': user.get('email', '') if user else '',
            'is_admin': session.get('is_admin', False)
        })
    return jsonify({'logged_in': False})


@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})


# ─── API: Products ──────────────────────────────────────────────────────────

@app.route('/api/products')
def api_products():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 24))
    collection = request.args.get('collection')
    query = {'is_active': True}

    if collection:
        query['collection_slug'] = collection

    total = products_collection.count_documents(query)
    products = list(products_collection.find(query).sort('created_at', -1).skip((page-1)*per_page).limit(per_page))

    return jsonify({
        'products': [{
            '_id': str(p['_id']),
            'name': p['name'],
            'slug': p.get('slug', ''),
            'sale_price': p['sale_price'],
            'original_price': p['original_price'],
            'image': p.get('images', [''])[0] if p.get('images') else '',
            'hover_image': p.get('hover_image', ''),
            'is_sale': p.get('is_sale', False),
            'is_new': p.get('is_new', False),
            'collection_slug': p.get('collection_slug', ''),
            'discount_pct': round((1 - p['sale_price'] / p['original_price']) * 100) if p['original_price'] > 0 else 0
        } for p in products],
        'total': total,
        'page': page,
        'total_pages': (total + per_page - 1) // per_page
    })


@app.route('/api/product/<product_id>')
def api_product_detail(product_id):
    try:
        product = products_collection.find_one({'_id': ObjectId(product_id)})
    except:
        product = products_collection.find_one({'slug': product_id})

    if not product:
        return jsonify({'error': 'Product not found'}), 404

    return jsonify({
        '_id': str(product['_id']),
        'name': product['name'],
        'slug': product.get('slug', ''),
        'description': product.get('description', ''),
        'sale_price': product['sale_price'],
        'original_price': product['original_price'],
        'images': product.get('images', []),
        'hover_image': product.get('hover_image', ''),
        'sizes': product.get('sizes', ['S', 'M', 'L', 'XL']),
        'colors': product.get('colors', []),
        'is_sale': product.get('is_sale', False),
        'is_new': product.get('is_new', False),
        'collection_slug': product.get('collection_slug', ''),
        'fabric': product.get('fabric', ''),
        'care_instructions': product.get('care_instructions', ''),
        'in_stock': product.get('in_stock', True),
        'discount_pct': round((1 - product['sale_price'] / product['original_price']) * 100) if product['original_price'] > 0 else 0
    })


@app.route('/api/collections')
def api_collections():
    cols = list(collections_collection.find({'is_active': True}).sort('sort_order', 1))
    return jsonify([{
        '_id': str(c['_id']),
        'name': c['name'],
        'slug': c['slug'],
        'description': c.get('description', ''),
        'banner_image': c.get('banner_image', ''),
        'product_count': products_collection.count_documents({'collection_slug': c['slug'], 'is_active': True})
    } for c in cols])


# ─── API: Cart ──────────────────────────────────────────────────────────────

@app.route('/api/cart', methods=['GET'])
def get_cart():
    cart_id = session.get('cart_id')
    if not cart_id:
        return jsonify({'items': [], 'total': 0, 'count': 0})

    cart = cart_collection.find_one({'_id': ObjectId(cart_id)})
    if not cart:
        return jsonify({'items': [], 'total': 0, 'count': 0})

    items = cart.get('items', [])
    total = sum(i.get('price', 0) * i.get('quantity', 1) for i in items)
    count = sum(i.get('quantity', 1) for i in items)

    return jsonify({'items': items, 'total': total, 'count': count})


@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    data = request.json
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))
    size = data.get('size', 'M')
    color = data.get('color', '')

    product = products_collection.find_one({'_id': ObjectId(product_id)})
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    cart_id = session.get('cart_id')
    if not cart_id:
        cart_result = cart_collection.insert_one({'items': [], 'created_at': istnow()})
        cart_id = str(cart_result.inserted_id)
        session['cart_id'] = cart_id

    item = {
        'product_id': str(product['_id']),
        'name': product['name'],
        'image': product.get('images', [''])[0] if product.get('images') else '',
        'price': product['sale_price'],
        'original_price': product['original_price'],
        'size': size,
        'color': color,
        'quantity': quantity
    }

    cart = cart_collection.find_one({'_id': ObjectId(cart_id)})
    items = cart.get('items', []) if cart else []

    # Check if same product/size/color already in cart
    updated = False
    for i, existing in enumerate(items):
        if (existing['product_id'] == item['product_id'] and
            existing.get('size') == size and
            existing.get('color') == color):
            items[i]['quantity'] += quantity
            updated = True
            break

    if not updated:
        items.append(item)

    cart_collection.update_one({'_id': ObjectId(cart_id)}, {'$set': {'items': items}})

    count = sum(i['quantity'] for i in items)
    return jsonify({'success': True, 'count': count})


@app.route('/api/cart/update', methods=['POST'])
def update_cart():
    data = request.json
    index = int(data.get('index', 0))
    quantity = int(data.get('quantity', 1))

    cart_id = session.get('cart_id')
    if not cart_id:
        return jsonify({'error': 'No cart'}), 400

    cart = cart_collection.find_one({'_id': ObjectId(cart_id)})
    if not cart:
        return jsonify({'error': 'Cart not found'}), 404

    items = cart.get('items', [])
    if 0 <= index < len(items):
        if quantity <= 0:
            items.pop(index)
        else:
            items[index]['quantity'] = quantity

    cart_collection.update_one({'_id': ObjectId(cart_id)}, {'$set': {'items': items}})

    total = sum(i.get('price', 0) * i.get('quantity', 1) for i in items)
    count = sum(i.get('quantity', 1) for i in items)
    return jsonify({'success': True, 'total': total, 'count': count})


@app.route('/api/cart/clear', methods=['POST'])
def clear_cart():
    cart_id = session.get('cart_id')
    if cart_id:
        cart_collection.update_one({'_id': ObjectId(cart_id)}, {'$set': {'items': []}})
    return jsonify({'success': True})


# ─── API: Orders ────────────────────────────────────────────────────────────

@app.route('/api/checkout', methods=['POST'])
def checkout():
    if not session.get('logged_in'):
        return jsonify({'error': 'Login required'}), 401

    cart_id = session.get('cart_id')
    if not cart_id:
        return jsonify({'error': 'Cart is empty'}), 400

    cart = cart_collection.find_one({'_id': ObjectId(cart_id)})
    if not cart or not cart.get('items'):
        return jsonify({'error': 'Cart is empty'}), 400

    data = request.json
    items = cart['items']
    total = sum(i.get('price', 0) * i.get('quantity', 1) for i in items)

    order = {
        'user_id': session.get('user_id'),
        'user_name': session.get('user_name', ''),
        'phone': session.get('phone', ''),
        'email': data.get('email', ''),
        'address': data.get('address', ''),
        'city': data.get('city', ''),
        'state': data.get('state', ''),
        'pincode': data.get('pincode', ''),
        'items': items,
        'subtotal': total,
        'shipping': 0 if total >= 999 else 99,
        'total': total + (0 if total >= 999 else 99),
        'payment_method': data.get('payment_method', 'cod'),
        'status': 'pending',
        'created_at': istnow(),
        'updated_at': istnow(),
        'order_id': f'HB{istnow().strftime("%Y%m%d")}{str(secrets.token_hex(3)).upper()}'
    }

    result = orders_collection.insert_one(order)

    # Update sold counts
    for item in items:
        products_collection.update_one(
            {'_id': ObjectId(item['product_id'])},
            {'$inc': {'sold_count': item.get('quantity', 1), 'stock': -item.get('quantity', 1)}}
        )

    # Clear cart
    cart_collection.update_one({'_id': ObjectId(cart_id)}, {'$set': {'items': []}})

    return jsonify({
        'success': True,
        'order_id': order['order_id'],
        'total': order['total']
    })


@app.route('/api/orders')
@login_required
def api_orders():
    user_id = session.get('user_id')
    orders = list(orders_collection.find({'user_id': user_id}).sort('created_at', -1))

    return jsonify([{
        '_id': str(o['_id']),
        'order_id': o['order_id'],
        'items': o['items'],
        'total': o['total'],
        'status': o['status'],
        'created_at': o['created_at'].isoformat() if o.get('created_at') else '',
    } for o in orders])


@app.route('/api/track-order')
def track_order_api():
    order_id = request.args.get('order_id', '').strip()
    phone = request.args.get('phone', '').strip()

    order = orders_collection.find_one({
        'order_id': order_id,
        'phone': phone
    })

    if not order:
        return jsonify({'error': 'Order not found'}), 404

    return jsonify({
        'order_id': order['order_id'],
        'items': order['items'],
        'total': order['total'],
        'status': order['status'],
        'created_at': order['created_at'].isoformat() if order.get('created_at') else '',
        'address': order.get('address', ''),
    })


# ─── Image Upload ───────────────────────────────────────────────────────────

@app.route('/api/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not (file and allowed_file(file.filename)):
        return jsonify({'error': 'File type not allowed. Use PNG, JPG, GIF, WebP, or SVG.'}), 400

    content = file.read()

    # Try Cloudinary first (permanent URL that survives deploys)
    url = upload_to_cloudinary(file.filename, file.mimetype, content)
    if url:
        return jsonify({'success': True, 'url': url,
                        'filename': url.rsplit('/', 1)[-1], 'storage': 'cloudinary'})

    # Fallback: local disk (ephemeral on Render free plan)
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{secrets.token_hex(8)}.{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    with open(filepath, 'wb') as fh:
        fh.write(content)
    url = url_for('static', filename=f'uploads/{filename}')
    return jsonify({'success': True, 'url': url, 'filename': filename, 'storage': 'local'})


@app.route('/api/upload/multiple', methods=['POST'])
def upload_multiple():
    if 'files' not in request.files:
        return jsonify({'error': 'No files'}), 400

    files = request.files.getlist('files')
    urls = []
    for file in files:
        if file and file.filename and allowed_file(file.filename):
            content = file.read()
            url = upload_to_cloudinary(file.filename, file.mimetype, content)
            if not url:
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{secrets.token_hex(8)}.{ext}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                with open(filepath, 'wb') as fh:
                    fh.write(content)
                url = url_for('static', filename=f'uploads/{filename}')
            urls.append(url)

    return jsonify({'success': True, 'urls': urls, 'count': len(urls)})


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# ─── Admin Routes ───────────────────────────────────────────────────────────

@app.route('/admin')
def admin_page():
    if not session.get('is_admin'):
        return render_template('admin_login.html')
    return render_template('admin.html')


@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')

    admin_username = os.getenv('ADMIN_USERNAME', 'admin')
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')

    if username == admin_username and password == admin_password:
        session['is_admin'] = True
        session['logged_in'] = True
        session['user_name'] = 'Admin'
        return jsonify({'success': True})

    return jsonify({'error': 'Invalid credentials'}), 401


@app.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    session.pop('is_admin', None)
    return jsonify({'success': True})


# ─── Admin API: Products ────────────────────────────────────────────────────

@app.route('/api/admin/products')
@admin_required
def admin_products():
    page = int(request.args.get('page', 1))
    per_page = 20
    total = products_collection.count_documents({})
    products = list(products_collection.find({}).sort('created_at', -1).skip((page-1)*per_page).limit(per_page))

    return jsonify({
        'products': [{
            '_id': str(p['_id']),
            'name': p.get('name', ''),
            'sale_price': p.get('sale_price', 0),
            'original_price': p.get('original_price', 0),
            'image': p.get('images', [''])[0] if p.get('images') else '',
            'collection_slug': p.get('collection_slug', ''),
            'is_active': p.get('is_active', True),
            'is_featured': p.get('is_featured', False),
            'is_new': p.get('is_new', False),
            'stock': p.get('stock', 0),
            'sold_count': p.get('sold_count', 0),
        } for p in products],
        'total': total,
        'page': page
    })


@app.route('/api/admin/product', methods=['POST'])
@admin_required
def admin_create_product():
    data = request.json
    product = {
        'name': data.get('name', ''),
        'slug': data.get('slug', data.get('name', '').lower().replace(' ', '-')),
        'description': data.get('description', ''),
        'sale_price': float(data.get('sale_price', 0)),
        'original_price': float(data.get('original_price', 0)),
        'images': data.get('images', []),
        'hover_image': data.get('hover_image', ''),
        'sizes': data.get('sizes', ['XS', 'S', 'M', 'L', 'XL', 'XXL']),
        'colors': data.get('colors', []),
        'collection_slug': data.get('collection_slug', ''),
        'fabric': data.get('fabric', ''),
        'care_instructions': data.get('care_instructions', ''),
        'is_active': data.get('is_active', True),
        'is_featured': data.get('is_featured', False),
        'is_new': data.get('is_new', True),
        'is_sale': data.get('is_sale', True),
        'in_stock': data.get('in_stock', True),
        'stock': int(data.get('stock', 100)),
        'sold_count': 0,
        'created_at': istnow(),
        'updated_at': istnow()
    }

    result = products_collection.insert_one(product)
    return jsonify({'success': True, '_id': str(result.inserted_id)})


@app.route('/api/admin/product/<product_id>', methods=['PUT'])
@admin_required
def admin_update_product(product_id):
    data = request.json
    data['updated_at'] = istnow()
    products_collection.update_one({'_id': ObjectId(product_id)}, {'$set': data})
    return jsonify({'success': True})


@app.route('/api/admin/product/<product_id>', methods=['DELETE'])
@admin_required
def admin_delete_product(product_id):
    products_collection.delete_one({'_id': ObjectId(product_id)})
    return jsonify({'success': True})


# ─── Admin API: Collections ─────────────────────────────────────────────────

@app.route('/api/admin/collections')
@admin_required
def admin_collections():
    cols = list(collections_collection.find({}).sort('sort_order', 1))
    return jsonify([{
        '_id': str(c['_id']),
        'name': c.get('name', ''),
        'slug': c.get('slug', ''),
        'description': c.get('description', ''),
        'banner_image': c.get('banner_image', ''),
        'is_active': c.get('is_active', True),
        'sort_order': c.get('sort_order', 0),
        'product_count': products_collection.count_documents({'collection_slug': c.get('slug', '')})
    } for c in cols])


@app.route('/api/admin/collection', methods=['POST'])
@admin_required
def admin_create_collection():
    data = request.json
    col = {
        'name': data.get('name', ''),
        'slug': data.get('slug', data.get('name', '').lower().replace(' ', '-')),
        'description': data.get('description', ''),
        'banner_image': data.get('banner_image', ''),
        'is_active': data.get('is_active', True),
        'sort_order': int(data.get('sort_order', 0)),
        'created_at': istnow()
    }
    result = collections_collection.insert_one(col)
    return jsonify({'success': True, '_id': str(result.inserted_id)})


@app.route('/api/admin/collection/<col_id>', methods=['PUT'])
@admin_required
def admin_update_collection(col_id):
    data = request.json
    collections_collection.update_one({'_id': ObjectId(col_id)}, {'$set': data})
    return jsonify({'success': True})


@app.route('/api/admin/collection/<col_id>', methods=['DELETE'])
@admin_required
def admin_delete_collection(col_id):
    collections_collection.delete_one({'_id': ObjectId(col_id)})
    return jsonify({'success': True})


# ─── Admin API: Orders ──────────────────────────────────────────────────────

@app.route('/api/admin/orders')
@admin_required
def admin_orders():
    status = request.args.get('status')
    query = {}
    if status:
        query['status'] = status
    orders = list(orders_collection.find(query).sort('created_at', -1))

    return jsonify([{
        '_id': str(o['_id']),
        'order_id': o.get('order_id', ''),
        'user_name': o.get('user_name', ''),
        'phone': o.get('phone', ''),
        'email': o.get('email', ''),
        'address': o.get('address', ''),
        'items': o.get('items', []),
        'subtotal': o.get('subtotal', 0),
        'shipping': o.get('shipping', 0),
        'total': o.get('total', 0),
        'payment_method': o.get('payment_method', 'cod'),
        'status': o.get('status', 'pending'),
        'created_at': o.get('created_at', '').isoformat() if isinstance(o.get('created_at'), datetime) else str(o.get('created_at', '')),
    } for o in orders])


@app.route('/api/admin/order/<order_id>/status', methods=['PUT'])
@admin_required
def admin_update_order_status(order_id):
    data = request.json
    new_status = data.get('status', '')
    orders_collection.update_one(
        {'_id': ObjectId(order_id)},
        {'$set': {'status': new_status, 'updated_at': istnow()}}
    )
    return jsonify({'success': True})


# ─── Admin API: Dashboard Stats ─────────────────────────────────────────────

@app.route('/api/admin/stats')
@admin_required
def admin_stats():
    total_products = products_collection.count_documents({})
    total_orders = orders_collection.count_documents({})
    pending_orders = orders_collection.count_documents({'status': 'pending'})
    total_users = users_collection.count_documents({})
    total_revenue = 0
    for order in orders_collection.find({'status': {'$in': ['delivered', 'shipped', 'processing', 'pending']}}):
        total_revenue += order.get('total', 0)

    return jsonify({
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_users': total_users,
        'total_revenue': total_revenue,
    })


# ─── Admin API: Users ───────────────────────────────────────────────────────

@app.route('/api/admin/users')
@admin_required
def admin_users():
    users = list(users_collection.find({}).sort('created_at', -1))
    return jsonify([{
        '_id': str(u['_id']),
        'name': u.get('name', ''),
        'phone': u.get('phone', ''),
        'email': u.get('email', ''),
        'address': u.get('address', ''),
        'created_at': u.get('created_at', '').isoformat() if isinstance(u.get('created_at'), datetime) else str(u.get('created_at', '')),
        'last_login': u.get('last_login', '').isoformat() if isinstance(u.get('last_login'), datetime) else str(u.get('last_login', '')),
    } for u in users])


@app.route('/api/admin/user/<user_id>', methods=['DELETE'])
@admin_required
def admin_delete_user(user_id):
    users_collection.delete_one({'_id': ObjectId(user_id)})
    return jsonify({'success': True})


# ─── Error Handlers ─────────────────────────────────────────────────────────

@app.errorhandler(404)
def page_not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Not found'}), 404
    return render_template('404.html'), 404


# ─── Template Context ───────────────────────────────────────────────────────

STORE_NAME = os.getenv('STORE_NAME', 'FASHION STORE')
STORE_TAGLINE = os.getenv('STORE_TAGLINE', 'Up to 50% off! Sale is live 🎉')

@app.context_processor
def inject_store():
    return {
        'store_name': STORE_NAME,
        'store_tagline': STORE_TAGLINE,
    }


# ─── Start ──────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5001))
    app.run(debug=True, port=port)
