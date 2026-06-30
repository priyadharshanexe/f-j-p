from flask import Flask, render_template_string, request, jsonify, session
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'supersecretkeyforflaskecommerceapp'

# In-memory data store (demo purposes only)
PRODUCTS = [
    {
        "id": "p1",
        "name": "UltraPhone X",
        "description": "A revolutionary smartphone with advanced camera and display.",
        "price": 999.99,
        "images": [
            "https://storage.googleapis.com/workspace-0f70711f-8b4e-4d94-86f1-2a93ccde5887/image/cf72616b-5b44-4b12-ae2e-7208c04eb2dd.png",
            "https://storage.googleapis.com/workspace-0f70711f-8b4e-4d94-86f1-2a93ccde5887/image/1d644fe5-9250-434b-865b-5bf4b7a01019.png",
            "https://storage.googleapis.com/workspace-0f70711f-8b4e-4d94-86f1-2a93ccde5887/image/430aaf3b-123f-4de9-b1a7-2be50671af2d.png"
        ],
        "category": "Smartphones",
        "brand": "TechCorp",
        "rating": 4.5,
        "reviews": ["r1", "r2"],
        "stock": 15,
        "variants": [
            {"id": "v1", "name": "128GB", "price": 999.99},
            {"id": "v2", "name": "256GB", "price": 1149.99},
        ],
        "tags": ["flagship", "camera", "touch"]
    },
    {
        "id": "p2",
        "name": "SoundMax Bluetooth Speaker",
        "description": "Portable wireless speaker with superior sound quality and 12h battery life.",
        "price": 149.99,
        "images": [
            "https://storage.googleapis.com/workspace-0f70711f-8b4e-4d94-86f1-2a93ccde5887/image/80c40c0d-b044-4002-ba05-f7ef131b6dfe.png",
            "https://storage.googleapis.com/workspace-0f70711f-8b4e-4d94-86f1-2a93ccde5887/image/910a1bd9-6c32-420b-b38a-8b36da2c6094.png",
        ],
        "category": "Audio",
        "brand": "SoundWave",
        "rating": 4.2,
        "reviews": ["r3"],
        "stock": 33,
        "variants": [],
        "tags": ["wireless", "battery", "portable"]
    },
    {
        "id": "p3",
        "name": "ProGamer Mechanical Keyboard",
        "description": "High-performance mechanical keyboard with customizable RGB lighting and fast response times.",
        "price": 199.99,
        "images": [
            "https://storage.googleapis.com/workspace-0f70711f-8b4e-4d94-86f1-2a93ccde5887/image/04e554ef-2b97-4f07-ad78-bc86c5401972.png",
            "https://storage.googleapis.com/workspace-0f70711f-8b4e-4d94-86f1-2a93ccde5887/image/0bb8cfbf-b7af-457f-adc8-7bd9c83ec284.png"
        ],
        "category": "Accessories",
        "brand": "HyperKey",
        "rating": 4.8,
        "reviews": [],
        "stock": 12,
        "variants": [],
        "tags": ["gaming", "mechanical", "rgb"]
    },
]

REVIEWS = [
    {
        "id": "r1",
        "productId": "p1",
        "userId": "u1",
        "rating": 5,
        "comment": "Amazing phone! Camera quality is breathtaking.",
        "helpful": 12,
        "verified": True,
        "createdAt": "2023-04-15T10:20:30"
    },
    {
        "id": "r2",
        "productId": "p1",
        "userId": "u2",
        "rating": 4,
        "comment": "Fast and sleek but battery could be better.",
        "helpful": 5,
        "verified": False,
        "createdAt": "2023-04-20T13:15:42"
    },
    {
        "id": "r3",
        "productId": "p2",
        "userId": "u1",
        "rating": 4,
        "comment": "Great sound for the price.",
        "helpful": 7,
        "verified": True,
        "createdAt": "2023-05-01T08:12:00"
    }
]

USERS = {
    "u1": {
        "id": "u1",
        "email": "alice@example.com",
        "name": "Alice",
        "addresses": ["123 Tech Street, Silicon Valley"],
        "paymentMethods": ["Visa **** 4242"],
        "wishlist": ["p3"],
        "orderHistory": []
    },
    "u2": {
        "id": "u2",
        "email": "bob@example.com",
        "name": "Bob",
        "addresses": [],
        "paymentMethods": [],
        "wishlist": [],
        "orderHistory": []
    }
}

ORDERS = []

COUPONS = {
    "SAVE10": 0.10,
    "TECH20": 0.20,
}

SHIPPING_OPTIONS = [
    {"id": "standard", "name": "Standard Shipping (5-7 days)", "cost": 5.99},
    {"id": "express", "name": "Express Shipping (2-3 days)", "cost": 15.99},
    {"id": "overnight", "name": "Overnight Shipping (1 day)", "cost": 29.99},
]

# Helper functions
def get_cart():
    return session.get("cart", [])

def save_cart(cart):
    session["cart"] = cart

def find_product(productId):
    for p in PRODUCTS:
        if p["id"] == productId:
            return p
    return None

def find_variant(product, variantId):
    if product and product.get("variants"):
        for v in product["variants"]:
            if v["id"] == variantId:
                return v
    return None

