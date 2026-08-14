import random
from datetime import datetime, timedelta

from app.database import Base, SessionLocal, engine
from app.models import Material, StockMovement

random.seed(42)

DAYS = 90

# Erdemir'in entegre demir-celik uretim surecine (yuksek firin girdileri) uygun
# malzemeler: demir cevheri, taskomuru, kok komuru, kireçtaşı ve kritik bir
# yedek parca (haddehane merdanesi).
# co2_factor: birim basina (ton veya adet) tahmini kg CO2 emisyonu, sektor
# ortalamalarina dayali kaba bir yaklasimdir, olculmus deger degildir.
# (isim, birim, kritik_esik, gunluk_ortalama_tuketim, trend_carpani, hedef_stok, restock_var_mi, co2_factor)
MATERIAL_DEFS = [
    ("Taşkömürü", "ton", 200, 13.0, 1.15, 175, False, 2500),
    ("Demir Cevheri", "ton", 500, 22.0, 1.0, 2400, True, 200),
    ("Kok Kömürü", "ton", 150, 6.5, 1.0, 620, True, 3000),
    ("Haddehane Merdanesi", "adet", 20, 0.35, 1.2, 14, False, 0),
    ("Kireçtaşı", "ton", 100, 4.0, 1.0, 340, True, 440),
    ("Ferrokrom", "ton", 30, 2.0, 1.1, 45, True, 1800),
    ("Hurda Çelik", "ton", 300, 18.0, 1.05, 850, True, 100),
    ("Dolomit", "ton", 80, 3.5, 1.0, 280, True, 420),
    ("Doğalgaz", "m³", 3000, 550, 1.0, 9500, True, 2.3),
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


def top_up_movements(db):
    """Son hareket tarihi ile bugun arasinda bosluk varsa, gecmis tuketim hizina
    uygun sahte cikis hareketleri ekleyerek grafik/tahmin/trend hesaplarinin
    her zaman 'bugune' kadar dolu kalmasini saglar. Uygulama her acildiginda calisir."""
    today = datetime.utcnow().date()
    materials = db.query(Material).all()

    for material in materials:
        last_movement = (
            db.query(StockMovement)
            .filter(StockMovement.material_id == material.id)
            .order_by(StockMovement.created_at.desc())
            .first()
        )
        if not last_movement:
            continue

        last_date = last_movement.created_at.date()
        gap_days = (today - last_date).days
        if gap_days <= 0:
            continue

        recent_cikis = (
            db.query(StockMovement)
            .filter(StockMovement.material_id == material.id, StockMovement.movement_type == "cikis")
            .order_by(StockMovement.created_at.desc())
            .limit(14)
            .all()
        )
        avg_daily = sum(m.quantity for m in recent_cikis) / len(recent_cikis) if recent_cikis else 0.0
        if avg_daily <= 0:
            continue

        for i in range(1, gap_days + 1):
            day = last_date + timedelta(days=i)
            created_at = datetime.combine(day, datetime.min.time()) + timedelta(hours=9)
            noise = random.gauss(0, avg_daily * 0.15)
            qty = round(max(0.0, min(avg_daily + noise, material.current_stock)), 2)
            if qty <= 0:
                continue
            db.add(
                StockMovement(
                    material_id=material.id,
                    movement_type="cikis",
                    quantity=qty,
                    note="Uretim tuketimi",
                    created_by="admin",
                    created_at=created_at,
                )
            )
            material.current_stock = round(material.current_stock - qty, 2)

    db.commit()


def add_missing_materials(db):
    """MATERIAL_DEFS'te olup veritabaninda henuz olmayan malzemeleri, 90 gunluk
    gecmis hareketiyle birlikte ekler. Zaten var olan malzemelere dokunmaz."""
    existing_names = {m.name for m in db.query(Material).all()}
    added = []

    for name, unit, threshold, avg_daily, trend, target_stock, has_restock, co2_factor in MATERIAL_DEFS:
        if name in existing_names:
            continue

        material = Material(
            name=name,
            unit=unit,
            current_stock=0,
            critical_threshold=threshold,
            co2_factor=co2_factor,
        )
        db.add(material)
        db.flush()

        movements, final_stock = generate_movements(material, avg_daily, trend, target_stock, has_restock)
        db.add_all(movements)
        material.current_stock = final_stock
        added.append(name)

    db.commit()
    return added


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        added = add_missing_materials(db)
        if added:
            print(f"Eklenen malzemeler: {', '.join(added)}")
        else:
            print("Eklenecek yeni malzeme yok, tum malzemeler zaten mevcut.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
