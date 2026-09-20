import mysql.connector
from datetime import date, datetime
import calendar

def connect_root():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345"
    )

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345",
        database="expense_tracker"
    )

def init_db():
    db = connect_root()
    cur = db.cursor()
    cur.execute("CREATE DATABASE IF NOT EXISTS expense_tracker")
    db.commit()
    db.close()

    db = connect_db()
    cur = db.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date DATE,
            category VARCHAR(50),
            amount DECIMAL(10,2),
            description VARCHAR(255)
        )
    """)
    db.commit()
    db.close()


def add_expense():
    db = connect_db()
    cur = db.cursor()

    dt = input("Enter date (YYYY-MM-DD) or press Enter for today: ")
    if dt == "":
        dt = date.today()
    else:
        try:
            dt = datetime.strptime(dt, "%Y-%m-%d").date()
        except ValueError:
            print("❌ Invalid date format!\n")
            db.close()
            return

    try:
        amount = float(input("Enter amount: "))
    except ValueError:
        print("❌ Invalid amount!\n")
        db.close()
        return

    category = input("Enter category: ")
    desc = input("Enter description: ")

    cur.execute(
        "INSERT INTO expenses (date, category, amount, description) VALUES (%s, %s, %s, %s)",
        (dt, category, amount, desc)
    )
    db.commit()
    db.close()
    print("✅ Expense added!\n")


def view_expenses():
    db = connect_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM expenses ORDER BY id")
    data = cur.fetchall()

    if not data:
        print("No expenses found.\n")
        db.close()
        return

    print("\nID | Date | Category | Amount | Description")
    print("----------------------------------------------")
    for row in data:
        print(f"{row[0]} | {row[1]} | {row[2]} | ₹{row[3]} | {row[4]}")
    print("----------------------------------------------\n")
    db.close()


def update_expense():
    db = connect_db()
    cur = db.cursor()
    eid = input("Enter Expense ID to update: ")

    if not eid.isdigit():
        print("❌ Invalid ID format!\n")
        db.close()
        return

    cur.execute("SELECT * FROM expenses WHERE id=%s", (eid,))
    if not cur.fetchone():
        print("❌ ID not found!\n")
        db.close()
        return

    try:
        new_amount = float(input("Enter new amount: "))
    except ValueError:
        print("❌ Invalid amount!\n")
        db.close()
        return
    cur.execute("UPDATE expenses SET amount=%s WHERE id=%s", (new_amount, eid))
    db.commit()
    db.close()
    print("✅ Expense updated!\n")


def delete_expense():
    db = connect_db()
    cur = db.cursor()

    eids_input = input("Enter Expense IDs to delete (comma-separated): ")
    eids = [eid.strip() for eid in eids_input.split(",") if eid.strip().isdigit()]

    if not eids:
        print("❌ No valid IDs entered!\n")
        db.close()
        return

   
    cur.execute("SELECT id FROM expenses")
    existing_ids = {str(row[0]) for row in cur.fetchall()}

    invalid_ids = [eid for eid in eids if eid not in existing_ids]
    valid_ids = [eid for eid in eids if eid in existing_ids]

    if not valid_ids:
        print("❌ None of the entered IDs exist!\n")
        db.close()
        return

    for eid in valid_ids:
        cur.execute("DELETE FROM expenses WHERE id=%s", (eid,))
    db.commit()

    
    cur.execute("SELECT COUNT(*) FROM expenses")
    if cur.fetchone()[0] == 0:
        cur.execute("ALTER TABLE expenses AUTO_INCREMENT = 1")
        db.commit()

    db.close()
    print(f"🗑️ Deleted IDs: {', '.join(valid_ids)}")
    if invalid_ids:
        print(f"⚠️ Invalid IDs not found: {', '.join(invalid_ids)}\n")
    else:
        print("✅ All selected expenses deleted!\n")


def total_expense():
    db = connect_db()
    cur = db.cursor()
    cur.execute("""
        SELECT YEAR(date), MONTH(date), SUM(amount)
        FROM expenses
        GROUP BY YEAR(date), MONTH(date)
        ORDER BY YEAR(date), MONTH(date)
    """)
    data = cur.fetchall()

    if not data:
        print("No expenses found.\n")
        db.close()
        return

    print("\n📅 Yearly Expense Summary (Month-wise)")
    current_year = None
    yearly_total = 0
    grand_total = 0

    for year, month, total in data:
        if year != current_year:
            if current_year is not None:
                print(f"  ➤ Total for {current_year}: ₹{yearly_total:.2f}\n")
            print(f"Year {year}:")
            current_year = year
            yearly_total = 0
        month_name = calendar.month_name[month]
        print(f"  {month_name}: ₹{total:.2f}")
        yearly_total += float(total)
        grand_total += float(total)

    print(f"  ➤ Total for {current_year}: ₹{yearly_total:.2f}")
    print(f"\n💰 Overall Total Expense: ₹{grand_total:.2f}\n")
    db.close()
def main():
    init_db()
    while True:
        print("=== Personal Expense Tracker ===")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Update Expense")
        print("4. Delete Expense")
        print("5. Yearly + Total Expense")
        print("6. Exit")
        choice = input("Enter choice: ")

        if choice == '1':
            add_expense()
        elif choice == '2':
            view_expenses()
        elif choice == '3':
            update_expense()
        elif choice == '4':
            delete_expense()
        elif choice == '5':
            total_expense()
        elif choice == '6':
            print("Goodbye 👋")
            break
        else:
            print("Invalid choice!\n")
if __name__ == "__main__":
    main()
