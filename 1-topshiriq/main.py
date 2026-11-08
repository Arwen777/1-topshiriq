import csv
from collections import defaultdict
from datetime import datetime

def read_orders(path):
    """Generatsiyalash orqali CSV faylni qatorma-qator o'qish (xotirani tejash uchun)"""
    with open(path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row

def validate_row(row):
    """1-qoida: Ma'lumotlarni validatsiya qilish (tiplar va yetishmayotgan qiymatlar)"""
    try:
        # order_id mavjudligi va bo'sh emasligi
        if not row.get("order_id"):
            return False
        
        # customer_id mavjudligi
        if not row.get("customer_id"):
            return False
            
        # amount ni float ga o'tkazib tekshirish (manfiy bo'lmasligi kerak)
        amount = float(row["amount"])
        if amount < 0:
            return False
            
        # created_at sanasining to'g'ri formatdaligini tekshirish (YYYY-MM yoki YYYY-MM-DD)
        date_str = row["created_at"].strip()
        # Masalan, YYYY-MM formatini ajratib olamiz yoki to'liq sanani tekshiramiz
        parsed_date = datetime.fromisoformat(date_str)
        
        return True
    except (ValueError, TypeError, AttributeError):
        return False

def process_pipeline():
    file_path = "orders.csv"
    
    total_rows = 0
    valid_rows = 0
    invalid_rows = 0
    
    # Oylik va mijoz kesimida daromadni yig'ish uchun defaultdict (dict o'rniga qulay)
    # Kalit: (customer_id, year_month), Qiymat: total_revenue
    revenue_per_customer_month = defaultdict(float)
    
    for row in read_orders(file_path):
        total_rows += 1
        
        if not validate_row(row):
            invalid_rows += 1
            print(f"[OGOHLANTIRISH] Yaroqsiz qator tashlab yuborildi: {row}")
            continue
            
        valid_rows += 1
        customer_id = row["customer_id"].strip()
        
        # Sanadan yil va oyni ajratib olish (masalan: "2023-10")
        date_obj = datetime.fromisoformat(row["created_at"].strip())
        year_month = date_obj.strftime("%Y-%m")
        
        amount = float(row["amount"])
        
        # Mijoz va oy bo'yicha yig'indiga qo'shamiz
        revenue_per_customer_month[(customer_id, year_month)] += amount

    # 3-qoida: Har bir qadam va natijalarni log qilish
    print("\n--- STATISTIKA ---")
    print(f"Jami o'qilgan qatorlar: {total_rows}")
    print(f"Yaroqli qatorlar: {valid_rows}")
    print(f"Yaroqsiz/tashlab yuborilgan qatorlar: {invalid_rows}")
    
    # Natijani daromad bo'yicha saralash (eng ko'p daromad keltirgani yuqorida turishi uchun)
    sorted_revenue = sorted(
        revenue_per_customer_month.items(), 
        key=lambda item: item[1], 
        reverse=True
    )
    
    print("\n--- OYLIK VA MIJOZ KESIMIDA DAROMAD (Saralangan) ---")
    print(f"{'Customer ID':<15} | {'Year-Month':<12} | {'Revenue':<10}")
    print("-" * 45)
    for (cust_id, ym), rev in sorted_revenue:
        print(f"{cust_id:<15} | {ym:<12} | {rev:<10.2f}")

if __name__ == "__main__":
    process_pipeline()