def calculate_cart_total(cart):
    subtotal = 0.0
    for item in cart:
        subtotal += item["price"] * item["quantity"]
    return subtotal

# Routes

@app.route('/')
def index():
    # Render full page with inline template
    return render_template_string(PAGE_TEMPLATE, products=PRODUCTS, reviews=REVIEWS, user=USERS["u1"], coupons=COUPONS, shipping=SHIPPING_OPTIONS)

@app.route('/product/<product_id>')
def product_detail(product_id):
    product = find_product(product_id)
    if not product:
        return "Product not found", 404
    product_reviews = [r for r in REVIEWS if r["productId"] == product_id]
    return render_template_string(PRODUCT_DETAIL_TEMPLATE,product=product,reviews=product_reviews,user=USERS["u1"],USERS=USERS)

@app.route('/api/cart', methods=["GET", "POST", "PUT", "DELETE"])
def cart_api():
    if "cart" not in session:
        session["cart"] = []
    cart = session["cart"]
    data = request.get_json() or {}

    if request.method == "GET":
        return jsonify(cart)

    if request.method == "POST":
        # Add item to cart
        productId = data.get("productId")
        variantId = data.get("variantId")
        quantity = int(data.get("quantity", 1))

        product = find_product(productId)
        if not product:
            return jsonify({"error": "Product not found"}), 404

        variant = find_variant(product, variantId)
        price = variant["price"] if variant else product["price"]

        existing = None
        for item in cart:
            if item["productId"] == productId and item.get("variantId") == variantId:
                existing = item
                break

        if existing:
            existing["quantity"] += quantity
        else:
            cart_item = {
                "id": str(uuid.uuid4()),
                "productId": productId,
                "variantId": variantId,
                "quantity": quantity,
                "price": price,
                "addedAt": datetime.utcnow().isoformat()
            }
            cart.append(cart_item)
        save_cart(cart)
        return jsonify(cart)

    if request.method == "PUT":
        # Update quantity or variant
        itemId = data.get("id")
        quantity = int(data.get("quantity", 1))
        new_variantId = data.get("variantId", None)

        item = next((i for i in cart if i["id"] == itemId), None)
        if not item:
            return jsonify({"error": "Cart item not found"}), 404

        product = find_product(item["productId"])
        variant = find_variant(product, new_variantId) if new_variantId else None

        item["quantity"] = quantity
        if variant:
            item["variantId"] = new_variantId
            item["price"] = variant["price"]
        save_cart(cart)
        return jsonify(cart)

    if request.method == "DELETE":
        itemId = data.get("id")
        cart = [i for i in cart if i["id"] != itemId]
        save_cart(cart)
        return jsonify(cart)

@app.route('/api/checkout', methods=["POST"])
def checkout_api():
    data = request.get_json() or {}
    cart = get_cart()
    if not cart:
        return jsonify({"error": "Cart is empty"}), 400

    shippingId = data.get("shippingId")
    couponCode = data.get("couponCode", "").upper()
    billing = data.get("billing", {})
    shippingAddress = data.get("shipping", {})

    shipping_option = next((s for s in SHIPPING_OPTIONS if s["id"] == shippingId), None)
    if not shipping_option:
        return jsonify({"error": "Invalid shipping option"}), 400

    subtotal = calculate_cart_total(cart)
    discount = COUPONS.get(couponCode, 0)
    discounted = subtotal * (1 - discount)
    total = discounted + shipping_option["cost"]

    order = {
        "id": str(uuid.uuid4()),
        "userId": "u1",
        "items": cart,
        "total": round(total, 2),
        "status": "Processing",
        "shipping": shippingAddress,
        "billing": billing,
        "tracking": "MSG1234567890",
        "createdAt": datetime.utcnow().isoformat()
    }
    ORDERS.append(order)

    # Clear cart after checkout
    session["cart"] = []

    # Append to user order history
    USERS["u1"]["orderHistory"].append(order["id"])

    return jsonify({"success": True, "orderId": order["id"]})

@app.route('/api/orders')
def orders_api():
    user_orders = [o for o in ORDERS if o["userId"] == "u1"]
    return jsonify(user_orders)

@app.route('/api/wishlist', methods=["GET", "POST", "DELETE"])
def wishlist_api():
    user = USERS["u1"]
    if request.method == "GET":
        return jsonify(user.get("wishlist", []))
    data = request.get_json() or {}
    productId = data.get("productId")
    if request.method == "POST":
        if productId and productId not in user["wishlist"]:
            user["wishlist"].append(productId)
        return jsonify(user["wishlist"])
    if request.method == "DELETE":
        if productId and productId in user["wishlist"]:
            user["wishlist"].remove(productId)
        return jsonify(user["wishlist"])

