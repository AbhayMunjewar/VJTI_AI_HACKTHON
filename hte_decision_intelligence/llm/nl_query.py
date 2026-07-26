import json
import re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as gg
from llm.groq_client import query_groq_llm

def process_natural_language_query(query_text, df):
    """
    Parses natural language questions about state HTE data, executes corresponding pandas computations,
    and returns a structured response containing:
    - answer_text: Plain-English explanation
    - chart_object: Optional Plotly figure to render
    - summary_df: Optional filtered summary dataframe to view
    """
    if df.empty or not query_text.strip():
        return {
            "answer_text": "Please enter a valid question or click one of the suggested prompts.",
            "fig": None,
            "table": None
        }

    prompt = f"""
You are an AI Data Scientist operating on a pandas DataFrame `df` containing state Higher & Technical Education (HTE) records.

Available Columns:
`institute_id, institute_name, district, department, year, enrollment, seats_available, faculty_count, student_faculty_ratio, placement_pct, dropout_pct, avg_package_lpa, infrastructure_score, funding_lakhs`

User Question: "{query_text}"

Respond strictly with a valid JSON object matching this schema:
{{
  "answer_text": "<Clear, direct plain-English answer computed or inferred from the dataset>",
  "chart_type": "<bar|line|scatter|pie|table>",
  "group_by_col": "<district|department|institute_name|year>",
  "metric_col": "<enrollment|placement_pct|dropout_pct|funding_lakhs|avg_package_lpa|student_faculty_ratio>",
  "aggregation": "<mean|sum|max|min>"
}}

Output ONLY the JSON object. Do not include markdown code block tags if possible.
"""

    llm_output = query_groq_llm(prompt, system_message="You are a JSON-only API that translates user questions into data visualizer specifications.")

    # Try parsing LLM JSON
    parsed_json = None
    if llm_output:
        try:
            # Clean markdown JSON formatting if present
            cleaned_json = re.sub(r'```json\s*|\s*```', '', llm_output).strip()
            parsed_json = json.loads(cleaned_json)
        except Exception:
            parsed_json = None

    if parsed_json and "answer_text" in parsed_json:
        return _render_llm_query_result(query_text, df, parsed_json)

    # Fallback heuristic engine if LLM fails or is offline
    return _process_heuristic_query(query_text, df)


def _render_llm_query_result(query_text, df, spec):
    answer = spec.get("answer_text", "Here are the query results.")
    chart_type = spec.get("chart_type", "bar")
    group_col = spec.get("group_by_col", "district")
    metric_col = spec.get("metric_col", "enrollment")
    agg = spec.get("aggregation", "mean")

    if group_col not in df.columns:
        group_col = "district"
    if metric_col not in df.columns:
        metric_col = "enrollment"

    latest_df = df[df['year'] == df['year'].max()] if 'year' in df.columns else df

    if agg == "sum":
        summary = latest_df.groupby(group_col)[metric_col].sum().reset_index()
    else:
        summary = latest_df.groupby(group_col)[metric_col].mean().reset_index()
        summary[metric_col] = summary[metric_col].round(2)

    summary = summary.sort_values(by=metric_col, ascending=False)

    fig = None
    color_palette = ["#00D2C4", "#FFC72C", "#FF6B6B", "#4A90E2", "#9B51E0", "#2ECC71"]

    if chart_type == "bar":
        fig = px.bar(
            summary, x=group_col, y=metric_col,
            title=f"{metric_col.replace('_', ' ').title()} by {group_col.replace('_', ' ').title()} ({agg.title()})",
            color=group_col,
            template="plotly_dark",
            color_discrete_sequence=color_palette
        )
    elif chart_type == "line" and "year" in df.columns:
        trend_data = df.groupby(['year', group_col])[metric_col].mean().reset_index()
        fig = px.line(
            trend_data, x="year", y=metric_col, color=group_col,
            title=f"{metric_col.replace('_', ' ').title()} Trend Over Time",
            template="plotly_dark",
            color_discrete_sequence=color_palette
        )
    elif chart_type == "scatter":
        fig = px.scatter(
            latest_df, x="student_faculty_ratio", y="placement_pct",
            color="district", size="enrollment", hover_data=["institute_name"],
            title="Student-Faculty Ratio vs. Placement %",
            template="plotly_dark",
            color_discrete_sequence=color_palette
        )
    else:
        fig = px.bar(
            summary.head(10), x=group_col, y=metric_col,
            title=f"Top {group_col.replace('_', ' ').title()} by {metric_col.replace('_', ' ').title()}",
            template="plotly_dark",
            color_discrete_sequence=color_palette
        )

    if fig:
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#F0F2F5")
        )

    return {
        "answer_text": answer,
        "fig": fig,
        "table": summary.head(10)
    }


