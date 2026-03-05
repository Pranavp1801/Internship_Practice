from fastapi import FastAPI

app = FastAPI()

# Sample product data
products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499, 'category': 'Electronics', 'in_stock': True},
    {'id': 2, 'name': 'Notebook', 'price': 99, 'category': 'Stationery', 'in_stock': True},
    {'id': 3, 'name': 'USB Hub', 'price': 799, 'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set', 'price': 49, 'category': 'Stationery', 'in_stock': True},
    {'id': 5, 'name': 'Laptop Stand', 'price': 1299, 'category': 'Electronics', 'in_stock': True}, 
    {'id': 6, 'name': 'Mechanical Keyboard', 'price': 2499, 'category': 'Electronics', 'in_stock': True},
    {'id': 7, 'name': 'Webcam', 'price': 1899, 'category': 'Electronics', 'in_stock': False},
]

# Home route
@app.get('/')
def home():
    return {'message': 'Welcome to our E-commerce API'}

# Get all products
@app.get('/products')
def get_all_products():
    return {'products': products, 'total': len(products)}

# --- Static product routes come first to avoid conflicts with dynamic route ---

# Get only in-stock products
@app.get('/products/instock')
def get_instock():
    available = [p for p in products if p["in_stock"]]
    return {
        "in_stock_products": available,
        "count": len(available)
    }

# Search products by keyword
@app.get("/products/search/{keyword}")
def search_products(keyword: str):
    results = [p for p in products if keyword.lower() in p["name"].lower()]
    if not results:
        return {"message": "No products matched your search"}
    return {
        "keyword": keyword,
        "results": results,
        "total_matches": len(results)
    }

# Get deals: cheapest and most expensive products
@app.get("/products/deals")
def get_deals():
    cheapest = min(products, key=lambda p: p["price"])
    expensive = max(products, key=lambda p: p["price"])
    return {
        "best_deal": cheapest,
        "premium_pick": expensive,
    }

# Get products by category
@app.get('/products/category/{category_name}')
def get_products_by_category(category_name: str):
    result = [p for p in products if p['category'].lower() == category_name.lower()]
    if not result:
        return {'error': 'No products found'}
    return {'category': category_name, 'products': result}

# --- Dynamic product route comes last ---
@app.get('/products/{product_id}')
def get_product(product_id: int):
    for product in products:
        if product['id'] == product_id:
            return {'product': product}
    return {'error': 'Product not found'}

# Store summary endpoint
@app.get("/store/summary")
def store_summary():
    in_stock_count = len([p for p in products if p["in_stock"]])
    out_stock_count = len(products) - in_stock_count
    categories = list(set([p["category"] for p in products]))
    return {
        "store_name": "My E-commerce Store",
        "total_products": len(products),
        "in_stock": in_stock_count,
        "out_of_stock": out_stock_count,
        "categories": categories,
    }