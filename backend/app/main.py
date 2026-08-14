import io
import os
from datetime import datetime, timedelta
from urllib.parse import quote

import pandas as pd
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine, get_db
from app.forecast import compute_daily_consumption, compute_trend, forecast_days_remaining
from app.models import Material, StockMovement
from app.report import build_material_report, build_summary_report
from app.seed import top_up_movements
from app.schemas import (
    AlertOut,
    ConsumptionComparisonItem,
    EnvironmentalItem,
    EnvironmentalSummary,
    LoginRequest,
    LoginResponse,
    MaterialAnalysis,
    MaterialCreate,
    MaterialOut,
    MaterialUpdate,
    MovementCreate,
    MovementOut,
    SupplierMaterialBreakdown,
    SupplierSummaryItem,
)

load_dotenv()

AUTH_TOKEN = os.getenv("AUTH_TOKEN")
LOGIN_USERNAME = os.getenv("LOGIN_USERNAME")
LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD")

Base.metadata.create_all(bind=engine)

with SessionLocal() as _startup_db:
    top_up_movements(_startup_db)

app = FastAPI(title="Envanter/Stok Takip ve Tahmin Sistemi")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def require_auth(authorization: str | None = Header(default=None)) -> None:
    if not authorization or authorization != f"Bearer {AUTH_TOKEN}":
        raise HTTPException(status_code=401, detail="Yetkisiz erisim")


def material_status(material: Material) -> str:
    return "kritik" if material.current_stock <= material.critical_threshold else "normal"


def get_material_trend(db: Session, material_id: int) -> str:
    since = datetime.utcnow() - timedelta(days=14)
    movements = db.execute(
        select(StockMovement).where(
            StockMovement.material_id == material_id,
            StockMovement.created_at >= since,
        )
    ).scalars().all()
    daily_totals = compute_daily_consumption(movements, days=14)
    return compute_trend(daily_totals)


@app.post("/api/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    if payload.username != LOGIN_USERNAME or payload.password != LOGIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Kullanici adi veya sifre hatali")
    return LoginResponse(access_token=AUTH_TOKEN)


@app.get("/api/summary")
def get_summary(db: Session = Depends(get_db), _: None = Depends(require_auth)):
    materials = db.execute(select(Material)).scalars().all()
    critical_count = sum(1 for m in materials if material_status(m) == "kritik")

    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_out = db.execute(
        select(StockMovement)
        .join(Material)
        .where(
            StockMovement.movement_type == "cikis",
            StockMovement.created_at >= week_ago,
            Material.unit == "ton",
        )
    ).scalars().all()
    # Farkli birimler (m3, adet) toplamda karismasin diye sadece "ton" birimli
    # malzemeler toplaniyor; bu, kartta gosterilen "ton" etiketiyle tutarli olur.
    total_consumption_7d = sum(m.quantity for m in recent_out)

    return {
        "total_materials": len(materials),
        "critical_materials": critical_count,
        "total_consumption_7d": round(total_consumption_7d, 2),
    }


@app.get("/api/materials", response_model=list[MaterialOut])
def list_materials(
    search: str = Query(default=""),
    sort_by: str = Query(default="name"),
    order: str = Query(default="asc"),
    db: Session = Depends(get_db),
    _: None = Depends(require_auth),
):
    query = select(Material)
    if search:
        query = query.where(Material.name.ilike(f"%{search}%"))

    sort_column = {
        "name": Material.name,
        "current_stock": Material.current_stock,
    }.get(sort_by, Material.name)

    query = query.order_by(sort_column.desc() if order == "desc" else sort_column.asc())

    materials = db.execute(query).scalars().all()
    return [
        MaterialOut(
            id=m.id,
            name=m.name,
            unit=m.unit,
            current_stock=m.current_stock,
            critical_threshold=m.critical_threshold,
            co2_factor=m.co2_factor,
            status=material_status(m),
            trend=get_material_trend(db, m.id),
        )
        for m in materials
    ]


