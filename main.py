from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.utils import platform
from database import DatabaseManager
import os

# تحميل ملفات واجهة Kivy
Builder.load_file('screens/dashboard.kv')
Builder.load_file('screens/inventory.kv')
Builder.load_file('screens/customers.kv')
Builder.load_file('screens/sales.kv')
Builder.load_file('screens/prescriptions.kv')

class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        
    def on_enter(self):
        self.update_stats()
        
    def update_stats(self):
        # تحديث الإحصائيات
        total_products = self.db.get_total_products()
        total_customers = self.db.get_total_customers()
        today_sales = self.db.get_today_sales()
        expiring_soon = self.db.get_expiring_soon()
        
        # تحديث Labels في الواجهة
        self.ids.total_products_label.text = str(total_products)
        self.ids.total_customers_label.text = str(total_customers)
        self.ids.today_sales_label.text = f"{today_sales:.2f}"
        self.ids.expiring_soon_label.text = str(expiring_soon)

class InventoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        
    def on_enter(self):
        self.load_products()
        
    def load_products(self):
        # تحميل المنتجات وعرضها
        products = self.db.get_all_products()
        self.ids.products_rv.data = [
            {
                'barcode': p['barcode'],
                'name': p['name'],
                'quantity': str(p['quantity']),
                'sale_price': f"{p['sale_price']:.2f}"
            }
            for p in products
        ]
    
    def add_product(self):
        self.manager.current = 'add_product'
        
    def delete_product(self, product_id):
        self.db.delete_product(product_id)
        self.load_products()

class CustomersScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        
    def on_enter(self):
        self.load_customers()
        
    def load_customers(self):
        customers = self.db.get_all_customers()
        self.ids.customers_rv.data = [
            {
                'id': str(c['id']),
                'name': c['name'],
                'phone': c['phone'] or '',
                'diagnosis': c['diagnosis'] or ''
            }
            for c in customers
        ]

class SalesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.cart = []
        
    def add_to_cart(self, product_id, quantity):
        # إضافة منتج إلى سلة الفاتورة
        product = self.db.get_product(product_id)
        if product and product['quantity'] >= quantity:
            self.cart.append({
                'product': product,
                'quantity': quantity,
                'total': product['sale_price'] * quantity
            })
            self.update_cart()
            
    def update_cart(self):
        total = sum(item['total'] for item in self.cart)
        self.ids.total_label.text = f"{total:.2f}"
        
    def complete_sale(self):
        if self.cart:
            invoice_number = self.db.create_sale(self.cart)
            self.cart = []
            self.update_cart()
            # إظهار رسالة نجاح

class PharmacyApp(App):
    def build(self):
        # إعداد إدارة الشاشات
        sm = ScreenManager()
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(InventoryScreen(name='inventory'))
        sm.add_widget(CustomersScreen(name='customers'))
        sm.add_widget(SalesScreen(name='sales'))
        
        # ضبط خلفية النافذة
        Window.clearcolor = (0.95, 0.95, 0.95, 1)
        
        return sm
    
    def on_pause(self):
        # التعامل مع حالة التوقف (مهم لتطبيقات Android)
        return True
        
    def on_resume(self):
        # التعامل مع حالة الاستئناف
        pass

if __name__ == '__main__':
    PharmacyApp().run()
