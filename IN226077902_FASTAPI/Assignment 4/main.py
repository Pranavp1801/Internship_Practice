from fastapi import FastAPI, Query, HTTPException, Response, status
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

# ==========================================================
# SAMPLE DATA
# ==========================================================

products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499, 'category': 'Electronics', 'in_stock': True},
    {'id': 2, 'name': 'Notebook', 'price': 99, 'category': 'Stationery', 'in_stock': True},
    {'id': 3, 'name': 'USB Hub', 'price': 799, 'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set', 'price': 49, 'category': 'Stationery', 'in_stock': True},
    {'id': 5, 'name': 'Laptop Stand', 'price': 1299, 'category': 'Electronics', 'in_stock': True},
    {'id': 6, 'name': 'Mechanical Keyboard', 'price': 2499, 'category': 'Electronics', 'in_stock': True},
    {'id': 7, 'name': 'Webcam', 'price': 1899, 'category': 'Electronics', 'in_stock': False},
]

feedback = []
orders = []
cart = []

order_counter = 1

# ==========================================================
# PYDANTIC MODELS
# ==========================================================

class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)


class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=50)


class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem] = Field(..., min_items=1)


class NewProduct(BaseModel):
    name: str = Field(..., min_length=2)
    price: int = Field(..., gt=0)
    category: str = Field(..., min_length=2)
    in_stock: bool = True


class CheckoutRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    delivery_address: str = Field(..., min_length=10)


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def find_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product
    return None


def calculate_total(price, quantity):
    return price * quantity


# ==========================================================
# HOME
# ==========================================================

@app.get("/")
def home():
    """API welcome endpoint"""
    return {"message": "Welcome to our E-commerce API"}


# ==========================================================
# PRODUCT READ ENDPOINTS
# ==========================================================

@app.get("/products")
def get_all_products():
    """Return all products"""
    return {"products": products, "total": len(products)}


@app.get("/products/filter")
def filter_products(
    category: str = Query(None),
    max_price: int = Query(None),
    min_price: int = Query(None)
):
    """Filter products by category or price range"""

    result = products

    if category:
        result = [p for p in result if p["category"].lower() == category.lower()]

    if max_price:
        result = [p for p in result if p["price"] <= max_price]

    if min_price:
        result = [p for p in result if p["price"] >= min_price]

    return {"products": result, "count": len(result)}


@app.get("/products/instock")
def get_instock():
    """Return products currently in stock"""
    available = [p for p in products if p["in_stock"]]

    return {
        "in_stock_products": available,
        "count": len(available)
    }


@app.get("/products/search/{keyword}")
def search_products(keyword: str):
    """Search products by keyword"""

    results = [p for p in products if keyword.lower() in p["name"].lower()]

    if not results:
        return {"message": "No products matched your search"}

    return {
        "keyword": keyword,
        "results": results,
        "total_matches": len(results)
    }


@app.get("/products/deals")
def get_deals():
    """Return cheapest and most expensive product"""

    cheapest = min(products, key=lambda p: p["price"])
    expensive = max(products, key=lambda p: p["price"])

    return {
        "best_deal": cheapest,
        "premium_pick": expensive,
    }


@app.get("/products/category/{category_name}")
def get_products_by_category(category_name: str):
    """Get products from specific category"""

    result = [p for p in products if p["category"].lower() == category_name.lower()]

    if not result:
        return {"error": "No products found"}

    return {"category": category_name, "products": result}


@app.get("/products/summary")
def product_summary():
    """Return product statistics"""

    in_stock = [p for p in products if p["in_stock"]]
    out_stock = [p for p in products if not p["in_stock"]]

    expensive = max(products, key=lambda p: p["price"])
    cheapest = min(products, key=lambda p: p["price"])

    categories = list(set(p["category"] for p in products))

    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock),
        "out_of_stock_count": len(out_stock),
        "most_expensive": expensive,
        "cheapest": cheapest,
        "categories": categories
    }


# ==========================================================
# PRODUCT CRUD
# ==========================================================

@app.post("/products", status_code=201)
def add_product(product: NewProduct):
    """Add new product"""

    for p in products:
        if p["name"].lower() == product.name.lower():
            raise HTTPException(
                status_code=400,
                detail="Product with this name already exists"
            )

    new_id = max(p["id"] for p in products) + 1

    new_product = {
        "id": new_id,
        "name": product.name,
        "price": product.price,
        "category": product.category,
        "in_stock": product.in_stock
    }

    products.append(new_product)

    return {"message": "Product added", "product": new_product}


