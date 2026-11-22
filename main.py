import time
import json
import os
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List, Optional

from database import init_db, get_db
from auth import (
    hash_password, verify_password, create_access_token,
    get_current_user, require_role
)
from schemas import (
    UserRegister, UserLogin, TokenResponse,
    MenuItemCreate, MenuItemUpdate,
    OrderCreate, OrderPay,
    ExpenseCreate, VendorCreate,
    StaffCreate, AttendanceRecord, RestockRequest,
    ReviewDispatchedCreate, ReviewTestRequest
)

# --- AI FOOD REVIEW AGENT UTILITIES ---
def generate_ai_review_text(customer_name: str, items_summary: str, google_review_url: str = "") -> str:
    name_prefix = f"Namaste {customer_name} ji! 🙏" if customer_name else "Namaste! 🙏"
    dish_part = f"fresh *{items_summary}*" if items_summary else "khana aur drinks"
    g_link = google_review_url if google_review_url else "https://maps.google.com"
    return (
        f"{name_prefix}\n\n"
        f"Brew & Bytes Cafe me aane ke liye dil se shukriya! ☕✨\n\n"
        f"Aapko hamara {dish_part} kaisa laga? Hamare chef ne ise special pyaar se banaya tha.\n\n"
        f"⭐ *Aapka feedback hamare liye bahut keemti hai!*\n"
        f"Kripya 10 second nikal kar hume apna pyara review ya 5-star rating dein:\n"
        f"{g_link}\n\n"
        f"🎁 *Special Gift:* Agli visit par ye message dikhayein aur payein *flat 10% discount* on total bill!\n"
        f"— Team Brew & Bytes ☕"
    )

