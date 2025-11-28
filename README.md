# **BellaDesk – Salon Management Desktop App**

BellaDesk is a lightweight **Python Tkinter desktop application** designed for small salons to manage daily operations such as appointments, services, staff, billing, and analytics.
It is completely **offline**, uses **CSV files** as storage, and generates **professional PDF invoices and daily business reports**.

---

## **Technology Stack**

Python, Tkinter, CSV, ReportLab, Matplotlib, PIL (Pillow)

---

# **1. Overview**

BellaDesk is a simple and efficient **salon management system** built using Tkinter.
It manages daily salon workflows:

* Appointments
* Staff specialization
* Billing and discounts
* Analytics & charts
* PDF invoices and daily reports

All data is stored locally in CSV files, making the system portable and easy to run on any machine.

---

# **2. Core Functionalities**

---

## **2.1 Dashboard**

Displays:

* Total customers
* Daily income
* Most used services
* Staff performance insights
* Visual charts using Matplotlib

---

## **2.2 Appointment Management**

Users can:

* Add new appointments
* Choose multiple services
* Auto-calculate service duration
* Auto-assign qualified staff
* Check available time slots
* Save appointments to `appointments.csv`

### **Key Logic**

* Each service has a fixed time duration
* Previous appointment’s end-time determines the next slot
* Only staff who specialize in selected services appear in the list

---

## **2.3 Staff Management**

Stored in `staff.csv` with:

* Staff name
* Specialization (Haircut, Facial, Coloring, etc.)
* Salary

Specialization data is used during appointments for intelligent staff assignment.

---

## **2.4 Billing System**

Features:

* Total price calculation based on selected services
* Discount support
* On-screen bill preview
* Prevents duplicate bills for the same appointment
* Saves transaction data to `bills.csv`

### **PDF Invoice (ReportLab)**

Includes:

* Salon logo
* Customer information
* Services table with price
* Total → Discount → Final payable
* Footer message

---

## **2.5 Daily Report PDF**

Generates a **complete business summary** for any selected date:

* Total income
* Number of customers
* Most used service
* Top-performing staff
* Transaction table
* Auto-pagination for long data

---

## **2.6 File Storage System**

BellaDesk uses three simple CSV files:

| File               | Purpose                         |
| ------------------ | ------------------------------- |
| `staff.csv`        | Staff data with specialization  |
| `appointments.csv` | Appointment details             |
| `bills.csv`        | Billing and transaction history |

No database configuration required.

---

## **2.7 User Interface**

Tkinter-based interface featuring:

* Fullscreen responsive layout
* Sidebar navigation menu
* Header with app logo
* Dedicated screens for each function

Modular frames keep navigation smooth.

---

# **3. Technical Breakdown**

### **Libraries Used**

* **Tkinter** – GUI
* **PIL (Pillow)** – Image support
* **ReportLab** – PDF bills & reports
* **Matplotlib** – Dashboard visualizations
* **CSV module** – Data storage
* **Datetime** – Scheduling logic
* **OS** – File handling

---

# **4. Business Value**

BellaDesk helps salons:

* Automate appointment scheduling
* Reduce manual errors
* Track income and staff performance
* Generate professional invoices
* Produce daily business reports
* Maintain organized service records

---

# **5. Short Summary Description**

BellaDesk is a Python Tkinter-based salon management application with features for appointments, staff specialization, billing, analytics, and PDF reporting. It uses CSV files for storage and integrates Pillow, Matplotlib, and ReportLab for images, charts, and invoice generation. The system automates scheduling, assigns skilled staff, and provides dashboards and printable business reports.

---

# **6. Feature List**

* Customer & appointment management
* Multiple service selection
* Automated billing
* CSV-based data storage
* Dashboard statistics
* PDF invoice generation
* PDF daily business report
* Matplotlib charts inside Tkinter
* Pop-up confirmations
* Clean and simple UI

---

# **7. Technologies Used**

* Python
* Tkinter
* CSV
* Pillow (optional)
* ReportLab
* Matplotlib

---

# **8. Project Structure (Linear)**

```
BDUI.py
appointments.csv
staff.csv
bills.csv
logo.png
```

All core logic resides in the main file: `BDUI.py`.

---

# **9. How to Run**

1. Install Python 3.8+
2. Install dependencies:

   ```sh
   pip install pillow matplotlib reportlab
   ```
3. Run the application:

   ```sh
   python BDUI.py
   ```

---

# **10. Data Storage Explanation**

| Purpose              | File               |
| -------------------- | ------------------ |
| Appointment records  | `appointments.csv` |
| Staff data           | `staff.csv`        |
| Billing transactions | `bills.csv`        |

The app works completely offline with no database setup required.

---

# **11. Key App Functions**

* Add customer
* Select services
* Generate bill
* Save data to CSV
* Display charts
* Print and export PDF
* Exit confirmations
* Success pop-up notifications

Example pop-up:

```python
messagebox.showinfo("Success", "All data saved successfully!")
```

---

# **12. Future Improvements**

* Shift from CSV to SQLite or MongoDB
* Add login/authentication
* Cloud sync for multi-device use
* Enhanced staff analytics

---

# **License**

Free to use for learning and personal projects.
