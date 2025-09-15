from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, IntegerField, FloatField
from wtforms.validators import DataRequired, Email, Length, Optional
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import json
import uuid
from PIL import Image
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import openpyxl
from flask_mail import Mail, Message
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///pos_system.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Email configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
mail = Mail(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'products'), exist_ok=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='cashier')  # admin, manager, cashier, inventory_manager
    is_active = db.Column(db.Boolean, default=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    branch = db.relationship('Branch', backref=db.backref('users', lazy=True))

class Branch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    parent = db.relationship('Category', remote_side=[id], backref=db.backref('subcategories', lazy=True))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    barcodes = db.Column(db.Text, nullable=True)  # JSON array of barcodes
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    price = db.Column(db.Float, nullable=False)
    cost_price = db.Column(db.Float, nullable=True)
    image = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    track_inventory = db.Column(db.Boolean, default=True)
    min_stock = db.Column(db.Integer, default=0)
    max_stock = db.Column(db.Integer, nullable=True)
    # New fields
    box_qty = db.Column(db.Integer, default=1)  # Units per box
    is_favorite = db.Column(db.Boolean, default=False)  # Favorite product
    expiry_date = db.Column(db.Date, nullable=True)  # Expiration date
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = db.relationship('Category', backref=db.backref('products', lazy=True))
    inventories = db.relationship('Inventory', backref='product', lazy=True)

    @property
    def barcode_list(self):
        """Get barcodes as a list"""
        if self.barcodes:
            try:
                return json.loads(self.barcodes)
            except:
                return [self.barcodes] if self.barcodes else []
        return []

    @barcode_list.setter
    def barcode_list(self, value):
        """Set barcodes from a list"""
        if isinstance(value, list):
            self.barcodes = json.dumps(value)
        else:
            self.barcodes = json.dumps([value]) if value else None

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    reserved_quantity = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    branch = db.relationship('Branch', backref=db.backref('inventories', lazy=True))

    __table_args__ = (db.UniqueConstraint('product_id', 'branch_id', name='unique_product_branch'),)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    customer_type = db.Column(db.String(20), default='regular')  # regular, vip, wholesale
    loyalty_points = db.Column(db.Integer, default=0)
    total_purchases = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    birthday = db.Column(db.Date, nullable=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    tax_amount = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    payment_method = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='completed')  # completed, cancelled, refunded
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    customer = db.relationship('Customer', backref=db.backref('transactions', lazy=True))
    user = db.relationship('User', backref=db.backref('transactions', lazy=True))
    branch = db.relationship('Branch', backref=db.backref('transactions', lazy=True))
    items = db.relationship('TransactionItem', backref='transaction', lazy=True, cascade='all, delete-orphan')

class TransactionItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, nullable=False)

    product = db.relationship('Product', backref=db.backref('transaction_items', lazy=True))

class HeldTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=False)
    cart_data = db.Column(db.Text, nullable=False)  # JSON string
    customer_data = db.Column(db.Text, nullable=True)  # JSON string
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=7))

    user = db.relationship('User', backref=db.backref('held_transactions', lazy=True))
    branch = db.relationship('Branch', backref=db.backref('held_transactions', lazy=True))

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SupportTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    status = db.Column(db.String(20), default='open')  # open, in_progress, resolved, closed
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('created_tickets', lazy=True))
    assignee = db.relationship('User', foreign_keys=[assigned_to], backref=db.backref('assigned_tickets', lazy=True))

class PurchaseInvoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=False)
    invoice_date = db.Column(db.Date, nullable=False)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='draft')  # draft, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    supplier = db.relationship('Supplier', backref=db.backref('purchase_invoices', lazy=True))
    user = db.relationship('User', backref=db.backref('purchase_invoices', lazy=True))
    branch = db.relationship('Branch', backref=db.backref('purchase_invoices', lazy=True))
    items = db.relationship('PurchaseInvoiceItem', backref='invoice', lazy=True, cascade='all, delete-orphan')

class PurchaseInvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    purchase_invoice_id = db.Column(db.Integer, db.ForeignKey('purchase_invoice.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)

    product = db.relationship('Product', backref=db.backref('purchase_invoice_items', lazy=True))

class ProductMovement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=False)
    movement_type = db.Column(db.String(20), nullable=False)  # purchase, sale, return, transfer, adjustment
    quantity = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reason = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product', backref=db.backref('movements', lazy=True))
    branch = db.relationship('Branch', backref=db.backref('movements', lazy=True))
    user = db.relationship('User', backref=db.backref('movements', lazy=True))

# Forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    sku = StringField('SKU', validators=[DataRequired()])
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    price = FloatField('Price', validators=[DataRequired()])
    cost_price = FloatField('Cost Price', validators=[Optional()])
    min_stock = IntegerField('Minimum Stock', default=0, validators=[Optional()])
    max_stock = IntegerField('Maximum Stock', validators=[Optional()])
    # New fields
    box_qty = IntegerField('Units per Box', default=1, validators=[Optional()])
    is_favorite = SelectField('Favorite Product', choices=[('False', 'No'), ('True', 'Yes')], default='False')
    expiry_date = StringField('Expiry Date (YYYY-MM-DD)', validators=[Optional()])
    submit = SubmitField('Save Product')

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    parent_id = SelectField('Parent Category', coerce=int, validators=[Optional()])
    submit = SubmitField('Save Category')

class CustomerForm(FlaskForm):
    name = StringField('Customer Name', validators=[DataRequired()])
    email = StringField('Email', validators=[Optional()])
    phone = StringField('Phone')
    address = TextAreaField('Address')
    customer_type = SelectField('Customer Type', choices=[
        ('regular', 'Regular'),
        ('vip', 'VIP'),
        ('wholesale', 'Wholesale')
    ], default='regular')
    birthday = StringField('Birthday (YYYY-MM-DD)')
    submit = SubmitField('Save Customer')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Optional()])
    role = SelectField('Role', choices=[
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('cashier', 'Cashier'),
        ('inventory_manager', 'Inventory Manager')
    ], default='cashier')
    branch_id = SelectField('Branch', coerce=int, validators=[Optional()])
    submit = SubmitField('Save User')

class BranchForm(FlaskForm):
    name = StringField('Branch Name', validators=[DataRequired()])
    address = TextAreaField('Address')
    phone = StringField('Phone')
    submit = SubmitField('Save Branch')

class HeldTransactionForm(FlaskForm):
    notes = TextAreaField('Notes')
    submit = SubmitField('Hold Transaction')

# Context processors
@app.context_processor
def inject_held_transactions_count():
    """Make held transactions count available in all templates"""
    if current_user.is_authenticated:
        count = HeldTransaction.query.filter(
            HeldTransaction.user_id == current_user.id,
            HeldTransaction.expires_at > datetime.utcnow()
        ).count()
        return {'held_transactions_count': count}
    return {'held_transactions_count': 0}

# Routes
@app.route('/')
@login_required
def index():
    # Dashboard with quick stats
    total_sales = db.session.query(db.func.sum(Transaction.total_amount)).filter(
        Transaction.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    ).scalar() or 0

    total_transactions = Transaction.query.filter(
        Transaction.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    ).count()

    low_stock_products = Product.query.filter(
        Product.is_active == True,
        Product.track_inventory == True
    ).join(Inventory).filter(
        Inventory.quantity <= Product.min_stock
    ).count()

    held_transactions_count = HeldTransaction.query.filter(
        HeldTransaction.user_id == current_user.id,
        HeldTransaction.expires_at > datetime.utcnow()
    ).count()

    return render_template('dashboard.html',
                         total_sales=total_sales,
                         total_transactions=total_transactions,
                         low_stock_products=low_stock_products,
                         held_transactions_count=held_transactions_count)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/pos')
