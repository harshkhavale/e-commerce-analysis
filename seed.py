from faker import Faker
import random
from app.db.db import get_connection
from datetime import datetime

fake = Faker()

def insert_brands(cursor):
    brands = ["Amul", "Nestle", "Britannia", "Dabur", "Patanjali", "Mother Dairy", "Parle", "Tata", "Haldiram's", "Catch"]
    for brand in brands:
        cursor.execute("INSERT INTO BrandsTbl (BrandName) VALUES (%s)", (brand,))

def insert_categories(cursor):
    categories = ["Fruits", "Vegetables", "Dairy Products", "Snacks", "Beverages", "Bakery", "Cereals", "Personal Care", "Household", "Frozen Foods"]
    for category in categories:
        cursor.execute("INSERT INTO CategoriesTbl (CategoryName) VALUES (%s)", (category,))

def insert_products(cursor):
    product_names = [
        "Banana", "Apple", "Tomato", "Onion", "Milk", "Paneer", "Bread", "Chips", "Soft Drink", "Basmati Rice",
        "Toothpaste", "Shampoo", "Frozen Peas", "Yogurt", "Cookies", "Cooking Oil", "Masala Powder", "Ice Cream", "Energy Drink", "Salt Pack"
    ]
    for i in range(100):
        name = f"{random.choice(product_names)} - {random.choice(['500g', '1kg', '2L', '1L', '250g'])}"
        price = round(random.uniform(20, 500), 2)
        selling_price = round(price * random.uniform(0.9, 0.98), 2)
        stock = random.randint(50, 500)
        details = f"High quality {name} sourced fresh and hygienically packed."
        description = f"Enjoy the rich taste and nutrition of {name}. Perfect for your daily needs."
        highlights = ["Fresh", "Organic", "Premium Quality", "Hygienically Packed", "No Preservatives"]
        
        cursor.execute("""
            INSERT INTO ProductDataTbl (
                ProductName, ProductPrice, ProductSellingPrice, ProductStock,
                ProductDetails, ProductDescription, ProductHighlight1, ProductHighlight2,
                `30DaysReturn`, FreeDelivery, CashOnDelivery,
                BrandId, CategoryId
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            name, price, selling_price, stock,
            details, description, random.choice(highlights), random.choice(highlights),
            1, 1, 1,
            random.randint(1, 10), random.randint(1, 10)
        ))

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
        users.append(username)
    return users

def get_user_map(cursor, usernames):
    user_map = {}
    cursor.execute("SELECT UserId, UserName FROM UserDataTbl")
    for uid, uname in cursor.fetchall():
        if uname in usernames:
            user_map[uname] = uid
    return user_map

def insert_cart(cursor, users):
    for _ in range(100):
        username = random.choice(users)
        cursor.execute("""
            INSERT INTO UserCartTbl (ProductId, DateTime, Size, UserName)
            VALUES (%s, %s, %s, %s)
        """, (
            random.randint(1, 100), fake.date_time_this_year(), None, username
        ))

def insert_delivery(cursor, users):
    for _ in range(100):
        username = random.choice(users)
        cursor.execute("""
            INSERT INTO ProductDeliveryTbl (
                ProductId, DateTime, UserName, CustomerAddress, CustomerPinCode,
                CustomerMoNo, CustomerName, PaymentMode, Size
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            random.randint(1, 100), fake.date_time_this_year(), username, fake.address(),
            fake.postcode(), fake.phone_number(), fake.name(), random.choice(["COD", "Online"]), None
        ))

def insert_feedback(cursor):
    for _ in range(100):
        cursor.execute("""
            INSERT INTO FeedbackTbl (name, email, message)
            VALUES (%s, %s, %s)
        """, (
            fake.name(), fake.email(), fake.sentence(nb_words=12)
        ))

def insert_user_activity(cursor, user_map):
    product_ids = list(range(1, 101))
    activity_types = ["view", "add_to_cart", "purchase"]

    for _ in range(100):
        username = random.choice(list(user_map.keys()))
        user_id = user_map[username]
        product_id = random.choice(product_ids)
        activity_type = random.choice(activity_types)
        quantity = random.randint(1, 5) if activity_type == "purchase" else None
        amount_spent = round(random.uniform(20, 500), 2) if activity_type == "purchase" else None

        cursor.execute("""
            INSERT INTO UserActivityTbl (
                UserId, ProductId, ActivityType, ActivityDate, Quantity, AmountSpent
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            user_id, product_id, activity_type, fake.date_time_this_year(), quantity, amount_spent
        ))

def main():
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        insert_brands(cursor)
        insert_categories(cursor)
        insert_products(cursor)
        users = insert_users(cursor)
        user_map = get_user_map(cursor, users)

        insert_cart(cursor, users)
        insert_delivery(cursor, users)
        insert_feedback(cursor)
        insert_user_activity(cursor, user_map)

        conn.commit()
        print("✅ Grocery shop data inserted successfully!")
    except Exception as e:
        print("❌ Error inserting data:", e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
