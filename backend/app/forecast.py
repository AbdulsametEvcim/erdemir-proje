from datetime import datetime, timedelta

import numpy as np
from sklearn.linear_model import LinearRegression


def compute_daily_consumption(movements: list, days: int = 90) -> dict[str, float]:
    """Verilen hareketlerden gun bazinda toplam cikis miktarini hesaplar."""
    today = datetime.utcnow().date()
    start_date = today - timedelta(days=days - 1)

    daily_totals = {
        (start_date + timedelta(days=i)).isoformat(): 0.0 for i in range(days)
    }

    for m in movements:
        if m.movement_type != "cikis":
            continue
        day = m.created_at.date()
        if day < start_date or day > today:
            continue
        key = day.isoformat()
        daily_totals[key] = daily_totals.get(key, 0.0) + m.quantity

    return daily_totals


def forecast_days_remaining(daily_totals: dict[str, float], current_stock: float) -> tuple[float, float | None, str]:
    """Son gunlerdeki tuketim trendine bakarak kacan gun sonra tukenecegini tahmin eder."""
    dates = sorted(daily_totals.keys())
    values = np.array([daily_totals[d] for d in dates])

    avg_daily = float(values.mean()) if len(values) else 0.0

    nonzero_days = values[values > 0]
    if len(nonzero_days) == 0 or avg_daily <= 0:
        return avg_daily, None, "Son donemde tuketim hareketi yok, tahmin yapilamiyor."

    x = np.arange(len(values)).reshape(-1, 1)
    y = np.cumsum(values)
    model = LinearRegression()
    model.fit(x, y)
    daily_rate = float(model.coef_[0])

    if daily_rate <= 0:
        daily_rate = avg_daily

    if daily_rate <= 0:
        return avg_daily, None, "Tuketim trendi durgun, tahmin yapilamiyor."

    days_remaining = current_stock / daily_rate
    message = f"Bu trend devam ederse yaklasik {days_remaining:.0f} gun sonra tukenir."
    return avg_daily, round(days_remaining, 1), message


def compute_trend(daily_totals: dict[str, float]) -> str:
    """Son 7 gunu, ondan onceki 7 gunle karsilastirarak tuketim trendini belirler."""
    dates = sorted(daily_totals.keys())
    if len(dates) < 14:
        return "sabit"

    older_days = dates[-14:-7]
    recent_days = dates[-7:]
    older_sum = sum(daily_totals[d] for d in older_days)
    recent_sum = sum(daily_totals[d] for d in recent_days)

    if older_sum == 0 and recent_sum == 0:
        return "sabit"
    if recent_sum > older_sum * 1.05:
        return "artiyor"
    if recent_sum < older_sum * 0.95:
        return "azaliyor"
    return "sabit"