@login_required
def pos():
    search = request.args.get('search', '').strip()

    # Base query for products
    query = Product.query.filter_by(is_active=True)

    if search:
        # Search in product name, SKU, and barcodes
        search_conditions = [
            Product.name.contains(search),
            Product.sku.contains(search)
        ]

        # Also search in barcodes JSON field
        if search:
            # For exact barcode matches in the JSON array
            search_conditions.append(Product.barcodes.contains(search))

        query = query.filter(db.or_(*search_conditions))

    # Order by name for consistent display
    products = query.order_by(Product.name).all()

    customers = Customer.query.filter_by(is_active=True).all()
    held_transactions = HeldTransaction.query.filter(
        HeldTransaction.user_id == current_user.id,
        HeldTransaction.expires_at > datetime.utcnow()
    ).all()

    held_transactions_count = len(held_transactions)

    return render_template('pos.html',
                          products=products,
                          customers=customers,
                          held_transactions=held_transactions,
                          held_transactions_count=held_transactions_count,
                          search=search)

@app.route('/api/hold_transaction', methods=['POST'])
@login_required
def hold_transaction():
    data = request.get_json()
    cart_data = data.get('cart', [])
    customer_data = data.get('customer', {})
    notes = data.get('notes', '')

    if not cart_data:
        return jsonify({'success': False, 'message': 'Cart is empty'}), 400

    # Generate unique transaction ID
    transaction_id = f"HLD{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"

    held_transaction = HeldTransaction(
        transaction_id=transaction_id,
        user_id=current_user.id,
        branch_id=current_user.branch_id or 1,
        cart_data=json.dumps(cart_data),
        customer_data=json.dumps(customer_data) if customer_data else None,
        notes=notes
    )

    db.session.add(held_transaction)
    db.session.commit()

    return jsonify({
        'success': True,
        'transaction_id': transaction_id,
        'message': 'Transaction held successfully'
    })

@app.route('/api/resume_transaction/<transaction_id>', methods=['POST'])
@login_required
def resume_transaction(transaction_id):
    held_transaction = HeldTransaction.query.filter_by(
        transaction_id=transaction_id,
        user_id=current_user.id
    ).first()

    if not held_transaction:
        return jsonify({'success': False, 'message': 'Transaction not found'}), 404

    cart_data = json.loads(held_transaction.cart_data)
    customer_data = json.loads(held_transaction.customer_data) if held_transaction.customer_data else {}

    # Delete the held transaction
    db.session.delete(held_transaction)
    db.session.commit()

    return jsonify({
        'success': True,
        'cart': cart_data,
        'customer': customer_data,
        'message': 'Transaction resumed successfully'
    })

@app.route('/api/delete_held_transaction/<transaction_id>', methods=['DELETE'])
@login_required
def delete_held_transaction(transaction_id):
    held_transaction = HeldTransaction.query.filter_by(
        transaction_id=transaction_id,
        user_id=current_user.id
    ).first()

    if not held_transaction:
        return jsonify({'success': False, 'message': 'Transaction not found'}), 404

    db.session.delete(held_transaction)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Transaction deleted successfully'})

@app.route('/api/held_transactions_count')
@login_required
def held_transactions_count():
    count = HeldTransaction.query.filter(
        HeldTransaction.user_id == current_user.id,
        HeldTransaction.expires_at > datetime.utcnow()
    ).count()

    return jsonify({'count': count})