async def schedule_ai_review(order_id: str, customer_name: str, customer_phone: str, items_summary: str, delay_seconds: int = 300):
    await asyncio.sleep(delay_seconds)
    now = int(time.time() * 1000)
    ai_msg = generate_ai_review_text(customer_name, items_summary)
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO customer_reviews (order_id, customer_name, customer_phone, items_summary, ai_message, scheduled_at, dispatched_at, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'dispatched', ?)
        """, (order_id, customer_name, customer_phone, items_summary, ai_msg, now - (delay_seconds * 1000), now, now))
        conn.commit()
        conn.close()

        # Broadcast review dispatch over WebSocket
        await manager.broadcast({
            "event": "review_dispatched",
            "order_id": order_id,
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "message": ai_msg,
            "dispatched_at": now
        })
    except Exception as e:
        print(f"Error recording dispatched review for order {order_id}: {e}")

# Initialize Database tables
init_db()

app = FastAPI(
    title="Brew & Bytes Cafe POS Backend",
    description="Unified Cafe OS: POS, KDS, Inventory, Payroll, Khata Book & Live WebSocket",
    version="2.0.0"
)

# Enable CORS for phone & local network access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POSSIBLE_PATHS = [
    os.path.join(BASE_DIR, "index.html"),
    os.path.join(BASE_DIR, "Brew & Bytes_ Waiter aur Kitchen.html"),
    "/Users/waghk833gmail.com/Desktop/Brew & Bytes_ Waiter aur Kitchen.html"
]
HTML_PATH = next((p for p in POSSIBLE_PATHS if os.path.exists(p)), POSSIBLE_PATHS[0])

# Serve Frontend directly on cafe Wi-Fi network (Phone, Tablet, Laptop)
@app.api_route("/", methods=["GET", "HEAD"])
def serve_frontend():
    if os.path.exists(HTML_PATH):
        return FileResponse(HTML_PATH)
    return {"message": "Brew & Bytes API is running. Frontend file not found at path."}

# Get Live Public Online URL (No Wi-Fi needed - works on 4G/5G mobile data)
@app.get("/api/online-url")
def get_online_url():
    tunnel_file = os.path.join(os.path.dirname(__file__), "tunnel_url.txt")
    if os.path.exists(tunnel_file):
        try:
            with open(tunnel_file, "r") as f:
                url = f.read().strip()
                if url:
                    return {"online_url": url, "active": True}
        except Exception:
            pass
    return {"online_url": None, "active": False}

# WebSocket connection manager for live phone -> kitchen broadcast
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)

manager = ConnectionManager()

# Recipes for stock auto-deduction
RECIPES = {
    'Cappuccino': {'d': 0.2, 'b': 0.018},
    'Cold coffee': {'d': 0.25, 'b': 0.02},
    'Masala chai': {'d': 0.1},
    'Paneer sandwich': {'br': 0.15, 'p': 0.08, 'c': 1},
    'Cheese toast': {'br': 0.12, 'c': 2},
    'Cheese sandwich': {'br': 0.15, 'c': 2},
    'Fries': {'fr': 1},
    'Brownie': {'bw': 1}
}

STOCK_ITEMS = {
    'd': ('Doodh', 'L'),
    'b': ('Coffee beans', 'kg'),
    'br': ('Bread', 'loaf'),
    'p': ('Paneer', 'kg'),
    'c': ('Cheese slices', 'pcs'),
    'fr': ('Fries packet', 'pkt'),
    'bw': ('Brownie pcs', 'pcs')
}

# --- WEBSOCKET ENDPOINT ---
@app.websocket("/ws/kitchen")
async def websocket_kitchen(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# --- AUTH ENDPOINTS ---
@app.post("/api/auth/register", response_model=TokenResponse)
def register(user_data: UserRegister):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (user_data.username,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Username already exists")

    pwd_hash = hash_password(user_data.password)
    cursor.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (user_data.username, pwd_hash, user_data.role)
    )
    conn.commit()
    conn.close()

    token = create_access_token({"sub": user_data.username, "role": user_data.role})
    return {"access_token": token, "username": user_data.username, "role": user_data.role}

@app.post("/api/auth/login", response_model=TokenResponse)
def login(login_data: UserLogin):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash, role FROM users WHERE username = ?", (login_data.username,))
    row = cursor.fetchone()
    conn.close()

    if not row or not verify_password(login_data.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token({"sub": login_data.username, "role": row["role"]})
    return {"access_token": token, "username": login_data.username, "role": row["role"]}

# --- MENU ENDPOINTS ---
@app.get("/api/menu")
def get_menu():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price_paise, category, available FROM menu_items")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

@app.post("/api/menu")
def create_menu_item(item: MenuItemCreate):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO menu_items (name, price_paise, category) VALUES (?, ?, ?)",
            (item.name, item.price_paise, item.category)
        )
        conn.commit()
        item_id = cursor.lastrowid
    except Exception:
        conn.close()
        raise HTTPException(status_code=400, detail="Item already exists or invalid data")
    conn.close()
    return {"id": item_id, **item.model_dump()}

@app.put("/api/menu/{item_id}")
def update_menu_item(item_id: int, item: MenuItemUpdate):
    conn = get_db()
    cursor = conn.cursor()
    updates = []
    params = []
    if item.price_paise is not None:
        updates.append("price_paise = ?")
        params.append(item.price_paise)
    if item.category is not None:
        updates.append("category = ?")
        params.append(item.category)
    if item.available is not None:
        updates.append("available = ?")
        params.append(item.available)

    if not updates:
        conn.close()
        return {"message": "No updates provided"}

    params.append(item_id)
    cursor.execute(f"UPDATE menu_items SET {', '.join(updates)} WHERE id = ?", params)
    conn.commit()
    conn.close()
    return {"message": "Updated successfully"}

# --- ORDERS ENDPOINTS ---
@app.get("/api/orders")
def get_orders(status: Optional[str] = None):
    conn = get_db()
    cursor = conn.cursor()
    if status:
        cursor.execute("SELECT * FROM orders WHERE status = ? ORDER BY created_at ASC", (status,))
    else:
        cursor.execute("SELECT * FROM orders ORDER BY created_at DESC")
    orders = [dict(r) for r in cursor.fetchall()]

    for o in orders:
        cursor.execute("SELECT item_name, qty, unit_price_paise FROM order_items WHERE order_id = ?", (o["id"],))
        rows = cursor.fetchall()
        o["items"] = [{"name": r["item_name"], "item_name": r["item_name"], "qty": r["qty"], "unit_price_paise": r["unit_price_paise"]} for r in rows]
        o["table"] = o.get("table_number") or 1
        o["table_number"] = o["table"]
        o["at"] = o.get("created_at") or int(time.time() * 1000)

    conn.close()
    return orders

@app.post("/api/orders")
async def create_order(order: OrderCreate):
    conn = get_db()
    cursor = conn.cursor()

    order_id = f"l{int(time.time() * 1000)}"
    now = int(time.time() * 1000)

    subtotal_paise = sum(it.qty * it.price_paise for it in order.items)
    total_paise = subtotal_paise

    cursor.execute("""
    INSERT INTO orders (id, table_number, customer_name, customer_phone, note, status, subtotal_paise, total_paise, created_at)
    VALUES (?, ?, ?, ?, ?, 'new', ?, ?, ?)
    """, (
        order_id, order.table_number, order.customer_name, order.customer_phone,
        order.note, subtotal_paise, total_paise, now
    ))

    # Log items and stock movements automatically
    for it in order.items:
        cursor.execute("""
        INSERT INTO order_items (order_id, item_name, qty, unit_price_paise)
        VALUES (?, ?, ?, ?)
        """, (order_id, it.name, it.qty, it.price_paise))

        recipe = RECIPES.get(it.name)
        if recipe:
            for ing_code, amt_per_unit in recipe.items():
                ing_info = STOCK_ITEMS.get(ing_code, (ing_code, "unit"))
                cursor.execute("""
                INSERT INTO stock_movements (movement_type, order_id, ingredient_code, ingredient_name, qty_change, unit, created_at)
                VALUES ('order_deduct', ?, ?, ?, ?, ?, ?)
                """, (order_id, ing_code, ing_info[0], -amt_per_unit * it.qty, ing_info[1], now))

    conn.commit()
    conn.close()

    order_payload = {
        "event": "new_order",
        "order": {
            "id": order_id,
            "table": order.table_number,
            "table_number": order.table_number,
            "items": [{"name": it.name, "item_name": it.name, "qty": it.qty, "price_paise": it.price_paise} for it in order.items],
            "customer_name": order.customer_name,
            "customer_phone": order.customer_phone,
            "note": order.note,
            "status": "new",
            "at": now,
            "subtotal_paise": subtotal_paise,
            "total_paise": total_paise
        }
    }
    await manager.broadcast(order_payload)
    return {"id": order_id, "table": order.table_number, "table_number": order.table_number, "status": "new", "subtotal_paise": subtotal_paise, "total_paise": total_paise}

@app.patch("/api/orders/{order_id}/status")
async def update_order_status(order_id: str, status: str):
    valid_statuses = ['new', 'cooking', 'ready', 'served', 'cancelled']
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Choose from: {valid_statuses}")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    
    # If order is served, check if customer phone exists to trigger 5-min AI review
    if status == 'served':
        cursor.execute("SELECT customer_name, customer_phone, table_number FROM orders WHERE id = ?", (order_id,))
        ord_row = cursor.fetchone()
        if ord_row and ord_row["customer_phone"]:
            cname = ord_row["customer_name"] or ""
            cphone = ord_row["customer_phone"]
            cursor.execute("SELECT item_name FROM order_items WHERE order_id = ?", (order_id,))
            item_rows = cursor.fetchall()
            items_summary = ", ".join([r["item_name"] for r in item_rows]) if item_rows else "food & drinks"
            
            # Start background review task (5 minutes = 300 seconds)
            asyncio.create_task(schedule_ai_review(order_id, cname, cphone, items_summary, delay_seconds=300))
            await manager.broadcast({
                "event": "review_scheduled",
                "order_id": order_id,
                "customer_name": cname,
                "customer_phone": cphone,
                "items_summary": items_summary,
                "delay_seconds": 300
            })

    conn.commit()
    conn.close()

    await manager.broadcast({"event": "status_change", "order_id": order_id, "status": status})
    return {"order_id": order_id, "status": status}

@app.post("/api/orders/{order_id}/pay")
async def pay_order(order_id: str, pay_data: OrderPay):
    conn = get_db()
    cursor = conn.cursor()
    now = int(time.time() * 1000)

    cursor.execute("""
    UPDATE orders
    SET paid_method = ?, paid_at = ?, discount_paise = ?, gst_paise = ?, total_paise = ?
    WHERE id = ?
    """, (pay_data.paid_method, now, pay_data.discount_paise, pay_data.gst_paise, pay_data.total_paise, order_id))
    conn.commit()
    conn.close()

    await manager.broadcast({"event": "order_paid", "order_id": order_id, "paid_method": pay_data.paid_method, "total_paise": pay_data.total_paise})
    return {"order_id": order_id, "paid": True, "total_paise": pay_data.total_paise}

# --- STOCK MOVEMENTS LEDGER ---
@app.get("/api/stock/movements")
def get_stock_movements(limit: int = 50):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stock_movements ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

@app.post("/api/stock/restock")
async def restock(request: RestockRequest):
    conn = get_db()
    cursor = conn.cursor()
    now = int(time.time() * 1000)

    for code, (name, unit) in STOCK_ITEMS.items():
        cursor.execute("""
        INSERT INTO stock_movements (movement_type, ingredient_code, ingredient_name, qty_change, unit, note, created_at)
        VALUES ('restock', ?, ?, 0, ?, ?, ?)
        """, (code, name, unit, request.note, now))

    conn.commit()
    conn.close()
    await manager.broadcast({"event": "stock_restocked", "at": now})
    return {"message": "Stock restocked successfully", "at": now}

# --- EXPENSES, VENDORS, STAFF ---
@app.get("/api/expenses")
def get_expenses():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses ORDER BY created_at DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

@app.post("/api/expenses")
async def create_expense(expense: ExpenseCreate):
    conn = get_db()
    cursor = conn.cursor()
    now = int(time.time() * 1000)
    cursor.execute(
        "INSERT INTO expenses (category, amount_paise, created_at) VALUES (?, ?, ?)",
        (expense.category, expense.amount_paise, now)
    )
    conn.commit()
    conn.close()
    await manager.broadcast({"event": "expense_added", "category": expense.category, "amount_paise": expense.amount_paise})
    return {"category": expense.category, "amount_paise": expense.amount_paise, "at": now}

@app.get("/api/vendors")
def get_vendors():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vendors ORDER BY created_at DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

@app.post("/api/vendors")
async def create_vendor_entry(v: VendorCreate):
    conn = get_db()
    cursor = conn.cursor()
    now = int(time.time() * 1000)
    cursor.execute(
        "INSERT INTO vendors (vendor_name, amount_paise, entry_type, created_at) VALUES (?, ?, ?, ?)",
        (v.vendor_name, v.amount_paise, v.entry_type, now)
    )
    if v.entry_type == 'paid':
        cursor.execute(
            "INSERT INTO expenses (category, amount_paise, created_at) VALUES ('Vendor bill', ?, ?)",
            (v.amount_paise, now)
        )
    conn.commit()
    conn.close()
    await manager.broadcast({"event": "vendor_updated"})
    return {"vendor_name": v.vendor_name, "amount_paise": v.amount_paise, "entry_type": v.entry_type}

@app.get("/api/staff")
def get_staff():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM staff")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

@app.post("/api/staff")
def create_staff(s: StaffCreate):
    conn = get_db()
    cursor = conn.cursor()
    sid = f"st_{int(time.time() * 1000)}"
    cursor.execute(
        "INSERT INTO staff (id, name, role, shift, salary_paise) VALUES (?, ?, ?, ?, ?)",
        (sid, s.name, s.role, s.shift, s.salary_paise)
    )
    conn.commit()
    conn.close()
    return {"id": sid, **s.model_dump()}

@app.get("/api/attendance")
def get_attendance():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attendance")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

@app.post("/api/attendance")
def record_attendance(rec: AttendanceRecord):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO attendance (staff_id, date_str, is_present)
    VALUES (?, ?, ?)
    ON CONFLICT(staff_id, date_str) DO UPDATE SET is_present = excluded.is_present
    """, (rec.staff_id, rec.date_str, 1 if rec.is_present else 0))
    conn.commit()
    conn.close()
    return {"staff_id": rec.staff_id, "date_str": rec.date_str, "is_present": rec.is_present}

