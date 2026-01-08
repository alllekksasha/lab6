#  Константы 

DEFAULT_CURRENCY = "USD"
TAX_RATE = 0.21

COUPON_SAVE10_RATE = 0.10
COUPON_SAVE20_RATE = 0.20
COUPON_SAVE20_MIN_SUBTOTAL = 200
COUPON_SAVE20_FALLBACK_RATE = 0.05
COUPON_VIP_DISCOUNT = 50
COUPON_VIP_MIN_SUBTOTAL = 100
COUPON_VIP_FALLBACK_DISCOUNT = 10

# Валидация входных данных запроса
def validate_request(user_id, items):
    if user_id is None:
        raise ValueError("user_id is required")
    if items is None:
        raise ValueError("items is required")
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    if len(items) == 0:
        raise ValueError("items must not be empty")

# Валидация товаров в списке
def validate_items(items):
    for item in items:
        if "price" not in item or "qty" not in item:
            raise ValueError("item must have price and qty")
        if item["price"] <= 0:
            raise ValueError("price must be positive")
        if item["qty"] <= 0:
            raise ValueError("qty must be positive")

# -- Расчеты --

# Вычисление суммы заказа до скидок и налогов
def calculate_subtotal(items):
    return sum(item["price"] * item["qty"] for item in items)

# Вычисление размера скидки по купону
def calculate_discount(coupon, subtotal):
    if coupon is None or coupon == "":
        return 0

    if coupon == "SAVE10":
        return int(subtotal * COUPON_SAVE10_RATE)

    if coupon == "SAVE20":
        if subtotal >= COUPON_SAVE20_MIN_SUBTOTAL:
            return int(subtotal * COUPON_SAVE20_RATE)
        return int(subtotal * COUPON_SAVE20_FALLBACK_RATE)

    if coupon == "VIP":
        if subtotal >= COUPON_VIP_MIN_SUBTOTAL:
            return COUPON_VIP_DISCOUNT
        return COUPON_VIP_FALLBACK_DISCOUNT

    raise ValueError("unknown coupon")


# Вычисление налога от суммы
def calculate_tax(amount):
    return int(amount * TAX_RATE)


# Генерация идентификатора заказа
def generate_order_id(user_id, items_count):
    return f"{user_id}-{items_count}-X"


# Основная функция обработки запроса на офорлмение заказа
def process_checkout(request):

    # Обработка входных данных
    user_id = request.get("user_id")
    items = request.get("items")
    coupon = request.get("coupon")
    currency = request.get("currency") or DEFAULT_CURRENCY

    # Валидация
    validate_request(user_id, items)
    validate_items(items)

    # Расчёты
    subtotal = calculate_subtotal(items)
    discount = calculate_discount(coupon, subtotal)
    total_after_discount = max(subtotal - discount, 0)
    tax = calculate_tax(total_after_discount)
    total = total_after_discount + tax

    # Формирование результата
    return {
        "order_id": generate_order_id(user_id, len(items)),
        "user_id": user_id,
        "currency": currency,
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": total,
        "items_count": len(items),
    }