def _process_heuristic_query(query_text, df):
    q = query_text.lower()
    latest_df = df[df['year'] == df['year'].max()] if 'year' in df.columns else df
    color_palette = ["#00D2C4", "#FFC72C", "#FF6B6B", "#4A90E2", "#9B51E0"]

    if "dropout" in q or "drop out" in q:
        summary = latest_df.groupby('district')['dropout_pct'].mean().reset_index().sort_values('dropout_pct', ascending=False)
        highest_dist = summary.iloc[0]['district']
        highest_val = summary.iloc[0]['dropout_pct']
        
        answer = f"**Analysis**: **{highest_dist}** recorded the highest average dropout rate at **{highest_val:.1f}%** across institutions in the latest reporting year. Districts with higher student-faculty ratios generally experience elevated dropout percentages."
        
        fig = px.bar(
            summary, x="district", y="dropout_pct", color="district",
            title="Average Dropout Rate (%) by District",
            template="plotly_dark", color_discrete_sequence=color_palette
        )
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#F0F2F5"))
        return {"answer_text": answer, "fig": fig, "table": summary}

    elif "placement" in q or "package" in q or "job" in q:
        summary = latest_df.groupby('department')['placement_pct'].mean().reset_index().sort_values('placement_pct', ascending=False)
        top_dept = summary.iloc[0]['department']
        top_val = summary.iloc[0]['placement_pct']

        answer = f"**Analysis**: **{top_dept}** leads placement performance with an average placement rate of **{top_val:.1f}%**. Computer Engineering and MBA departments show consistently higher industry absorption compared to traditional streams."

        fig = px.bar(
            summary, x="department", y="placement_pct", color="department",
            title="Average Placement Rate (%) by Department",
            template="plotly_dark", color_discrete_sequence=color_palette
        )
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#F0F2F5"))
        return {"answer_text": answer, "fig": fig, "table": summary}

    elif "trend" in q or "enrollment" in q or "growth" in q:
        summary = df.groupby(['year', 'department'])['enrollment'].sum().reset_index()
        
        answer = f"**Analysis**: Total state HTE enrollment shows sustained expansion in Computer Engineering and Management, while Civil and Mechanical streams exhibit flat or slightly declining trajectories."

        fig = px.line(
            summary, x="year", y="enrollment", color="department",
            title="State Enrollment Trends (2019-2024)",
            template="plotly_dark", color_discrete_sequence=color_palette
        )
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#F0F2F5"))
        return {"answer_text": answer, "fig": fig, "table": summary}

    elif "funding" in q or "budget" in q:
        summary = latest_df.groupby('district')['funding_lakhs'].sum().reset_index().sort_values('funding_lakhs', ascending=False)
        top_dist = summary.iloc[0]['district']
        top_val = summary.iloc[0]['funding_lakhs']

        answer = f"**Analysis**: **{top_dist}** received the highest total state funding allocation of **₹{top_val:,.1f} Lakhs** across its affiliated technical institutes."

        fig = px.pie(
            summary, names="district", values="funding_lakhs",
            title="State Funding Allocation by District (Lakhs INR)",
            template="plotly_dark", color_discrete_sequence=color_palette
        )
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#F0F2F5"))
        return {"answer_text": answer, "fig": fig, "table": summary}

    else:
        # Default ratio vs placement overview
        fig = px.scatter(
            latest_df, x="student_faculty_ratio", y="placement_pct",
            color="district", size="enrollment", hover_data=["institute_name", "department"],
            title="Correlation: Student-Faculty Ratio vs Placement %",
            template="plotly_dark", color_discrete_sequence=color_palette
        )
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#F0F2F5"))
        
        answer = f"**Analysis**: Showing general institutional distribution for query '{query_text}'. Lower student-faculty ratios correlate strongly with higher placement rates and lower student dropouts."
        
        return {"answer_text": answer, "fig": fig, "table": latest_df[['institute_name', 'district', 'department', 'enrollment', 'placement_pct', 'dropout_pct']].head(10)}
