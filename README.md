# POS System - Point of Sale Management System

A comprehensive Point of Sale (POS) system built with Flask, featuring a complete hold transaction system, multi-branch support, inventory management, and more.

## 🚀 Features

### 🛒 Core POS Functionality
- **Touch-friendly Sales Interface** - Intuitive POS interface optimized for touch devices
- **Product Search & Barcode Support** - Quick product lookup by name, SKU, or barcode
- **Multiple Payment Methods** - Support for cash, card, mobile payments
- **Real-time Inventory Updates** - Automatic stock deduction on sales
- **Receipt Generation** - Print or email receipts with QR codes for tax compliance
- **Hold Transaction System** - Pause and resume transactions with full state preservation
- **Held Transaction Notifications** - Real-time alerts for pending transactions
- **Transaction Recovery** - Resume interrupted sales with complete cart restoration

### ⏸️ Hold Transaction System

The Hold Transaction System provides comprehensive transaction management capabilities:

#### **Core Features:**
- **Transaction Holding** - Pause current transaction with complete state preservation
- **Cart Persistence** - Save all items, quantities, discounts, and customer information
- **Notes Support** - Add optional notes for held transactions
- **Transaction Recovery** - Resume any held transaction with full cart restoration
- **Transaction Management** - View, resume, or delete held transactions

#### **Notification System:**
- **Real-time Badge Updates** - Live count of pending transactions on POS interface
- **Dashboard Integration** - Held transactions widget in main dashboard
- **Automatic Updates** - Real-time synchronization across all interfaces
- **User-specific Notifications** - Show only transactions held by current user (unless admin)

#### **User Interface:**
- **Hold Button** - One-click transaction holding with notes prompt
- **Held Transactions Modal** - Comprehensive management interface
- **Dashboard Widgets** - Quick stats and detailed alerts sections
- **Resume Functionality** - One-click transaction restoration

#### **Technical Implementation:**
- **Database Model** - Dedicated `HeldTransaction` table with JSON data storage
- **API Endpoints** - RESTful APIs for all hold transaction operations
- **Real-time Updates** - JavaScript polling for live notifications
- **Security** - User-based permissions and data isolation

### 📦 Product Management
- **Product CRUD Operations** - Create, read, update, delete products
- **Category Management** - Organize products in hierarchical categories
- **Multiple Barcodes** - Support for multiple barcodes per product
- **Image Support** - Product images with automatic resizing
- **Stock Level Monitoring** - Min/max stock levels with alerts
- **Favorite Products** - Quick access to frequently sold items

### 📊 Inventory Management
- **Multi-branch Inventory** - Track stock across multiple locations
- **Inventory Entry System** - Comprehensive stock entry with supplier tracking
- **Stock Adjustments** - Handle inventory discrepancies
- **Inter-branch Transfers** - Move stock between branches
- **Low Stock Alerts** - Automated notifications for low inventory
- **Supplier Management** - Maintain supplier information and purchase history

### 👥 Customer Management
- **Customer Database** - Store customer information and purchase history
- **Loyalty Points System** - Reward repeat customers
- **Customer Types** - Regular, VIP, wholesale customer categories
- **Purchase Analytics** - Track customer buying patterns
- **Birthday Reminders** - Automated birthday notifications

### 👨‍💼 Employee Management
- **Role-based Access Control** - Admin, Manager, Cashier, Inventory Manager roles
- **User Authentication** - Secure login with password encryption
- **Performance Tracking** - Monitor employee sales performance
- **Attendance Tracking** - Track employee login/logout times
- **Branch Assignment** - Assign employees to specific branches

### 📈 Reports & Analytics
- **Sales Reports** - Daily, weekly, monthly sales analysis
- **Product Performance** - Best/worst selling products
- **Customer Analytics** - Customer behavior and loyalty analysis
- **Inventory Reports** - Stock levels, movements, and valuations
- **Profit & Loss** - Financial performance tracking
- **Export Functionality** - Export reports to Excel/PDF

### 🧾 Invoice Management
- **Invoice Generation** - Professional invoices with QR codes
- **Tax Compliance** - Built-in tax calculations and reporting
- **Invoice History** - Complete transaction history
- **Cancellation Support** - Handle invoice cancellations with proper controls
- **PDF Generation** - Generate PDF invoices for printing/emailing

### ⚙️ System Settings
- **Store Configuration** - Store details, tax rates, currency settings
- **Branch Management** - Multi-branch setup and configuration
- **User Preferences** - Language, timezone, and display settings
- **Backup & Restore** - Database backup and restoration tools
- **System Monitoring** - Performance and health monitoring

### 🆘 Support System
- **Ticket Management** - Internal support ticket system
- **Issue Tracking** - Track and resolve system issues
- **User Support** - Help desk functionality for employees
- **Knowledge Base** - Built-in documentation and help

### 🔄 Synchronization
- **Offline Support** - Continue operations without internet
- **Data Synchronization** - Sync data when connection is restored
- **Multi-device Support** - Use across multiple devices
- **Conflict Resolution** - Handle data conflicts intelligently

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLAlchemy with SQLite (easily configurable for PostgreSQL/MySQL)
- **Frontend**: Bootstrap 5, jQuery, Font Awesome
- **Authentication**: Flask-Login with bcrypt password hashing
- **File Handling**: Pillow for image processing
- **Reports**: ReportLab for PDF generation, OpenPyXL for Excel exports
- **QR Codes**: python-qrcode for tax compliance
- **Email**: Flask-Mail for notifications

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/pos-system.git
   cd pos-system
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   - Copy `.env` file and update the values:
   ```bash
   cp .env.example .env
   ```
   - Edit `.env` with your configuration

