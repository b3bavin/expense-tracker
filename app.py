import tkinter as tk
from tkinter import messagebox
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import os

# -------------------------------
# File names
# -------------------------------
EXPENSE_FILE = "expenses.csv"
LIMIT_FILE = "limit.txt"
MONTH_FILE = "month.txt"

# Predefined categories
CATEGORIES = ["Food", "Travel", "Study", "Entertainment", "Others"]

# Current month in YYYY-MM format
current_month = datetime.now().strftime("%Y-%m")

# -------------------------------
# Initialize files
# -------------------------------
if not os.path.exists(EXPENSE_FILE):
    open(EXPENSE_FILE, "w").close()

if not os.path.exists(LIMIT_FILE):
    with open(LIMIT_FILE, "w") as f:
        f.write("0")

# Check if month changed; reset expenses if needed
if not os.path.exists(MONTH_FILE):
    with open(MONTH_FILE, "w") as f:
        f.write(current_month)
else:
    with open(MONTH_FILE, "r") as f:
        saved_month = f.read().strip()
    if saved_month != current_month:
        open(EXPENSE_FILE, "w").close()
        with open(MONTH_FILE, "w") as f:
            f.write(current_month)

# -------------------------------
# Load monthly limit
# -------------------------------
def load_limit():
    with open(LIMIT_FILE, "r") as f:
        return float(f.read())

# Save monthly limit entered by user
def save_limit():
    try:
        limit = float(limit_entry.get())
        with open(LIMIT_FILE, "w") as f:
            f.write(str(limit))
        update_summary()
        messagebox.showinfo("Saved", "Monthly limit updated!")
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number")

# -------------------------------
# Calculate total spent this month
# -------------------------------
def get_month_total():
    total = 0
    with open(EXPENSE_FILE, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 3:
                total += float(row[1])
    return total

# -------------------------------
# Update summary labels
# -------------------------------
def update_summary():
    total_spent = get_month_total()
    limit = load_limit()
    remaining = limit - total_spent

    total_label.config(text=f"Total Spent This Month: ₹{total_spent:.2f}")
    balance_label.config(text=f"Remaining Balance: ₹{remaining:.2f}")

    # Change color if over limit
    if remaining < 0:
        balance_label.config(fg="red")
    else:
        balance_label.config(fg="green")

# -------------------------------
# Load expenses into listbox
# -------------------------------
def load_expenses():
    expense_list.delete(0, tk.END)
    with open(EXPENSE_FILE, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 3:
                expense_list.insert(
                    tk.END, f"{row[0]} | ₹{row[1]} | {row[2]}"
                )
    update_summary()

# -------------------------------
# Add new expense
# -------------------------------
def add_expense():
    amount = amount_entry.get()
    category = category_var.get()

    if not amount:
        messagebox.showerror("Error", "Please enter amount")
        return

    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Error", "Amount must be a number")
        return

    date = datetime.now().strftime("%Y-%m-%d")

    with open(EXPENSE_FILE, "a", newline="") as f:
        csv.writer(f).writerow([date, amount, category])

    amount_entry.delete(0, tk.END)
    load_expenses()

# -------------------------------
# Delete selected expense
# -------------------------------
def delete_expense():
    selected = expense_list.curselection()
    if not selected:
        messagebox.showerror("Error", "Select an expense to delete")
        return

    index = selected[0]

    with open(EXPENSE_FILE, "r") as f:
        rows = list(csv.reader(f))

    rows.pop(index)

    with open(EXPENSE_FILE, "w", newline="") as f:
        csv.writer(f).writerows(rows)

    load_expenses()

# -------------------------------
# Show category pie chart
# -------------------------------
def show_pie_chart():
    data = {}
    with open(EXPENSE_FILE, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 3:
                category = row[2]
                data[category] = data.get(category, 0) + float(row[1])

    if not data:
        messagebox.showinfo("Info", "No expenses to show")
        return

    plt.figure(figsize=(6,6))
    plt.pie(data.values(), labels=data.keys(), autopct="%1.1f%%")
    plt.title("Expenses by Category")
    plt.show()

# -------------------------------
# GUI Setup
# -------------------------------
root = tk.Tk()
root.title("Expense Tracker")
root.geometry("460x560")

# Monthly limit
tk.Label(root, text="Monthly Limit (₹)").pack(pady=(10,0))
limit_entry = tk.Entry(root)
limit_entry.pack()
limit_entry.insert(0, load_limit())
tk.Button(root, text="Save Limit", command=save_limit).pack(pady=5)

# Summary labels
total_label = tk.Label(root, text="Total Spent This Month: ₹0")
total_label.pack()
balance_label = tk.Label(root, text="Remaining Balance: ₹0", fg="green")
balance_label.pack(pady=5)

# Add new expense
tk.Label(root, text="Amount").pack(pady=(10,0))
amount_entry = tk.Entry(root)
amount_entry.pack()

tk.Label(root, text="Category").pack(pady=(10,0))
category_var = tk.StringVar(value=CATEGORIES[0])
tk.OptionMenu(root, category_var, *CATEGORIES).pack()

tk.Button(root, text="Add Expense", command=add_expense).pack(pady=10)

# Expense list
expense_list = tk.Listbox(root, width=50)
expense_list.pack(pady=10)

# Buttons
tk.Button(root, text="Delete Selected", command=delete_expense).pack(pady=5)
tk.Button(root, text="Category Pie Chart", command=show_pie_chart).pack(pady=5)

# Load data on start
load_expenses()

root.mainloop()
