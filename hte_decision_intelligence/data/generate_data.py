import os
import pandas as pd
import numpy as np

def generate_hte_dataset(output_path="data/hte_data.csv"):
    """
    Generates a synthetic but highly realistic AISHE-style Higher & Technical Education (HTE) dataset.
    Includes 18 institutes across 6 districts, 5 departments, spanning 6 years (2019-2024).
    Seed set for full reproducibility.
    """
    np.random.seed(42)

    institutes_data = [
        # Pune District
        ("INST_001", "COEP Technological University", "Pune"),
        ("INST_002", "Sinhgad College of Engineering", "Pune"),
        ("INST_003", "MIT World Peace University", "Pune"),

        # Mumbai District
        ("INST_004", "Veermata Jijabai Technological Institute (VJTI)", "Mumbai"),
        ("INST_005", "Sardar Patel Institute of Technology (SPIT)", "Mumbai"),
        ("INST_006", "Shah & Anchor Kutchhi Engineering College", "Mumbai"),

        # Nagpur District
        ("INST_007", "Visvesvaraya National Institute of Technology (VNIT)", "Nagpur"),
        ("INST_008", "Shri Ramdeobaba College of Engineering", "Nagpur"),
        ("INST_009", "Government Engineering College Nagpur", "Nagpur"),

        # Nashik District
        ("INST_010", "K.K. Wagh Institute of Engineering Education", "Nashik"),
        ("INST_011", "MET Institute of Engineering", "Nashik"),
        ("INST_012", "Sandip Institute of Technology & Research", "Nashik"),

        # Chhatrapati Sambhaji Nagar (Aurangabad)
        ("INST_013", "Government College of Engineering Chhatrapati Sambhaji Nagar", "Chhatrapati Sambhaji Nagar"),
        ("INST_014", "Jawaharlal Nehru Engineering College", "Chhatrapati Sambhaji Nagar"),
        ("INST_015", "Deogiri Institute of Engineering", "Chhatrapati Sambhaji Nagar"),

        # Thane District
        ("INST_016", "A.P. Shah Institute of Technology", "Thane"),
        ("INST_017", "Vidyalankar Institute of Technology", "Thane"),
        ("INST_018", "Terna Engineering College", "Thane")
    ]

    departments = [
        "Computer Engineering",
        "Electronics & Telecommunication",
        "Mechanical Engineering",
        "Civil Engineering",
        "MBA / Management Studies"
    ]

    years = [2019, 2020, 2021, 2022, 2023, 2024]

    # Department base multipliers for capacity, placement, package, and enrollment growth trends
    dept_config = {
        "Computer Engineering": {"base_seats": 120, "seat_growth": 10, "placement_base": 88.0, "pkg_base": 11.5, "dropout_base": 3.0, "trend_coef": 12.0},
        "Electronics & Telecommunication": {"base_seats": 120, "seat_growth": 0, "placement_base": 78.0, "pkg_base": 8.0, "dropout_base": 4.5, "trend_coef": 5.0},
        "Mechanical Engineering": {"base_seats": 120, "seat_growth": -5, "placement_base": 68.0, "pkg_base": 6.5, "dropout_base": 7.0, "trend_coef": -3.0},
        "Civil Engineering": {"base_seats": 60, "seat_growth": -5, "placement_base": 62.0, "pkg_base": 5.8, "dropout_base": 8.5, "trend_coef": -4.0},
        "MBA / Management Studies": {"base_seats": 60, "seat_growth": 5, "placement_base": 82.0, "pkg_base": 9.2, "dropout_base": 4.0, "trend_coef": 8.0}
    }

    records = []

    for inst_id, inst_name, district in institutes_data:
        # Tier factor based on top tier institutes vs mid tier
        is_top_tier = "COEP" in inst_name or "VJTI" in inst_name or "VNIT" in inst_name or "SPIT" in inst_name
        tier_multiplier = 1.25 if is_top_tier else 1.0

        for dept in departments:
            cfg = dept_config[dept]

            # Base infrastructure & funding per institute-department pair
            infra_score = round(min(9.8, max(5.5, (8.0 if is_top_tier else 6.8) + np.random.normal(0, 0.4))), 1)
            base_funding = (250.0 if is_top_tier else 120.0) + np.random.normal(0, 15.0)

            for idx, year in enumerate(years):
                year_offset = idx  # 0 to 5

                # Seat availability progression
                seats_available = int(max(30, cfg["base_seats"] + (cfg["seat_growth"] * year_offset) + np.random.choice([0, 0, 10, -10])))

                # Enrollment with trend component
                fill_rate = min(1.0, max(0.45, (0.95 if is_top_tier else 0.80) + (cfg["trend_coef"] * 0.01 * year_offset) + np.random.normal(0, 0.03)))
                enrollment = int(min(seats_available, max(20, round(seats_available * fill_rate))))

                # Faculty Count & Student-Faculty Ratio
                faculty_count = max(3, int(round(enrollment / (13.0 if is_top_tier else 18.0) + np.random.normal(0, 1.0))))
                student_faculty_ratio = round(enrollment / faculty_count, 1)

                # COVID anomaly (2020-2021) adjustment
                covid_factor = -5.0 if year in [2020, 2021] else 0.0

                # Placement Percentage
                placement_pct = min(99.5, max(30.0, round(
                    (cfg["placement_base"] * (1.15 if is_top_tier else 0.95))
                    + (year_offset * 1.5)
                    + (infra_score * 1.2)
                    - (student_faculty_ratio * 0.4)
                    + covid_factor
                    + np.random.normal(0, 2.5), 1
                )))

                # Dropout Percentage
                dropout_pct = min(25.0, max(1.0, round(
                    cfg["dropout_base"]
                    - (infra_score * 0.3)
                    + (student_faculty_ratio * 0.25)
                    + (3.0 if year == 2020 else 0)
                    + np.random.normal(0, 0.8), 1
                )))

                # Average Package (LPA)
                avg_package_lpa = round(max(3.0,
                    (cfg["pkg_base"] * tier_multiplier)
                    + (year_offset * 0.6)
                    + np.random.normal(0, 0.5)
                ), 2)

                # Annual Funding (Lakhs INR)
                funding_lakhs = round(max(40.0, base_funding + (year_offset * 12.0) + np.random.normal(0, 8.0)), 2)

                records.append({
                    "institute_id": inst_id,
                    "institute_name": inst_name,
                    "district": district,
                    "department": dept,
                    "year": year,
                    "enrollment": enrollment,
                    "seats_available": seats_available,
                    "faculty_count": faculty_count,
                    "student_faculty_ratio": student_faculty_ratio,
                    "placement_pct": placement_pct,
                    "dropout_pct": dropout_pct,
                    "avg_package_lpa": avg_package_lpa,
                    "infrastructure_score": infra_score,
                    "funding_lakhs": funding_lakhs
                })

    df = pd.DataFrame(records)

    # Ensure output directory exists
    dir_name = os.path.dirname(output_path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)

    df.to_csv(output_path, index=False)
    print(f"[SUCCESS] HTE Synthetic Dataset generated successfully at '{output_path}' with {len(df)} rows.")
    return df

if __name__ == "__main__":
    generate_hte_dataset("data/hte_data.csv")
