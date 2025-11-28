import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import csv
import os
import datetime
from collections import Counter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Optional imports
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False

# ----------------- Configuration / Files -----------------
STAFF_FILE = "staff.csv"
APPT_FILE = "appointments.csv"
BILL_FILE = "bills.csv"

# Use uploaded logo (developer-provided file)
LOGO_PATH = "D:/New folder/Salon_Management_System/logo.png"

# ----------------- Data Structures -----------------
Appointments = []
Next_id = 1
Limit = 500

staffNames = []
staffSpecs = []
staffSalaries = []

# Service catalog (name -> price)
services_catalog = {
    "Haircut": 80,
    "Shaving": 150,
    "Hair Coloring": 100,
    "Facial": 200,
    "Manicure": 400,
    "Pedicure": 300,
    "Massage": 200
}

service_duration = {
    "Haircut": 30,
    "Shaving": 15,
    "Hair Coloring": 90,
    "Facial": 45,
    "Manicure": 30,
    "Pedicure": 45,
    "Massage": 60
}

# ----------------- File IO -----------------
def save_staff():
    with open(STAFF_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Specialization", "Salary"])
        for i in range(len(staffNames)):
            writer.writerow([staffNames[i], staffSpecs[i], staffSalaries[i]])

def load_staff():
    staffNames.clear(); staffSpecs.clear(); staffSalaries.clear()
    try:
        with open(STAFF_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                staffNames.append(row.get("Name",""))
                staffSpecs.append(row.get("Specialization",""))
                try:
                    staffSalaries.append(int(row.get("Salary",0)))
                except ValueError:
                    staffSalaries.append(0)
    except FileNotFoundError:
        # default sample staff if file missing
        staffNames.extend(["Asha", "Rohit"])
        staffSpecs.extend(["Haircut,Shaving", "Haircut,Hair Coloring,Facial"])
        staffSalaries.extend([15000, 18000])
        save_staff()

def save_appointments():
    with open(APPT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID","Name","Services","Date","Time","Staff"])
        for a in Appointments:
            writer.writerow([a["id"], a["name"], ";".join(a["services"]), a["date"], a["time"], a["staff"]])

def load_appointments():
    global Next_id
    Appointments.clear()
    try:
        with open(APPT_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                services = row.get("Services","").split(";") if row.get("Services") else []
                Appointments.append({
                    "id": int(row.get("ID",0)),
                    "name": row.get("Name",""),
                    "services": services,
                    "date": row.get("Date",""),
                    "time": row.get("Time",""),
                    "staff": row.get("Staff","")
                })
        if Appointments:
            Next_id = max(a["id"] for a in Appointments) + 1
    except FileNotFoundError:
        Next_id = 1

def save_bill_record(appointment, total, discount_amt, final_amt):
    today = datetime.date.today().strftime("%Y-%m-%d")
    file_exists = os.path.exists(BILL_FILE)
    headers = ["ID","Name","Staff","Services","Total","Discount","Final","Date"]
    with open(BILL_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists or os.stat(BILL_FILE).st_size == 0:
            writer.writerow(headers)
        writer.writerow([appointment["id"], appointment["name"], appointment["staff"], ";".join(appointment["services"]), total, discount_amt, final_amt, today])

# ----------------- Utilities -----------------
def total_time(services):
    return sum(service_duration.get(s, 30) for s in services)

def next_time_slot_for_services(services):
    if not Appointments:
        return datetime.datetime.now()
    def appt_dt(a):
        return datetime.datetime.strptime(a["date"] + " " + a["time"], "%Y-%m-%d %H:%M")
    last = max(Appointments, key=appt_dt)
    last_start = appt_dt(last)
    slot = last_start + datetime.timedelta(minutes=total_time(last["services"]))
    return max(slot, datetime.datetime.now())

def find_qualified_staff(selected_services):
    qualified = []
    for i in range(len(staffNames)):
        staff_services = [s.strip().lower() for s in staffSpecs[i].split(',')]
        if all(s.lower() in staff_services for s in selected_services):
            qualified.append(staffNames[i])
    return qualified

# ----------------- PDF helpers (reportlab) -----------------
def create_invoice_pdf(path, appointment, total, discount_amt, final_amt):
    if not REPORTLAB_AVAILABLE:
        raise RuntimeError("reportlab not installed")

    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4

    margin = 20 * mm
    x_left = margin
    x_right = width - margin
    y = height - margin

    # ----------------------------------------------------------
    # 1. LOGO (Top Right)
    # ----------------------------------------------------------
    if PIL_AVAILABLE and os.path.exists(LOGO_PATH):
        try:
            img = Image.open(LOGO_PATH)
            img_w, img_h = img.size
            scale = (80 * mm) / img_w
            resized = img.resize((int(img_w * scale), int(img_h * scale)))
            temp_logo_path = path + "_tmp_logo.png"
            resized.save(temp_logo_path)
            c.drawImage(temp_logo_path, x_right - (img_w * scale), y - 40 * mm, mask='auto')
            os.remove(temp_logo_path)
        except Exception:
            pass

    # ----------------------------------------------------------
    # 2. TITLE
    # ----------------------------------------------------------
    c.setFont("Helvetica-Bold", 20)
    c.drawString(x_left, y - 20, "BellaDesk Invoice")

    # Horizontal line
    c.line(x_left, y - 28, x_right, y - 28)

    # ----------------------------------------------------------
    # 3. CUSTOMER DETAILS
    # ----------------------------------------------------------
    y_info = y - 55
    c.setFont("Helvetica", 10)

    details = [
        ("Invoice Date", datetime.date.today().strftime("%Y-%m-%d")),
        ("Customer", appointment["name"]),
        ("Appointment ID", str(appointment["id"])),
        ("Staff", appointment["staff"]),
        ("Date & Time", f"{appointment['date']} {appointment['time']}")
    ]

    for label, value in details:
        c.drawString(x_left, y_info, f"{label}: {value}")
        y_info -= 14

    # ----------------------------------------------------------
    # 4. SERVICES TABLE
    # ----------------------------------------------------------
    y_info -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x_left, y_info, "Services")
    c.drawString(x_left + 300, y_info, "Price (Rupees)")
    y_info -= 14

    c.setFont("Helvetica", 10)

    for srv in appointment["services"]:
        price = services_catalog.get(srv, 0)
        c.drawString(x_left, y_info, f"- {srv}")
        c.drawString(x_left + 300, y_info, f"{price:.2f}")
        y_info -= 14

    # ----------------------------------------------------------
    # 5. TOTALS SECTION (Box Format)
    # ----------------------------------------------------------
    y_info -= 20
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x_left, y_info, f"Total Amount: Rupees {total:.2f}")
    y_info -= 14
    c.drawString(x_left, y_info, f"Discount: Rupees {discount_amt:.2f}")
    y_info -= 14
    c.drawString(x_left, y_info, f"Final Payable: Rupees {final_amt:.2f}")

    # ----------------------------------------------------------
    # 6. FOOTER
    # ----------------------------------------------------------
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(x_left, 30, "Thank you for choosing BellaDesk Beauty Studio!")
    c.drawString(x_left, 18, "This is a computer generated invoice.")

    # Final save
    c.showPage()
    c.save()

def create_daily_report_pdf(path, report_date, rows, totals):
    if not REPORTLAB_AVAILABLE:
        raise RuntimeError("reportlab not installed")
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    margin = 20*mm
    x = margin
    y = height - margin

    c.setFont("Helvetica-Bold", 16)
    c.drawString(x, y - 10, f"BellaDesk Daily Report - {report_date}")
    c.setFont("Helvetica", 10)
    y_line = y - 40
    c.drawString(x, y_line, f"Total Income: Rs {totals['income']:.2f}")
    c.drawString(x+250, y_line, f"Total Customers: {totals['customers']}")
    y_line -= 20

    c.setFont("Helvetica-Bold", 11)
    c.drawString(x, y_line, "Top Service")
    c.drawString(x+150, y_line, "Top Staff")
    y_line -= 14
    c.setFont("Helvetica", 10)
    c.drawString(x, y_line, totals.get("top_service","-"))
    c.drawString(x+150, y_line, totals.get("top_staff","-"))
    y_line -= 26

    # table header
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y_line, "ID")
    c.drawString(x+40, y_line, "Name")
    c.drawString(x+200, y_line, "Services")
    c.drawString(x+420, y_line, "Final")
    y_line -= 12
    c.setFont("Helvetica", 9)
    for r in rows:
        c.drawString(x, y_line, str(r.get("ID","")))
        c.drawString(x+40, y_line, str(r.get("Name",""))[:20])
        c.drawString(x+200, y_line, str(r.get("Services",""))[:30])
        c.drawString(x+420, y_line, str(r.get("Final","")))
        y_line -= 12
        if y_line < 60:
            c.showPage()
            y_line = height - margin

    c.showPage()
    c.save()

def bill_exists(appointment_id):
    if not os.path.exists(BILL_FILE):
        return False
    with open(BILL_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if str(row.get("ID")) == str(appointment_id):
                return True
    return False

# ----------------- Main GUI App -----------------
class BellaDeskApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BellaDesk Management System")
        w = self.winfo_screenwidth()
        h = self.winfo_screenheight()
        self.geometry(f"{w}x{h}")
        self.configure(bg="#f6f7f9")

        load_staff()
        load_appointments()

        self.create_header()
        self.create_sidebar()
        self.create_frames()
        self.active_frame = None
        self.show_dashboard()

    def create_header(self):
        header = tk.Frame(self, bg="#2f3640", height=68)
        header.pack(side="top", fill="x")
        # logo
        if PIL_AVAILABLE and os.path.exists(LOGO_PATH):
            try:
                img = Image.open(LOGO_PATH)
                img = img.resize((200,52), Image.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(img)
                tk.Label(header, image=self.logo_img, bg="#2f3640").pack(side="left", padx=12)
            except Exception:
                pass
        tk.Label(header, text="Welcome to Belladesk's Beauty Studio", bg="#2f3640", fg="white", font=("Arial", 18, "bold")).pack(side="left", padx=10)

    def create_sidebar(self):
        sidebar = tk.Frame(self, bg="#2f3640", width=230)
        sidebar.pack(side="left", fill="y")
        tk.Label(sidebar, text="BELLADESK", bg="#2f3640", fg="white", font=("Arial", 20, "bold")).pack(pady=24)
        buttons = [
            ("Dashboard", self.show_dashboard),
            ("Appointments", self.show_appointments),
            ("Staff", self.show_staff),
            ("Billing", self.show_billing),
            ("Daily Report", self.show_daily_report),
            ("Exit", self.quit)
        ]
        for (txt, cmd) in buttons:
            tk.Button(sidebar, text=txt, bg="#353b48", fg="white", font=("Arial", 13), bd=0, relief="flat", activebackground="#40739e", activeforeground="white", command=cmd).pack(fill="x", padx=14, pady=8)

    def create_frames(self):
        self.container = tk.Frame(self, bg="#f6f7f9")
        self.container.pack(fill="both", expand=True, padx=10, pady=10)

        self.dashboard_frame = DashboardFrame(self.container, self)
        self.appointment_frame = AppointmentFrame(self.container, self)
        self.staff_frame = StaffFrame(self.container, self)
        self.billing_frame = BillingFrame(self.container, self)
        self.daily_report_frame = DailyReportFrame(self.container, self)

    def switch_frame(self, frame):
        if self.active_frame:
            self.active_frame.pack_forget()
        self.active_frame = frame
        self.active_frame.pack(fill="both", expand=True)

    def show_dashboard(self):
        self.switch_frame(self.dashboard_frame)
    def show_appointments(self):
        self.switch_frame(self.appointment_frame)
    def show_staff(self):
        self.switch_frame(self.staff_frame)
    def show_billing(self):
        self.switch_frame(self.billing_frame)
    def show_daily_report(self):
        self.switch_frame(self.daily_report_frame)

# ----------------- Frames -----------------
class DashboardFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")

        # -------------------------
        # WELCOME BANNER
        # -------------------------
        greeting = self.get_greeting()
        tk.Label(
            self,
            text=f"{greeting}, Welcome to BellaDesk!",
            font=("Arial", 22, "bold"),
            bg="white",
            fg="#2f3640"
        ).pack(pady=20)

        # -------------------------
        # KPI CARDS (Top Stats)
        # -------------------------
        kpi_frame = tk.Frame(self, bg="white")
        kpi_frame.pack(pady=10)

        total_appt = len(Appointments)
        total_staff = len(staffNames)
        total_income = self.calculate_total_income()

        today_count = self.today_appointments()

        cards = [
            ("Total Appointments", total_appt, "#0984e3"),
            ("Total Staff", total_staff, "#6c5ce7"),
            ("Revenue Collected", f"Rs. {total_income}", "#00b894"),
            ("Today's Bookings", today_count, "#d63031"),
        ]

        for title, value, color in cards:
            self.create_kpi_card(kpi_frame, title, value, color)

        # -------------------------
        # CHARTS
        # -------------------------
        chart_frame = tk.Frame(self, bg="white")
        chart_frame.pack(fill="both", expand=True, pady=10)

        # Left Chart → Service Popularity
        self.service_popularity_chart(chart_frame)

        # Right Chart → Monthly Revenue Trend
        self.monthly_revenue_chart(chart_frame)

    # -------------------------
    # HELPERS
    # -------------------------
    def get_greeting(self):
        hour = datetime.datetime.now().hour
        if hour < 12:
            return "Good Morning"
        elif hour < 17:
            return "Good Afternoon"
        else:
            return "Good Evening"

    def calculate_total_income(self):
        total = 0
        if not os.path.exists(BILL_FILE):
            return 0
        with open(BILL_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                try:
                    total += float(r.get("Final", 0))
                except:
                    pass
        return int(total)

    def today_appointments(self):
        today = datetime.date.today().strftime("%Y-%m-%d")
        return sum(1 for a in Appointments if a["date"] == today)

    # KPI card box
    def create_kpi_card(self, parent, title, value, color):
        frame = tk.Frame(parent, bg=color, width=200, height=100)
        frame.pack(side="left", padx=15)

        tk.Label(frame, text=title, bg=color, fg="white",
                 font=("Arial", 12, "bold")).pack(pady=8)
        tk.Label(frame, text=value, bg=color, fg="white",
                 font=("Arial", 18, "bold")).pack()

    # -------------------------
    # CHART 1: Service Popularity
    # -------------------------
    def service_popularity_chart(self, parent):
        service_count = Counter()

        if os.path.exists(BILL_FILE):
            with open(BILL_FILE, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    for s in row.get("Services", "").split(";"):
                        service_count[s.strip()] += 1

        fig = Figure(figsize=(7.5, 6.5), dpi=90)
        ax = fig.add_subplot(111)

        if service_count:
            services = list(service_count.keys())
            values = list(service_count.values())
            ax.bar(services, values)
            ax.set_title("Service Popularity")
            ax.set_ylabel("Total Bookings")
            ax.set_xticks(range(len(services)))
            ax.set_xticklabels(services, rotation=25)
        else:
            ax.text(0.3, 0.5, "No data", fontsize=14)

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.get_tk_widget().pack(side="left", padx=20)

    # -------------------------
    # CHART 2: Monthly Revenue Trend
    # -------------------------
    def monthly_revenue_chart(self, parent):
        monthly = {}

        if os.path.exists(BILL_FILE):
            with open(BILL_FILE, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    date = row.get("Date", "")
                    if not date:
                        continue
                    month = date[:7]   # YYYY-MM
                    try:
                        monthly[month] = monthly.get(month, 0) + float(row.get("Final", 0))
                    except:
                        pass

        fig = Figure(figsize=(7.5, 6.5), dpi=90)
        ax = fig.add_subplot(111)

        if monthly:
            months = list(monthly.keys())
            revenue = list(monthly.values())
            ax.plot(months, revenue, marker="o")
            ax.set_title("Monthly Revenue Trend")
            ax.set_ylabel("Revenue (Rupees)")
            ax.set_xticks(range(len(months)))
            ax.set_xticklabels(months, rotation=25)
        else:
            ax.text(0.3, 0.5, "No data", fontsize=14)

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.get_tk_widget().pack(side="right", padx=20)

class AppointmentFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        tk.Label(self, text="APPOINTMENTS MANAGEMENT", font=("Arial", 16, "bold"), bg="white").pack(pady=8)
        frame = tk.Frame(self, bg="white")
        frame.pack(fill="both", expand=True, padx=12, pady=8)

        # left form
        left = tk.Frame(frame, bg="white", bd=1, relief="solid")
        left.place(x=10, y=10, width=360, height=560)
        tk.Label(left, text="Book Appointment", bg="white", font=("Arial", 12, "bold")).pack(pady=8)
        tk.Label(left, text="Customer Name:", bg="white").pack(anchor="w", padx=8)
        self.name_var = tk.StringVar()
        tk.Entry(left, textvariable=self.name_var).pack(fill="x", padx=8, pady=4)
        tk.Label(left, text="Select Services (Ctrl+Click):", bg="white").pack(anchor="w", padx=8)
        self.serv_listbox = tk.Listbox(left, selectmode="multiple", exportselection=False, height=8)
        for s in services_catalog.keys():
            self.serv_listbox.insert("end", s)
        self.serv_listbox.pack(fill="both", padx=8, pady=4)
        tk.Label(left, text="Suggested Slot:", bg="white").pack(anchor="w", padx=8)
        self.sugg_var = tk.StringVar(value="(Select services -> Suggest Slot)")
        tk.Label(left, textvariable=self.sugg_var, bg="white", fg="#2f3640").pack(anchor="w", padx=8)
        tk.Label(left, text="Assign Staff (optional):", bg="white").pack(anchor="w", padx=8, pady=(8,0))
        self.staff_cb_var = tk.StringVar()
        self.staff_cb = ttk.Combobox(left, textvariable=self.staff_cb_var, state="readonly")
        self.staff_cb['values'] = ["-- Auto --"] + staffNames
        self.staff_cb.current(0)
        self.staff_cb.pack(fill="x", padx=8, pady=4)
        tk.Button(left, text="Suggest Slot", command=self.suggest_slot).pack(pady=6)
        tk.Button(left, text="Book", bg="#44bd32", fg="white", command=self.book_action).pack(pady=6)
        tk.Button(left, text="Enroll Staff", command=self.enroll_staff_dialog).pack(pady=6)

        # right table
        right = tk.Frame(frame, bg="white")
        right.place(x=380, y=10, width=850, height=560)
        cols = ("ID","Name","Services","Date","Time","Staff")
        self.tree = ttk.Treeview(right, columns=cols, show="headings", height=20)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=110, anchor="center")
        self.tree.column("Services", width=260, anchor="w")
        self.tree.column("Name", width=140, anchor="w")
        self.tree.pack(fill="both", padx=8, pady=8)
        ctl = tk.Frame(right, bg="white")
        ctl.pack(fill="x", padx=8, pady=6)
        tk.Button(ctl, text="Refresh", command=self.refresh).pack(side="left", padx=6)
        tk.Button(ctl, text="View", command=self.view_appt).pack(side="left", padx=6)
        tk.Button(ctl, text="Reschedule", command=self.reschedule).pack(side="left", padx=6)
        tk.Button(ctl, text="Cancel", command=self.cancel).pack(side="left", padx=6)
        self.refresh()

    def get_selected_services(self):
        sel = self.serv_listbox.curselection()
        return [self.serv_listbox.get(i) for i in sel]

    def suggest_slot(self):
        services = self.get_selected_services()
        if not services:
            messagebox.showwarning("Select", "Select services first.")
            return
        slot = next_time_slot_for_services(services).replace(second=0, microsecond=0)
        self.sugg_var.set(slot.strftime("%Y-%m-%d %H:%M"))

    def enroll_staff_dialog(self):
        name = simpledialog.askstring("Staff Name", "Name:", parent=self)
        if not name:
            return
        spec = simpledialog.askstring("Specialization", "Comma separated services:", parent=self)
        if spec is None:
            return
        salary = simpledialog.askstring("Salary", "Salary (int):", parent=self)
        try:
            sal = int(salary) if salary else 0
        except Exception:
            sal = 0
        staffNames.append(name); staffSpecs.append(spec); staffSalaries.append(sal)
        save_staff()
        self.staff_cb['values'] = ["-- Auto --"] + staffNames
        messagebox.showinfo("Done", "Staff enrolled.")

    def insert_sorted(self, appt):
        new_dt = datetime.datetime.strptime(appt["date"] + " " + appt["time"], "%Y-%m-%d %H:%M")
        for i, ex in enumerate(Appointments):
            ex_dt = datetime.datetime.strptime(ex["date"] + " " + ex["time"], "%Y-%m-%d %H:%M")
            if new_dt < ex_dt:
                Appointments.insert(i, appt)
                return
        Appointments.append(appt)

    def book_action(self):
        global Next_id
        name = self.name_var.get().strip()
        if not name or not name.replace(" ", "").isalpha():
            messagebox.showerror("Invalid", "Enter valid name")
            return
        services = self.get_selected_services()
        if not services:
            messagebox.showerror("Invalid", "Select services")
            return
        # determine slot
        sugg = self.sugg_var.get()
        if sugg and "Select" not in sugg:
            try:
                slot = datetime.datetime.strptime(sugg, "%Y-%m-%d %H:%M")
            except Exception:
                slot = next_time_slot_for_services(services)
        else:
            slot = next_time_slot_for_services(services)
        date = slot.strftime("%Y-%m-%d"); time = slot.strftime("%H:%M")
        staff_choice = self.staff_cb_var.get()
        if staff_choice and staff_choice != "-- Auto --":
            staff_assigned = staff_choice
        else:
            q = find_qualified_staff(services)
            staff_assigned = q[0] if q else "Not Assigned"
        appt = {"id": Next_id, "name": name, "services": services, "date": date, "time": time, "staff": staff_assigned}
        self.insert_sorted(appt)
        Next_id += 1
        save_appointments()
        self.refresh()
        messagebox.showinfo("Booked", f"Appointment booked for {name} at {date} {time} with {staff_assigned}")
        self.name_var.set(""); self.serv_listbox.selection_clear(0, "end"); self.sugg_var.set("(Select services -> Suggest Slot)")

    def refresh(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        for a in Appointments:
            self.tree.insert("", "end", values=(a["id"], a["name"], ", ".join(a["services"]), a["date"], a["time"], a["staff"]))
    def view_appt(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select an appointment")
            return
        vals = self.tree.item(sel[0], "values")
        aid = int(vals[0])
        appt = next((x for x in Appointments if x["id"]==aid), None)
        if not appt:
            messagebox.showerror("Not found", "Appointment not found")
            return
        messagebox.showinfo("Details", f"ID:{appt['id']}\nName:{appt['name']}\nServices:{', '.join(appt['services'])}\nDate:{appt['date']} {appt['time']}\nStaff:{appt['staff']}")

    def reschedule(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select an appointment")
            return
        vals = self.tree.item(sel[0], "values")
        aid = int(vals[0])
        idx = next((i for i,a in enumerate(Appointments) if a["id"]==aid), None)
        if idx is None:
            messagebox.showerror("Error", "Not found")
            return
        new_date = simpledialog.askstring("New Date", "YYYY-MM-DD:", parent=self)
        if not new_date:
            return
        new_time = simpledialog.askstring("New Time", "HH:MM:", parent=self)
        if not new_time:
            return
        try:
            datetime.datetime.strptime(new_date, "%Y-%m-%d"); datetime.datetime.strptime(new_time, "%H:%M")
        except Exception:
            messagebox.showerror("Format", "Invalid format")
            return
        for ex in Appointments:
            if ex["date"]==new_date and ex["time"]==new_time:
                messagebox.showwarning("Collision", "Slot exists")
                return
        appt = Appointments.pop(idx)
        appt["date"] = new_date; appt["time"] = new_time
        self.insert_sorted(appt)
        save_appointments()
        self.refresh()
        messagebox.showinfo("Done", "Rescheduled")

    def cancel(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select an appointment")
            return
        vals = self.tree.item(sel[0], "values")
        aid = int(vals[0])
        if messagebox.askyesno("Confirm", f"Cancel ID {aid}?"):
            for a in list(Appointments):
                if a["id"]==aid:
                    Appointments.remove(a)
                    save_appointments()
                    self.refresh()
                    messagebox.showinfo("Cancelled", "Appointment cancelled")
                    return

class StaffFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        tk.Label(self, text="STAFF MANAGEMENT", font=("Arial", 16, "bold"), bg="white").pack(pady=8)
        frame = tk.Frame(self, bg="white")
        frame.pack(fill="both", expand=True, padx=12, pady=8)
        self.tree = ttk.Treeview(frame, columns=("Name","Spec","Salary"), show="headings", height=20)
        for c in ("Name","Spec","Salary"):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=200, anchor="center")
        self.tree.column("Name", width=100)
        self.tree.pack(fill="both", padx=8, pady=8)
        ctl = tk.Frame(frame, bg="white")
        ctl.pack(fill="x", padx=8, pady=6)
        tk.Button(ctl, text="Refresh", command=self.refresh).pack(side="left", padx=6)
        tk.Button(ctl, text="Add", command=self.add).pack(side="left", padx=6)
        tk.Button(ctl, text="Fire", command=self.fire).pack(side="left", padx=6)
        self.refresh()
        
    def refresh(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        for i in range(len(staffNames)):
            self.tree.insert("", "end", values=(staffNames[i], staffSpecs[i], staffSalaries[i]))

    def add(self):
        name = simpledialog.askstring("Name","Name:", parent=self)
        if not name: return
        spec = simpledialog.askstring("Spec","Comma separated services:", parent=self) or ""
        salary = simpledialog.askstring("Salary","Salary:", parent=self) or "0"
        try: sal = int(salary)
        except: sal = 2000
        staffNames.append(name); staffSpecs.append(spec); staffSalaries.append(sal)
        save_staff(); self.refresh()

    def fire(self):
        sel = self.tree.selection()
        if not sel: messagebox.showwarning("Select","Select staff")
        else:
            vals = self.tree.item(sel[0],"values")
            name = vals[0]
            if messagebox.askyesno("Confirm", f"Fire {name}?"):
                idx = staffNames.index(name)
                del staffNames[idx]; del staffSpecs[idx]; del staffSalaries[idx]
                save_staff(); self.refresh()

class BillingFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        tk.Label(self, text="BILLING SECTION", font=("Arial", 16, "bold"), bg="white").pack(pady=8)
        frame = tk.Frame(self, bg="white")
        frame.pack(fill="both", expand=True, padx=12, pady=8)

        left = tk.Frame(frame, bg="white", bd=1, relief="solid")
        left.place(x=10, y=10, width=360, height=560)
        tk.Label(left, text="Select Appointment:", bg="white").pack(anchor="w", padx=8, pady=6)
        self.appt_cb_var = tk.StringVar()
        self.appt_cb = ttk.Combobox(left, textvariable=self.appt_cb_var, state="readonly")
        self._refresh_appt_list()
        self.appt_cb.pack(fill="x", padx=8, pady=6)
        tk.Button(left, text="Load Appointment", command=self.load_selected_appointment).pack(pady=6)
        tk.Label(left, text="Services & Prices:", bg="white").pack(anchor="w", padx=8)
        self.services_text = tk.Text(left, height=10)
        self.services_text.pack(fill="x", padx=8, pady=6)
        tk.Label(left, text="Discount (%)", bg="white").pack(anchor="w", padx=8)
        self.discount_var = tk.StringVar(value="0")
        tk.Entry(left, textvariable=self.discount_var).pack(fill="x", padx=8, pady=6)
        tk.Button(left, text="Generate Invoice & Save Bill", bg="#2980b9", fg="white", command=self.generate_invoice).pack(pady=6)
        tk.Button(left, text="Clear", command=self.clear_form).pack(pady=6)

        right = tk.Frame(frame, bg="white")
        right.place(x=380, y=10, width=780, height=560)
        tk.Label(right, text="Saved Bills (recent)", bg="white", font=("Arial", 12, "bold")).pack(anchor="w", padx=8, pady=8)
        cols = ("ID","Name","Staff","Services","Total","Discount","Final","Date")
        self.bill_tree = ttk.Treeview(right, columns=cols, show="headings", height=18)
        for c in cols:
            self.bill_tree.heading(c, text=c)
            self.bill_tree.column(c, width=90)
        self.bill_tree.pack(fill="both", padx=8, pady=6)
        ctl = tk.Frame(right, bg="white")
        ctl.pack(fill="x", padx=8, pady=6)
        tk.Button(ctl, text="Refresh", command=self.refresh_bills).pack(side="left", padx=6)
        tk.Button(ctl, text="Export CSV", command=self.export_bills_csv).pack(side="left", padx=6)
        tk.Button(ctl, text="Print Selected Invoice (PDF)", command=self.print_selected_bill).pack(side="left", padx=6)
        self.refresh_bills()

    def print_selected_bill(self):
        """Generate invoice PDF for selected bill record."""
        selected = self.bill_tree.focus()
        if not selected:
            messagebox.showwarning("Print", "Select a bill first")
            return

        row = self.bill_tree.item(selected, "values")
        if not row or len(row) < 8:
            messagebox.showerror("Error", "Invalid record selected")
            return

        # --- FIX: Now includes staff so PDF will not crash ---
        appointment_dummy = {
            "id": row[0],
            "name": row[1],
            "services": row[3].split(";"),
            "date": row[7],
            "time": "",
            "staff": row[2] if row[2].strip() else "Not Assigned"   # FIXED
        }

        total = float(row[4])
        discount_amt = float(row[5])
        final_amt = float(row[6])

        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF File", "*.pdf")],
            initialfile=f"Invoice_{row[0]}.pdf"
        )

        if not save_path:
            return

        try:
            create_invoice_pdf(save_path, appointment_dummy, total, discount_amt, final_amt)
            messagebox.showinfo("Success", f"Invoice saved:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PDF:\n{e}")

    def _refresh_appt_list(self):
        opts = []
        for a in Appointments:
            opts.append(f"{a['id']} | {a['name']} | {a['date']} {a['time']}")
        if not opts:
            opts = ["No appointments"]
        self.appt_cb['values'] = opts
        self.appt_cb.current(0)

    def load_selected_appointment(self):
        sel = self.appt_cb_var.get()
        if not sel or sel.startswith("No"):
            messagebox.showwarning("Select", "No appointment selected")
            return
        aid = int(sel.split("|")[0].strip())
        appt = next((x for x in Appointments if x["id"]==aid), None)
        if not appt:
            messagebox.showerror("Error", "Appointment not found")
            return
        # display services and prices
        self.current_appt = appt
        self.services_text.delete("1.0", "end")
        total = 0
        for s in appt["services"]:
            price = services_catalog.get(s, 0)
            total += price
            self.services_text.insert("end", f"{s} - Rs {price}\n")
        self.services_text.insert("end", f"\nTotal: Rs {total}")
        self.current_total = total

    def generate_invoice(self):
        if not hasattr(self, "current_appt") or not self.current_appt:
            messagebox.showwarning("Load", "Load appointment first")
            return

        # Validate discount (must be 1–100)
        try:
            discount_pct = float(self.discount_var.get())
            if not (0 <= discount_pct <= 100):
                messagebox.showerror("Invalid Discount", "Discount must be between 1 and 100.")
                return
        except ValueError:
            messagebox.showerror("Invalid Input", "Enter a valid numeric discount.")
            return

        total = float(self.current_total)
        discount_amt = total * discount_pct / 100.0
        final_amt = total - discount_amt


        # Avoid duplicates
        if bill_exists(self.current_appt["id"]):
            messagebox.showerror("Duplicate Bill", f"Bill for Appointment ID {self.current_appt['id']} already exists.")
            return

        # save bill record
        save_bill_record(self.current_appt, total, discount_amt, final_amt)


        # generate invoice PDF
        if REPORTLAB_AVAILABLE:
            invoice_dir = filedialog.askdirectory(title="Select folder to save invoice PDF") or os.getcwd()
            fname = f"invoice_{self.current_appt['id']}_{datetime.date.today().strftime('%Y%m%d')}.pdf"
            outpath = os.path.join(invoice_dir, fname)
            try:
                create_invoice_pdf(outpath, self.current_appt, total, discount_amt, final_amt)
                messagebox.showinfo("Invoice", f"Invoice PDF generated:\n{outpath}")
            except Exception as e:
                messagebox.showwarning("PDF", f"Could not create PDF: {e}")
        else:
            messagebox.showwarning("PDF", "reportlab not installed — PDF generation skipped")

        self.refresh_bills()
        self._refresh_appt_list()

    def clear_form(self):
        self.services_text.delete("1.0", "end")
        self.discount_var.set("0")
        self.current_appt = None
        self.current_total = 0

    def refresh_bills(self):
        # load bills.csv and show recent
        for r in self.bill_tree.get_children():
            self.bill_tree.delete(r)
        try:
            with open(BILL_FILE, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                for row in reversed(rows[-200:]):
                    self.bill_tree.insert("", "end", values=(row.get("ID",""), row.get("Name",""), row.get("Staff",""), row.get("Services",""), row.get("Total",""), row.get("Discount",""), row.get("Final",""), row.get("Date","")))
        except FileNotFoundError:
            pass

    def export_bills_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")], title="Export bills to CSV")
        if not path:
            return
        try:
            with open(BILL_FILE, newline="", encoding="utf-8") as src, open(path, "w", newline="", encoding="utf-8") as dst:
                dst.write(src.read())
            messagebox.showinfo("Exported", f"Bills exported to {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not export: {e}")

    def _selected_bill(self):
        sel = self.bill_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a saved bill to ")
            return
        vals = self.bill_tree.item(sel[0], "values")
        # prepare a quick pdf from the selected row
        try:
            row = {
                "ID": vals[0], "Name": vals[1], "Staff": vals[2], "Services": vals[3], "Total": vals[4], "Discount": vals[5], "Final": vals[6], "Date": vals[7]
            }
            if not REPORTLAB_AVAILABLE:
                messagebox.showwarning("PDF", "reportlab not installed — cannot generate printable PDF")
                return
            outdir = filedialog.askdirectory(title="Select folder to save printable PDF") or os.getcwd()
            fname = f"bill_{row['ID']}_{row.get('Date','')}.pdf"
            outpath = os.path.join(outdir, fname)
            # convert services string to list for invoice routine
            appointment_dummy = {"id": row["ID"], "name": row["Name"], "services": row["Services"].split(";"), "date": row.get("Date",""), "time": ""}
            create_invoice_pdf(outpath, appointment_dummy, float(row.get("Total",0)), float(row.get("Discount",0)), float(row.get("Final",0)))
            # print using Windows call
            try:
                os.startfile(outpath, "print")
                messagebox.showinfo("Print", "Sent to printer (default).")
            except Exception as e:
                messagebox.showwarning("Print", f"Could not print: {e}\nPDF saved at: {outpath}")
        except Exception as ee:
            messagebox.showerror("Error", f"Failed: {ee}")

class DailyReportFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        tk.Label(self, text="DAILY REPORT", font=("Arial", 16, "bold"), bg="white").pack(pady=8)
        frame = tk.Frame(self, bg="white")
        frame.pack(fill="both", expand=True, padx=12, pady=8)
        ctrl = tk.Frame(frame, bg="white")
        ctrl.pack(anchor="w", padx=8, pady=8)
        tk.Label(ctrl, text="Report Date (YYYY-MM-DD):", bg="white").pack(side="left")
        self.date_var = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
        tk.Entry(ctrl, textvariable=self.date_var, width=12).pack(side="left", padx=6)
        tk.Button(ctrl, text="Generate", command=self.generate).pack(side="left", padx=6)
        tk.Button(ctrl, text="Export CSV", command=self.export_csv).pack(side="left", padx=6)
        tk.Button(ctrl, text="Export PDF", command=self.export_pdf).pack(side="left", padx=6)
        tk.Button(ctrl, text="Print PDF", command=self.print_pdf).pack(side="left", padx=6)

        # report area
        self.text = tk.Text(frame)
        self.text.pack(fill="both", expand=True, padx=8, pady=6)
        self.report_rows = []
        self.report_totals = {}

    def generate(self):
        target = self.date_var.get().strip()
        try:
            datetime.datetime.strptime(target, "%Y-%m-%d")
        except Exception:
            messagebox.showerror("Date", "Invalid date format")
            return
        rows = []
        totals = {"income": 0.0, "customers": 0}
        service_counter = Counter()
        staff_counter = Counter()
        try:
            with open(BILL_FILE, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("Date") != target:
                        continue
                    rows.append(row)
                    try:
                        totals["income"] += float(row.get("Final",0))
                        totals["customers"] += 1
                    except:
                        pass
                    for s in row.get("Services","").split(";"):
                        service_counter[s.strip()] += 1
                    staff_counter[row.get("Staff","")] += 1
        except FileNotFoundError:
            messagebox.showinfo("No Data", "No billing records found")
            return

        top_service = service_counter.most_common(1)[0][0] if service_counter else "-"
        top_staff = staff_counter.most_common(1)[0][0] if staff_counter else "-"
        totals["top_service"] = top_service
        totals["top_staff"] = top_staff

        self.report_rows = rows
        self.report_totals = totals

        # render in text
        self.text.delete("1.0", "end")
        self.text.insert("end", f"Daily Report - {target}\n")
        self.text.insert("end", f"Total Income: Rs {totals['income']:.2f}\n")
        self.text.insert("end", f"Customers Served: {totals['customers']}\n")
        self.text.insert("end", f"Top Service: {top_service}\n")
        self.text.insert("end", f"Top Staff: {top_staff}\n\n")
        self.text.insert("end", "Details:\n")
        for r in rows:
            self.text.insert("end", f"{r.get('ID','')} | {r.get('Name','')} | {r.get('Services','')} | Final: {r.get('Final','')}\n")

    def export_csv(self):
        if not self.report_rows:
            messagebox.showwarning("Generate", "Generate the report first")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")], title="Save report CSV")
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["ID","Name","Staff","Services","Total","Discount","Final","Date"])
                writer.writeheader()
                for r in self.report_rows:
                    writer.writerow(r)
            messagebox.showinfo("Exported", f"Report exported to {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not export: {e}")

    def export_pdf(self):
        if not self.report_rows:
            messagebox.showwarning("Generate", "Generate the report first")
            return
        if not REPORTLAB_AVAILABLE:
            messagebox.showwarning("PDF", "reportlab not installed")
            return
        outdir = filedialog.askdirectory(title="Select folder to save report PDF") or os.getcwd()
        fname = f"daily_report_{self.date_var.get()}.pdf"
        outpath = os.path.join(outdir, fname)
        try:
            create_daily_report_pdf(outpath, self.date_var.get(), self.report_rows, self.report_totals)
            messagebox.showinfo("Saved", f"PDF saved: {outpath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create PDF: {e}")

    def print_pdf(self):
        if not self.report_rows:
            messagebox.showwarning("Generate", "Generate the report first")
            return
        if not REPORTLAB_AVAILABLE:
            messagebox.showwarning("PDF", "reportlab not installed")
            return
        outdir = filedialog.askdirectory(title="Select folder to save temp PDF") or os.getcwd()
        fname = f"daily_report_{self.date_var.get()}.pdf"
        outpath = os.path.join(outdir, fname)
        try:
            create_daily_report_pdf(outpath, self.date_var.get(), self.report_rows, self.report_totals)
            # Windows print
            try:
                os.startfile(outpath, "print")
                messagebox.showinfo("Print", "Report sent to default printer.")
            except Exception as e:
                messagebox.showwarning("Print", f"Could not send to printer: {e}\nPDF saved at: {outpath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create PDF: {e}")

# ----------------- Run App -----------------
if __name__ == "__main__":
    load_staff()
    load_appointments()
    app = BellaDeskApp()
    app.mainloop()
