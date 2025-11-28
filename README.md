# BellaDesk – Salon Management Desktop App

BellaDesk is a lightweight Python-based desktop application built with `tkinter` to help salons manage daily operations such as customers, services, billing, and data storage. It is designed for small salons needing an offline, simple, and easy-to-use system.

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
   pip install tkinter pillow matplotlib
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
| Customers | `customers.csv` |
| Services  | `services.csv`  |
| Bills     | `bills.csv`     |

No external database or internet connection required.

---

## Key Functions (Inside the App)

* **Add Customer**
* **Add Service / View Services**
* **Save Bill to CSV**
* **Generate Charts** (daily summary, service usage, etc.)
* **Add printing and PDF bill export
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

---

If you want, I can generate:

* A more professional README
* A GitHub-optimized version with badges
* Screenshots section
* “How to Contribute” section
