"""
Invoice management module for Sales and Purchase invoices
"""

from datetime import datetime
from src.database import DatabaseManager

class InvoiceManager:
    def __init__(self):
        self.db = DatabaseManager()
    
    def create_sales_invoice(self, company_id, party_id, invoice_date, **kwargs):
        """Create a new sales invoice"""
        try:
            # Generate invoice number
            invoice_number = self._generate_invoice_number(company_id, 'sales')
            
            query = '''
                INSERT INTO sales_invoices 
                (company_id, invoice_number, party_id, invoice_date, due_date,
                 subtotal, tax_amount, discount, total, status, notes, template_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            params = (
                company_id, invoice_number, party_id, invoice_date, 
                kwargs.get('due_date'), kwargs.get('subtotal', 0),
                kwargs.get('tax_amount', 0), kwargs.get('discount', 0),
                kwargs.get('total', 0), kwargs.get('status', 'Draft'),
                kwargs.get('notes'), kwargs.get('template_id'),
                datetime.now(), datetime.now()
            )
            
            cursor = self.db.execute_query(query, params)
            return True, cursor.lastrowid, invoice_number
        except Exception as e:
            return False, None, f"Failed to create sales invoice: {str(e)}"
    
    def create_purchase_invoice(self, company_id, party_id, invoice_date, **kwargs):
        """Create a new purchase invoice"""
        try:
            # Generate invoice number
            invoice_number = self._generate_invoice_number(company_id, 'purchase')
            
            query = '''
                INSERT INTO purchase_invoices 
                (company_id, invoice_number, party_id, invoice_date, due_date,
                 subtotal, tax_amount, discount, total, status, notes, template_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            params = (
                company_id, invoice_number, party_id, invoice_date,
                kwargs.get('due_date'), kwargs.get('subtotal', 0),
                kwargs.get('tax_amount', 0), kwargs.get('discount', 0),
                kwargs.get('total', 0), kwargs.get('status', 'Draft'),
                kwargs.get('notes'), kwargs.get('template_id'),
                datetime.now(), datetime.now()
            )
            
            cursor = self.db.execute_query(query, params)
            return True, cursor.lastrowid, invoice_number
        except Exception as e:
            return False, None, f"Failed to create purchase invoice: {str(e)}"
    
    def add_invoice_item(self, invoice_id, invoice_type, product_id=None, description=None, 
                        quantity=0, unit_price=0, tax_rate=0):
        """Add item to invoice"""
        try:
            line_total = quantity * unit_price
            tax_amount = line_total * (tax_rate / 100)
            
            if invoice_type == 'sales':
                query = '''
                    INSERT INTO sales_invoice_items
                    (invoice_id, product_id, description, quantity, unit_price, tax_rate, line_total)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                '''
            else:
                query = '''
                    INSERT INTO purchase_invoice_items
                    (invoice_id, product_id, description, quantity, unit_price, tax_rate, line_total)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                '''
            
            params = (invoice_id, product_id, description, quantity, unit_price, tax_rate, line_total)
            cursor = self.db.execute_query(query, params)
            
            return True, cursor.lastrowid, line_total
        except Exception as e:
            return False, None, f"Failed to add item: {str(e)}"
    
    def get_sales_invoice(self, invoice_id):
        """Get sales invoice details"""
        try:
            query = 'SELECT * FROM sales_invoices WHERE id = ?'
            invoice = self.db.fetch_one(query, (invoice_id,))
            return invoice
        except Exception as e:
            return None
    
    def get_purchase_invoice(self, invoice_id):
        """Get purchase invoice details"""
        try:
            query = 'SELECT * FROM purchase_invoices WHERE id = ?'
            invoice = self.db.fetch_one(query, (invoice_id,))
            return invoice
        except Exception as e:
            return None
    
    def get_company_sales_invoices(self, company_id, status=None):
        """Get all sales invoices for a company"""
        try:
            if status:
                query = '''
                    SELECT * FROM sales_invoices 
                    WHERE company_id = ? AND status = ?
                    ORDER BY invoice_date DESC
                '''
                invoices = self.db.fetch_all(query, (company_id, status))
            else:
                query = '''
                    SELECT * FROM sales_invoices 
                    WHERE company_id = ?
                    ORDER BY invoice_date DESC
                '''
                invoices = self.db.fetch_all(query, (company_id,))
            return invoices
        except Exception as e:
            return []
    
    def get_company_purchase_invoices(self, company_id, status=None):
        """Get all purchase invoices for a company"""
        try:
            if status:
                query = '''
                    SELECT * FROM purchase_invoices 
                    WHERE company_id = ? AND status = ?
                    ORDER BY invoice_date DESC
                '''
                invoices = self.db.fetch_all(query, (company_id, status))
            else:
                query = '''
                    SELECT * FROM purchase_invoices 
                    WHERE company_id = ?
                    ORDER BY invoice_date DESC
                '''
                invoices = self.db.fetch_all(query, (company_id,))
            return invoices
        except Exception as e:
            return []
    
    def get_invoice_items(self, invoice_id, invoice_type):
        """Get items for an invoice"""
        try:
            if invoice_type == 'sales':
                query = 'SELECT * FROM sales_invoice_items WHERE invoice_id = ?'
            else:
                query = 'SELECT * FROM purchase_invoice_items WHERE invoice_id = ?'
            
            items = self.db.fetch_all(query, (invoice_id,))
            return items
        except Exception as e:
            return []
    
    def update_sales_invoice(self, invoice_id, **kwargs):
        """Update sales invoice"""
        try:
            updates = []
            params = []
            
            fields = ['invoice_date', 'due_date', 'subtotal', 'tax_amount', 
                     'discount', 'total', 'status', 'notes']
            
            for field in fields:
                if field in kwargs:
                    updates.append(f'{field} = ?')
                    params.append(kwargs[field])
            
            if not updates:
                return False, "No fields to update"
            
            updates.append('updated_at = ?')
            params.append(datetime.now())
            params.append(invoice_id)
            
            query = f'UPDATE sales_invoices SET {", ".join(updates)} WHERE id = ?'
            self.db.execute_query(query, params)
            
            return True, "Invoice updated successfully"
        except Exception as e:
            return False, f"Update failed: {str(e)}"
    
    def update_purchase_invoice(self, invoice_id, **kwargs):
        """Update purchase invoice"""
        try:
            updates = []
            params = []
            
            fields = ['invoice_date', 'due_date', 'subtotal', 'tax_amount', 
                     'discount', 'total', 'status', 'notes']
            
            for field in fields:
                if field in kwargs:
                    updates.append(f'{field} = ?')
                    params.append(kwargs[field])
            
            if not updates:
                return False, "No fields to update"
            
            updates.append('updated_at = ?')
            params.append(datetime.now())
            params.append(invoice_id)
            
            query = f'UPDATE purchase_invoices SET {", ".join(updates)} WHERE id = ?'
            self.db.execute_query(query, params)
            
            return True, "Invoice updated successfully"
        except Exception as e:
            return False, f"Update failed: {str(e)}"
    
    def delete_sales_invoice(self, invoice_id):
        """Delete a sales invoice"""
        try:
            # Delete items first
            self.db.execute_query('DELETE FROM sales_invoice_items WHERE invoice_id = ?', (invoice_id,))
            # Delete invoice
            self.db.execute_query('DELETE FROM sales_invoices WHERE id = ?', (invoice_id,))
            return True, "Invoice deleted successfully"
        except Exception as e:
            return False, f"Delete failed: {str(e)}"
    
    def delete_purchase_invoice(self, invoice_id):
        """Delete a purchase invoice"""
        try:
            # Delete items first
            self.db.execute_query('DELETE FROM purchase_invoice_items WHERE invoice_id = ?', (invoice_id,))
            # Delete invoice
            self.db.execute_query('DELETE FROM purchase_invoices WHERE id = ?', (invoice_id,))
            return True, "Invoice deleted successfully"
        except Exception as e:
            return False, f"Delete failed: {str(e)}"
    
    def _generate_invoice_number(self, company_id, invoice_type):
        """Generate unique invoice number"""
        try:
            if invoice_type == 'sales':
                query = 'SELECT COUNT(*) as count FROM sales_invoices WHERE company_id = ?'
            else:
                query = 'SELECT COUNT(*) as count FROM purchase_invoices WHERE company_id = ?'
            
            result = self.db.fetch_one(query, (company_id,))
            count = result['count'] + 1
            
            prefix = 'SI' if invoice_type == 'sales' else 'PI'
            return f'{prefix}-{company_id}-{count:06d}'
        except Exception as e:
            return f'INV-{datetime.now().strftime("%Y%m%d%H%M%S")}'
    
    def close(self):
        """Close database connection"""
        self.db.close()
