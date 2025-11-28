# BellaDesk – Salon Management Desktop App

BellaDesk is a lightweight Python-based desktop application built with `tkinter` to help salons manage daily operations such as customers, services, billing, and data storage. It is designed for small salons needing an offline, simple, and easy-to-use system.

---

**Technology:** Python, Tkinter, CSV, ReportLab, Matplotlib, PIL

## 1. Overview

BellaDesk is a **desktop-based salon management system** built using Tkinter. It handles daily salon operations such as **appointments, staff management, billing, analytics, and PDF report generation**.
The app uses **CSV files as a lightweight database**, and **ReportLab** to generate invoices & daily business reports.

---

## 2. Core Functionalities

### 2.1 Dashboard

Displays:

* Total customers
* Total income
* Most used services
* Staff performance
* Daily analytics using Matplotlib charts

---

## 2.2 Appointment Management

Users can:

* Add new appointments
* Select multiple services
* Automatically calculate service time duration
* Auto-assign qualified staff based on service specialization
* Auto-generate next available time slot
* Store all appointments in `appointments.csv`

### Key Logic

* Each service has fixed duration
* Last appointment’s end-time decides next appointment slot
* Only staff who *specialize* in selected services are listed

---

## 2.3 Staff Management

Stores details in `staff.csv`.

Staff data includes:

* Name
* Specialization (Haircut, Coloring, Facial etc.)
* Salary

Users can add/edit staff, and staff qualifications are used during appointment creation.

---

## 2.4 Billing System

Features:

* Calculates total amount based on selected services
* Applies discounts
* Generates invoice on screen
* Saves all bills in `bills.csv`
* Prevents duplicate bill generation (one bill per appointment)

### PDF Invoice (ReportLab)

Invoice contains:

* Logo
* Customer details
* Appointment details
* Services & prices
* Total, discount, final payable
* Footer message

---

## 2.5 Daily Report PDF

Generates a **business report for any selected date** showing:

* Total income
* Total customers
* Most used service
* Top-performing staff
* Table of all transactions
* Auto-pagination

---

## 2.6 File Storage System

Your app uses three CSV files:

| File               | Purpose                                  |
| ------------------ | ---------------------------------------- |
| `staff.csv`        | Store staff name, specialization, salary |
| `appointments.csv` | Store all booked appointments            |
| `bills.csv`        | Store generated bills for analytics      |

No SQL database is used, making the app portable and lightweight.

---

## 2.7 UI/UX

Built with Tkinter:

* Fullscreen responsive window
* Sidebar navigation (Dashboard, Appointments, Staff, Billing, Reports)
* Header with app branding and logo
* Modular frames for easy navigation

---

## 3. Technical Breakdown

### Libraries Used

* **Tkinter** → GUI
* **PIL (Pillow)** → Image handling
* **ReportLab** → PDF generation
* **Matplotlib** → Dashboard charts
* **CSV module** → Local data storage
* **Datetime** → Scheduling logic
* **OS** → File handling

---

## 4. Business Value

BellaDesk helps salons to:

* Automate appointments
* Reduce manual scheduling
* Track income & performance
* Produce professional invoices
* Generate daily business reports
* Maintain staff and service records

---

## 5. Summary Description (Short Version)

BellaDesk is a Python Tkinter-based salon management system that manages appointments, staff specialization, billing, analytics, and PDF reporting. It uses CSV files for storage and integrates Pillow, Matplotlib, and ReportLab for images, charts, and invoice generation. The system automates customer scheduling, assigns qualified staff, provides business dashboards, and produces professional invoices and daily reports.

---

## Features

* Customer details entry
* Service selection and bill generation
* CSV-based data storage (no database required)
* Dashboard with basic statistics
* Pop-up notifications (e.g., **“Data saved successfully”**)
* Image support using Pillow (optional)
* Matplotlib charts integrated inside Tkinter
* Clean and interactive user interface

---

## Technologies Used

* Python
* tkinter
* CSV
* Pillow *(optional)*
* Matplotlib

---

## Project Structure (Simple Linear)

```
BDUI.py
appointments.csv
staff.csv
bills.csv
logo.png
```

All core logic is inside a single main file: **BDUI.py**.

---

## How to Run

1. Install Python 3.8+
2. Install dependencies:

   ```sh
   pip install tkinter pillow matplotlib reportlab
   ```
3. Run the application:

   ```sh
   python BDUI.py
   ```

---

## How Data is Stored

BellaDesk stores all data locally in CSV files:

| Purpose   | File Name       |
| --------- | --------------- |
| Appointments | `appointments.csv` |
| Staff  | `staff.csv`  |
| Bills     | `bills.csv`     |

No external database or internet connection required.

---

## Key Functions (Inside the App)

* **Add Customer**
* **Add Service / View Services**
* **Save Bill to CSV**
* **Generate Charts** (daily summary, service usage, etc.)
* **Add printing and PDF bill export**
* **Exit Confirmation + Success Popups**

---

## Example Popup

Uses:

```python
messagebox.showinfo("Success", "All data saved successfully!")
```

---

## Future Improvements

* Shift from CSV to a database (SQLite or MongoDB)
* Add authentication/login
* Add cloud sync

---

## License

This project is free to use for learning and personal projects.