# HTML template with inline CSS and JS
PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Flask Premium E-commerce</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet" />
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet" />
<style>
    /* Reset and basics */
    * {
        box-sizing: border-box;
    }
    body, html {
        margin: 0; padding: 0; height: 100%;
        font-family: 'Inter', sans-serif;
        background: #f9fafb;
        color: #1f2937;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    header {
        position: sticky;
        top: 0; z-index: 1000;
        background: #7c3aed;
        color: white;
        display: flex;
        align-items: center;
        padding: 0 24px;
        height: 60px;
        gap: 16px;
    }
    header .logo {
        font-weight: 700;
        font-size: 1.5rem;
        letter-spacing: 2px;
        user-select: none;
    }
    header input[type="search"] {
        flex-grow: 1;
        border-radius: 8px;
        border: none;
        height: 36px;
        padding: 0 12px;
        font-size: 1rem;
        outline: none;
    }
    header nav {
        display: flex;
        gap: 20px;
        align-items: center;
    }
    header nav button {
        border: none;
        background: transparent;
        color: white;
        cursor: pointer;
        position: relative;
        font-size: 24px;
    }
    header nav button .badge {
        position: absolute;
        top: -6px;
        right: -6px;
        background: #ef4444;
        color: white;
        border-radius: 50%;
        padding: 2px 6px;
        font-size: 12px;
        font-weight: 700;
        user-select: none;
    }
    /* Layout grid */
    #main {
        display: grid;
        grid-template-columns: 300px 1fr 350px;
        height: calc(100vh - 60px);
        gap: 16px;
        padding: 16px 24px;
        background: #f9fafb;
    }
    /* Sidebar filters */
    #filter-sidebar {
        background: white;
        border-radius: 16px;
        padding: 20px;
        overflow-y: auto;
        box-shadow: 0 4px 12px rgba(124, 58, 237, 0.2);
    }
    #filter-sidebar h2 {
        font-size: 1.25rem;
        margin-bottom: 12px;
        font-weight: 600;
        color: #5b21b6;
        border-bottom: 2px solid #a78bfa;
        padding-bottom: 6px;
    }
    .filter-group {
        margin-bottom: 24px;
    }
    .filter-group label {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.95rem;
        user-select: none;
        cursor: pointer;
    }
    .filter-group input[type="checkbox"],
    .filter-group input[type="radio"] {
        accent-color: #7c3aed;
    }
    /* Product grid */
    #product-grid {
        background: white;
        border-radius: 16px;
        padding: 20px;
        overflow-y: auto;
        box-shadow: 0 4px 12px rgba(124, 58, 237, 0.2);
        display: grid;
        grid-template-columns: repeat(auto-fill,minmax(260px,1fr));
        gap: 20px;
    }
    .product-card {
        background: #fafafa;
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(124, 58, 237, 0.15);
        display: flex;
        flex-direction: column;
        transition: box-shadow 0.3s ease;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    .product-card:hover {
        box-shadow: 0 8px 25px rgba(124, 58, 237, 0.4);
    }
    .product-image-wrapper {
        height: 180px;
        overflow: hidden;
        border-top-left-radius: 16px;
        border-top-right-radius: 16px;
        background: linear-gradient(135deg, #7c3aed, #a78bfa);
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .product-image-wrapper img {
        max-width: 100%;
        height: auto;
        object-fit: contain;
        transition: transform 0.3s ease;
    }
    .product-card:hover .product-image-wrapper img {
        transform: scale(1.05);
    }
    .product-info {
        padding: 12px 16px 16px;
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .product-name {
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 6px;
        color: #4c1d95;
    }
    .product-description {
        font-size: 0.85rem;
        color: #6b7280;
        margin-bottom: 12px;
        flex-grow: 1;
    }
    .product-price {
        font-weight: 700;
        font-size: 1.125rem;
        color: #7c3aed;
        margin-bottom: 12px;
    }
    .product-rating {
        display: flex;
        align-items: center;
        gap: 4px;
        margin-bottom: 12px;
    }
    .material-icons.star {
        color: #c084fc;
        font-size: 18px;
    }
    .btn-add-cart {
        background: #7c3aed;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 0;
        font-weight: 600;
        cursor: pointer;
        font-size: 1rem;
        transition: background-color 0.3s ease;
        width: 100%;
        user-select: none;
    }
    .btn-add-cart:hover {
        background: #a78bfa;
    }
    /* Cart sidebar */
    #cart-sidebar {
        background: white;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(124, 58, 237, 0.2);
        display: flex;
        flex-direction: column;
        height: 100%;
    }
    #cart-sidebar h2 {
        font-size: 1.25rem;
        font-weight: 600;
        color: #5b21b6;
        margin-bottom: 16px;
        border-bottom: 2px solid #a78bfa;
        padding-bottom: 6px;
    }
    #cart-items {
        flex-grow: 1;
        overflow-y: auto;
        margin-bottom: 16px;
    }
    .cart-item {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;
        border-bottom: 1px solid #e5e7eb;
        padding-bottom: 12px;
    }
    .cart-item img {
        width: 64px;
        height: 64px;
        object-fit: contain;
        border-radius: 12px;
        background: linear-gradient(135deg,#7c3aed,#a78bfa);
        padding: 6px;
    }
    .cart-item-info {
        flex-grow: 1;
        display: flex;
        flex-direction: column;
    }
    .cart-item-name {
        font-weight: 600;
        font-size: 1rem;
        color: #4c1d95;
    }
    .cart-item-variant {
        color: #6b7280;
        font-size: 0.85rem;
    }
    .cart-item-price {
        font-weight: 600;
        color: #7c3aed;
        font-size: 1rem;
        margin-top: 4px;
    }
    .cart-item-controls {
        display: flex;
        flex-direction: column;
        gap: 8px;
        align-items: center;
    }
    .quantity-control {
        display: flex;
        align-items: center;
        border: 1px solid #a78bfa;
        border-radius: 8px;
        overflow: hidden;
        user-select: none;
    }
    .quantity-control button {
        background: transparent;
        border: none;
        color: #7c3aed;
        font-size: 20px;
        width: 28px;
        height: 28px;
        cursor: pointer;
        padding: 0;
        line-height: 1;
    }
    .quantity-control span {
        width: 24px;
        text-align: center;
        font-weight: 600;
    }
    .btn-remove {
        background: transparent;
        border: none;
        color: #ef4444;
        cursor: pointer;
        font-size: 20px;
    }
    /* Checkout area */
    #checkout {
        border-top: 2px solid #a78bfa;
        padding-top: 16px;
    }
    #checkout h3 {
        font-weight: 700;
        color: #5b21b6;
        font-size: 1.15rem;
        margin-bottom: 12px;
    }
    #checkout .total {
        font-weight: 900;
        font-size: 1.5rem;
        color: #7c3aed;
        margin-bottom: 16px;
    }
    #checkout button {
        background: #7c3aed;
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px;
        font-weight: 700;
        font-size: 1.25rem;
        cursor: pointer;
        width: 100%;
        user-select: none;
        transition: background-color 0.3s ease;
    }
    #checkout button:hover {
        background: #a78bfa;
    }
    /* Scrollbar styling */
    #filter-sidebar::-webkit-scrollbar,
    #product-grid::-webkit-scrollbar,
    #cart-items::-webkit-scrollbar {
        width: 8px;
    }
    #filter-sidebar::-webkit-scrollbar-thumb,
    #product-grid::-webkit-scrollbar-thumb,
    #cart-items::-webkit-scrollbar-thumb {
        background-color: #a78bfa;
        border-radius: 4px;
    }
    /* Responsive */
    @media (max-width: 1024px) {
        #main {
            grid-template-columns: 1fr 350px;
            padding: 16px;
        }
        #filter-sidebar {
            display: none;
        }
    }
    @media (max-width: 640px) {
        #main {
            grid-template-columns: 1fr;
            height: auto;
            padding: 12px 12px 80px;
        }
        #cart-sidebar {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: 300px;
            border-radius: 16px 16px 0 0;
            box-shadow: 0 -4px 16px rgba(124, 58, 237, 0.3);
            background: white;
            padding: 12px 16px;
            z-index: 1050;
            transform: translateY(100%);
            transition: transform 0.3s ease;
            display: flex;
            flex-direction: column;
        }
        #cart-sidebar.open {
            transform: translateY(0);
        }
        #cart-sidebar h2 {
            font-size: 1.1rem;
            margin-bottom: 8px;
        }
        #cart-toggle-btn {
            position: fixed;
            bottom: 310px;
            right: 20px;
            background: #7c3aed;
            color: white;
            border: none;
            border-radius: 50%;
            width: 48px;
            height: 48px;
            font-size: 32px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(124, 58, 237, 0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1100;
        }
    }
