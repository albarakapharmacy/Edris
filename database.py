import sqlite3
from datetime import datetime, timedelta
import json
import os
from kivy.utils import platform

class DatabaseManager:
    def __init__(self):
        # تحديد مسار قاعدة البيانات بناءً على المنصة
        if platform == 'android':
            from android.storage import app_storage_path
            db_path = os.path.join(app_storage_path(), 'pharmacy.db')
        else:
            db_path = 'pharmacy.db'
            
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.create_tables()
        
    def create_tables(self):
        tables = [
            """CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT,
                name TEXT NOT NULL,
                unit TEXT,
                type TEXT,
                manufacturer TEXT,
                purchase_price REAL,
                sale_price REAL,
                quantity INTEGER,
                min_stock INTEGER DEFAULT 10,
                expiry_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            
            """CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER,
                phone TEXT,
                diagnosis TEXT,
                last_visit DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            
            """CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT UNIQUE,
                date DATE NOT NULL,
                patient_name TEXT,
                total_amount REAL,
                payment_method TEXT,
                items TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""
        ]
        
        for table in tables:
            self.cursor.execute(table)
        self.conn.commit()
    
    # دوال CRUD للمنتجات
    def add_product(self, product_data):
        query = """INSERT INTO products 
                   (barcode, name, unit, type, manufacturer, purchase_price, 
                    sale_price, quantity, min_stock, expiry_date)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        self.cursor.execute(query, product_data)
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_all_products(self):
        self.cursor.execute("SELECT * FROM products ORDER BY name")
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_product(self, product_id):
        self.cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def update_product(self, product_id, product_data):
        query = """UPDATE products SET 
                   barcode=?, name=?, unit=?, type=?, manufacturer=?,
                   purchase_price=?, sale_price=?, quantity=?, 
                   min_stock=?, expiry_date=?
                   WHERE id=?"""
        self.cursor.execute(query, (*product_data, product_id))
        self.conn.commit()
    
    def delete_product(self, product_id):
        self.cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        self.conn.commit()
    
    # دوال للتقارير والإحصائيات
    def get_total_products(self):
        self.cursor.execute("SELECT COUNT(*) FROM products")
        return self.cursor.fetchone()[0]
    
    def get_total_customers(self):
        self.cursor.execute("SELECT COUNT(*) FROM customers")
        return self.cursor.fetchone()[0]
    
    def get_today_sales(self):
        today = datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute("SELECT SUM(total_amount) FROM sales WHERE date = ?", (today,))
        result = self.cursor.fetchone()[0]
        return result or 0.0
    
    def get_expiring_soon(self, days=90):
        expiry_limit = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        self.cursor.execute("""
            SELECT COUNT(*) FROM products 
            WHERE expiry_date IS NOT NULL 
            AND expiry_date <= ? AND expiry_date >= ?
        """, (expiry_limit, datetime.now().strftime('%Y-%m-%d')))
        return self.cursor.fetchone()[0]
    
    def create_sale(self, cart_items):
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        total_amount = sum(item['total'] for item in cart_items)
        
        # تحويل عناصر السلة إلى JSON
        items_json = json.dumps([
            {
                'product_id': item['product']['id'],
                'name': item['product']['name'],
                'quantity': item['quantity'],
                'price': item['product']['sale_price'],
                'total': item['total']
            }
            for item in cart_items
        ], ensure_ascii=False)
        
        query = """INSERT INTO sales 
                   (invoice_number, date, total_amount, items)
                   VALUES (?, ?, ?, ?)"""
        self.cursor.execute(query, (
            invoice_number,
            datetime.now().strftime('%Y-%m-%d'),
            total_amount,
            items_json
        ))
        self.conn.commit()
        
        # تحديث كميات المنتجات
        for item in cart_items:
            self.cursor.execute(
                "UPDATE products SET quantity = quantity - ? WHERE id = ?",
                (item['quantity'], item['product']['id'])
            )
        
        self.conn.commit()
        return invoice_number
