"""
State Higher & Technical Education Decision Intelligence Platform
High-Precision Enrollment Prediction Pipeline using XGBoost Regressor

This script implements an enhanced, production-ready machine learning pipeline with 
advanced feature engineering to achieve >95% prediction accuracy (MAPE < 5%) for student 
enrollment (filled seats) in the next academic year.

Author: Senior Machine Learning Engineer
Organization: State Higher & Technical Education Department
"""

import os
import logging
from typing import Tuple, Dict, Any, List

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    mean_absolute_percentage_error
)
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBRegressor

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("EnrollmentPipelineHighPrecision")

# Global Constants
RANDOM_STATE = 42
DATASET_PATH = "dataset/admissions.csv"
MODEL_SAVE_PATH = "models/enrollment_model.pkl"
PREPROCESSOR_SAVE_PATH = "models/enrollment_preprocessor.pkl"

TARGET_COL = "filled_seats_next_year"
CATEGORICAL_COLS = ["college_id", "branch", "district"]

BASE_NUMERICAL_COLS = [
    "year",
    "applications",
    "sanctioned_seats",
    "filled_seats",
    "vacant_seats",
    "cutoff_percentile",
    "placement_rate",
    "graduation_rate"
]

ENGINEERED_NUMERICAL_COLS = [
    "fill_rate",
    "vacancy_rate",
    "demand_ratio",
    "seats_per_app",
    "placement_cutoff_index"
]

ALL_NUMERICAL_COLS = BASE_NUMERICAL_COLS + ENGINEERED_NUMERICAL_COLS


def load_data(filepath: str = DATASET_PATH) -> pd.DataFrame:
    """
    Load admissions dataset from specified CSV filepath.

    Args:
        filepath (str): Path to the input dataset CSV.

    Returns:
        pd.DataFrame: Loaded pandas DataFrame.

    Raises:
        FileNotFoundError: If the dataset file does not exist.
        ValueError: If dataset is empty or corrupted.
    """
    logger.info(f"Loading dataset from: {filepath}")
    if not os.path.exists(filepath):
        error_msg = f"Dataset file not found at path: {filepath}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    try:
        df = pd.read_csv(filepath)
        if df.empty:
            raise ValueError("Loaded dataset is empty.")
        logger.info(f"Successfully loaded dataset with shape: {df.shape}")
        return df
    except Exception as e:
        logger.error(f"Error loading dataset: {str(e)}")
        raise


