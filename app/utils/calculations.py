from decimal import Decimal

def calculate_amount(hours: Decimal,
                     hourly_rate: Decimal) -> Decimal:
    return (hours * hourly_rate).quantize(
        Decimal("0.01")
    )

def calculate_subtotal(amounts: list[Decimal]) -> Decimal:
    return sum(amounts, Decimal("0.00"),
               ).quantize(Decimal ("0.01"))

def calculate_total(subtotal: Decimal, tax: Decimal = Decimal("0.00")) -> Decimal:
    return(subtotal + tax).quantize(Decimal("0.01"))
