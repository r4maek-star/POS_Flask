#!/usr/bin/env python3
"""
Simple Data 30 Experiment - Database Population Script
This script populates the POS database with 30 sample products for testing.
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Flask app and database models
from app import app, db
from app import Product, Category, Branch, Inventory

def create_sample_data():
    """Create 30 sample products with categories and inventory"""

    with app.app_context():
        print("Creating sample data for POS system...")

        # Create sample categories if they don't exist
        categories_data = [
            {"name": "Electronics", "description": "Electronic devices and accessories"},
            {"name": "Clothing", "description": "Clothing and fashion items"},
            {"name": "Food", "description": "Food and beverages"},
            {"name": "Books", "description": "Books and educational materials"},
            {"name": "Home", "description": "Home and garden items"},
            {"name": "Sports", "description": "Sports and fitness equipment"}
        ]

        categories = []
        for cat_data in categories_data:
            category = Category.query.filter_by(name=cat_data["name"]).first()
            if not category:
                category = Category(
                    name=cat_data["name"],
                    description=cat_data["description"]
                )
                db.session.add(category)
                print(f"Created category: {cat_data['name']}")
            categories.append(category)

        # Create sample branch if it doesn't exist
        branch = Branch.query.filter_by(name="Main Branch").first()
        if not branch:
            branch = Branch(name="Main Branch", address="123 Main Street")
            db.session.add(branch)
            print("Created branch: Main Branch")

        db.session.commit()

        # Sample product data with barcodes
        products_data = [
            # Electronics (Category 1)
            {"name": "Wireless Mouse", "sku": "WM001", "price": 25.99, "cost_price": 15.50, "category": categories[0], "barcodes": ["123456789012", "987654321098"]},
            {"name": "USB Keyboard", "sku": "KB001", "price": 45.99, "cost_price": 25.00, "category": categories[0], "barcodes": ["111111111111", "222222222222"]},
            {"name": "Bluetooth Headphones", "sku": "HP001", "price": 89.99, "cost_price": 50.00, "category": categories[0], "barcodes": ["333333333333", "444444444444"]},
            {"name": "Smartphone Charger", "sku": "CH001", "price": 19.99, "cost_price": 10.00, "category": categories[0], "barcodes": ["555555555555"]},
            {"name": "Wireless Router", "sku": "RT001", "price": 79.99, "cost_price": 45.00, "category": categories[0], "barcodes": ["666666666666", "777777777777"]},

            # Clothing (Category 2)
            {"name": "Cotton T-Shirt", "sku": "TS001", "price": 15.99, "cost_price": 8.00, "category": categories[1], "barcodes": ["100000000001", "100000000002"]},
            {"name": "Denim Jeans", "sku": "JN001", "price": 59.99, "cost_price": 30.00, "category": categories[1], "barcodes": ["100000000003"]},
            {"name": "Winter Jacket", "sku": "JK001", "price": 89.99, "cost_price": 50.00, "category": categories[1], "barcodes": ["100000000004", "100000000005"]},
            {"name": "Running Shoes", "sku": "SH001", "price": 79.99, "cost_price": 40.00, "category": categories[1], "barcodes": ["100000000006"]},
            {"name": "Baseball Cap", "sku": "CP001", "price": 12.99, "cost_price": 6.00, "category": categories[1], "barcodes": ["100000000007", "100000000008"]},

            # Food (Category 3)
            {"name": "Organic Apples", "sku": "AP001", "price": 3.99, "cost_price": 2.00, "category": categories[2], "barcodes": ["200000000001"]},
            {"name": "Whole Milk", "sku": "MK001", "price": 2.49, "cost_price": 1.50, "category": categories[2], "barcodes": ["200000000002", "200000000003"]},
            {"name": "Bread Loaf", "sku": "BR001", "price": 2.99, "cost_price": 1.20, "category": categories[2], "barcodes": ["200000000004"]},
            {"name": "Coffee Beans", "sku": "CF001", "price": 12.99, "cost_price": 8.00, "category": categories[2], "barcodes": ["200000000005", "200000000006"]},
            {"name": "Chocolate Bar", "sku": "CH002", "price": 1.99, "cost_price": 1.00, "category": categories[2], "barcodes": ["200000000007"]},

            # Books (Category 4)
            {"name": "Python Programming", "sku": "BK001", "price": 39.99, "cost_price": 25.00, "category": categories[3], "barcodes": ["300000000001", "300000000002"]},
            {"name": "Data Science Handbook", "sku": "BK002", "price": 49.99, "cost_price": 30.00, "category": categories[3], "barcodes": ["300000000003"]},
            {"name": "Web Development Guide", "sku": "BK003", "price": 34.99, "cost_price": 20.00, "category": categories[3], "barcodes": ["300000000004", "300000000005"]},
            {"name": "Database Design", "sku": "BK004", "price": 44.99, "cost_price": 28.00, "category": categories[3], "barcodes": ["300000000006"]},
            {"name": "AI Fundamentals", "sku": "BK005", "price": 54.99, "cost_price": 35.00, "category": categories[3], "barcodes": ["300000000007", "300000000008"]},

            # Home (Category 5)
            {"name": "Coffee Mug", "sku": "MG001", "price": 8.99, "cost_price": 4.00, "category": categories[4], "barcodes": ["400000000001"]},
            {"name": "Throw Pillow", "sku": "PL001", "price": 19.99, "cost_price": 10.00, "category": categories[4], "barcodes": ["400000000002", "400000000003"]},
            {"name": "Desk Lamp", "sku": "LP001", "price": 29.99, "cost_price": 15.00, "category": categories[4], "barcodes": ["400000000004"]},
            {"name": "Wall Clock", "sku": "CL001", "price": 24.99, "cost_price": 12.00, "category": categories[4], "barcodes": ["400000000005", "400000000006"]},
            {"name": "Picture Frame", "sku": "FR001", "price": 14.99, "cost_price": 7.00, "category": categories[4], "barcodes": ["400000000007"]},

            # Sports (Category 6)
            {"name": "Yoga Mat", "sku": "YM001", "price": 34.99, "cost_price": 20.00, "category": categories[5], "barcodes": ["500000000001", "500000000002"]},
            {"name": "Dumbbells Set", "sku": "DB001", "price": 49.99, "cost_price": 30.00, "category": categories[5], "barcodes": ["500000000003"]},
            {"name": "Basketball", "sku": "BB001", "price": 24.99, "cost_price": 15.00, "category": categories[5], "barcodes": ["500000000004", "500000000005"]},
            {"name": "Tennis Racket", "sku": "TR001", "price": 79.99, "cost_price": 45.00, "category": categories[5], "barcodes": ["500000000006"]},
            {"name": "Swimming Goggles", "sku": "SG001", "price": 12.99, "cost_price": 6.00, "category": categories[5], "barcodes": ["500000000007", "500000000008"]}
        ]

        # Create products first
        created_count = 0
        created_products = []

        for product_data in products_data:
            # Check if product already exists
            existing_product = Product.query.filter_by(sku=product_data["sku"]).first()
            if existing_product:
                print(f"Product {product_data['sku']} already exists, skipping...")
                continue

            # Create new product
            product = Product(
                name=product_data["name"],
                sku=product_data["sku"],
                price=product_data["price"],
                cost_price=product_data["cost_price"],
                category_id=product_data["category"].id,
                min_stock=5,
                max_stock=100
            )

            # Set barcodes if provided
            if "barcodes" in product_data and product_data["barcodes"]:
                product.barcode_list = product_data["barcodes"]

            db.session.add(product)
            created_products.append(product)
            created_count += 1
            print(f"Created product: {product_data['name']} (SKU: {product_data['sku']}) - Barcodes: {product_data.get('barcodes', [])}")

        # Commit products first to get IDs
        db.session.commit()

        # Now create inventory for each created product
        for product in created_products:
            inventory = Inventory(
                product_id=product.id,
                branch_id=branch.id,
                quantity=10  # Default quantity
            )
            db.session.add(inventory)
            print(f"Created inventory for: {product.name}")

        # Final commit
        db.session.commit()

        print(f"\n[SUCCESS] Successfully created {created_count} sample products!")
        print("[INFO] Database now contains test data for:")
        print("   - 6 Categories")
        print("   - 30 Products (5 per category)")
        print("   - Inventory records for each product")
        print("\n[READY] You can now test the POS system with realistic data!")

if __name__ == "__main__":
    create_sample_data()