"""
State Higher & Technical Education Decision Intelligence Platform
Enrollment Prediction Inference Script

This script loads the trained model artifacts and performs inference to predict student 
enrollment (filled seats) for new input college dataset records.

Author: Senior Machine Learning Engineer
Organization: State Higher & Technical Education Department
"""

import os
import logging
from typing import Dict, Any, List

import joblib
import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("EnrollmentInference")

# File Paths
MODEL_PATH = "models/enrollment_model.pkl"
PREPROCESSOR_PATH = "models/enrollment_preprocessor.pkl"

REQUIRED_COLUMNS = [
    "college_id",
    "branch",
    "district",
    "year",
    "applications",
    "sanctioned_seats",
    "filled_seats",
    "vacant_seats",
    "cutoff_percentile",
    "placement_rate",
    "graduation_rate"
]


def add_engineered_features(data: pd.DataFrame) -> pd.DataFrame:
    """
    Perform Domain-Specific Feature Engineering for Inference:
    - Fill Rate
    - Vacancy Rate
    - Demand Ratio
    - Seats per Application
    - Placement-Cutoff Index

    Args:
        data (pd.DataFrame): Raw input feature dataframe.

    Returns:
        pd.DataFrame: Dataframe with engineered feature columns.
    """
    df = data.copy()
    epsilon = 1e-5
    sanctioned = df["sanctioned_seats"].astype(float) + epsilon
    apps = df["applications"].astype(float) + epsilon

    df["fill_rate"] = df["filled_seats"] / sanctioned
    df["vacancy_rate"] = df["vacant_seats"] / sanctioned
    df["demand_ratio"] = df["applications"] / sanctioned
    df["seats_per_app"] = df["sanctioned_seats"] / apps
    df["placement_cutoff_index"] = (df["placement_rate"] / 100.0) * (df["cutoff_percentile"] / 100.0)

    return df


def load_model_artifacts(
    model_path: str = MODEL_PATH,
    preprocessor_path: str = PREPROCESSOR_PATH
) -> tuple[Pipeline, ColumnTransformer]:
    """
    Load saved model pipeline and preprocessor transformer from disk.

    Args:
        model_path (str): Filepath to the model pickle file.
        preprocessor_path (str): Filepath to the preprocessor pickle file.

    Returns:
        tuple[Pipeline, ColumnTransformer]: Loaded model pipeline and preprocessor.

    Raises:
        FileNotFoundError: If model files do not exist.
    """
    logger.info(f"Loading model pipeline from: {model_path}")
    if not os.path.exists(model_path):
        error_msg = f"Model file not found at: {model_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    logger.info(f"Loading preprocessor from: {preprocessor_path}")
    if not os.path.exists(preprocessor_path):
        error_msg = f"Preprocessor file not found at: {preprocessor_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    try:
        model: Pipeline = joblib.load(model_path)
        preprocessor: ColumnTransformer = joblib.load(preprocessor_path)
        logger.info("Artifacts loaded successfully.")
        return model, preprocessor
    except Exception as e:
        logger.error(f"Error loading model artifacts: {str(e)}")
        raise


def predict_enrollment(
    model: Pipeline,
    input_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Generate enrollment predictions for input college records.

    Args:
        model (Pipeline): Loaded Scikit-learn Pipeline.
        input_df (pd.DataFrame): DataFrame containing input features.

    Returns:
        pd.DataFrame: Copy of input dataframe with added 'predicted_filled_seats_next_year' column.
    """
    logger.info("Performing prediction on input data...")

    # Check for missing required features
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in input_df.columns]
    if missing_cols:
        error_msg = f"Input dataset missing required columns: {missing_cols}"
        logger.error(error_msg)
        raise KeyError(error_msg)

    try:
        features = add_engineered_features(input_df)
        raw_preds = model.predict(features)
        
        # Clip negative predictions if any and round to nearest integer for seat counts
        preds_rounded = np.clip(np.round(raw_preds), 0, None).astype(int)

        output_df = input_df.copy()
        output_df["predicted_filled_seats_next_year"] = preds_rounded
        logger.info("Predictions generated successfully.")
        return output_df
    except Exception as e:
        logger.error(f"Error during prediction execution: {str(e)}")
        raise


def create_sample_input_data() -> pd.DataFrame:
    """
    Generate sample input data representing various higher education institutions.

    Returns:
        pd.DataFrame: Sample feature dataset for inference.
    """
    sample_records: List[Dict[str, Any]] = [
        {
            "college_id": "COL0001",
            "branch": "BCom",
            "district": "Dharashiv",
            "year": 2025,
            "applications": 904,
            "sanctioned_seats": 410,
            "filled_seats": 316,
            "vacant_seats": 94,
            "cutoff_percentile": 53.24,
            "placement_rate": 68.10,
            "graduation_rate": 81.50
        },
        {
            "college_id": "COL0002",
            "branch": "BSc Mathematics",
            "district": "Yavatmal",
            "year": 2025,
            "applications": 879,
            "sanctioned_seats": 240,
            "filled_seats": 211,
            "vacant_seats": 29,
            "cutoff_percentile": 71.95,
            "placement_rate": 90.00,
            "graduation_rate": 100.00
        },
        {
            "college_id": "COL0008",
            "branch": "BE Computer Engineering",
            "district": "Amravati",
            "year": 2025,
            "applications": 153,
            "sanctioned_seats": 70,
            "filled_seats": 55,
            "vacant_seats": 15,
            "cutoff_percentile": 81.04,
            "placement_rate": 80.80,
            "graduation_rate": 98.70
        },
        {
            "college_id": "COL0020",
            "branch": "BCom",
            "district": "Amravati",
            "year": 2025,
            "applications": 1483,
            "sanctioned_seats": 280,
            "filled_seats": 279,
            "vacant_seats": 1,
            "cutoff_percentile": 67.71,
            "placement_rate": 91.20,
            "graduation_rate": 100.00
        },
        {
            "college_id": "COL0028",
            "branch": "MBBS",
            "district": "Pune",
            "year": 2025,
            "applications": 452,
            "sanctioned_seats": 100,
            "filled_seats": 97,
            "vacant_seats": 3,
            "cutoff_percentile": 99.95,
            "placement_rate": 89.40,
            "graduation_rate": 100.00
        }
    ]
    return pd.DataFrame(sample_records)


def main() -> None:
    """
    Main inference execution handler.
    """
    logger.info("=== Starting Enrollment Prediction Inference ===")

    try:
        # Load Model Pipeline & Preprocessor
        model, preprocessor = load_model_artifacts()

        # Create or Load New Input Data
        sample_df = create_sample_input_data()
        logger.info(f"Loaded {len(sample_df)} new input records for prediction.")

        # Generate Predictions
        results_df = predict_enrollment(model, sample_df)

        # Display Prediction Results
        display_cols = [
            "college_id",
            "branch",
            "district",
            "sanctioned_seats",
            "filled_seats",
            "applications",
            "predicted_filled_seats_next_year"
        ]

        print("\n" + "=" * 70)
        print("ENROLLMENT PREDICTION RESULTS FOR NEXT ACADEMIC YEAR")
        print("=" * 70)
        print(results_df[display_cols].to_string(index=False))
        print("=" * 70 + "\n")

    except Exception as e:
        logger.critical(f"Inference process failed: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
