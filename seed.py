from faker import Faker
import random
from app.db.db import get_connection
from datetime import datetime

fake = Faker()

# Structured data for products
PRODUCTS_DATA = [
    {"name": "Milk", "brand": "Amul", "category": "Dairy Products", "sizes": ["500ml", "1L", "2L"]},
    {"name": "Paneer", "brand": "Mother Dairy", "category": "Dairy Products", "sizes": ["200g", "500g"]},
    {"name": "Basmati Rice", "brand": "Tata", "category": "Cereals", "sizes": ["1kg", "5kg"]},
    {"name": "Tomato", "brand": "Local", "category": "Vegetables", "sizes": ["500g", "1kg"]},
    {"name": "Banana", "brand": "Local", "category": "Fruits", "sizes": ["500g", "1kg"]},
    {"name": "Chips", "brand": "Parle", "category": "Snacks", "sizes": ["100g", "250g"]},
    {"name": "Soft Drink", "brand": "Coca-Cola", "category": "Beverages", "sizes": ["500ml", "1L"]},
    {"name": "Shampoo", "brand": "Dabur", "category": "Personal Care", "sizes": ["200ml", "500ml"]},
    {"name": "Frozen Peas", "brand": "Haldiram's", "category": "Frozen Foods", "sizes": ["500g", "1kg"]},
    {"name": "Cookies", "brand": "Britannia", "category": "Bakery", "sizes": ["200g", "400g"]},
]

BRANDS = list({product['brand'] for product in PRODUCTS_DATA})
CATEGORIES = list({product['category'] for product in PRODUCTS_DATA})

def insert_brands(cursor):
    brand_ids = {}
    for brand in BRANDS:
        cursor.execute("INSERT INTO BrandsTbl (BrandName) VALUES (%s)", (brand,))
        brand_ids[brand] = cursor.lastrowid
    return brand_ids

def insert_categories(cursor):
    category_ids = {}
    for category in CATEGORIES:
        cursor.execute("INSERT INTO CategoriesTbl (CategoryName) VALUES (%s)", (category,))
        category_ids[category] = cursor.lastrowid
    return category_ids

def insert_products(cursor, brand_ids, category_ids):
    product_ids = []
    for product in PRODUCTS_DATA:
        name = product['name']
        price = round(random.uniform(20, 500), 2)
        selling_price = round(price * random.uniform(0.9, 0.98), 2)
        stock = random.randint(50, 200)
        details = f"Fresh and high-quality {name}."
        description = f"{name} is perfect for your daily needs, sourced with care."
        highlight1 = random.choice(["Organic", "Fresh", "Premium Quality"])
        highlight2 = random.choice(["Hygienically Packed", "No Preservatives", "Best in Market"])

        cursor.execute("""
            INSERT INTO ProductDataTbl (
                ProductName, ProductPrice, ProductSellingPrice, ProductStock,
                ProductDetails, ProductDescription, ProductHighlight1, ProductHighlight2,
                `30DaysReturn`, FreeDelivery, CashOnDelivery,
                BrandId, CategoryId
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            name, price, selling_price, stock,
            details, description, highlight1, highlight2,
            1, 1, 1,
            brand_ids[product['brand']], category_ids[product['category']]
        ))

        product_ids.append(cursor.lastrowid)
    return product_ids

def insert_users(cursor):
    users = []
    for _ in range(10):
        username = fake.unique.user_name()
        email = fake.unique.email()
        password = "hashed_password"
        cursor.execute("""
            INSERT INTO UserDataTbl (UserName, Password, ConfirmPassword, UserType, Email)
            VALUES (%s, %s, %s, %s, %s)
        """, (username, password, password, "Customer", email))
        users.append({"username": username, "email": email})
    return users

def insert_feedback(cursor, users):
    for user in users:
        cursor.execute("""
            INSERT INTO FeedbackTbl (name, email, message)
            VALUES (%s, %s, %s)
        """, (
            user['username'], user['email'], fake.sentence(nb_words=10)
        ))

def insert_cart(cursor, users, product_ids):
    cart_entries = []
    for _ in range(50):
        user = random.choice(users)
        product_id = random.choice(product_ids)
        size = random.choice(PRODUCTS_DATA[product_id % len(PRODUCTS_DATA)]['sizes'])
        datetime_added = fake.date_time_this_year()

        cursor.execute("""
            INSERT INTO UserCartTbl (ProductId, DateTime, Size, UserName)
            VALUES (%s, %s, %s, %s)
        """, (
            product_id, datetime_added, size, user['username']
        ))

        cart_entries.append({"product_id": product_id, "username": user['username'], "size": size, "datetime": datetime_added})
    return cart_entries

def insert_delivery(cursor, cart_entries):
    for cart in random.sample(cart_entries, k=40):
        cursor.execute("""
            INSERT INTO ProductDeliveryTbl (
                ProductId, DateTime, UserName, CustomerAddress, CustomerPinCode,
                CustomerMoNo, CustomerName, PaymentMode, Size
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            cart['product_id'], cart['datetime'], cart['username'], fake.address(),
            fake.postcode(), fake.phone_number(), fake.name(), random.choice(["COD", "Online"]), cart['size']
        ))

def insert_user_activity(cursor, users, product_ids):
    activity_types = ["view", "add_to_cart", "purchase"]
    for _ in range(100):
        user = random.choice(users)
        product_id = random.choice(product_ids)
        activity_type = random.choice(activity_types)
        quantity = random.randint(1, 5) if activity_type == "purchase" else None
        amount_spent = round(random.uniform(20, 500), 2) if activity_type == "purchase" else None

        cursor.execute("""
            INSERT INTO UserActivityTbl (
                UserId, ProductId, ActivityType, ActivityDate, Quantity, AmountSpent
            ) VALUES (
                (SELECT UserId FROM UserDataTbl WHERE UserName = %s LIMIT 1),
                %s, %s, %s, %s, %s
            )
        """, (
            user['username'], product_id, activity_type, fake.date_time_this_year(), quantity, amount_spent
        ))

def main():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        brand_ids = insert_brands(cursor)
        category_ids = insert_categories(cursor)
        product_ids = insert_products(cursor, brand_ids, category_ids)
        users = insert_users(cursor)
        
        insert_feedback(cursor, users)
        cart_entries = insert_cart(cursor, users, product_ids)
        insert_delivery(cursor, cart_entries)
        insert_user_activity(cursor, users, product_ids)

        conn.commit()
        print("✅ Grocery shop realistic data inserted successfully!")
    except Exception as e:
        print("❌ Error inserting data:", e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
