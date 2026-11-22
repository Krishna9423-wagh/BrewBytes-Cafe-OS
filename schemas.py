from pydantic import BaseModel
from typing import List, Optional

class UserRegister(BaseModel):
    username: str
    password: str
    role: str # 'waiter', 'kitchen', 'cashier', 'owner'

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str

class MenuItemCreate(BaseModel):
    name: str
    price_paise: int
    category: str

class MenuItemUpdate(BaseModel):
    price_paise: Optional[int] = None
    category: Optional[str] = None
    available: Optional[int] = None

class OrderItemInput(BaseModel):
    name: str
    qty: int
    price_paise: int

class OrderCreate(BaseModel):
    table_number: int
    customer_name: Optional[str] = ""
    customer_phone: Optional[str] = ""
    note: Optional[str] = ""
    items: List[OrderItemInput]

class OrderPay(BaseModel):
    paid_method: str # 'Cash', 'UPI', 'Card'
    discount_paise: int = 0
    gst_paise: int = 0
    total_paise: int

class ExpenseCreate(BaseModel):
    category: str
    amount_paise: int

class VendorCreate(BaseModel):
    vendor_name: str
    amount_paise: int
    entry_type: str # 'bill' or 'paid'

class StaffCreate(BaseModel):
    name: str
    role: str
    shift: str
    salary_paise: int

class AttendanceRecord(BaseModel):
    staff_id: str
    date_str: str # 'YYYY-MM-DD'
    is_present: bool

class RestockRequest(BaseModel):
    note: Optional[str] = "Manual Restock"

class ReviewDispatchedCreate(BaseModel):
    order_id: str
    customer_name: Optional[str] = ""
    customer_phone: str
    message: str
    items_summary: Optional[str] = ""

class ReviewTestRequest(BaseModel):
    customer_name: Optional[str] = "Rahul"
    customer_phone: str = "9876543210"
    items: Optional[List[str]] = ["Cappuccino", "Cheese Sandwich"]

