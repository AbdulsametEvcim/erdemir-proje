import random
from datetime import datetime, timedelta

from app.database import Base, SessionLocal, engine
from app.models import Material, StockMovement

random.seed(42)

DAYS = 90

# (isim, birim, kritik_esik, gunluk_ortalama_tuketim, trend_carpani, hedef_stok, restock_var_mi)
MATERIAL_DEFS = [
    ("Komur", "ton", 200, 13.0, 1.15, 175, False),
    ("Demir Cevheri", "ton", 500, 22.0, 1.0, 2400, True),
    ("Kok Komuru", "ton", 150, 6.5, 1.0, 620, True),
    ("Yedek Parca X", "adet", 20, 0.35, 1.2, 14, False),
    ("Kirectasi", "ton", 100, 4.0, 1.0, 340, True),
]


def generate_movements(material: Material, avg_daily: float, trend: float, target_stock: float, has_restock: bool):
    today = datetime.utcnow().date()
    start_date = today - timedelta(days=DAYS - 1)

    daily_consumption = []
    for i in range(DAYS):
        progress = i / (DAYS - 1)
        rate_multiplier = 1 + (trend - 1) * progress
        base = avg_daily * rate_multiplier
        noise = random.gauss(0, avg_daily * 0.15)
        qty = max(0.0, base + noise)
        daily_consumption.append(qty)

    total_consumption = sum(daily_consumption)

    restock_events = []
    total_restock = 0.0
    if has_restock:
        restock_day = random.randint(5, 20)
        restock_qty = total_consumption * 0.5
        restock_events.append((restock_day, restock_qty))
        total_restock = restock_qty

    initial_stock = target_stock + total_consumption - total_restock

    movements = []
    running_stock = initial_stock
    for i in range(DAYS):
        day = start_date + timedelta(days=i)
        created_at = datetime.combine(day, datetime.min.time()) + timedelta(hours=9)

        for restock_day, restock_qty in restock_events:
            if restock_day == i:
                movements.append(
                    StockMovement(
                        material_id=material.id,
                        movement_type="giris",
                        quantity=round(restock_qty, 2),
                        note="Tedarikci sevkiyati",
                        created_by="admin",
                        created_at=created_at,
                    )
                )
                running_stock += restock_qty

        qty = round(daily_consumption[i], 2)
        if qty > 0:
            movements.append(
                StockMovement(
                    material_id=material.id,
                    movement_type="cikis",
                    quantity=qty,
                    note="Uretim tuketimi",
                    created_by="admin",
                    created_at=created_at,
                )
            )
            running_stock -= qty

    return movements, round(running_stock, 2)


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(Material).count()
        if existing > 0:
            print(f"Zaten {existing} malzeme var, seed atlaniyor.")
            return

        for name, unit, threshold, avg_daily, trend, target_stock, has_restock in MATERIAL_DEFS:
            material = Material(
                name=name,
                unit=unit,
                current_stock=0,
                critical_threshold=threshold,
            )
            db.add(material)
            db.flush()

            movements, final_stock = generate_movements(
                material, avg_daily, trend, target_stock, has_restock
            )
            db.add_all(movements)
            material.current_stock = final_stock

        db.commit()
        print("Ornek veri basariyla olusturuldu: 5 malzeme, 90 gunluk hareket gecmisi.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