@app.post("/api/materials", response_model=MaterialOut)
def create_material(
    payload: MaterialCreate,
    db: Session = Depends(get_db),
    _: None = Depends(require_auth),
):
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Malzeme adi bos olamaz")

    existing = db.execute(select(Material).where(Material.name.ilike(name))).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Bu isimde bir malzeme zaten var")

    if payload.current_stock < 0 or payload.critical_threshold < 0:
        raise HTTPException(status_code=400, detail="Miktarlar negatif olamaz")
    if payload.co2_factor < 0:
        raise HTTPException(status_code=400, detail="CO2 faktoru negatif olamaz")

    material = Material(
        name=name,
        unit=payload.unit,
        current_stock=payload.current_stock,
        critical_threshold=payload.critical_threshold,
        co2_factor=payload.co2_factor,
    )
    db.add(material)
    db.commit()
    db.refresh(material)

    return MaterialOut(
        id=material.id,
        name=material.name,
        unit=material.unit,
        current_stock=material.current_stock,
        critical_threshold=material.critical_threshold,
        co2_factor=material.co2_factor,
        status=material_status(material),
        trend="sabit",
    )


@app.put("/api/materials/{material_id}", response_model=MaterialOut)
def update_material(
    material_id: int,
    payload: MaterialUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(require_auth),
):
    material = db.get(Material, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Malzeme bulunamadi")

    if payload.name is not None:
        name = payload.name.strip()
        if not name:
            raise HTTPException(status_code=400, detail="Malzeme adi bos olamaz")
        existing = db.execute(
            select(Material).where(Material.name.ilike(name), Material.id != material_id)
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=400, detail="Bu isimde bir malzeme zaten var")
        material.name = name

    if payload.unit is not None:
        material.unit = payload.unit

    if payload.current_stock is not None:
        if payload.current_stock < 0:
            raise HTTPException(status_code=400, detail="Stok negatif olamaz")
        material.current_stock = payload.current_stock

    if payload.critical_threshold is not None:
        if payload.critical_threshold < 0:
            raise HTTPException(status_code=400, detail="Kritik esik negatif olamaz")
        material.critical_threshold = payload.critical_threshold

    if payload.co2_factor is not None:
        if payload.co2_factor < 0:
            raise HTTPException(status_code=400, detail="CO2 faktoru negatif olamaz")
        material.co2_factor = payload.co2_factor

    db.commit()
    db.refresh(material)

    return MaterialOut(
        id=material.id,
        name=material.name,
        unit=material.unit,
        current_stock=material.current_stock,
        critical_threshold=material.critical_threshold,
        co2_factor=material.co2_factor,
        status=material_status(material),
        trend=get_material_trend(db, material.id),
    )


@app.delete("/api/materials/{material_id}")
def delete_material(
    material_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_auth),
):
    material = db.get(Material, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Malzeme bulunamadi")
    db.delete(material)
    db.commit()
    return {"ok": True}


@app.get("/api/materials/export")
def export_materials(db: Session = Depends(get_db), _: None = Depends(require_auth)):
    materials = db.execute(select(Material).order_by(Material.name)).scalars().all()
    rows = [
        {
            "Malzeme": m.name,
            "Birim": m.unit,
            "Stok Miktari": m.current_stock,
            "Kritik Esik": m.critical_threshold,
            "Durum": material_status(m),
        }
        for m in materials
    ]
    df = pd.DataFrame(rows)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Malzemeler")
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=malzemeler.xlsx"},
    )


@app.get("/api/movements", response_model=list[MovementOut])
def list_movements(
    limit: int = Query(default=20, le=200),
    material_id: int | None = Query(default=None),
    movement_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: None = Depends(require_auth),
):
    query = select(StockMovement)
    if material_id:
        query = query.where(StockMovement.material_id == material_id)
    if movement_type in ("giris", "cikis"):
        query = query.where(StockMovement.movement_type == movement_type)
    query = query.order_by(StockMovement.created_at.desc()).limit(limit)

    movements = db.execute(query).scalars().all()
    return [
        MovementOut(
            id=mv.id,
            material_id=mv.material_id,
            material_name=mv.material.name,
            movement_type=mv.movement_type,
            quantity=mv.quantity,
            note=mv.note,
            supplier=mv.supplier,
            created_by=mv.created_by,
            created_at=mv.created_at,
        )
        for mv in movements
    ]