@app.route('/api/complete_sale', methods=['POST'])
@login_required
def complete_sale():
    data = request.get_json()
    cart = data.get('cart', [])
    customer_id = data.get('customer_id')
    payment_method = data.get('payment_method', 'cash')
    amount_received = data.get('amount_received', 0)
    notes = data.get('notes', '')

    if not cart:
        return jsonify({'success': False, 'message': 'Cart is empty'}), 400

    # Calculate totals
    total_amount = sum(item['price'] * item['quantity'] for item in cart)
    tax_amount = 0  # You can implement tax calculation here
    discount_amount = 0  # You can implement discount calculation here

    # Generate unique transaction ID
    transaction_id = f"SALE{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"

    # Create transaction
    transaction = Transaction(
        transaction_id=transaction_id,
        customer_id=customer_id,
        user_id=current_user.id,
        branch_id=current_user.branch_id or 1,
        total_amount=total_amount,
        tax_amount=tax_amount,
        discount_amount=discount_amount,
        payment_method=payment_method,
        notes=notes
    )
    db.session.add(transaction)
    db.session.flush()  # Get transaction.id

    # Create transaction items and movements
    for item in cart:
        product_id = item['product_id']
        quantity = item['quantity']
        unit_price = item['price']

        # Create transaction item
        transaction_item = TransactionItem(
            transaction_id=transaction.id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
            total=unit_price * quantity
        )
        db.session.add(transaction_item)

        # Create product movement for sale
        movement = ProductMovement(
            product_id=product_id,
            branch_id=current_user.branch_id or 1,
            movement_type='sale',
            quantity=-quantity,  # Negative for stock out
            user_id=current_user.id,
            reason='Sale',
            notes=f'Sold in transaction {transaction_id}'
        )
        db.session.add(movement)

        # Update inventory
        inventory = Inventory.query.filter_by(product_id=product_id, branch_id=current_user.branch_id or 1).first()
        if inventory:
            inventory.quantity -= quantity
            inventory.last_updated = datetime.utcnow()

    db.session.commit()

    return jsonify({
        'success': True,
        'transaction_id': transaction_id,
        'total': total_amount,
        'message': 'Sale completed successfully'
    })

@app.route('/inventory')
@login_required
def inventory():
    if current_user.role not in ['admin', 'manager', 'inventory_manager']:
        flash('Access denied', 'error')
        return redirect(url_for('index'))

    page = request.args.get('page', 1, type=int)
    per_page = 20
    search = request.args.get('search', '')
    branch_filter = request.args.get('branch', '')

    # Base query joining Product and Inventory
    query = db.session.query(Product, Inventory).join(Inventory).filter(Product.is_active == True)

    if search:
        query = query.filter(
            db.or_(
                Product.name.contains(search),
                Product.sku.contains(search)
            )
        )

    if branch_filter:
        query = query.filter(Inventory.branch_id == branch_filter)

    # Order by product name
    query = query.order_by(Product.name)

    # Paginate
    results = query.paginate(page=page, per_page=per_page, error_out=False)

    # Get branches for filter
    branches = Branch.query.filter_by(is_active=True).all()

    # Get low stock items
    low_stock_query = db.session.query(Product, Inventory).join(Inventory).filter(
        Product.is_active == True,
        Product.track_inventory == True,
        Inventory.quantity <= Product.min_stock
    )
    low_stock_items = low_stock_query.all()

    return render_template('inventory.html',
                          results=results,
                          branches=branches,
                          search=search,
                          branch_filter=branch_filter,
                          low_stock_items=low_stock_items)

@app.route('/products')
@login_required
def products():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search = request.args.get('search', '')

    query = Product.query.filter_by(is_active=True).order_by(Product.created_at.desc())

    if search:
        query = query.filter(
            db.or_(
                Product.name.contains(search),
                Product.sku.contains(search),
                Product.barcodes.contains(search)  # Search in barcodes JSON
            )
        )

    products = query.paginate(page=page, per_page=per_page, error_out=False)
    categories = Category.query.filter_by(is_active=True).all()

    return render_template('products.html',
                         products=products,
                         categories=categories,
                         search=search)

