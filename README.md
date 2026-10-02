# 🛍️ Fashion Store — Complete Documentation

A full-featured e-commerce web application built with Flask + MongoDB, inspired by Hashboosh.com.

---

## 📋 Table of Contents

1. [Getting Started](#1-getting-started)
2. [Database Configuration](#2-database-configuration)
3. [Admin Panel Guide](#3-admin-panel-guide)
4. [Product Management](#4-product-management)
5. [Collection Management](#5-collection-management)
6. [Order Management](#6-order-management)
7. [User Management](#7-user-management)
8. [Customer-Facing Features](#8-customer-facing-features)
9. [API Reference](#9-api-reference)
10. [Deployment](#10-deployment)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Getting Started

### Prerequisites

- Python 3.10+
- MongoDB (local or Atlas cloud)
- pip (Python package manager)

### Installation

```bash
# Navigate to the fashion store directory
cd "D:\Farhaan's_Farm\farhaans-farm\fashion_store"

# Install dependencies
pip install -r requirements.txt

# Seed the database with sample data
python -X utf8 seed.py

# Start the server
python -X utf8 run.py
```

### Environment Variables (`.env`)

```env
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/fashion_store?retryWrites=true&w=majority
SECRET_KEY=your-secret-key-for-sessions
FLASK_ENV=development
FLASK_PORT=5001
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

| Variable | Description | Default |
|---|---|---|
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017/` |
| `SECRET_KEY` | Flask session encryption key | Auto-generated |
| `FLASK_PORT` | Server port | `5001` |
| `ADMIN_USERNAME` | Admin panel login username | `admin` |
| `ADMIN_PASSWORD` | Admin panel login password | `admin123` |

> ⚠️ **Change admin credentials before deploying to production!**

---

## 2. Database Configuration

### MongoDB Connection

The app uses **PyMongo** to connect to MongoDB. The connection is established in `app.py`:

```python
MONGO_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client.get_database()  # Uses 'fashion_store' from the URI
```

### Collections Overview

| Collection | Purpose | Key Fields |
|---|---|---|
| `products` | All product listings | name, sale_price, original_price, images, sizes, colors, collection_slug, stock |
| `collections` | Product categories/groups | name, slug, description, banner_image, sort_order, is_active |
| `orders` | Customer orders | order_id, user_id, items, total, status, address, payment_method |
| `users` | Registered customers | name, phone, email, address, created_at, last_login |
| `carts` | Shopping carts (session-based) | items (array of product refs with qty/size/color) |
| `settings` | Site-wide settings | Key-value pairs for configuration |

### Setting Up MongoDB

#### Option A: Local MongoDB

1. Install MongoDB Community Edition from https://www.mongodb.com/try/download/community
2. Start the service
3. Set `.env`:
   ```env
   MONGODB_URI=mongodb://localhost:27017/fashion_store
   ```

#### Option B: MongoDB Atlas (Cloud — Recommended)

1. Create account at https://cloud.mongodb.com
2. Create a cluster (free tier M0 is fine)
3. Go to **Database Access** → Create a database user
4. Go to **Network Access** → Add your IP (or `0.0.0.0/0` for all)
5. Go to **Database** → Connect → Copy the connection string
6. Set `.env`:
   ```env
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/fashion_store?retryWrites=true&w=majority
   ```

### Seeding Initial Data

```bash
python -X utf8 seed.py
```

This creates:
- **7 collections** (Dresses, Shrug Dresses, Hand Embroidered, Linen Collection, Pinafore Picks, Luxe Looms, Sale)
- **24 sample products** with images, prices, sizes, colors, and descriptions

> 💡 Safe to run multiple times — it drops and recreates the data each time.

---

## 3. Admin Panel Guide

### Accessing the Admin Panel

1. Open browser: `http://localhost:5001/admin`
2. Enter credentials:
   - **Username:** `admin`
   - **Password:** `admin123`

### Admin Dashboard

The dashboard shows key metrics at a glance:

| Metric | Description |
|---|---|
| **Total Products** | Number of products in the store |
| **Total Orders** | All orders placed |
| **Pending Orders** | Orders awaiting processing |
| **Total Users** | Registered customers |
| **Total Revenue** | Sum of all order totals |

### Navigation

| Tab | What You Can Do |
|---|---|
| 📊 **Dashboard** | View stats and metrics |
| 📦 **Products** | Add, edit, delete products |
| 📁 **Collections** | Manage product categories |
| 🛒 **Orders** | View and update order status |
| 👥 **Users** | View and manage customers |

---

## 4. Product Management

### Adding a New Product

1. Go to **Admin → Products**
2. Click **"+ Add Product"**
3. Fill in the form:

| Field | Required | Description |
|---|---|---|
| **Name** | ✅ | Product name (e.g., "Petal Romance Dress") |
| **Description** | No | Product description text |
| **Sale Price** | ✅ | Current selling price in ₹ |
| **Original Price** | ✅ | Original/mrp price in ₹ (shown crossed out) |
| **Stock** | No | Available quantity (default: 100) |
| **Fabric** | No | Fabric type (e.g., "Pure Linen", "Cotton Blend") |
| **Image URLs** | No | One image URL per line (see image hosting below) |
| **Collection** | No | Which collection/category it belongs to |
| **Sizes** | No | Comma-separated sizes (default: XS,S,M,L,XL,XXL) |
| **Featured** | No | Show on homepage "Best Sellers" section |
| **New Arrival** | No | Show in "New Arrivals" section |
| **On Sale** | No | Show in "Sale" section with discount badge |
| **Active** | No | Visible on the storefront |

4. Click **"Save Product"**

### Product Image Hosting

Products use image URLs. Free hosting options:

| Service | How to Use |
|---|---|
| **ImgBB** (Recommended) | Upload at https://imgbb.com → copy direct URL |
| **Cloudinary** | Upload → copy "Secure URL" |
| **Placehold.co** (for testing) | Use `https://placehold.co/600x800/FF5722/fff?text=Product+Name` |
| **Google Drive** | Upload → make public → change `/file/d/` to `/uc?export=view&id=` |

**Image Tips:**
- Use square images (600×800px recommended for product cards)
- Use high-quality images (the site displays them at various sizes)
- You can add multiple images — the first one shows on product cards, all show on the detail page
- One URL per line in the "Image URLs" field

### Discount Calculation

The discount percentage is **automatically calculated**:
```
Discount = (1 - Sale Price / Original Price) × 100
```

Example: If Original Price = ₹2,000 and Sale Price = ₹1,500
- Discount = (1 - 1500/2000) × 100 = **25% OFF**

### Editing a Product

1. Go to **Admin → Products**
2. Find the product in the table
3. Click the **✏️ edit** button
4. Modify the fields
5. Click **"Save Product"**

### Deleting a Product

1. Go to **Admin → Products**
2. Find the product
3. Click the **🗑️ delete** button
4. Confirm the deletion

### Stock Management

- Stock decreases automatically when orders are placed
- Update stock manually via the edit form
- Set stock to 0 to mark as out of stock (or uncheck "Active")

---

## 5. Collection Management

Collections are **product categories** that group products together (like "Dresses", "Linen Collection", "Sale").

### Creating a Collection

1. Go to **Admin → Collections**
2. Click **"+ Add Collection"**
3. Fill in:

| Field | Required | Description |
|---|---|---|
| **Name** | ✅ | Collection name (e.g., "Summer Linen") |
| **Description** | No | Brief description |
| **Banner Image URL** | No | Banner image for the collection page |
| **Sort Order** | No | Display order (lower = first) |
| **Active** | No | Whether it shows on the site |

4. Click **"Save Collection"**

> ⚠️ The **slug** is auto-generated from the name (e.g., "Summer Linen" → "summer-linen"). This slug is used in URLs like `/shop/summer-linen`.

### Assigning Products to Collections

When creating/editing a product, select the collection from the dropdown. Products show in that collection's page automatically.

### Deleting a Collection

- Deleting a collection does **NOT** delete the products in it
- Products become "uncategorized" and still appear in "Shop All"

---

## 6. Order Management

### Order Lifecycle

```
pending → processing → shipped → delivered
                       ↘ cancelled
```

| Status | Meaning |
|---|---|
| **pending** | New order, not yet processed |
| **processing** | Being prepared/packed |
| **shipped** | Handed to delivery partner |
| **delivered** | Successfully delivered |
| **cancelled** | Order cancelled |

### Viewing Orders

1. Go to **Admin → Orders**
2. See all orders with:
   - Order ID (format: `HB20260911A1B2C3`)
   - Customer name and phone
   - Items ordered
   - Total amount
   - Current status
   - Order date

### Updating Order Status

1. Find the order in the table
2. Use the **status dropdown** to change status
3. Changes are saved automatically

### Cancelling an Order

1. Find the order
2. Click the **❌ cancel** button
3. The order status changes to "cancelled"

### Order Details Available

Each order contains:
- **Order ID** — Unique identifier for tracking
- **Customer info** — Name, phone, email
- **Shipping address** — Full address with city, state, pincode
- **Items** — Product name, size, color, quantity, price
- **Payment** — Method (COD/UPI), total amount
- **Dates** — When the order was placed

### Customer Order Tracking

Customers can track their orders at `/track-order` using:
- Their **Order ID** (shown after checkout)
- Their **phone number**

---

## 7. User Management

### Viewing Users

1. Go to **Admin → Users**
2. See all registered customers with:
   - Name
   - Phone number
   - Email
   - Registration date
   - Last login date

### How Users Register

Users register through the **customer website**:
1. Click **"Account"** in the header
2. Enter phone number
3. Click **"Continue"**
4. If new user, they're automatically created
5. If existing user, they're logged in

### Deleting a User

1. Go to **Admin → Users**
2. Find the user
3. Click **🗑️ delete**

> ⚠️ Deleting a user does **NOT** delete their orders. Order history is preserved.

### User Data Stored

```json
{
  "name": "Nawap Patel",
  "phone": "919876543210",
  "email": "nawap@example.com",
  "address": "123 Main St, Mumbai",
  "created_at": "2026-09-11T10:00:00+05:30",
  "last_login": "2026-09-11T10:30:00+05:30",
  "auth_method": "phone"
}
```

---

## 8. Customer-Facing Features

### Homepage Sections

| Section | Content |
|---|---|
| **Hero Banner** | Main call-to-action with "Shop Now" button |
| **Category Pills** | Quick links to each collection |
| **New Arrivals** | Products marked as `is_new: true` |
| **Best Sellers** | Products marked as `is_featured: true` |
| **Sale** | Products with discount badges |
| **Collection Sections** | Each collection with its products |
| **Testimonials** | Customer reviews (hardcoded) |
| **Trust Bar** | Free Shipping, Exchanges, Secure Payment, Support |

### Shopping Flow

1. **Browse** → Homepage or Shop page
2. **Filter** → By collection or sort order
3. **View Product** → Click product card → see details, sizes, colors
4. **Add to Cart** → "Quick Add" or "Add to Cart" on detail page
5. **View Cart** → Review items, quantities, totals
6. **Checkout** → Enter shipping details, choose payment
7. **Order Placed** → Confirmation with order ID
8. **Track** → Use `/track-order` with order ID + phone

### Cart Features

- **Quick Add** — Adds with default size M, quantity 1
- **Quantity control** — Increase/decrease in cart
- **Remove items** — Delete from cart
- **Free shipping** — Automatically applied on orders above ₹999
- **Cart persists** — Stored in session (survives page refresh)

### Checkout

| Payment Method | Description |
|---|---|
| **Cash on Delivery** | Pay when delivered |
| **UPI / Google Pay** | Online payment (placeholder — needs gateway integration) |

---

## 9. API Reference

### Public Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/products` | List products (supports `?page=`, `?collection=`, `?per_page=`) |
| GET | `/api/product/{id}` | Get single product details |
| GET | `/api/collections` | List all active collections |
| GET | `/api/session` | Check current user session |
| GET | `/api/cart` | Get current cart contents |
| POST | `/api/cart/add` | Add item to cart |
| POST | `/api/cart/update` | Update cart item quantity |
| POST | `/api/cart/clear` | Clear the cart |
| POST | `/api/register` | Register new user |
| POST | `/api/login-phone` | Login with phone number |
| POST | `/api/logout` | Logout |
| POST | `/api/checkout` | Place an order |
| GET | `/api/orders` | Get user's orders (login required) |
| GET | `/api/track-order` | Track order by ID + phone |

### Admin Endpoints (Require Admin Session)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/admin/login` | Admin login |
| POST | `/api/admin/logout` | Admin logout |
| GET | `/api/admin/stats` | Dashboard statistics |
| GET | `/api/admin/products` | List all products |
| POST | `/api/admin/product` | Create product |
| PUT | `/api/admin/product/{id}` | Update product |
| DELETE | `/api/admin/product/{id}` | Delete product |
| GET | `/api/admin/collections` | List all collections |
| POST | `/api/admin/collection` | Create collection |
| PUT | `/api/admin/collection/{id}` | Update collection |
| DELETE | `/api/admin/collection/{id}` | Delete collection |
| GET | `/api/admin/orders` | List all orders |
| PUT | `/api/admin/order/{id}/status` | Update order status |
| GET | `/api/admin/users` | List all users |
| DELETE | `/api/admin/user/{id}` | Delete user |

### Example API Calls

**Add product via API:**
```bash
curl -X POST http://localhost:5001/api/admin/product \
  -H "Content-Type: application/json" \
  -b "session=YOUR_SESSION_COOKIE" \
  -d '{
    "name": "New Dress",
    "sale_price": 1990,
    "original_price": 2490,
    "images": ["https://example.com/image.jpg"],
    "sizes": ["S", "M", "L", "XL"],
    "collection_slug": "dresses",
    "fabric": "Pure Linen",
    "is_active": true,
    "is_new": true,
    "is_sale": true
  }'
```

**Update order status:**
```bash
curl -X PUT http://localhost:5001/api/admin/order/ORDER_ID/status \
  -H "Content-Type: application/json" \
  -b "session=YOUR_SESSION_COOKIE" \
  -d '{"status": "shipped"}'
```

---

## 10. Deployment

### Deploy to Render

1. Push the `fashion_store` directory to a GitHub repo
2. Go to https://dashboard.render.com → **New Web Service**
3. Connect your GitHub repo
4. Configure:
   - **Root Directory:** `fashion_store`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Port:** 5001
5. Add environment variables:
   ```
   MONGODB_URI=your_mongodb_atlas_uri
   SECRET_KEY=your_random_secret_key
   FLASK_PORT=5001
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=your_secure_password
   ```
6. Deploy!

### Production Checklist

- [ ] Change `ADMIN_PASSWORD` to a strong password
- [ ] Change `SECRET_KEY` to a long random string
- [ ] Enable MongoDB Atlas network access for Render's IP
- [ ] Set `FLASK_ENV=production` (disables debug mode)
- [ ] Use HTTPS (Render provides free SSL)
- [ ] Add product images (replace placeholder images)

---

## 11. Troubleshooting

### Common Issues

| Problem | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'flask'` | Run `pip install -r requirements.txt` |
| `Connection refused` to MongoDB | Check `MONGODB_URI` in `.env`, ensure MongoDB is running |
| `UnicodeEncodeError` on Windows | Always use `python -X utf8` to run |
| Products not showing on homepage | Check `is_active: true` in MongoDB |
| Images not loading | Verify image URLs are accessible (not broken links) |
| Cart empty after adding | Check session cookies are enabled in browser |
| Admin login fails | Verify `ADMIN_USERNAME` and `ADMIN_PASSWORD` in `.env` |

### Useful MongoDB Commands

```javascript
// Connect to the database
mongo "mongodb+srv://cluster.mongodb.net/fashion_store"

// Count products
db.products.countDocuments({})

// Find products without is_active field
db.products.find({is_active: {$exists: false}})

// Add is_active to all products
db.products.updateMany({}, {$set: {is_active: true}})

// View all orders
db.orders.find().sort({created_at: -1}).pretty()

// Delete all products (careful!)
db.products.deleteMany({})

// Reset a product's stock
db.products.updateOne({name: "Petal Romance"}, {$set: {stock: 100}})
```

---

## File Structure

```
fashion_store/
├── app.py              # Flask application (routes, models, API)
├── run.py              # Entry point to start the server
├── seed.py             # Database seeding script
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (DO NOT commit)
├── README.md           # This documentation
├── templates/
│   ├── base.html           # Base layout (header, footer, nav)
│   ├── index.html          # Homepage
│   ├── shop.html           # Product listing page
│   ├── product_detail.html # Single product page
│   ├── cart.html           # Shopping cart
│   ├── checkout.html       # Checkout form
│   ├── account.html        # User account / login
│   ├── track_order.html    # Order tracking
│   ├── admin.html          # Admin dashboard
│   ├── admin_login.html    # Admin login page
│   └── 404.html            # Not found page
└── static/
    ├── css/
    │   └── style.css       # All styling (responsive, modern)
    └── js/
        └── app.js          # Client-side JavaScript
```