@app.post("/api/movements", response_model=MovementOut)
def create_movement(
    payload: MovementCreate,
    db: Session = Depends(get_db),
    _: None = Depends(require_auth),
):
    if payload.movement_type not in ("giris", "cikis"):
        raise HTTPException(status_code=400, detail="Gecersiz hareket tipi")
    if payload.quantity <= 0:
        raise HTTPException(status_code=400, detail="Miktar sifirdan buyuk olmalidir")

    material = db.get(Material, payload.material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Malzeme bulunamadi")

    if payload.movement_type == "cikis":
        if payload.quantity > material.current_stock:
            raise HTTPException(status_code=400, detail="Stoktan fazla cikis yapilamaz")
        material.current_stock -= payload.quantity
    else:
        material.current_stock += payload.quantity

    movement = StockMovement(
        material_id=material.id,
        movement_type=payload.movement_type,
        quantity=payload.quantity,
        note=payload.note,
        supplier=payload.supplier if payload.movement_type == "giris" else None,
        created_by=LOGIN_USERNAME,
    )
    db.add(movement)
    db.commit()
    db.refresh(movement)

    return MovementOut(
        id=movement.id,
        material_id=movement.material_id,
        material_name=material.name,
        movement_type=movement.movement_type,
        quantity=movement.quantity,
        note=movement.note,
        supplier=movement.supplier,
        created_by=movement.created_by,
        created_at=movement.created_at,
    )


def compute_material_analysis(db: Session, material: Material) -> dict:
    movements = db.execute(
        select(StockMovement).where(StockMovement.material_id == material.id)
    ).scalars().all()

    daily_totals = compute_daily_consumption(movements, days=90)
    avg_daily, days_remaining, message = forecast_days_remaining(daily_totals, material.current_stock)

    return {
        "material_id": material.id,
        "material_name": material.name,
        "unit": material.unit,
        "current_stock": material.current_stock,
        "critical_threshold": material.critical_threshold,
        "daily_consumption": [
            {"date": d, "quantity": round(q, 2)} for d, q in sorted(daily_totals.items())
        ],
        "avg_daily_consumption": round(avg_daily, 2),
        "days_remaining": days_remaining,
        "forecast_message": message,
    }


@app.get("/api/materials/{material_id}/analysis", response_model=MaterialAnalysis)
def get_material_analysis(
    material_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_auth),
):
    material = db.get(Material, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Malzeme bulunamadi")

    return MaterialAnalysis(**compute_material_analysis(db, material))


@app.get("/api/materials/{material_id}/report")
def download_material_report(
    material_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_auth),
):
    material = db.get(Material, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Malzeme bulunamadi")

    analysis = compute_material_analysis(db, material)
    pdf_buffer = build_material_report(analysis)

    raw_filename = f"{material.name.replace(' ', '_')}_rapor.pdf"
    ascii_fallback = raw_filename.encode("ascii", "ignore").decode("ascii") or "rapor.pdf"
    encoded_filename = quote(raw_filename)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f"attachment; filename=\"{ascii_fallback}\"; filename*=UTF-8''{encoded_filename}"
            )
        },
    )


@app.get("/api/reports/consumption-comparison", response_model=list[ConsumptionComparisonItem])
def consumption_comparison(
    days: int = Query(default=30, le=90),
    db: Session = Depends(get_db),
    _: None = Depends(require_auth),
):
    since = datetime.utcnow() - timedelta(days=days)
    # Farkli birimler (m3, adet) ayni cubuk grafikte anlamsiz bir karsilastirma
    # yaratir; ozet karttaki gibi burada da sadece ton bazli malzemeler kiyaslanir.
    materials = db.execute(
        select(Material).where(Material.unit == "ton").order_by(Material.name)
    ).scalars().all()

    result = []
    for m in materials:
        total = db.execute(
            select(func.coalesce(func.sum(StockMovement.quantity), 0.0)).where(
                StockMovement.material_id == m.id,
                StockMovement.movement_type == "cikis",
                StockMovement.created_at >= since,
            )
        ).scalar_one()
        result.append(
            ConsumptionComparisonItem(
                material_id=m.id,
                material_name=m.name,
                unit=m.unit,
                total_consumption=round(float(total), 2),
            )
        )
    return result


