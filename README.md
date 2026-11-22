# ☕ BrewBytes CafeOS (CafeOS Pro)
### *The Next-Gen, Zero-Subscription Restaurant & Cafe Operating System*

[![FastAPI](https://img.shields.io/badge/FastAPI-Modern_Async_Backend-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![WebSocket](https://img.shields.io/badge/WebSocket-Real--Time_Live_Sync-blue?style=for-the-badge&logo=socketdotio)](https://developer.mozilla.org)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![SQLite](https://img.shields.io/badge/Database-SQLite_Strict_Schema-003B57?style=for-the-badge&logo=sqlite)](https://sqlite.org)
[![Platform](https://img.shields.io/badge/Device-Android_|_iPhone_|_Mac_|_Windows-orange?style=for-the-badge)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

> **"All-in-One Cafe & Restaurant OS: QR Mobile Waiter Ordering, Live Kitchen Display (KDS), Thermal Billing with GST, Auto-Inventory Ledger & Owner Profit Dashboard. Zero Monthly Fee. Available for Licensing & Custom Deployment."**

---

## 🚀 Stop Paying ₹2,000 – ₹5,000/Month in POS Subscriptions

Traditional POS systems (Petpooja, Posist, Toast, Square) charge steep recurring monthly fees and lock you into expensive proprietary hardware. 

**BrewBytes CafeOS** gives cafe and restaurant owners complete ownership:
- ❌ **No Monthly Fees:** Pay once or self-host forever with zero subscription costs.
- ❌ **No Expensive Hardware:** Runs smoothly on existing laptops, tablets, or any Android/iPhone.
- ⚡ **Ultra-Fast & Offline-Ready:** Sub-millisecond local responses with instant WebSocket synchronization.
- 🌐 **Works Anywhere (Wi-Fi or 4G/5G Mobile Data):** Waiters can place orders even from the outdoor patio without Wi-Fi dropouts via built-in secure cloud tunneling.

---

## 🌟 Key Features Overview

```
 ┌────────────────────────────────────────────────────────────────────────┐
 │                          BrewBytes CafeOS                              │
 └───────┬───────────────────┬───────────────────┬────────────────┬───────┘
         │                   │                   │                │
         ▼                   ▼                   ▼                ▼
  📱 Waiter App        🍳 Kitchen KDS       🧾 Cashier POS    📊 Owner Hub
   • Table status      • Real-time queue    • 1-click bill    • Live revenue
   • Instant order     • Audio alerts       • GST & discounts • Expense ledger
   • Special notes     • Ready triggers     • Cash/UPI/Card   • Staff payroll
```

### 1. 📱 Mobile Waiter Ordering (Any Smartphone)
- **Zero App Installation:** Waiters simply open a link or scan a QR code on Android or iPhone.
- **Table Grid Management:** Color-coded table layout (Vacant, Running Order, Billed).
- **Custom Modifiers & Notes:** Add special customer requests (e.g. *"Extra crispy", "Less sugar"*).
- **Works on 4G/5G:** Built-in auto-reconnecting tunnel means waiters don't need to stay on cafe Wi-Fi.

### 2. 🍳 Live Kitchen Display System (KDS)
- **Instant WebSocket Synchronization:** Orders appear in the kitchen the exact millisecond the waiter taps submit.
- **Audible Alerts:** Soft ding alert notifies kitchen staff of newly incoming orders.
- **Smart Elapsed Timer:** Live badges turn from green to yellow to red as preparation time increases.
- **One-Tap "Mark Ready":** Automatically notifies the cashier and waiter when food is prepared.

### 3. 🧾 Fast Thermal Billing & Cashier Desk
- **Thermal Printer Ready:** One-click receipt formatting for standard 58mm and 80mm thermal receipt printers.
- **Multiple Payment Modes:** Split or single payments via Cash, UPI (GPay/PhonePe/Paytm QR), or Card.
- **Automated Tax & Discount Calculations:** Configurable GST rates and discount overrides.
- **Table Auto-Release:** Automatically frees the table once payment is marked complete.

### 4. 📦 Auto-Inventory & Recipe Stock Ledger
- **Order-Level Stock Depletion:** Selling a cappuccino automatically logs ingredient deductions (milk, coffee beans) in real time.
- **Strict Ledger Mode:** Avoids floating-point discrepancies by tracking all units with precision.
- **Wastage & Restock Tracking:** Easy one-click stock replenishment and damage logging.

### 5. 👥 Staff Attendance & Payout Calculator
- **Daily Attendance Marking:** Fast 1-tap Present / Absent toggles for full-time and part-time staff.
- **Automated Salary Calculation:** Calculates monthly net payouts based on actual days worked.

### 6. 📊 Owner Dashboard & Khata (Vendor Ledger)
- **Real-Time Profit Calculator:** `Net Profit = Total Sales - (Expenses + Vendor Bills + Staff Salary)`.
- **Vendor Khata Book:** Track pending vs. settled bills for dairy, bakery, and beverage suppliers.
- **One-Click Backup:** Export complete cafe transaction history to encrypted JSON anytime.

---

## 🛠️ Tech Stack & Architecture

- **Backend:** High-performance **FastAPI (Python 3.9+)** asynchronous core.
- **Storage:** **SQLite** with strict schema constraints. All monetary values stored in **Paise (`INTEGER`)** to completely eliminate floating-point rounding errors.
- **Real-Time Engine:** Bi-directional **WebSockets (`/ws/kitchen`)** with auto-reconnect logic.
- **Security:** Salted **SHA-256** password hashing, **JWT (JSON Web Token)** authentication, and Owner PIN protection.
- **Frontend:** Zero-bloat, high-performance HTML5/CSS3/ES6 (loads in `< 0.2s` even on low-spec devices).
- **Tunneling:** Embedded background tunnel for seamless access over cellular data.

---

## ⚡ Quick Start (Run Locally in 2 Minutes)

### Prerequisites
- Python 3.9 or higher installed.

### 1. Clone the Repository
```bash
git clone https://github.com/Krishna9423-wagh/BrewBytes-Cafe-OS.git
cd BrewBytes-Cafe-OS
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the Server
```bash
# On macOS / Linux:
./Start_Brew_Bytes.command

# Or directly with Python:
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Open in Your Browser
- **Cashier / Owner / Kitchen Dashboard:** Open `http://localhost:8000` (or your local IP: `http://192.168.x.x:8000`)
- **Interactive API Documentation:** Open `http://localhost:8000/docs`

---

## 💼 Commercial Licensing & Custom Cafe Deployment

Are you a cafe owner, restaurant chain, food truck, or bakery looking for a complete, hassle-free deployment branded with your logo and menu?

### What is Included in the Commercial Setup:
1. **Custom Branding:** Your cafe name, logo, custom menu items, pricing, and GST details pre-configured.
2. **Turnkey Multi-Device Setup:** Setup on your counter laptop/tablet and staff mobile phones.
3. **Thermal Printer Integration:** Configured to work out-of-the-box with your USB or Bluetooth thermal receipt printer.
4. **Cloud / Local Hosting Assistance:** Dedicated support to deploy on-premise or on a private VPS cloud.
5. **No Monthly Royalty:** One-time licensing with lifetime usage.

---

## 📞 Contact for Purchase, Demo & Customization

| Channel | Contact Link / Details |
| :--- | :--- |
| 👤 **Developer / Creator** | **Krishna Wagh** |
| 📱 **Phone / Direct Call** | **`+91 7840946414`** |
| 💬 **WhatsApp** | [**Click here to Chat on WhatsApp**](https://api.whatsapp.com/send/?phone=917840946414&text=Hi%20Krishna,%20I%20am%20interested%20in%20CafeOS%20Pro%20for%20my%20cafe/restaurant.&type=phone_number&app_absent=0) |
| 📧 **Email** | [**waghk833@gmail.com**](mailto:waghk833@gmail.com) |
| 🌐 **GitHub Repository** | [github.com/Krishna9423-wagh/BrewBytes-Cafe-OS](https://github.com/Krishna9423-wagh/BrewBytes-Cafe-OS) |
| 📍 **Location** | India 🇮🇳 |

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

*Built with ❤️ for modern cafes, food trucks, and bakeries seeking high efficiency without high SaaS fees.*
