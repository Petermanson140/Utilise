import os
import pandas as pd
from prophet import Prophet
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ── UK Monthly Seasonal Weights (Normalized around 1.0) ─────────────
# Based on Ofgem / NEED UK energy consumption profile data
UK_SEASONAL_WEIGHTS = {
    1:  {"electricity": 1.20, "gas": 1.80, "water": 0.95},  # January
    2:  {"electricity": 1.15, "gas": 1.70, "water": 0.95},  # February
    3:  {"electricity": 1.05, "gas": 1.30, "water": 1.00},  # March
    4:  {"electricity": 0.95, "gas": 0.90, "water": 1.00},  # April
    5:  {"electricity": 0.90, "gas": 0.50, "water": 1.05},  # May
    6:  {"electricity": 0.85, "gas": 0.30, "water": 1.05},  # June
    7:  {"electricity": 0.85, "gas": 0.25, "water": 1.10},  # July
    8:  {"electricity": 0.85, "gas": 0.25, "water": 1.10},  # August
    9:  {"electricity": 0.90, "gas": 0.40, "water": 1.00},  # September
    10: {"electricity": 1.00, "gas": 0.90, "water": 0.95},  # October
    11: {"electricity": 1.10, "gas": 1.40, "water": 0.95},  # November
    12: {"electricity": 1.20, "gas": 1.70, "water": 0.90},  # December
}


def prepare_real_data(bills: list) -> pd.DataFrame:
    """
    Convert user bill records into a clean DataFrame sorted chronologically.
    """
    records = []
    
    for bill in bills:
        date_str = f"{bill['year']}-{bill['month']}-01"
        try:
            date = pd.to_datetime(date_str, format="%Y-%B-%d")
        except Exception:
            try:
                date = pd.to_datetime(date_str, format="%Y-%m-%d")
            except Exception:
                continue
        
        elec = float(bill.get("electricity_cost", 0.0))
        gas = float(bill.get("gas_cost", 0.0))
        water = float(bill.get("water_cost", 0.0))
        
        records.append({
            "ds": date,
            "month_num": int(date.month),
            "electricity": elec,
            "gas": gas,
            "water": water,
            "total": elec + gas + water
        })
    
    if not records:
        return pd.DataFrame(columns=["ds", "month_num", "electricity", "gas", "water", "total"])

    return pd.DataFrame(records).sort_values("ds").reset_index(drop=True)


