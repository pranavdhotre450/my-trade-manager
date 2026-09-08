"""
Product/Inventory management module
"""

from datetime import datetime
from src.database import DatabaseManager

class ProductManager:
    def __init__(self):
        self.db = DatabaseManager()
    
    def create_product(self, company_id, name, unit='Piece', **kwargs):
        """Create a new product"""
        try:
            query = '''
                INSERT INTO products 
                (company_id, name, description, sku, unit, hsn_code, gst_rate,
                 purchase_price, selling_price, stock_quantity, min_stock_level, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            params = (
                company_id, name, kwargs.get('description'), kwargs.get('sku'),
                unit, kwargs.get('hsn_code'), kwargs.get('gst_rate', 0),
                kwargs.get('purchase_price', 0), kwargs.get('selling_price', 0),
                kwargs.get('stock_quantity', 0), kwargs.get('min_stock_level', 0),
                datetime.now(), datetime.now()
            )
            
            cursor = self.db.execute_query(query, params)
            return True, cursor.lastrowid, "Product created successfully"
        except Exception as e:
            return False, None, f"Failed to create product: {str(e)}"
    
    def get_product(self, product_id):
        """Get product details"""
        try:
            query = 'SELECT * FROM products WHERE id = ?'
            product = self.db.fetch_one(query, (product_id,))
            return product
        except Exception as e:
            return None
    
    def get_company_products(self, company_id):
        """Get all products for a company"""
        try:
            query = 'SELECT * FROM products WHERE company_id = ? ORDER BY name'
            products = self.db.fetch_all(query, (company_id,))
            return products
        except Exception as e:
            return []
    
    def update_product(self, product_id, **kwargs):
        """Update product details"""
        try:
            updates = []
            params = []
            
            fields = ['name', 'description', 'sku', 'unit', 'hsn_code', 'gst_rate',
                     'purchase_price', 'selling_price', 'stock_quantity', 'min_stock_level']
            
            for field in fields:
                if field in kwargs:
                    updates.append(f'{field} = ?')
                    params.append(kwargs[field])
            
            if not updates:
                return False, "No fields to update"
            
            updates.append('updated_at = ?')
            params.append(datetime.now())
            params.append(product_id)
            
            query = f'UPDATE products SET {", ".join(updates)} WHERE id = ?'
            self.db.execute_query(query, params)
            
            return True, "Product updated successfully"
        except Exception as e:
            return False, f"Update failed: {str(e)}"
    
    def delete_product(self, product_id):
        """Delete a product"""
        try:
            query = 'DELETE FROM products WHERE id = ?'
            self.db.execute_query(query, (product_id,))
            return True, "Product deleted successfully"
        except Exception as e:
            return False, f"Delete failed: {str(e)}"
    
    def record_inventory_transaction(self, company_id, product_id, trans_type, quantity, **kwargs):
        """Record inventory transaction (In/Out/Adjustment)"""
        try:
            # Update product stock
            product = self.get_product(product_id)
            if not product:
                return False, "Product not found"
            
            new_stock = product['stock_quantity']
            if trans_type == 'In':
                new_stock += quantity
            elif trans_type == 'Out':
                new_stock -= quantity
            elif trans_type == 'Adjustment':
                new_stock = quantity
            
            # Update product stock
            update_query = 'UPDATE products SET stock_quantity = ? WHERE id = ?'
            self.db.execute_query(update_query, (new_stock, product_id))
            
            # Record transaction
            trans_query = '''
                INSERT INTO inventory_transactions
                (company_id, product_id, transaction_type, quantity, 
                 reference_id, reference_type, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            params = (
                company_id, product_id, trans_type, quantity,
                kwargs.get('reference_id'), kwargs.get('reference_type'),
                kwargs.get('notes'), datetime.now()
            )
            
            self.db.execute_query(trans_query, params)
            
            return True, "Inventory transaction recorded"
        except Exception as e:
            return False, f"Transaction failed: {str(e)}"
    
    def get_low_stock_products(self, company_id):
        """Get products below minimum stock level"""
        try:
            query = '''
                SELECT * FROM products 
                WHERE company_id = ? AND stock_quantity <= min_stock_level
                ORDER BY stock_quantity
            '''
            products = self.db.fetch_all(query, (company_id,))
            return products
        except Exception as e:
            return []
    
    def close(self):
        """Close database connection"""
        self.db.close()