@app.route('/product/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if current_user.role not in ['admin', 'manager', 'inventory_manager']:
        flash('Access denied', 'error')
        return redirect(url_for('products'))

    form = ProductForm()
    form.category_id.choices = [(0, 'No Category')] + [(c.id, c.name) for c in Category.query.filter_by(is_active=True).all()]

    if form.validate_on_submit():
        # Check if SKU already exists
        existing_product = Product.query.filter_by(sku=form.sku.data).first()
        if existing_product:
            print(f"SKU {form.sku.data} already exists")
            flash('SKU already exists', 'error')
            return render_template('product_form.html', form=form, title='Add Product')

        # Handle multiple barcodes
        barcodes = request.form.get('barcodes')
        if barcodes:
            try:
                barcode_list = json.loads(barcodes)
            except:
                barcode_list = []
        else:
            barcode_list = []

        # Handle expiry date
        expiry_date = None
        if form.expiry_date.data:
            try:
                expiry_date = datetime.strptime(form.expiry_date.data, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid expiry date format. Use YYYY-MM-DD', 'error')
                return render_template('product_form.html', form=form, title='Add Product')

        product = Product(
            name=form.name.data,
            description=form.description.data,
            sku=form.sku.data,
            category_id=form.category_id.data if form.category_id.data != 0 else None,
            price=form.price.data,
            cost_price=form.cost_price.data,
            min_stock=form.min_stock.data,
            max_stock=form.max_stock.data,
            box_qty=form.box_qty.data,
            is_favorite=form.is_favorite.data == 'True',
            expiry_date=expiry_date
        )
        product.barcode_list = barcode_list

        db.session.add(product)
        db.session.commit()

        # Create inventory entries for all branches
        branches = Branch.query.filter_by(is_active=True).all()
        for branch in branches:
            inventory = Inventory(
                product_id=product.id,
                branch_id=branch.id,
                quantity=0
            )
            db.session.add(inventory)

        db.session.commit()

        flash('Product added successfully', 'success')
        return redirect(url_for('products'))

    return render_template('product_form.html', form=form, title='Add Product')

@app.route('/product/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    if current_user.role not in ['admin', 'manager', 'inventory_manager']:
        flash('Access denied', 'error')
        return redirect(url_for('products'))

    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    form.category_id.choices = [(0, 'No Category')] + [(c.id, c.name) for c in Category.query.filter_by(is_active=True).all()]

    if form.validate_on_submit():
        # Check if SKU already exists (excluding current product)
        existing_product = Product.query.filter(
            Product.sku == form.sku.data,
            Product.id != id
        ).first()
        if existing_product:
            flash('SKU already exists', 'error')
            return render_template('product_form.html', form=form, title='Edit Product', product=product)

        # Handle multiple barcodes
        barcodes = request.form.get('barcodes')
        if barcodes:
            try:
                barcode_list = json.loads(barcodes)
            except:
                barcode_list = []
        else:
            barcode_list = []

        # Handle expiry date
        expiry_date = None
        if form.expiry_date.data:
            try:
                expiry_date = datetime.strptime(form.expiry_date.data, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid expiry date format. Use YYYY-MM-DD', 'error')
                return render_template('product_form.html', form=form, title='Edit Product', product=product)

        product.name = form.name.data
        product.description = form.description.data
        product.sku = form.sku.data
        product.barcode_list = barcode_list
        product.category_id = form.category_id.data if form.category_id.data != 0 else None
        product.price = form.price.data
        product.cost_price = form.cost_price.data
        product.min_stock = form.min_stock.data
        product.max_stock = form.max_stock.data
        product.box_qty = form.box_qty.data
        product.is_favorite = form.is_favorite.data == 'True'
        product.expiry_date = expiry_date
        product.updated_at = datetime.utcnow()

        db.session.commit()

        flash('Product updated successfully', 'success')
        return redirect(url_for('products'))

    return render_template('product_form.html', form=form, title='Edit Product', product=product)

@app.route('/product/delete/<int:id>', methods=['POST'])
@login_required
def delete_product(id):
    if current_user.role not in ['admin', 'manager', 'inventory_manager']:
        return jsonify({'success': False, 'message': 'Access denied'}), 403

    product = Product.query.get_or_404(id)
    product.is_active = False
    db.session.commit()

    return jsonify({'success': True, 'message': 'Product deleted successfully'})

@app.route('/product/<int:id>/movements')
@login_required
def product_movements(id):
    product = Product.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = 20
    movements = ProductMovement.query.filter_by(product_id=id).order_by(ProductMovement.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('product_movements.html', product=product, movements=movements)

@app.route('/product/<int:id>/add_movement', methods=['GET', 'POST'])
@login_required
def add_product_movement(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        movement_type = request.form.get('movement_type')
        quantity = int(request.form.get('quantity'))
        reason = request.form.get('reason')
        notes = request.form.get('notes')
        branch_id = current_user.branch_id or 1

        movement = ProductMovement(
            product_id=id,
            branch_id=branch_id,
            movement_type=movement_type,
            quantity=quantity,
            user_id=current_user.id,
            reason=reason,
            notes=notes
        )
        db.session.add(movement)

        # Update inventory
        inventory = Inventory.query.filter_by(product_id=id, branch_id=branch_id).first()
        if inventory:
            inventory.quantity += quantity
            db.session.commit()

        flash('Movement added successfully', 'success')
        return redirect(url_for('product_movements', id=id))

    return render_template('add_movement.html', product=product)

@app.route('/categories')
@login_required
def categories():
    categories = Category.query.filter_by(is_active=True).all()
    return render_template('categories.html', categories=categories)

@app.route('/category/add', methods=['GET', 'POST'])
@login_required
def add_category():
    if current_user.role not in ['admin', 'manager', 'inventory_manager']:
        flash('Access denied', 'error')
        return redirect(url_for('categories'))

    form = CategoryForm()
    categories = Category.query.filter_by(is_active=True).all()
    form.parent_id.choices = [(0, 'No Parent')] + [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            description=form.description.data,
            parent_id=form.parent_id.data if form.parent_id.data != 0 else None
        )

        db.session.add(category)
        db.session.commit()

        flash('Category added successfully', 'success')
        return redirect(url_for('categories'))

    return render_template('category_form.html', form=form, title='Add Category')

@app.route('/category/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    if current_user.role not in ['admin', 'manager', 'inventory_manager']:
        flash('Access denied', 'error')
        return redirect(url_for('categories'))

    category = Category.query.get_or_404(id)
    form = CategoryForm(obj=category)
    categories = Category.query.filter_by(is_active=True).all()
    form.parent_id.choices = [(0, 'No Parent')] + [(c.id, c.name) for c in categories if c.id != id]

    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        category.parent_id = form.parent_id.data if form.parent_id.data != 0 else None

        db.session.commit()

        flash('Category updated successfully', 'success')
        return redirect(url_for('categories'))

    return render_template('category_form.html', form=form, title='Edit Category', category=category)

@app.route('/category/delete/<int:id>', methods=['POST'])
@login_required
def delete_category(id):
    if current_user.role not in ['admin', 'manager', 'inventory_manager']:
        return jsonify({'success': False, 'message': 'Access denied'}), 403

    category = Category.query.get_or_404(id)
    category.is_active = False
    db.session.commit()

    return jsonify({'success': True, 'message': 'Category deleted successfully'})

@app.route('/suppliers')
@login_required
def suppliers():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search = request.args.get('search', '')

    query = Supplier.query.filter_by(is_active=True)

    if search:
        query = query.filter(
            db.or_(
                Supplier.name.contains(search),
                Supplier.email.contains(search),
                Supplier.phone.contains(search)
            )
        )

    suppliers = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('suppliers.html', suppliers=suppliers, search=search)

@app.route('/supplier/add', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if request.method == 'POST':
        supplier = Supplier(
            name=request.form.get('name'),
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            address=request.form.get('address')
        )

        db.session.add(supplier)
        db.session.commit()

        flash('Supplier added successfully', 'success')
        return redirect(url_for('suppliers'))

    return render_template('supplier_form.html', title='Add Supplier')

@app.route('/supplier/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_supplier(id):
    supplier = Supplier.query.get_or_404(id)

    if request.method == 'POST':
        supplier.name = request.form.get('name')
        supplier.email = request.form.get('email')
        supplier.phone = request.form.get('phone')
        supplier.address = request.form.get('address')

        db.session.commit()

        flash('Supplier updated successfully', 'success')
        return redirect(url_for('suppliers'))

    return render_template('supplier_form.html', title='Edit Supplier', supplier=supplier)

@app.route('/supplier/delete/<int:id>', methods=['POST'])
@login_required
def delete_supplier(id):
    supplier = Supplier.query.get_or_404(id)
    supplier.is_active = False
    db.session.commit()

    return jsonify({'success': True, 'message': 'Supplier deleted successfully'})

@app.route('/purchase_invoices')
@login_required
def purchase_invoices():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')

    query = PurchaseInvoice.query

    if search:
        query = query.filter(
            db.or_(
                PurchaseInvoice.invoice_number.contains(search),
                PurchaseInvoice.supplier.has(Supplier.name.contains(search))
            )
        )

    if status_filter:
        query = query.filter(PurchaseInvoice.status == status_filter)

    query = query.order_by(PurchaseInvoice.created_at.desc())
    invoices = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('purchase_invoices.html', invoices=invoices, search=search, status_filter=status_filter)

@app.route('/purchase_invoice/<int:id>')
@login_required
def purchase_invoice_detail(id):
    invoice = PurchaseInvoice.query.get_or_404(id)
    return render_template('purchase_invoice_detail.html', invoice=invoice)

@app.route('/purchase_invoice/add', methods=['GET', 'POST'])
@login_required
def add_purchase_invoice():
    if request.method == 'POST':
        data = request.get_json()

        # Generate invoice number
        invoice_number = f"PI{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"

        # Create invoice
        invoice = PurchaseInvoice(
            invoice_number=invoice_number,
            supplier_id=data['supplier_id'],
            user_id=current_user.id,
            branch_id=current_user.branch_id or 1,
            invoice_date=datetime.strptime(data['invoice_date'], '%Y-%m-%d').date(),
            total_amount=data['total_amount'],
            tax_amount=data.get('tax_amount', 0),
            discount_amount=data.get('discount_amount', 0),
            notes=data.get('notes', ''),
            status='completed'
        )

        db.session.add(invoice)
        db.session.flush()

        # Create invoice items and update inventory
        for item in data['items']:
            invoice_item = PurchaseInvoiceItem(
                purchase_invoice_id=invoice.id,
                product_id=item['product_id'],
                quantity=item['quantity'],
                unit_cost=item['unit_cost'],
                total=item['total']
            )
            db.session.add(invoice_item)

            # Create product movement
            movement = ProductMovement(
                product_id=item['product_id'],
                branch_id=current_user.branch_id or 1,
                movement_type='purchase',
                quantity=item['quantity'],
                user_id=current_user.id,
                reason='Purchase Invoice',
                notes=f'Invoice: {invoice_number}'
            )
            db.session.add(movement)

            # Update inventory
            inventory = Inventory.query.filter_by(
                product_id=item['product_id'],
                branch_id=current_user.branch_id or 1
            ).first()
            if inventory:
                inventory.quantity += item['quantity']
                inventory.last_updated = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'success': True,
            'invoice_id': invoice.id,
            'invoice_number': invoice_number,
            'message': 'Purchase invoice created successfully'
        })

    suppliers = Supplier.query.filter_by(is_active=True).all()
    categories = Category.query.filter_by(is_active=True).all()
    today_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('purchase_invoice_form.html', title='Add Purchase Invoice', suppliers=suppliers, categories=categories, today_date=today_date)

@app.route('/api/products/search')
@login_required
def search_products():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])

    products = Product.query.filter(
        Product.is_active == True,
        db.or_(
            Product.name.contains(query),
            Product.sku.contains(query),
            Product.barcodes.contains(query)
        )
    ).limit(10).all()

    results = []
    for product in products:
        results.append({
            'id': product.id,
            'name': product.name,
            'sku': product.sku,
            'price': product.price,
            'cost_price': product.cost_price or product.price,
            'box_qty': product.box_qty
        })

    return jsonify(results)

@app.route('/api/products/list')
@login_required
def products_list():
    page = request.args.get('page', 1, type=int)
    per_page = 50  # Load more products for modal
    search = request.args.get('search', '')
    category_filter = request.args.get('category', '')

    query = Product.query.filter_by(is_active=True)

    if search:
        query = query.filter(
            db.or_(
                Product.name.contains(search),
                Product.sku.contains(search),
                Product.barcodes.contains(search)
            )
        )

    if category_filter:
        query = query.filter(Product.category_id == category_filter)

    query = query.order_by(Product.name)

    # Get paginated results
    products_page = query.paginate(page=page, per_page=per_page, error_out=False)

    # Get total stock for each product
    products_data = []
    for product in products_page.items:
        total_stock = 0
        for inventory in product.inventories:
            total_stock += inventory.quantity

        products_data.append({
            'id': product.id,
            'name': product.name,
            'sku': product.sku,
            'price': product.price,
            'cost_price': product.cost_price,
            'image': product.image,
            'category': {
                'id': product.category.id if product.category else None,
                'name': product.category.name if product.category else None
            } if product.category else None,
            'total_stock': total_stock,
            'min_stock': product.min_stock,
            'box_qty': product.box_qty
        })

    return jsonify({
        'products': products_data,
        'total': products_page.total,
        'pages': products_page.pages,
        'current_page': products_page.page
    })

@app.route('/customers')
@login_required
def customers():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search = request.args.get('search', '')

    query = Customer.query.filter_by(is_active=True)

    if search:
        query = query.filter(
            db.or_(
                Customer.name.contains(search),
                Customer.email.contains(search),
                Customer.phone.contains(search)
            )
        )

    customers = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('customers.html', customers=customers, search=search)

@app.route('/customer/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    form = CustomerForm()

    if form.validate_on_submit():
        # Parse birthday
        birthday = None
        if form.birthday.data:
            try:
                birthday = datetime.strptime(form.birthday.data, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid birthday format. Use YYYY-MM-DD', 'error')
                return render_template('customer_form.html', form=form, title='Add Customer')

        customer = Customer(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data,
            customer_type=form.customer_type.data,
            birthday=birthday
        )

        db.session.add(customer)
        db.session.commit()

        flash('Customer added successfully', 'success')
        return redirect(url_for('customers'))

    return render_template('customer_form.html', form=form, title='Add Customer')

@app.route('/users')
@login_required
def users():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))

    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/user/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('users'))

    form = UserForm()
    form.branch_id.choices = [(0, 'No Branch')] + [(b.id, b.name) for b in Branch.query.filter_by(is_active=True).all()]

    if form.validate_on_submit():
        # Check if username or email already exists
        existing_user = User.query.filter(
            db.or_(
                User.username == form.username.data,
                User.email == form.email.data
            )
        ).first()
        if existing_user:
            flash('Username or email already exists', 'error')
            return render_template('user_form.html', form=form, title='Add User')

        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            role=form.role.data,
            branch_id=form.branch_id.data if form.branch_id.data != 0 else None
        )

        db.session.add(user)
        db.session.commit()

        flash('User added successfully', 'success')
        return redirect(url_for('users'))

    return render_template('user_form.html', form=form, title='Add User')

@app.route('/branches')
@login_required
def branches():
    if current_user.role not in ['admin', 'manager']:
        flash('Access denied', 'error')
        return redirect(url_for('index'))

    branches = Branch.query.all()
    return render_template('branches.html', branches=branches)

@app.route('/branch/add', methods=['GET', 'POST'])
@login_required
def add_branch():
    if current_user.role not in ['admin', 'manager']:
        flash('Access denied', 'error')
        return redirect(url_for('branches'))

    form = BranchForm()

    if form.validate_on_submit():
        branch = Branch(
            name=form.name.data,
            address=form.address.data,
            phone=form.phone.data
        )

        db.session.add(branch)
        db.session.commit()

        flash('Branch added successfully', 'success')
        return redirect(url_for('branches'))

    return render_template('branch_form.html', form=form, title='Add Branch')

@app.route('/reports')
@login_required
def reports():
    return render_template('reports.html')

@app.route('/settings')
@login_required
def settings():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))

    return render_template('settings.html')

@app.route('/support')
@login_required
def support():
    tickets = SupportTicket.query.filter_by(user_id=current_user.id).all()
    return render_template('support.html', tickets=tickets)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Create default admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)

            # Create default branch
            default_branch = Branch.query.filter_by(name='Main Branch').first()
            if not default_branch:
                default_branch = Branch(name='Main Branch', address='Default Address')
                db.session.add(default_branch)

            db.session.commit()

    app.run(debug=True, host='0.0.0.0', port=5000)