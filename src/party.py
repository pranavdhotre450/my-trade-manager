"""
Parties (Customers/Suppliers) management module
"""

from datetime import datetime
from src.database import DatabaseManager

class PartyManager:
    def __init__(self):
        self.db = DatabaseManager()
    
    def create_party(self, company_id, name, party_type, email=None, phone=None, **kwargs):
        """Create a new party (customer or supplier)"""
        try:
            query = '''
                INSERT INTO parties 
                (company_id, name, email, phone, type, address, city, state, 
                 postal_code, gstin, pan, opening_balance, balance_type, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            params = (
                company_id, name, email, phone, party_type,
                kwargs.get('address'), kwargs.get('city'), kwargs.get('state'),
                kwargs.get('postal_code'), kwargs.get('gstin'), kwargs.get('pan'),
                kwargs.get('opening_balance', 0), kwargs.get('balance_type', 'Debit'),
                datetime.now(), datetime.now()
            )
            
            cursor = self.db.execute_query(query, params)
            return True, cursor.lastrowid, "Party created successfully"
        except Exception as e:
            return False, None, f"Failed to create party: {str(e)}"
    
    def get_party(self, party_id):
        """Get party details"""
        try:
            query = 'SELECT * FROM parties WHERE id = ?'
            party = self.db.fetch_one(query, (party_id,))
            return party
        except Exception as e:
            return None
    
    def get_company_parties(self, company_id, party_type=None):
        """Get all parties for a company"""
        try:
            if party_type:
                query = 'SELECT * FROM parties WHERE company_id = ? AND type IN (?, "Both") ORDER BY name'
                parties = self.db.fetch_all(query, (company_id, party_type))
            else:
                query = 'SELECT * FROM parties WHERE company_id = ? ORDER BY name'
                parties = self.db.fetch_all(query, (company_id,))
            return parties
        except Exception as e:
            return []
    
    def update_party(self, party_id, **kwargs):
        """Update party details"""
        try:
            updates = []
            params = []
            
            fields = ['name', 'email', 'phone', 'type', 'address', 'city', 'state',
                     'postal_code', 'gstin', 'pan', 'opening_balance', 'balance_type']
            
            for field in fields:
                if field in kwargs:
                    updates.append(f'{field} = ?')
                    params.append(kwargs[field])
            
            if not updates:
                return False, "No fields to update"
            
            updates.append('updated_at = ?')
            params.append(datetime.now())
            params.append(party_id)
            
            query = f'UPDATE parties SET {", ".join(updates)} WHERE id = ?'
            self.db.execute_query(query, params)
            
            return True, "Party updated successfully"
        except Exception as e:
            return False, f"Update failed: {str(e)}"
    
    def delete_party(self, party_id):
        """Delete a party"""
        try:
            query = 'DELETE FROM parties WHERE id = ?'
            self.db.execute_query(query, (party_id,))
            return True, "Party deleted successfully"
        except Exception as e:
            return False, f"Delete failed: {str(e)}"
    
    def get_party_balance(self, party_id):
        """Calculate current balance of a party"""
        try:
            # Get opening balance
            party = self.get_party(party_id)
            if not party:
                return 0
            
            balance = party['opening_balance']
            
            # Add sales invoice totals
            sales_query = '''
                SELECT COALESCE(SUM(total), 0) as total 
                FROM sales_invoices WHERE party_id = ?
            '''
            sales_result = self.db.fetch_one(sales_query, (party_id,))
            
            # Add purchase invoice totals
            purchase_query = '''
                SELECT COALESCE(SUM(total), 0) as total 
                FROM purchase_invoices WHERE party_id = ?
            '''
            purchase_result = self.db.fetch_one(purchase_query, (party_id,))
            
            if party['balance_type'] == 'Debit':
                balance += sales_result['total'] if sales_result else 0
                balance -= purchase_result['total'] if purchase_result else 0
            else:
                balance -= sales_result['total'] if sales_result else 0
                balance += purchase_result['total'] if purchase_result else 0
            
            return balance
        except Exception as e:
            return 0
    
    def close(self):
        """Close database connection"""
        self.db.close()