5. **Initialize the database:**
   ```bash
   python app.py
   ```
   The database will be created automatically on first run.

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Flask Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
FLASK_ENV=development

# Database Configuration
DATABASE_URL=sqlite:///pos_system.db

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Application Settings
APP_NAME=POS System
COMPANY_NAME=Your Company Name
CURRENCY_SYMBOL=$
TAX_RATE=0.0
```

## 🏃‍♂️ Running the Application

1. **Start the development server:**
   ```bash
   python app.py
   ```

2. **Open your browser and navigate to:**
   ```
   http://localhost:5000
   ```

3. **Login with default credentials:**
   - Username: `admin`
   - Password: `admin123`

## 📖 Usage

### First Time Setup

1. **Login** with the default admin account
2. **Configure System Settings**:
   - Go to Settings → General
   - Update store information, tax rates, currency
3. **Create Branches** (if multi-branch):
   - Go to Settings → Branches
   - Add your store locations
4. **Add Products**:
   - Go to Products → Add Product
   - Create product categories and add inventory
5. **Create Employee Accounts**:
   - Go to Employees → Add Employee
   - Assign appropriate roles and permissions
6. **Start Selling**:
   - Go to POS Sale interface
   - Begin processing transactions

### Daily Operations

1. **Morning Setup**:
    - Login to the system
    - Check low stock alerts
    - Review overnight reports
    - **Check held transactions** from previous day

2. **Sales Processing**:
    - Use POS interface for transactions
    - Handle customer inquiries
    - Process returns/exchanges
    - **Hold transactions** when customers need time to decide
    - **Resume held transactions** when customers return

3. **Inventory Management**:
    - Receive new stock
    - Update inventory levels
    - Handle stock transfers

4. **End of Day**:
    - Generate daily sales reports
    - Backup data
    - Review system alerts
    - **Clear old held transactions** that are no longer needed

### Hold Transaction Workflow

#### **Holding a Transaction:**
1. Add items to cart as usual
2. Click **"Hold Transaction"** button
3. Add optional notes for the transaction
4. Transaction is saved and cart is cleared
5. Badge count updates automatically

#### **Resuming a Transaction:**
1. Click **"Held Transactions"** button in POS
2. Select transaction from the list
3. Click **"Resume"** to restore cart
4. Complete the sale normally

#### **Managing Held Transactions:**
1. View all held transactions in the modal
2. See customer name, item count, total, and time
3. Resume or delete transactions as needed
4. Monitor pending transactions from dashboard

#### **Dashboard Monitoring:**
1. Check **"Held Transactions"** card in Quick Stats
2. Review detailed list in Alerts section
3. Click **"Manage"** to go to POS interface
4. Monitor real-time updates every 30 seconds

## 👥 User Roles & Permissions

### Admin
- Full system access
- User management
- System configuration
- All reports and analytics

### Manager
- Sales operations
- Inventory management
- Customer management
- Reports (branch-specific)

### Cashier
- POS operations
- Customer lookup
- Basic reporting

### Inventory Manager
- Inventory operations
- Product management
- Stock reports

## 🔒 Security Considerations

1. **Password Security**
   - Change default admin password
   - Enforce strong password policies
   - Regular password updates

2. **Data Protection**
   - Regular backups
   - Encrypt sensitive data
   - Secure file permissions

3. **Network Security**
   - Use HTTPS in production
   - Firewall configuration
   - Regular security updates

## 📊 API Documentation

The system provides RESTful APIs for integration:

### Hold Transaction APIs
- `POST /api/hold_transaction` - Hold a transaction
- `POST /api/resume_transaction/<id>` - Resume a held transaction
- `DELETE /api/delete_held_transaction/<id>` - Delete a held transaction
- `GET /api/held_transactions_count` - Get count of held transactions

## 🧪 Testing

Run the test suite:

```bash
python -m pytest
```

## 🚀 Deployment

### Production Deployment

1. **Set environment variables:**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-production-secret-key
   ```

2. **Use a production WSGI server:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

3. **Use a reverse proxy (nginx):**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the built-in support system

## 📈 Changelog

### Version 1.1.0 - Hold Transaction System
- **Hold Transaction System** - Complete transaction pause and resume functionality
- **Held Transaction Notifications** - Real-time badge updates and dashboard widgets
- **Transaction Recovery** - Full cart state preservation and restoration
- **Dashboard Integration** - Held transactions monitoring in main dashboard
- **API Enhancements** - New REST endpoints for transaction management
- **User Experience** - Intuitive modal interface for transaction management
- **Real-time Updates** - Automatic synchronization across all interfaces
- **Security Features** - User-based permissions and data isolation

### Version 1.0.0
- Initial release
- Core POS functionality
- Multi-module architecture
- Role-based access control
- Comprehensive reporting
- Offline support

---

**Note**: This is a comprehensive POS system designed for small to medium-sized retail businesses. It provides all essential features needed for daily operations while maintaining flexibility for customization and growth."# POS_Flask"  
