"""Monthly spending prediction using Linear Regression.

This module is independent of Django views. It takes plain data (a list of
(year, month, total) values) and returns a PredictionResult. Keeping it
separate makes it easy to test and reuse.
"""
from dataclasses import dataclass
from typing import Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

MIN_MONTHS_REQUIRED = 3
MIN_MONTHS_FOR_EVALUATION = 6

INSUFFICIENT_DATA_MESSAGE = (
    f"At least {MIN_MONTHS_REQUIRED} months of expense history is required to generate a prediction."
)


@dataclass
class PredictionResult:
    success: bool
    message: str
    predicted_amount: Optional[float] = None
    next_month_label: Optional[str] = None
    months_used: int = 0
    mae: Optional[float] = None  # mean absolute error on the held-out last month(s)
    trend_per_month: Optional[float] = None  # slope of the fitted line

    def to_dict(self):
        return {
            "success": self.success,
            "message": self.message,
            "predicted_amount": self.predicted_amount,
            "next_month_label": self.next_month_label,
            "months_used": self.months_used,
            "mae": self.mae,
            "trend_per_month": self.trend_per_month,
        }


def prepare_monthly_dataframe(monthly_totals: Sequence[Tuple[int, int, float]]) -> pd.DataFrame:
    """Turn (year, month, total) tuples into a clean, sorted DataFrame with a time index.

    Cleaning steps: drop missing/negative totals, merge duplicate months,
    sort chronologically, then fill any skipped calendar months with 0 so the
    time index (month_index = 1, 2, 3, ...) matches real elapsed months.
    """
    df = pd.DataFrame(monthly_totals, columns=["year", "month", "total"])
    if df.empty:
        return df

    df["total"] = pd.to_numeric(df["total"], errors="coerce")
    df = df.dropna(subset=["total"])
    df = df[df["total"] >= 0]
    df = df.groupby(["year", "month"], as_index=False)["total"].sum()
    df["period"] = pd.PeriodIndex(
        df["year"].astype(int).astype(str) + "-" + df["month"].astype(int).astype(str).str.zfill(2),
        freq="M",
    )
    df = df.sort_values("period")

    full_range = pd.period_range(df["period"].min(), df["period"].max(), freq="M")
    df = df.set_index("period").reindex(full_range)
    df["total"] = df["total"].fillna(0.0)
    df = df.drop(columns=["year", "month"]).reset_index().rename(columns={"index": "period"})
    df["month_index"] = np.arange(1, len(df) + 1)
    return df


def predict_next_month(monthly_totals: Sequence[Tuple[int, int, float]]) -> PredictionResult:
    """Fit a Linear Regression on month_index -> total and predict the next month."""
    df = prepare_monthly_dataframe(monthly_totals)
    months_used = len(df)

    if months_used < MIN_MONTHS_REQUIRED:
        return PredictionResult(False, INSUFFICIENT_DATA_MESSAGE, months_used=months_used)

    X = df[["month_index"]].to_numpy()
    y = df["total"].to_numpy()

    # Evaluate only when we have enough data to hold out the most recent month.
    mae = None
    if months_used >= MIN_MONTHS_FOR_EVALUATION:
        eval_model = LinearRegression().fit(X[:-1], y[:-1])
        mae = float(mean_absolute_error(y[-1:], eval_model.predict(X[-1:])))

    model = LinearRegression().fit(X, y)
    next_index = months_used + 1
    predicted = float(max(model.predict([[next_index]])[0], 0.0))  # spending cannot be negative

    next_period = df["period"].iloc[-1] + 1
    return PredictionResult(
        success=True,
        message=(
            "Estimate from a simple linear trend of your past monthly totals. "
            "It is not a guarantee; real spending varies."
        ),
        predicted_amount=round(predicted, 2),
        next_month_label=next_period.strftime("%B %Y"),
        months_used=months_used,
        mae=round(mae, 2) if mae is not None else None,
        trend_per_month=round(float(model.coef_[0]), 2),
    )