</style>
</head>
<body>
<header>
    <div class="logo">ShopPrime</div>
    <input type="search" placeholder="Search products..." id="search-input" aria-label="Search products" />
    <nav>
        <button id="wishlist-btn" title="Wishlist" aria-label="Wishlist">
            <span class="material-icons">favorite_border</span>
            <span class="badge" id="wishlist-count">0</span>
        </button>
        <button id="cart-btn" title="Shopping Cart" aria-label="Shopping Cart">
            <span class="material-icons">shopping_cart</span>
            <span class="badge" id="cart-count">0</span>
        </button>
    </nav>
</header>

<div id="main" role="main">
    <aside id="filter-sidebar" aria-label="Filter products">
        <h2>Filters</h2>
        <div class="filter-group" role="group" aria-labelledby="category-label">
            <h3 id="category-label">Category</h3>
            <label><input type="checkbox" name="category" value="Smartphones" /> Smartphones</label>
            <label><input type="checkbox" name="category" value="Audio" /> Audio</label>
            <label><input type="checkbox" name="category" value="Accessories" /> Accessories</label>
        </div>
        <div class="filter-group" role="group" aria-labelledby="brand-label">
            <h3 id="brand-label">Brand</h3>
            <label><input type="checkbox" name="brand" value="TechCorp" /> TechCorp</label>
            <label><input type="checkbox" name="brand" value="SoundWave" /> SoundWave</label>
            <label><input type="checkbox" name="brand" value="HyperKey" /> HyperKey</label>
        </div>
        <div class="filter-group" role="group" aria-labelledby="rating-label">
            <h3 id="rating-label">Minimum Rating</h3>
            <label><input type="radio" name="rating" value="0" checked /> Any</label>
            <label><input type="radio" name="rating" value="4" /> 4 & Up</label>
            <label><input type="radio" name="rating" value="4.5" /> 4.5 & Up</label>
        </div>
        <div class="filter-group" role="group" aria-labelledby="price-label">
            <h3 id="price-label">Price Range</h3>
            <label><input type="radio" name="price" value="any" checked /> Any</label>
            <label><input type="radio" name="price" value="0-150" /> $0 - $150</label>
            <label><input type="radio" name="price" value="150-500" /> $150 - $500</label>
            <label><input type="radio" name="price" value="500-2000" /> $500+</label>
        </div>
    </aside>

    <section id="product-grid" aria-live="polite" aria-label="Product catalog">
        <!-- Products inserted by JS -->
    </section>

    <aside id="cart-sidebar" aria-label="Shopping cart" aria-live="polite">
        <h2>Shopping Cart</h2>
        <div id="cart-items" tabindex="0" aria-label="Cart items list">
            <!-- Cart items inserted here -->
        </div>
        <div id="checkout">
            <h3>Order Summary</h3>
            <div class="total" id="cart-total">$0.00</div>
            <button id="checkout-btn" disabled>Proceed to Checkout</button>
        </div>
    </aside>
