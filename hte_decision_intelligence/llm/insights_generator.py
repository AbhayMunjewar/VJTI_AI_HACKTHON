import pandas as pd
from llm.groq_client import query_groq_llm

def generate_ai_insights(df_filtered):
    """
    Generates 3-4 bullet point executive insights for the visible data slice.
    Uses Groq LLM (llama-3.3-70b-versatile) with local statistical fallback if offline.
    """
    if df_filtered.empty:
        return [
            "⚠️ No data records match the current filter selection.",
            "💡 Try broadening your district, institute, or department filters."
        ]

    # Calculate summary metrics to feed prompt
    total_enrollment = df_filtered[df_filtered['year'] == df_filtered['year'].max()]['enrollment'].sum()
    avg_placement = df_filtered['placement_pct'].mean()
    avg_dropout = df_filtered['dropout_pct'].mean()
    top_dept = df_filtered.groupby('department')['enrollment'].sum().idxmax()
    worst_dropout_dept = df_filtered.groupby('department')['dropout_pct'].mean().idxmax()
    top_placement_inst = df_filtered.groupby('institute_name')['placement_pct'].mean().idxmax()

    prompt = f"""
Given the following state Higher & Technical Education (HTE) data summary:
- Total Current Enrollment: {total_enrollment:,} students
- Average Placement Rate: {avg_placement:.1f}%
- Average Dropout Rate: {avg_dropout:.1f}%
- Top Enrolled Department: {top_dept}
- Highest Dropout Department: {worst_dropout_dept}
- Leading Institute by Placement: {top_placement_inst}

Generate exactly 3-4 concise, high-impact bullet point insights for state policy makers and institute directors.
Highlight trends, potential risks, and strategic policy recommendations.
Format: Output ONLY bullet points starting with '•'. No extra conversational text.
"""

    llm_output = query_groq_llm(prompt, system_message="You are a Chief Policy Advisor for State Technical Education.")

    if llm_output:
        bullets = [line.strip() for line in llm_output.split('\n') if line.strip().startswith('•') or line.strip().startswith('-')]
        if len(bullets) >= 2:
            return bullets

    # Deterministic heuristic fallback if LLM is unavailable
    fallback_bullets = [
        f"• **Enrollment Surge**: {top_dept} continues to dominate student preferences, accounting for the highest proportion of total enrollment ({total_enrollment:,} active students).",
        f"• **Placement Benchmark**: {top_placement_inst} leads placement outcomes across the visible dataset with an average placement rate above {avg_placement:.1f}%.",
        f"• **Retention Warning**: {worst_dropout_dept} shows elevated dropout rates (avg {avg_dropout:.1f}%), indicating a need for academic counselling and faculty ratio optimization.",
        f"• **Policy Recommendation**: Reallocate state infrastructure funding towards high-dropout districts to improve student-faculty ratios and retention outcomes."
    ]

    return fallback_bullets


def generate_forecast_explanation(selected_entity, forecast_df, metrics):
    """
    Generates a natural-language explanation of predictive model outputs.
    """
    trend = metrics.get('trend_direction', 'Stable')
    cagr = metrics.get('forecast_growth_pct', 0.0)
    r2 = metrics.get('r2_score', 0.8)

    prompt = f"""
Explain the 3-year enrollment forecast for '{selected_entity}':
- Overall Trend: {trend}
- Projected 3-Year Growth: {cagr:.1f}%
- Model R² Accuracy Score: {r2}

Provide a 2-paragraph clear explanation for institute administrators explaining the primary drivers of this trend (e.g. market demand shifts, capacity limits, placement reputation) and suggested strategic actions.
"""

    llm_output = query_groq_llm(prompt, system_message="You are an Academic Data Science Director.")

    if llm_output:
        return llm_output

    # Heuristic fallback
    if cagr > 5.0:
        return f"**Forecast Summary for {selected_entity}**: The 3-year polynomial projection indicates strong positive enrollment growth (+{cagr:.1f}%), backed by high model fit confidence (R² = {r2}).\n\n**Strategic Drivers**: Driven by expanding industry demand, strong placement records, and sustained student preference. It is recommended to expand faculty hiring and laboratory infrastructure to accommodate upcoming cohorts without increasing student-faculty ratios."
    elif cagr < -5.0:
        return f"**Forecast Summary for {selected_entity}**: The model projects a declining enrollment trajectory ({cagr:.1f}%) over the next 3 years.\n\n**Strategic Drivers**: Likely impacted by shifting candidate choices, lower placement conversion rates, or aging physical infrastructure. Immediate intervention via curriculum modernisation, industry tie-ups, and student support counseling is advised."
    else:
        return f"**Forecast Summary for {selected_entity}**: Enrollment is projected to remain stable (+{cagr:.1f}% variation) through 2027.\n\n**Strategic Drivers**: Balanced seat capacity utilization and steady demand. The institute should focus on improving placement packages and research funding to transition towards positive growth."