@app.get("/api/environmental/summary", response_model=EnvironmentalSummary)
def environmental_summary(
    days: int = Query(default=30, le=90),
    db: Session = Depends(get_db),
    _: None = Depends(require_auth),
):
    since = datetime.utcnow() - timedelta(days=days)
    materials = db.execute(select(Material).order_by(Material.name)).scalars().all()

    items = []
    total_co2_kg = 0.0
    for m in materials:
        total_consumption = db.execute(
            select(func.coalesce(func.sum(StockMovement.quantity), 0.0)).where(
                StockMovement.material_id == m.id,
                StockMovement.movement_type == "cikis",
                StockMovement.created_at >= since,
            )
        ).scalar_one()
        material_co2_kg = round(float(total_consumption) * m.co2_factor, 2)
        total_co2_kg += material_co2_kg
        items.append(
            EnvironmentalItem(
                material_id=m.id,
                material_name=m.name,
                unit=m.unit,
                total_consumption=round(float(total_consumption), 2),
                co2_factor=m.co2_factor,
                total_co2_kg=material_co2_kg,
            )
        )

    return EnvironmentalSummary(
        days=days,
        total_co2_kg=round(total_co2_kg, 2),
        total_co2_ton=round(total_co2_kg / 1000, 2),
        items=items,
    )


@app.get("/api/suppliers/summary", response_model=list[SupplierSummaryItem])
def suppliers_summary(db: Session = Depends(get_db), _: None = Depends(require_auth)):
    movements = db.execute(
        select(StockMovement).where(
            StockMovement.movement_type == "giris",
            StockMovement.supplier.isnot(None),
            StockMovement.supplier != "",
        )
    ).scalars().all()

    grouped: dict[str, dict] = {}
    for mv in movements:
        entry = grouped.setdefault(
            mv.supplier, {"deliveries": 0, "last_delivery": mv.created_at, "materials": {}}
        )
        entry["deliveries"] += 1
        entry["last_delivery"] = max(entry["last_delivery"], mv.created_at)
        mat_entry = entry["materials"].setdefault(
            mv.material.name, {"unit": mv.material.unit, "total_quantity": 0.0}
        )
        mat_entry["total_quantity"] += mv.quantity

    result = []
    for supplier, data in sorted(grouped.items()):
        result.append(
            SupplierSummaryItem(
                supplier=supplier,
                deliveries=data["deliveries"],
                last_delivery=data["last_delivery"],
                materials=[
                    SupplierMaterialBreakdown(
                        material_name=name, unit=info["unit"], total_quantity=round(info["total_quantity"], 2)
                    )
                    for name, info in sorted(data["materials"].items())
                ],
            )
        )
    return result


@app.get("/api/alerts", response_model=list[AlertOut])
def get_alerts(db: Session = Depends(get_db), _: None = Depends(require_auth)):
    materials = db.execute(select(Material)).scalars().all()
    critical = [m for m in materials if material_status(m) == "kritik"]
    return [
        AlertOut(
            id=m.id,
            name=m.name,
            current_stock=m.current_stock,
            critical_threshold=m.critical_threshold,
            unit=m.unit,
        )
        for m in critical
    ]


@app.get("/api/reports/summary-pdf")
def download_summary_report(db: Session = Depends(get_db), _: None = Depends(require_auth)):
    materials = db.execute(select(Material).order_by(Material.name)).scalars().all()

    critical_count = sum(1 for m in materials if material_status(m) == "kritik")
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_out = db.execute(
        select(StockMovement)
        .join(Material)
        .where(
            StockMovement.movement_type == "cikis",
            StockMovement.created_at >= week_ago,
            Material.unit == "ton",
        )
    ).scalars().all()
    summary = {
        "total_materials": len(materials),
        "critical_materials": critical_count,
        "total_consumption_7d": round(sum(m.quantity for m in recent_out), 2),
    }

    material_rows = [
        {
            "name": m.name,
            "unit": m.unit,
            "current_stock": m.current_stock,
            "critical_threshold": m.critical_threshold,
            "status": material_status(m),
        }
        for m in materials
    ]
    alert_rows = [{"name": m.name} for m in materials if material_status(m) == "kritik"]

    since_30d = datetime.utcnow() - timedelta(days=30)
    comparison_rows = []
    for m in [m for m in materials if m.unit == "ton"]:
        total = db.execute(
            select(func.coalesce(func.sum(StockMovement.quantity), 0.0)).where(
                StockMovement.material_id == m.id,
                StockMovement.movement_type == "cikis",
                StockMovement.created_at >= since_30d,
            )
        ).scalar_one()
        comparison_rows.append({"material_name": m.name, "total_consumption": round(float(total), 2)})

    pdf_buffer = build_summary_report(summary, material_rows, alert_rows, comparison_rows)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=envanter_genel_rapor.pdf"},
    )
