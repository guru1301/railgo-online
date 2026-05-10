import sys
sys.path.insert(0, r'd:\railgo (1)\railgo\railgo-python')

from app.database import engine
from sqlalchemy import text, inspect

insp = inspect(engine)
cols = [c['name'] for c in insp.get_columns('bookings')]
print('Existing columns:', cols)

with engine.connect() as conn:
    if 'payment_status' not in cols:
        conn.execute(text("ALTER TABLE bookings ADD COLUMN payment_status VARCHAR DEFAULT 'PENDING'"))
        print('Added payment_status')
    else:
        print('payment_status already exists')

    if 'razorpay_order_id' not in cols:
        conn.execute(text('ALTER TABLE bookings ADD COLUMN razorpay_order_id VARCHAR'))
        print('Added razorpay_order_id')
    else:
        print('razorpay_order_id already exists')

    if 'razorpay_payment_id' not in cols:
        conn.execute(text('ALTER TABLE bookings ADD COLUMN razorpay_payment_id VARCHAR'))
        print('Added razorpay_payment_id')
    else:
        print('razorpay_payment_id already exists')

    conn.commit()

print('Migration complete.')