</div>

<button id="cart-toggle-btn" aria-label="Toggle Cart" title="Toggle Cart" hidden>
    <span class="material-icons">shopping_cart</span>
</button>

<script>
(() => {
    // Data from server side rendered in JSON to JS
    const PRODUCTS = {{ products|tojson }};
    const REVIEWS = {{ reviews|tojson }};
    const COUPONS = {{ coupons|tojson }};
    const SHIPPING_OPTIONS = {{ shipping|tojson }};

    // User data simplified demo
    const USER = {{ user|tojson }};

    const cartBtn = document.getElementById('cart-btn');
    const wishlistBtn = document.getElementById('wishlist-btn');
    const cartCount = document.getElementById('cart-count');
    const wishlistCount = document.getElementById('wishlist-count');
    const searchInput = document.getElementById('search-input');
    const productGrid = document.getElementById('product-grid');
    const cartSidebar = document.getElementById('cart-sidebar');
    const cartItemsContainer = document.getElementById('cart-items');
    const cartTotalElem = document.getElementById('cart-total');
    const checkoutBtn = document.getElementById('checkout-btn');
    const cartToggleBtn = document.getElementById('cart-toggle-btn');

    // Filters state
    let activeFilters = {
        categories: new Set(),
        brands: new Set(),
        rating: 0,
        price: null,
        search: ''
    };

    let cart = [];
    let wishlist = [];

    // Utility - format price
    function formatPrice(val) {
        return new Intl.NumberFormat('en-US', { style:'currency', currency:'USD' }).format(val);
    }

    // Fetch cart from server
    async function fetchCart() {
        const res = await fetch('/api/cart');
        if (res.ok) {
            cart = await res.json();
            updateCartUI();
        }
    }

    // Fetch wishlist from server
    async function fetchWishlist() {
        const res = await fetch('/api/wishlist');
        if (res.ok) {
            wishlist = await res.json();
            updateWishlistUI();
        }
    }

    // Add to cart
    async function addToCart(productId, variantId = null, quantity = 1) {
        const payload = { productId, variantId, quantity };
        const res = await fetch('/api/cart', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            cart = await res.json();
            updateCartUI();
            showNotification('Added to cart');
        } else {
            const error = await res.json();
            alert(error.error || 'Error adding to cart');
        }
    }

    // Update cart item quantity or variant
    async function updateCartItem(id, quantity, variantId = null) {
        const payload = { id, quantity, variantId };
        const res = await fetch('/api/cart', {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            cart = await res.json();
            updateCartUI();
        }
    }

    // Remove item from cart
    async function removeCartItem(id) {
        const payload = { id };
        const res = await fetch('/api/cart', {
            method: 'DELETE',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            cart = await res.json();
            updateCartUI();
        }
    }

    // Add or remove from wishlist
    async function toggleWishlist(productId) {
        if (wishlist.includes(productId)) {
            // Remove
            const res = await fetch('/api/wishlist', {
                method: 'DELETE',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ productId })
            });
            if (res.ok) {
                wishlist = await res.json();
                updateWishlistUI();
            }
        } else {
            // Add
            const res = await fetch('/api/wishlist', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ productId })
            });
            if (res.ok) {
                wishlist = await res.json();
                updateWishlistUI();
            }
        }
    }

    // Update wishlist badge
    function updateWishlistUI() {
        wishlistCount.textContent = wishlist.length;
        // Update hearts on products
        document.querySelectorAll('.btn-wishlist').forEach(btn => {
            const pid = btn.dataset.productId;
            btn.innerHTML = wishlist.includes(pid)
                ? '<span class="material-icons" aria-label="Remove from wishlist">favorite</span>'
                : '<span class="material-icons" aria-label="Add to wishlist">favorite_border</span>';
        });
    }

    // Update cart badge and sidebar
    function updateCartUI() {
        cartCount.textContent = cart.reduce((a, i) => a + i.quantity, 0);
        if (cartCount.textContent === "0") {
            cartCount.style.display = "none";
            checkoutBtn.disabled = true;
        } else {
            cartCount.style.display = "inline-block";
            checkoutBtn.disabled = false;
        }

        cartItemsContainer.innerHTML = '';
        if (cart.length === 0) {
            cartItemsContainer.innerHTML = '<p>Your cart is empty.</p>';
            cartTotalElem.textContent = formatPrice(0);
            return;
        }

        let total = 0;

        cart.forEach(item => {
            const product = PRODUCTS.find(p => p.id === item.productId);
            if (!product) return;
            const variant = product.variants?.find(v => v.id === item.variantId);
            const price = variant ? variant.price : item.price || product.price;
            total += price * item.quantity;

            const variantName = variant ? variant.name : '';

            const div = document.createElement('div');
            div.className = 'cart-item';
            div.innerHTML = `
                <img src="${product.images[0]}" alt="Image of ${product.name}" />
                <div class="cart-item-info">
                    <div class="cart-item-name">${product.name}</div>
                    ${variantName ? `<div class="cart-item-variant">${variantName}</div>` : ''}
                    <div class="cart-item-price">${formatPrice(price)}</div>
                </div>
                <div class="cart-item-controls">
                    <div class="quantity-control" aria-label="Quantity controls for ${product.name}">
                      <button class="decrease" title="Decrease quantity" aria-label="Decrease quantity">−</button>
                      <span aria-live="polite">${item.quantity}</span>
                      <button class="increase" title="Increase quantity" aria-label="Increase quantity">+</button>
                    </div>
                    <button class="btn-remove" title="Remove item" aria-label="Remove ${product.name} from cart">&times;</button>
                </div>
            `;

            const decreaseBtn = div.querySelector('.decrease');
            const increaseBtn = div.querySelector('.increase');
            const removeBtn = div.querySelector('.btn-remove');

            decreaseBtn.addEventListener('click', () => {
                if (item.quantity > 1) {
                    updateCartItem(item.id, item.quantity - 1, item.variantId);
                } else {
                    removeCartItem(item.id);
                }
            });
            increaseBtn.addEventListener('click', () => {
                updateCartItem(item.id, item.quantity + 1, item.variantId);
            });
            removeBtn.addEventListener('click', () => {
                removeCartItem(item.id);
            });

            cartItemsContainer.appendChild(div);
        });

        cartTotalElem.textContent = formatPrice(total);
    }

    // Render product cards with applied filters and search
    function renderProducts() {
        let filtered = PRODUCTS;

        // Filter categories
        if(activeFilters.categories.size > 0) {
            filtered = filtered.filter(p => activeFilters.categories.has(p.category));
        }
        // Filter brands
        if(activeFilters.brands.size > 0) {
            filtered = filtered.filter(p => activeFilters.brands.has(p.brand));
        }
        // Filter rating
        if(activeFilters.rating > 0) {
            filtered = filtered.filter(p => p.rating >= activeFilters.rating);
        }
        // Filter price
        if(activeFilters.price) {
            filtered = filtered.filter(p => {
                switch(activeFilters.price) {
                    case '0-150': return p.price <= 150;
                    case '150-500': return p.price > 150 && p.price <= 500;
                    case '500-2000': return p.price > 500;
                    default: return true;
                }
            });
        }
        // Search
        if(activeFilters.search.trim() !== '') {
            const searchText = activeFilters.search.trim().toLowerCase();
            filtered = filtered.filter(p => 
                p.name.toLowerCase().includes(searchText) ||
                p.description.toLowerCase().includes(searchText) ||
                p.brand.toLowerCase().includes(searchText)
            );
        }

        productGrid.innerHTML = "";
        if(filtered.length === 0) {
            productGrid.innerHTML = "<p>No products found.</p>";
            return;
        }

        filtered.forEach(product => {
            const productEl = document.createElement('article');
            productEl.className = 'product-card';
            const lowestVariantPrice = product.variants && product.variants.length > 0
                ? Math.min(...product.variants.map(v => v.price))
                : product.price;

            const starsCount = Math.round(product.rating);
            const starsHtml = Array(5).fill(0).map((_, i) =>
                `<span class="material-icons star" aria-hidden="true">${i < starsCount ? 'star' : 'star_border'}</span>`
            ).join('');

            productEl.innerHTML = `
                <div class="product-image-wrapper" tabindex="0" aria-describedby="desc-${product.id}" role="img" aria-label="Image of ${product.name}">
                    <img src="${product.images[0]}" alt="Image of ${product.name}" />
                </div>
                <div class="product-info">
                    <h3 class="product-name">${product.name}</h3>
                    <div class="product-description" id="desc-${product.id}">${product.description}</div>
                    <div class="product-rating" aria-label="Rating: ${product.rating} out of 5 stars">${starsHtml}</div>
                    <div class="product-price">${formatPrice(lowestVariantPrice)}</div>
                    <button class="btn-add-cart" aria-label="Add ${product.name} to cart" data-product-id="${product.id}">Add to Cart</button>
                    <button class="btn-wishlist" aria-label="Add or remove ${product.name} to wishlist" data-product-id="${product.id}" title="Wishlist">
                        <span class="material-icons">favorite_border</span>
                    </button>
                </div>
            `;
            // Add to cart button
            productEl.querySelector('.btn-add-cart').addEventListener('click', (e) => {
                addToCart(product.id);
            });
            // Wishlist button
            const wishlistBtn = productEl.querySelector('.btn-wishlist');
            wishlistBtn.addEventListener('click', () => {
                toggleWishlist(product.id);
            });
            productGrid.appendChild(productEl);
        });
        updateWishlistUI();
    }

    // Event handlers for filter sidebar
    function setupFilters() {
        document.querySelectorAll('#filter-sidebar input[name="category"]').forEach(input => {
            input.addEventListener('change', e => {
                activeFilters.categories = new Set(
                    Array.from(document.querySelectorAll('#filter-sidebar input[name="category"]:checked'))
                    .map(i => i.value)
                );
                renderProducts();
            });
        });
        document.querySelectorAll('#filter-sidebar input[name="brand"]').forEach(input => {
            input.addEventListener('change', e => {
                activeFilters.brands = new Set(
                    Array.from(document.querySelectorAll('#filter-sidebar input[name="brand"]:checked'))
                    .map(i => i.value)
                );
                renderProducts();
            });
        });
        document.querySelectorAll('#filter-sidebar input[name="rating"]').forEach(input => {
            input.addEventListener('change', e => {
                const val = Number(e.target.value);
                activeFilters.rating = val;
                renderProducts();
            });
        });
        document.querySelectorAll('#filter-sidebar input[name="price"]').forEach(input => {
            input.addEventListener('change', e => {
                const val = e.target.value;
                activeFilters.price = val === 'any' ? null : val;
                renderProducts();
            });
        });

        searchInput.addEventListener('input', e => {
            activeFilters.search = e.target.value;
            renderProducts();
        });
    }

    // Notifications
    function showNotification(msg) {
        const notif = document.createElement('div');
        notif.textContent = msg;
        notif.style.position = 'fixed';
        notif.style.bottom = '24px';
        notif.style.left = '50%';
        notif.style.transform = 'translateX(-50%)';
        notif.style.background = '#7c3aed';
        notif.style.color = 'white';
        notif.style.padding = '12px 24px';
        notif.style.borderRadius = '12px';
        notif.style.boxShadow = '0 8px 24px rgba(124,58,237,0.35)';
        notif.style.zIndex = '1100';
        notif.style.fontWeight = '700';
        notif.style.opacity = '0';
        notif.style.transition = 'opacity 0.3s ease';

        document.body.appendChild(notif);
        requestAnimationFrame(() => {
            notif.style.opacity = '1';
        });
        setTimeout(() => {
            notif.style.opacity = '0';
            notif.addEventListener('transitionend', () => {
                notif.remove();
            });
        }, 2000);
    }

    // Cart sidebar toggle for mobile
    function setupCartToggle() {
        cartBtn.addEventListener('click', () => {
            if (window.innerWidth <= 640) {
                cartSidebar.classList.add('open');
                cartToggleBtn.hidden = false;
                cartToggleBtn.focus();
            }
        });
        cartToggleBtn.addEventListener('click', () => {
            cartSidebar.classList.toggle('open');
            if (!cartSidebar.classList.contains('open')) {
                cartToggleBtn.hidden = true;
            }
        });
    }

    // Checkout process (demo: open alert with order summary)
    async function performCheckout() {
        if (cart.length === 0) {
            alert("Your cart is empty");
            return;
        }

        // Dummy shipping and billing info for demo
        const shippingId = SHIPPING_OPTIONS[0].id;
        const couponCode = '';  // No coupon in demo
        const billing = { name: USER.name, email: USER.email };
        const shipping = { address: USER.addresses[0] || "123 Delivery St" };

        const payload = {
            shippingId,
            couponCode,
            billing,
            shipping
        };
        const res = await fetch('/api/checkout', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            const json = await res.json();
            alert("Order placed! Your order ID: " + json.orderId);
            fetchCart();
        } else {
            const error = await res.json();
            alert(error.error || "Checkout failed.");
        }
    }

    checkoutBtn.addEventListener('click', (e) => {
        e.preventDefault();
        performCheckout();
    });

    // Initial load
    fetchCart();
    fetchWishlist();
    setupFilters();
    renderProducts();
    setupCartToggle();

    // Accessibility: close cart sidebar with Escape
    document.addEventListener('keydown', e => {
        if (e.key === "Escape" && cartSidebar.classList.contains('open')) {
            cartSidebar.classList.remove('open');
            cartToggleBtn.hidden = true;
            cartBtn.focus();
        }
    });
})();
</script>
</body>
</html>
"""

PRODUCT_DETAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{{ product.name }}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet" />
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet" />
<style>
    body {
        font-family: 'Inter', sans-serif;
        margin: 0;
        background: #f9fafb;
        color: #1f2937;
        padding: 24px;
    }
    .container {
        max-width: 1000px;
        margin: auto;
        background: white;
        border-radius: 20px;
        box-shadow: 0 8px 24px rgba(124, 58, 237, 0.2);
        display: flex;
        gap: 32px;
        padding: 24px;
    }
    .image-gallery {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 16px;
        user-select: none;
    }
    .main-image {
        flex: 1;
        border-radius: 16px;
        overflow: hidden;
        background: linear-gradient(135deg,#7c3aed,#a78bfa);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: zoom-in;
        position: relative;
    }
    .main-image img {
        max-width: 100%;
        max-height: 450px;
        object-fit: contain;
        transition: transform 0.3s ease;
    }
    .thumbnail-list {
        display: flex;
        gap: 12px;
    }
    .thumbnail-list img {
        width: 80px;
        height: 80px;
        border-radius: 12px;
        cursor: pointer;
        object-fit: contain;
        background: linear-gradient(135deg,#7c3aed,#a78bfa);
        border: 2px solid transparent;
        transition: border-color 0.3s ease;
    }
    .thumbnail-list img.selected {
        border-color: #7c3aed;
    }
    .product-info {
        flex: 1;
        display: flex;
        flex-direction: column;
    }
    .product-title {
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 8px;
        color: #5b21b6;
    }
    .product-price {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 24px;
        color: #7c3aed;
    }
    .product-desc {
        flex-grow: 1;
        font-size: 1rem;
        color: #4b5563;
        margin-bottom: 16px;
    }
    .rating {
        display: flex;
        gap: 4px;
        margin-bottom: 16px;
    }
    .material-icons.star {
        color: #c084fc;
        font-size: 22px;
    }
    .reviews-section {
        margin-top: 48px;
    }
    .reviews-section h3 {
        font-weight: 700;
        font-size: 1.25rem;
        margin-bottom: 16px;
        color: #5b21b6;
    }
    .review {
        border-top: 1px solid #e5e7eb;
        padding: 16px 0;
    }
    .review:first-child {
        border-top: none;
    }
    .review .user {
        font-weight: 600;
        font-size: 0.95rem;
        color: #6b7280;
    }
    .review .date {
        font-size: 0.75rem;
        color: #9ca3af;
    }
    .review .comment {
        margin-top: 8px;
        font-size: 1rem;
        color: #374151;
    }
    .btn-add-cart {
        background: #7c3aed;
        color: white;
        border: none;
        border-radius: 12px;
        padding: 16px;
        font-weight: 700;
        font-size: 1.15rem;
        cursor: pointer;
        user-select: none;
    }
    .btn-add-cart:hover {
        background: #a78bfa;
    }
</style>
</head>
<body>

<div class="container" role="main">
    <div class="image-gallery">
        <div class="main-image" tabindex="0" id="main-image" aria-label="Product main image. Zoom on click">
            <img src="{{ product.images[0] }}" alt="Main image of {{product.name}}" />
        </div>
        <div class="thumbnail-list" role="list" id="thumbnails" aria-label="Product gallery thumbnails">
            {% for img in product.images %}
            <img src="{{ img }}" alt="Thumbnail image for {{product.name}}" role="listitem" class="{% if loop.first %}selected{% endif %}" tabindex="0" />
            {% endfor %}
        </div>
    </div>
    <section class="product-info">
        <h1 class="product-title">{{ product.name }}</h1>
        <div class="product-price">${{ "%.2f"|format(product.price) }}</div>
        <div class="rating" aria-label="Product rating: {{ product.rating }} out of 5 stars">
            {% for i in range(1,6) %}
                <span class="material-icons star" aria-hidden="true">{% if i <= product.rating|round(0,'floor') %}star{% else %}star_border{% endif %}</span>
            {% endfor %}
        </div>
        <p class="product-desc">{{ product.description }}</p>
        <button class="btn-add-cart" id="add-cart-btn">Add to Cart</button>
        <section class="reviews-section" aria-label="Customer reviews">
            <h3>Customer Reviews</h3>
            {% if reviews %}
                {% for r in reviews %}
                <div class="review">
                    <div class="user">{{ USERS[r.userId].name }}{% if r.verified %} (Verified Buyer){% endif %}</div>
                    <div class="date">{{ r.createdAt[:10] }}</div>
                    <div class="comment">{{ r.comment }}</div>
                </div>
                {% endfor %}
            {% else %}
                <p>No reviews yet.</p>
            {% endif %}
        </section>
    </section>
</div>

<script>
(() => {
    const mainImg = document.getElementById('main-image').querySelector('img');
    const thumbnails = document.getElementById('thumbnails').querySelectorAll('img');
    const addCartBtn = document.getElementById('add-cart-btn');
    const productId = "{{ product.id }}";

    thumbnails.forEach(t => {
        t.addEventListener('click', (e) => {
            thumbnails.forEach(img => img.classList.remove('selected'));
            t.classList.add('selected');
            mainImg.src = t.src;
        });
        t.addEventListener('keydown', e => {
            if(e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                t.click();
            }
        });
    });

    // Zoom simulation on main image click
    document.getElementById('main-image').addEventListener('click', () => {
        if(mainImg.style.transform === 'scale(2)') {
            mainImg.style.transform = 'scale(1)';
            mainImg.style.cursor = 'zoom-in';
        } else {
            mainImg.style.transform = 'scale(2)';
            mainImg.style.cursor = 'zoom-out';
        }
    });

    addCartBtn.addEventListener('click', async () => {
        // Call add to cart endpoint
        const res = await fetch('/api/cart', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ productId })
        });
        if (res.ok) {
            alert('Added to cart');
        } else {
            alert('Failed to add to cart');
        }
    });
})();
</script>

</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True, port=5000)