@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    price: Optional[int] = None,
    in_stock: Optional[bool] = None
):
    """Update product price or stock"""

    product = find_product(product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if price is not None:
        product["price"] = price

    if in_stock is not None:
        product["in_stock"] = in_stock

    return {"message": "Product updated", "product": product}


@app.delete("/products/{product_id}")
def delete_product(product_id: int, response: Response):
    """Delete product"""

    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    products.remove(product)

    return {"message": f"Product '{product['name']}' deleted"}


# ==========================================================
# CART SYSTEM
# ==========================================================

@app.post("/cart/add")
def add_to_cart(
    product_id: int = Query(...),
    quantity: int = Query(1)
):

    product = next((p for p in products if p["id"] == product_id), None)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not product["in_stock"]:
        raise HTTPException(status_code=400, detail=f"{product['name']} is out of stock")

    for item in cart:
        if item["product_id"] == product_id:

            item["quantity"] += quantity
            item["subtotal"] = item["quantity"] * item["unit_price"]

            return {
                "message": "Cart updated",
                "cart_item": item
            }

    cart_item = {
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": product["price"] * quantity
    }

    cart.append(cart_item)

    return {
        "message": "Added to cart",
        "cart_item": cart_item
    }


@app.get("/cart")
def view_cart():
    """View cart contents"""

    if not cart:
        return {"message": "Cart is empty", "items": [], "grand_total": 0}

    grand_total = sum(item["subtotal"] for item in cart)

    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": grand_total
    }


@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):
    """Remove product from cart"""

    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)
            return {"message": f"{item['product_name']} removed from cart"}

    raise HTTPException(status_code=404, detail="Product not in cart")


@app.post("/cart/checkout")
def checkout(checkout_data: CheckoutRequest):
    """Checkout cart and create orders"""

    global order_counter

    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")

    placed_orders = []
    grand_total = 0

    for item in cart:

        order = {
            "order_id": order_counter,
            "customer_name": checkout_data.customer_name,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "delivery_address": checkout_data.delivery_address,
            "total_price": item["subtotal"],
            "status": "confirmed"
        }

        orders.append(order)
        placed_orders.append(order)

        grand_total += item["subtotal"]
        order_counter += 1

    cart.clear()

    return {
        "message": "Checkout successful",
        "orders": placed_orders,
        "grand_total": grand_total
    }


# ==========================================================
# FEEDBACK SYSTEM
# ==========================================================

@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):
    """Submit product feedback"""

    feedback.append(data.dict())

    return {
        "message": "Feedback submitted",
        "feedback": data.dict(),
        "total_feedback": len(feedback)
    }


# ==========================================================
# BULK ORDER SYSTEM
# ==========================================================

@app.get("/orders")
def get_orders():

    return {
        "orders": orders,
        "total_orders": len(orders)
    }

@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):
    """Place bulk order for multiple products"""

    global order_counter

    confirmed = []
    failed = []
    grand_total = 0

    for item in order.items:

        product = find_product(item.product_id)

        if not product:
            failed.append({"product_id": item.product_id, "reason": "Product not found"})

        elif not product["in_stock"]:
            failed.append({"product_id": item.product_id, "reason": "Out of stock"})

        else:
            subtotal = product["price"] * item.quantity
            grand_total += subtotal

            confirmed.append({
                "product": product["name"],
                "qty": item.quantity,
                "subtotal": subtotal
            })

    new_order = {
        "order_id": order_counter,
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total,
        "status": "pending"
    }

    orders.append(new_order)
    order_counter += 1

    return {"message": "Order placed", "order": new_order}


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    """Get order by ID"""

    for order in orders:
        if order["order_id"] == order_id:
            return {"order": order}

    return {"error": "Order not found"}


@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):
    """Confirm order"""

    for order in orders:
        if order["order_id"] == order_id:

            order["status"] = "confirmed"

            return {"message": "Order confirmed", "order": order}

    return {"error": "Order not found"}


# ==========================================================
# STORE SUMMARY
# ==========================================================

@app.get("/store/summary")
def store_summary():
    """Return overall store statistics"""

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


# ==========================================================
# DYNAMIC PRODUCT ROUTE (MUST BE LAST)
# ==========================================================

@app.get('/products/{product_id}')
def get_product(product_id: int):
    """Get product by ID"""

    product = find_product(product_id)

    if not product:
        return {"error": "Product not found"}

    return {"product": product}