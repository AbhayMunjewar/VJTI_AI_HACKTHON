import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

def forecast_enrollment(df_slice, horizon_years=3):
    """
    Fits an explainable polynomial trend regression model on historical enrollment data
    and generates predictions for upcoming future years (2025-2027) with confidence bounds.
    
    Returns:
    - combined_df: DataFrame with historical actuals + forecasted values with confidence intervals
    - metrics: dictionary containing R2 score, trend direction, growth percentage, and key stats
    """
    if df_slice.empty or len(df_slice['year'].unique()) < 2:
        return pd.DataFrame(), {"trend": "Insufficient Data", "r2": 0.0, "cagr": 0.0}

    # Aggregate enrollment by year for the given slice
    yearly_df = df_slice.groupby('year')['enrollment'].sum().reset_index()
    yearly_df = yearly_df.sort_values('year')

    X_train = yearly_df[['year']].values
    y_train = yearly_df['enrollment'].values

    # Base year scaling for numerical stability
    min_year = X_train.min()
    X_train_scaled = X_train - min_year

    # Polynomial degree 2 for quadratic trend cap
    degree = 2 if len(X_train) >= 4 else 1
    model = make_pipeline(PolynomialFeatures(degree=degree), Ridge(alpha=1.0))
    model.fit(X_train_scaled, y_train)

    # In-sample predictions & residual calculation
    y_pred_in = model.predict(X_train_scaled)
    residuals = y_train - y_pred_in
    dof = max(1, len(y_train) - (degree + 1))
    std_error = np.sqrt(np.sum(residuals ** 2) / dof)

    # Forecast future years
    max_year = yearly_df['year'].max()
    future_years = [max_year + i for i in range(1, horizon_years + 1)]
    X_future = np.array(future_years).reshape(-1, 1)
    X_future_scaled = X_future - min_year

    y_pred_future = model.predict(X_future_scaled)

    # Build historical records
    hist_list = []
    for i, row in yearly_df.iterrows():
        hist_list.append({
            "year": int(row['year']),
            "enrollment": float(row['enrollment']),
            "lower_bound": float(row['enrollment']),
            "upper_bound": float(row['enrollment']),
            "type": "Historical Actual"
        })

    # Build forecast records with expanding margin of error
    forecast_list = []
    for i, yr in enumerate(future_years):
        pred_val = float(max(0, y_pred_future[i]))
        # Uncertainty grows with forecast horizon step
        expansion_factor = 1.0 + (0.25 * (i + 1))
        margin = 1.96 * std_error * expansion_factor
        
        forecast_list.append({
            "year": int(yr),
            "enrollment": round(pred_val, 1),
            "lower_bound": round(max(0.0, pred_val - margin), 1),
            "upper_bound": round(pred_val + margin, 1),
            "type": "AI Forecast"
        })

    combined_df = pd.DataFrame(hist_list + forecast_list)

    # Trend calculation
    first_actual = y_train[0]
    last_actual = y_train[-1]
    last_forecast = y_pred_future[-1]

    growth_historical = ((last_actual - first_actual) / first_actual * 100.0) if first_actual > 0 else 0.0
    forecast_growth = ((last_forecast - last_actual) / last_actual * 100.0) if last_actual > 0 else 0.0

    trend_direction = "Strong Growth 📈" if forecast_growth > 5.0 else ("Decline 📉" if forecast_growth < -5.0 else "Stable / Flat ⚖️")

    # Estimate R2 score
    ss_tot = np.sum((y_train - np.mean(y_train))**2)
    ss_res = np.sum(residuals**2)
    r2_score = round(1 - (ss_res / (ss_tot + 1e-8)), 3)

    metrics = {
        "trend_direction": trend_direction,
        "historical_growth_pct": round(growth_historical, 1),
        "forecast_growth_pct": round(forecast_growth, 1),
        "r2_score": max(0.0, min(1.0, r2_score)),
        "std_error": round(float(std_error), 1),
        "last_actual": int(last_actual),
        "forecast_2027": round(float(last_forecast), 1)
    }

    return combined_df, metrics