def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perform Domain-Specific Feature Engineering to boost model predictive power:
    - Fill Rate: proportion of sanctioned seats filled
    - Vacancy Rate: proportion of sanctioned seats remaining vacant
    - Demand Ratio: applications per sanctioned seat
    - Seats per Application: sanctioned seats per applicant
    - Placement-Cutoff Index: combined quality metric

    Args:
        df (pd.DataFrame): Raw feature dataframe.

    Returns:
        pd.DataFrame: Dataframe augmented with engineered feature columns.
    """
    logger.info("Computing domain-specific engineered features...")
    data = df.copy()
    
    # Avoid division by zero with tiny epsilon (1e-5)
    epsilon = 1e-5
    sanctioned = data["sanctioned_seats"].astype(float) + epsilon
    apps = data["applications"].astype(float) + epsilon

    data["fill_rate"] = data["filled_seats"] / sanctioned
    data["vacancy_rate"] = data["vacant_seats"] / sanctioned
    data["demand_ratio"] = data["applications"] / sanctioned
    data["seats_per_app"] = data["sanctioned_seats"] / apps
    data["placement_cutoff_index"] = (data["placement_rate"] / 100.0) * (data["cutoff_percentile"] / 100.0)

    return data


def preprocess_data(
    df: pd.DataFrame, target_col: str = TARGET_COL
) -> Tuple[pd.DataFrame, pd.Series, ColumnTransformer]:
    """
    Construct preprocessing ColumnTransformer and split DataFrame into features (X) and target (y).

    Numerical imputation: Median
    Categorical imputation: Mode (most frequent)
    Categorical encoding: OneHotEncoder (handle_unknown='ignore')

    Args:
        df (pd.DataFrame): Input DataFrame containing raw features and target.
        target_col (str): Column name for target variable.

    Returns:
        Tuple[pd.DataFrame, pd.Series, ColumnTransformer]: Features X, Target y, and preprocessor ColumnTransformer.
    """
    logger.info("Initializing preprocessing pipeline with feature engineering...")

    # Validate target column existence
    if target_col not in df.columns:
        error_msg = f"Target column '{target_col}' missing from DataFrame."
        logger.error(error_msg)
        raise KeyError(error_msg)

    # 1. Feature Engineering
    df_engineered = add_engineered_features(df)

    # Separate X and y
    feature_cols = CATEGORICAL_COLS + ALL_NUMERICAL_COLS
    X = df_engineered[feature_cols].copy()
    y = df_engineered[target_col].copy()

    # Numerical Transformer: Median Imputation
    numerical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median"))
        ]
    )

    # Categorical Transformer: Mode Imputation + OneHotEncoding
    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
        ]
    )

    # Combine into ColumnTransformer
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numerical_transformer, ALL_NUMERICAL_COLS),
            ("cat", categorical_transformer, CATEGORICAL_COLS)
        ]
    )

    logger.info("Preprocessing ColumnTransformer constructed successfully.")
    return X, y, preprocessor


def train_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    preprocessor: ColumnTransformer
) -> Pipeline:
    """
    Build Scikit-learn Pipeline and perform Hyperparameter Tuning with RandomizedSearchCV.

    Tunes:
    - n_estimators
    - max_depth
    - learning_rate
    - subsample
    - colsample_bytree
    - min_child_weight
    - gamma
    - reg_alpha
    - reg_lambda

    Using 5-fold cross validation.

    Args:
        X_train (pd.DataFrame): Training feature matrix.
        y_train (pd.Series): Training target vector.
        preprocessor (ColumnTransformer): Preprocessor ColumnTransformer.

    Returns:
        Pipeline: Best fitted Scikit-learn Pipeline containing preprocessor and tuned XGBRegressor.
    """
    logger.info("Building high-precision model pipeline with XGBRegressor...")

    base_xgb = XGBRegressor(
        random_state=RANDOM_STATE,
        objective="reg:squarederror",
        n_jobs=-1
    )

    # Full Scikit-learn Pipeline
    full_pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("regressor", base_xgb)
        ]
    )

    # Expanded Hyperparameter Search Distributions for >95% Accuracy
    param_distributions = {
        "regressor__n_estimators": [150, 200, 300, 400],
        "regressor__max_depth": [4, 5, 6, 7],
        "regressor__learning_rate": [0.01, 0.03, 0.05, 0.08],
        "regressor__subsample": [0.7, 0.8, 0.9, 1.0],
        "regressor__colsample_bytree": [0.7, 0.8, 0.9, 1.0],
        "regressor__min_child_weight": [1, 3, 5],
        "regressor__gamma": [0, 0.1, 0.2],
        "regressor__reg_alpha": [0, 0.1, 1.0],
        "regressor__reg_lambda": [1.0, 2.0, 5.0]
    }

    logger.info("Starting Hyperparameter Tuning using 5-Fold RandomizedSearchCV...")

    random_search = RandomizedSearchCV(
        estimator=full_pipeline,
        param_distributions=param_distributions,
        n_iter=15,
        cv=5,
        scoring="neg_root_mean_squared_error",
        random_state=RANDOM_STATE,
        n_jobs=-1,
        verbose=1
    )

    try:
        random_search.fit(X_train, y_train)
        logger.info(f"Hyperparameter tuning completed. Best CV RMSE: {-random_search.best_score_:.4f}")
        logger.info(f"Best Parameters: {random_search.best_params_}")

        best_pipeline = random_search.best_estimator_
        return best_pipeline
    except Exception as e:
        logger.error(f"Error during model training/tuning: {str(e)}")
        raise


def evaluate_model(
    model: Pipeline, X_test: pd.DataFrame, y_test: pd.Series
) -> Tuple[Dict[str, float], np.ndarray]:
    """
    Evaluate trained pipeline on test set and print metrics (MAE, RMSE, R2 Score, MAPE, Accuracy).

    Args:
        model (Pipeline): Fitted Scikit-learn Pipeline.
        X_test (pd.DataFrame): Test feature matrix.
        y_test (pd.Series): Test ground truth target vector.

    Returns:
        Tuple[Dict[str, float], np.ndarray]: Dictionary of evaluation metrics and array of predictions.
    """
    logger.info("Evaluating high-precision model on test dataset...")
    try:
        y_pred = model.predict(X_test)

        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        mape = mean_absolute_percentage_error(y_test, y_pred)
        accuracy_percentage = (1.0 - mape) * 100.0

        metrics = {
            "MAE": float(mae),
            "RMSE": float(rmse),
            "R2_Score": float(r2),
            "MAPE": float(mape),
            "Accuracy_Percentage": float(accuracy_percentage)
        }

        logger.info("Evaluation Completed Successfully.")
        logger.info(f"MAE: {mae:.4f}")
        logger.info(f"RMSE: {rmse:.4f}")
        logger.info(f"R² Score: {r2:.4f}")
        logger.info(f"MAPE: {mape:.4f} ({mape * 100:.2f}%)")
        logger.info(f"Prediction Accuracy: {accuracy_percentage:.2f}%")

        return metrics, y_pred
    except Exception as e:
        logger.error(f"Error evaluating model: {str(e)}")
        raise


def plot_evaluation_results(
    y_test: pd.Series, y_pred: np.ndarray, model: Pipeline
) -> None:
    """
    Generate and save evaluation plots:
    1. Actual vs Predicted
    2. Feature Importance
    3. Residual Plot

    Args:
        y_test (pd.Series): Actual test target values.
        y_pred (np.ndarray): Predicted target values.
        model (Pipeline): Fitted Scikit-learn Pipeline.
    """
    logger.info("Generating evaluation visualization plots...")
    os.makedirs("plots", exist_ok=True)
    sns.set_theme(style="whitegrid")

    # Figure 1: Actual vs Predicted
    fig1, ax1 = plt.subplots(figsize=(8, 6))
    ax1.scatter(y_test, y_pred, alpha=0.5, color="#1f77b4", label="Predictions")
    min_val = min(y_test.min(), y_pred.min())
    max_val = max(y_test.max(), y_pred.max())
    ax1.plot([min_val, max_val], [min_val, max_val], "r--", lw=2, label="Ideal (y=x)")
    ax1.set_xlabel("Actual Filled Seats", fontsize=12)
    ax1.set_ylabel("Predicted Filled Seats", fontsize=12)
    ax1.set_title("Actual vs Predicted Enrollment (>95% Accuracy Target)", fontsize=14, fontweight="bold")
    ax1.legend()
    plt.tight_layout()
    plot1_path = "plots/actual_vs_predicted.png"
    plt.savefig(plot1_path, dpi=300)
    logger.info(f"Saved plot: {plot1_path}")
    plt.close(fig1)

    # Figure 2: Feature Importance
    try:
        preprocessor = model.named_steps["preprocessor"]
        regressor = model.named_steps["regressor"]
        feature_names = preprocessor.get_feature_names_out()
        importances = regressor.feature_importances_

        importance_df = pd.DataFrame({
            "Feature": feature_names,
            "Importance": importances
        }).sort_values(by="Importance", ascending=False).head(15)

        fig2, ax2 = plt.subplots(figsize=(10, 6))
        sns.barplot(
            data=importance_df,
            x="Importance",
            y="Feature",
            hue="Feature",
            palette="viridis",
            legend=False,
            ax=ax2
        )
        ax2.set_title("Top 15 Feature Importances (XGBoost)", fontsize=14, fontweight="bold")
        ax2.set_xlabel("Importance Score", fontsize=12)
        ax2.set_ylabel("Features", fontsize=12)
        plt.tight_layout()
        plot2_path = "plots/feature_importance.png"
        plt.savefig(plot2_path, dpi=300)
        logger.info(f"Saved plot: {plot2_path}")
        plt.close(fig2)
    except Exception as e:
        logger.warning(f"Could not generate feature importance plot: {str(e)}")

    # Figure 3: Residual Plot
    residuals = y_test.values - y_pred
    fig3, ax3 = plt.subplots(figsize=(8, 6))
    ax3.scatter(y_pred, residuals, alpha=0.5, color="#2ca02c")
    ax3.axhline(0, color="red", linestyle="--", lw=2)
    ax3.set_xlabel("Predicted Filled Seats", fontsize=12)
    ax3.set_ylabel("Residuals (Actual - Predicted)", fontsize=12)
    ax3.set_title("Residual Plot", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plot3_path = "plots/residual_plot.png"
    plt.savefig(plot3_path, dpi=300)
    logger.info(f"Saved plot: {plot3_path}")
    plt.close(fig3)


def save_model(
    model: Pipeline,
    preprocessor: ColumnTransformer,
    model_path: str = MODEL_SAVE_PATH,
    preprocessor_path: str = PREPROCESSOR_SAVE_PATH
) -> None:
    """
    Save trained model pipeline and preprocessor transformer to disk using joblib.

    Args:
        model (Pipeline): Trained Scikit-learn Pipeline.
        preprocessor (ColumnTransformer): Preprocessor ColumnTransformer.
        model_path (str): Filepath to save full model.
        preprocessor_path (str): Filepath to save preprocessor.
    """
    logger.info("Saving trained model artifacts...")
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    os.makedirs(os.path.dirname(preprocessor_path), exist_ok=True)

    try:
        joblib.dump(model, model_path)
        logger.info(f"Saved full model pipeline to: {model_path}")

        joblib.dump(preprocessor, preprocessor_path)
        logger.info(f"Saved preprocessor to: {preprocessor_path}")
    except Exception as e:
        logger.error(f"Error saving model artifacts: {str(e)}")
        raise


def predict(
    model: Pipeline,
    preprocessor: ColumnTransformer,
    input_data: pd.DataFrame
) -> np.ndarray:
    """
    Predict enrollment for new input data using trained model pipeline.

    Args:
        model (Pipeline): Trained Scikit-learn Pipeline.
        preprocessor (ColumnTransformer): Preprocessor transformer.
        input_data (pd.DataFrame): New input feature dataframe.

    Returns:
        np.ndarray: Predicted enrollment counts.
    """
    try:
        # Automatically add engineered features if not already present
        if "fill_rate" not in input_data.columns:
            data_to_pred = add_engineered_features(input_data)
        else:
            data_to_pred = input_data.copy()

        required_cols = CATEGORICAL_COLS + ALL_NUMERICAL_COLS
        missing_cols = [c for c in required_cols if c not in data_to_pred.columns]
        if missing_cols:
            raise KeyError(f"Input DataFrame is missing required columns: {missing_cols}")

        predictions = model.predict(data_to_pred[required_cols])
        return predictions
    except Exception as e:
        logger.error(f"Error making predictions: {str(e)}")
        raise


def main() -> None:
    """
    Main execution pipeline runner.
    """
    logger.info("=== Starting High-Precision Enrollment Training Pipeline ===")

    try:
        # 1. Load Data
        df = load_data(DATASET_PATH)

        # 2. Preprocess Data & Split Features/Target
        X, y, preprocessor = preprocess_data(df, TARGET_COL)

        # 3. Train/Test Split (80% Train, 20% Test, random_state=42)
        logger.info("Splitting dataset into 80% Train and 20% Test sets (random_state=42)...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=RANDOM_STATE
        )
        logger.info(f"Train set size: {X_train.shape[0]}, Test set size: {X_test.shape[0]}")

        # 4. Train Model with Hyperparameter Tuning
        best_model = train_model(X_train, y_train, preprocessor)

        # 5. Extract Fitted Preprocessor from Best Model
        fitted_preprocessor = best_model.named_steps["preprocessor"]

        # 6. Evaluate Model
        metrics, y_pred = evaluate_model(best_model, X_test, y_test)

        # 7. Generate Evaluation Plots
        plot_evaluation_results(y_test, y_pred, best_model)

        # 8. Save Model and Preprocessor
        save_model(best_model, fitted_preprocessor, MODEL_SAVE_PATH, PREPROCESSOR_SAVE_PATH)

        # 9. Final Terminal Output Requirement
        print("\n" + "=" * 55)
        print("Training Completed Successfully.")
        print("Model saved successfully.")
        print("Evaluation metrics:")
        print(f"  - Mean Absolute Error (MAE): {metrics['MAE']:.4f}")
        print(f"  - Root Mean Squared Error (RMSE): {metrics['RMSE']:.4f}")
        print(f"  - R² Score: {metrics['R2_Score']:.4f}")
        print(f"  - Mean Absolute Percentage Error (MAPE): {metrics['MAPE']:.4f} ({metrics['MAPE']*100:.2f}%)")
        print(f"  - Overall Prediction Accuracy: {metrics['Accuracy_Percentage']:.2f}%")
        print("=" * 55 + "\n")

    except Exception as e:
        logger.critical(f"Pipeline execution failed: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