def forecast_costs(
    bills: list,
    property_type: str = None,
    num_occupants: int = None,
    periods: int = 12
) -> dict:
    """
    Non-synthetic forecasting pipeline:
    - < 12 months: Uses UK Seasonal Indexing derived from real bill baseline.
    - >= 12 months: Uses Prophet ML seasonal model.
    """
    df = prepare_real_data(bills)

    if df.empty:
        raise ValueError("No valid bill records provided. At least 1 historical bill is required.")

    num_obs = len(df)
    last_date = df["ds"].max()
    monthly_forecasts = []

    # ── Strategy A: < 12 months (Seasonal Indexing on Real Bills) ───────
    if num_obs < 12:
        print(f"📊 Forecasting via Seasonal Indexing using {num_obs} authentic bill(s)...")

        # Step 1: Deseasonalize user's bills to calculate their true average baseline
        elec_baselines, gas_baselines, water_baselines = [], [], []

        for _, row in df.iterrows():
            m_num = row["month_num"]
            weights = UK_SEASONAL_WEIGHTS[m_num]

            elec_baselines.append(row["electricity"] / weights["electricity"])
            gas_baselines.append(row["gas"] / weights["gas"])
            water_baselines.append(row["water"] / weights["water"])

        base_elec = sum(elec_baselines) / len(elec_baselines)
        base_gas = sum(gas_baselines) / len(gas_baselines)
        base_water = sum(water_baselines) / len(water_baselines)

        # Step 2: Apply UK seasonal curves to baseline for future months
        for i in range(1, periods + 1):
            next_date = last_date + pd.DateOffset(months=i)
            m_num = next_date.month
            weights = UK_SEASONAL_WEIGHTS[m_num]

            elec_cost  = round(base_elec * weights["electricity"], 2)
            gas_cost   = round(base_gas * weights["gas"], 2)
            water_cost = round(base_water * weights["water"], 2)
            total_cost = round(elec_cost + gas_cost + water_cost, 2)

            monthly_forecasts.append({
                "month": next_date.strftime("%B"),
                "year": int(next_date.year),
                "month_num": int(m_num),
                "electricity_cost": elec_cost,
                "gas_cost": gas_cost,
                "water_cost": water_cost,
                "total_cost": total_cost,
            })

    # ── Strategy B: >= 12 months (Fit Prophet Model on Real Multi-Year Data) ─
    else:
        print(f"📈 Fitting Prophet seasonal model on {num_obs} real historical bills...")
        results = {}

        for bill_type in ["electricity", "gas", "water"]:
            prophet_df = df[["ds", bill_type]].rename(columns={bill_type: "y"})

            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=False,
                daily_seasonality=False,
                seasonality_mode="multiplicative"
            )
            model.fit(prophet_df)

            future = model.make_future_dataframe(periods=periods, freq="MS")
            forecast = model.predict(future)
            results[bill_type] = forecast.tail(periods)[["ds", "yhat"]]

        for i in range(periods):
            month_date = results["electricity"].iloc[i]["ds"]
            elec_cost  = round(max(float(results["electricity"].iloc[i]["yhat"]), 0.0), 2)
            gas_cost   = round(max(float(results["gas"].iloc[i]["yhat"]), 0.0), 2)
            water_cost = round(max(float(results["water"].iloc[i]["yhat"]), 0.0), 2)
            total_cost = round(elec_cost + gas_cost + water_cost, 2)

            monthly_forecasts.append({
                "month": month_date.strftime("%B"),
                "year": int(month_date.year),
                "month_num": int(month_date.month),
                "electricity_cost": elec_cost,
                "gas_cost": gas_cost,
                "water_cost": water_cost,
                "total_cost": total_cost
            })

    # ── Identify Most & Least Expensive Months ─────────────────────────
    sorted_by_total = sorted(monthly_forecasts, key=lambda x: x["total_cost"])
    
    num_highlights = min(3, len(monthly_forecasts))
    least_expensive = sorted_by_total[:num_highlights]
    most_expensive  = sorted_by_total[-num_highlights:][::-1]

    for month in monthly_forecasts:
        month["is_most_expensive"]  = month in most_expensive
        month["is_least_expensive"] = month in least_expensive

    annual_predicted_total = round(sum(m["total_cost"] for m in monthly_forecasts), 2)

    return {
        "monthly_forecasts": monthly_forecasts,
        "most_expensive_months": most_expensive,
        "least_expensive_months": least_expensive,
        "annual_predicted_total": annual_predicted_total
    }


#Verification Run 
if __name__ == "__main__":
    sample_bills = [
        {"month": "January", "year": 2026, "electricity_cost": 95.50, "gas_cost": 120.00, "water_cost": 38.00},
        {"month": "February", "year": 2026, "electricity_cost": 88.00, "gas_cost": 115.00, "water_cost": 36.00},
        {"month": "March", "year": 2026, "electricity_cost": 75.00, "gas_cost": 89.00, "water_cost": 37.00}
    ]

    results = forecast_costs(bills=sample_bills, periods=12)

    print("Monthly Cost Forecast (Authentic Seasonal Curve):")
    print("-" * 65)
    for m in results["monthly_forecasts"]:
        tag = ""
        if m["is_most_expensive"]:
            tag = " ← MOST EXPENSIVE"
        elif m["is_least_expensive"]:
            tag = " ← LEAST EXPENSIVE"
            
        print(
            f"{m['month']} {m['year']}: £{m['total_cost']} total "
            f"(Elec: £{m['electricity_cost']} | Gas: £{m['gas_cost']} | Water: £{m['water_cost']}){tag}"
        )

    print(f"Predicted Annual Total: £{results['annual_predicted_total']}")