# --- AI CUSTOMER FOOD REVIEW AGENT ENDPOINTS ---
@app.get("/api/reviews")
def get_customer_reviews(limit: int = 50):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customer_reviews ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

@app.post("/api/reviews/dispatched")
async def record_dispatched_review(payload: ReviewDispatchedCreate):
    conn = get_db()
    cursor = conn.cursor()
    now = int(time.time() * 1000)
    cursor.execute("""
        INSERT INTO customer_reviews (order_id, customer_name, customer_phone, items_summary, ai_message, scheduled_at, dispatched_at, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'dispatched', ?)
    """, (payload.order_id, payload.customer_name, payload.customer_phone, payload.items_summary, payload.message, now, now, now))
    conn.commit()
    conn.close()
    
    await manager.broadcast({
        "event": "review_dispatched",
        "order_id": payload.order_id,
        "customer_name": payload.customer_name,
        "customer_phone": payload.customer_phone,
        "message": payload.message,
        "dispatched_at": now
    })
    return {"status": "success", "recorded_at": now}

@app.post("/api/reviews/test")
def test_ai_review(req: ReviewTestRequest):
    summary = ", ".join(req.items) if req.items else "Cappuccino, Sandwich"
    msg = generate_ai_review_text(req.customer_name, summary)
    return {
        "customer_name": req.customer_name,
        "customer_phone": req.customer_phone,
        "generated_message": msg
    }

