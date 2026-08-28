from datetime import datetime

def generate_invoice_number(invoiceid: int) -> str:
    year = datetime.now().year

    return f"INV-{year}-{invoiceid:05d}"