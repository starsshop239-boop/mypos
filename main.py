import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import sqlite3
from datetime import datetime

# -------------------------
# Database setup
# -------------------------
conn = sqlite3.connect("pos2.db")
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    stock INTEGER,
    price REAL
)""")

c.execute("""CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    qty INTEGER,
    total REAL,
    date TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS debts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer TEXT,
    amount REAL,
    date TEXT
)""")

conn.commit()

# -------------------------
# Main GUI
# -------------------------
root = tk.Tk()
root.title("Advanced POS System")

tree = ttk.Treeview(root, columns=("ID", "Name", "Stock", "Price"), show="headings")
tree.heading("ID", text="ID")
tree.heading("Name", text="Name")
tree.heading("Stock", text="Stock")
tree.heading("Price", text="Price")
tree.pack(fill=tk.BOTH, expand=True)

# -------------------------
# Functions
# -------------------------
def load_products():
    for i in tree.get_children():
        tree.delete(i)
    c.execute("SELECT * FROM products")
    for row in c.fetchall():
        tree.insert("", tk.END, values=row)

def sell_product():
    selected = tree.focus()
    if not selected:
        messagebox.showerror("Error", "Select a product first")
        return
    product = tree.item(selected)["values"]
    product_id, name, stock, price = product
    qty = simpledialog.askinteger("Sell Units", f"How many {name} units to sell?")
    if not qty or qty <= 0:
        return
    if qty > stock:
        messagebox.showerror("Error", "Not enough stock")
        return
    total = qty * price
    c.execute("INSERT INTO sales (product_id, qty, total, date) VALUES (?, ?, ?, ?)",
              (product_id, qty, total, datetime.now().strftime("%Y-%m-%d")))
    c.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (qty, product_id))
    conn.commit()
    load_products()
    messagebox.showinfo("Sold", f"Sold {qty} {name} units for ${total}")
    if stock - qty <= 5:  # Low-stock alert
        messagebox.showwarning("Low Stock", f"{name} stock is low!")

def add_product():
    name = simpledialog.askstring("Product Name", "Enter product name:")
    if not name:
        return
    stock = simpledialog.askinteger("Stock", "Enter initial stock:")
    price = simpledialog.askfloat("Price", "Enter unit price:")
    c.execute("INSERT INTO products (name, stock, price) VALUES (?, ?, ?)", (name, stock, price))
    conn.commit()
    load_products()

def add_debt():
    customer = simpledialog.askstring("Customer Name", "Enter customer name:")
    amount = simpledialog.askfloat("Debt Amount", "Enter debt amount:")
    c.execute("INSERT INTO debts (customer, amount, date) VALUES (?, ?, ?)",
              (customer, amount, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    messagebox.showinfo("Debt Added", f"Debt of ${amount} added for {customer}")

def sales_report():
    c.execute("""SELECT p.name, SUM(s.qty) as total_qty, SUM(s.total) as total_amount
                 FROM sales s JOIN products p ON s.product_id = p.id
                 GROUP BY p.id""")
    report = ""
    for row in c.fetchall():
        name, total_qty, total_amount = row
        report += f"{name}: Sold {total_qty}, Total ${total_amount}\n"
    messagebox.showinfo("Sales Report", report)

def fast_moving_products():
    c.execute("""SELECT p.name, SUM(s.qty) as sold_qty
                 FROM sales s JOIN products p ON s.product_id = p.id
                 GROUP BY p.id
                 ORDER BY sold_qty DESC
                 LIMIT 5""")
    report = "Top 5 Fast-moving Products:\n"
    for row in c.fetchall():
        report += f"{row[0]} - {row[1]} units\n"
    messagebox.showinfo("Fast-moving Products", report)

# -------------------------
# Buttons
# -------------------------
btn_frame = tk.Frame(root)
btn_frame.pack(fill=tk.X)

tk.Button(btn_frame, text="Add Product", command=add_product).pack(side=tk.LEFT, padx=5, pady=5)
tk.Button(btn_frame, text="Sell Product", command=sell_product).pack(side=tk.LEFT, padx=5, pady=5)
tk.Button(btn_frame, text="Add Debt", command=add_debt).pack(side=tk.LEFT, padx=5, pady=5)
tk.Button(btn_frame, text="Sales Report", command=sales_report).pack(side=tk.LEFT, padx=5, pady=5)
tk.Button(btn_frame, text="Fast-moving Products", command=fast_moving_products).pack(side=tk.LEFT, padx=5, pady=5)

load_products()
root.mainloop()