@app.post("/api/reviews/trigger/{order_id}")
async def trigger_instant_review(order_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT customer_name, customer_phone, table_number FROM orders WHERE id = ?", (order_id,))
    ord_row = cursor.fetchone()
    if not ord_row or not ord_row["customer_phone"]:
        conn.close()
        raise HTTPException(status_code=400, detail="Order not found or no customer phone number attached")

    cname = ord_row["customer_name"] or ""
    cphone = ord_row["customer_phone"]
    cursor.execute("SELECT item_name FROM order_items WHERE order_id = ?", (order_id,))
    item_rows = cursor.fetchall()
    items_summary = ", ".join([r["item_name"] for r in item_rows]) if item_rows else "food & drinks"
    conn.close()

    now = int(time.time() * 1000)
    ai_msg = generate_ai_review_text(cname, items_summary)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO customer_reviews (order_id, customer_name, customer_phone, items_summary, ai_message, scheduled_at, dispatched_at, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'dispatched', ?)
    """, (order_id, cname, cphone, items_summary, ai_msg, now, now, now))
    conn.commit()
    conn.close()

    await manager.broadcast({
        "event": "review_dispatched",
        "order_id": order_id,
        "customer_name": cname,
        "customer_phone": cphone,
        "message": ai_msg,
        "dispatched_at": now
    })
    return {"status": "success", "order_id": order_id, "dispatched_message": ai_msg}

if __name__ == "__main__":
    import uvicorn
    # Bind to 0.0.0.0 so phone can connect on cafe Wi-Fi
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
