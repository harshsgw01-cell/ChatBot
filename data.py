import pandas as pd
from db import get_connection

# ------------------------------
# FINANCE: from finance_kpi
# ------------------------------
def fetch_financial_data():
    conn = get_connection()
    if not conn:
        return {"revenue": 0.0, "expenses": 0.0, "profit": 0.0}

    cur = conn.cursor()
    cur.execute("""
        SELECT revenue_qr, expenses_qr
        FROM finance_kpi
        ORDER BY id DESC
    """)
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return {"revenue": 0.0, "expenses": 0.0, "profit": 0.0}

    revenue, expenses = row
    profit = revenue - expenses
    return {
        "revenue": float(revenue),
        "expenses": float(expenses),
        "profit": float(profit),
    }

# ------------------------------
# SALES TREND: from monthly_revenue
# ------------------------------
def fetch_sales_data():
    conn = get_connection()
    if not conn:
        return []

    df = pd.read_sql(
        """
        SELECT month_name AS "Month",
               revenue_qr AS "Revenue"
        FROM monthly_revenue
        ORDER BY year, month
        """,
        conn
    )
    conn.close()
    return df.to_dict(orient="records")

# ------------------------------
# EMPLOYEES: from employees + former_employees
# ------------------------------
def fetch_employee_data():
    conn = get_connection()
    if not conn:
        return {
            "total_employees": 0,
            "active_employees": 0,
            "former_employees": 0,
            "attrition_rate": 0.0,
            "turnover_last_year": 0,
            "turnover_breakdown": [],
            "top_turnover_department": None,
            "top_turnover_pct": 0.0,
            "turnover_main_reasons": [],
            "turnover_cost_qr": 0.0,
            "engagement_score": 0.0,
            "new_joiners_2023_2024": 0,
            "on_probation": 0,
        }

    cur = conn.cursor()

    # current employees
    cur.execute("SELECT COUNT(*) FROM employees;")
    total_emp = cur.fetchone()[0]

    # former employees
    cur.execute("SELECT COUNT(*) FROM former_employees;")
    former_emp = cur.fetchone()[0]

    total_population = total_emp + former_emp
    attrition_rate = (former_emp / total_population * 100) if total_population > 0 else 0.0

    # turnover in last 12 months
    cur.execute("""
        SELECT COUNT(*)
        FROM former_employees
        WHERE date_of_leaving >= DATEADD(month, -12, GETDATE())
    """)
    turnover_last_year = cur.fetchone()[0]

    # turnover breakdown by department
    cur.execute("""
        SELECT
            department,
            COUNT(*) AS totalformeremployees,
            SUM(CASE WHEN termination_type = 'Termination' THEN 1 ELSE 0 END) AS terminations,
            SUM(CASE WHEN termination_type = 'Resignation' THEN 1 ELSE 0 END) AS resignations,
            SUM(
                CASE
                    WHEN LOWER(termination_sub_reason) LIKE '%family%' OR
                         LOWER(termination_sub_reason) LIKE '%marriage%' OR
                         LOWER(termination_sub_reason) LIKE '%child%' OR
                         LOWER(termination_sub_reason) LIKE '%parent%'
                    THEN 1 ELSE 0
                END
            ) AS family_related
        FROM former_employees
        GROUP BY department
    """)
    dept_rows = cur.fetchall()

    turnover_breakdown = []
    top_turnover_department = None
    top_turnover_pct = 0.0

    if former_emp > 0 and dept_rows:
        for row in dept_rows:
            dept, total_exits, terminations, resignations, family_related = row
            pct = (total_exits / former_emp) * 100 if former_emp > 0 else 0.0
            turnover_breakdown.append({
                "department": dept,
                "total_exits": int(total_exits),
                "terminations": int(terminations or 0),
                "resignations": int(resignations or 0),
                "family_related_exits": int(family_related or 0),
                "percentage_of_exits": round(pct, 2),
            })

        # find department with highest exits
        top_row = max(turnover_breakdown, key=lambda r: r["total_exits"])
        top_turnover_department = top_row["department"]
        top_turnover_pct = top_row["percentage_of_exits"]

    # high-level reasons
    turnover_main_reasons = [
        "family-related commitments and relocation (childcare, elderly parents, marriage)",
        "long working hours, stress and work-life balance issues",
        "better external opportunities or higher pay elsewhere",
        "performance, safety or policy-related terminations",
    ]

    # 🔹 turnover cost calculation from salary columns
    cur.execute("""
        SELECT ISNULL(SUM(basic_salary + ISNULL(housing_allowance,0) + ISNULL(transport_allowance,0)),0)
        FROM former_employees
    """)
    total_salary_left = cur.fetchone()[0]
    turnover_cost_qr = float(total_salary_left) * 0.40

    # engagement placeholder
    engagement_score = 0.0

    # new joiners 2023–2024
    cur.execute("SELECT COUNT(*) FROM new_joiners_2023_2024;")
    new_joiners_count = cur.fetchone()[0]

    # on probation
    cur.execute("""
        SELECT COUNT(*)
        FROM new_joiners_2023_2024
        WHERE LOWER(probation_status) = 'on probation'
    """)
    on_probation = cur.fetchone()[0]

    cur.close()
    conn.close()

    return {
        "total_employees": total_emp,
        "active_employees": total_emp,
        "former_employees": former_emp,
        "attrition_rate": round(attrition_rate, 2),
        "turnover_last_year": turnover_last_year,
        "turnover_breakdown": turnover_breakdown,
        "top_turnover_department": top_turnover_department,
        "top_turnover_pct": round(top_turnover_pct, 2),
        "turnover_main_reasons": turnover_main_reasons,
        "turnover_cost_qr": turnover_cost_qr,
        "engagement_score": engagement_score,
        "new_joiners_2023_2024": new_joiners_count,
        "on_probation": on_probation,
    }

# ------------------------------
# EMPLOYEE DETAILS
# ------------------------------
def fetch_employee_details():
    conn = get_connection()
    if not conn:
        return pd.DataFrame()

    df = pd.read_sql(
        """
        SELECT
            employee_id,
            first_name,
            last_name,
            nationality,
            position,
            department,
            date_of_joining,
            contract_type,
            basic_salary,
            housing_allowance,
            transport_allowance
        FROM employees
        ORDER BY employee_id
        """,
        conn,
    )
    conn.close()
    return df

# ------------------------------
# FORMER EMPLOYEES
# ------------------------------
def fetch_former_employees():
    conn = get_connection()
    if not conn:
        return pd.DataFrame()

    df = pd.read_sql(
        """
        SELECT
            employee_id,
            first_name,
            last_name,
            nationality,
            position,
            department,
            date_of_joining,
            date_of_leaving,
            contract_type,
            basic_salary,
            housing_allowance,
            transport_allowance,
            leaving_reason,
            termination_type,
            termination_sub_reason
        FROM former_employees
        ORDER BY date_of_leaving DESC
        """,
        conn,
    )
    conn.close()
    return df

# ------------------------------
# INSTRUCTOR PERFORMANCE
# ------------------------------
def fetch_instructor_performance():
    conn = get_connection()
    if not conn:
        return pd.DataFrame()

    df = pd.read_sql(
        """
        SELECT employee_name,
               review_date,
               overall_score,
               overall_rating
        FROM instructor_performance
        ORDER BY review_date DESC
        """,
        conn
    )
    conn.close()
    return df

# ------------------------------
# NEW JOINERS
# ------------------------------
def fetch_new_joiners():
    conn = get_connection()
    if not conn:
        return pd.DataFrame()

    df = pd.read_sql(
        """
        SELECT employee_id,
               first_name,
               last_name,
               nationality,
               department,
               date_of_joining,
               contract_type,
               probation_status
        FROM new_joiners_2023_2024
        ORDER BY date_of_joining DESC
        """,
        conn
    )
    conn.close()
    return df

# ------------------------------
# EMPLOYEE TREND
# ------------------------------
def fetch_employee_trend():
    conn = get_connection()
    if not conn:
        return pd.DataFrame()

    df = pd.read_sql(
        """
        SELECT MONTH(date_of_joining) AS month,
               COUNT(*) AS monthly_new_employees
        FROM employees
        GROUP BY MONTH(date_of_joining)
        ORDER BY month ASC
        """,
        conn
    )
    conn.close()
    return df
# PERFORMANCE RISKS
# ------------------------------
def fetch_performance_risks():
    """
    High-level performance risk metrics based on instructor_performance + new_joiners_2023_2024.
    """
    # Instructor performance
    perf_df = fetch_instructor_performance()
    if perf_df is None or perf_df.empty:
        poor_count = 0
        exceed_pct = 0.0
        top_name = None
    else:
        total_reviews = len(perf_df)
        poor_df = perf_df[perf_df["overall_rating"] == "Below Expectations"]
        exceed_df = perf_df[perf_df["overall_rating"] == "Exceed Expectations"]

        poor_count = len(poor_df)
        exceed_pct = (len(exceed_df) / total_reviews * 100) if total_reviews > 0 else 0.0

        top_row = perf_df.sort_values("overall_score", ascending=False).iloc[0]
        top_name = top_row["employee_name"]

    # New joiners probation risk + names
    nj_df = fetch_new_joiners()
    if nj_df is None or nj_df.empty:
        probation_failed = 0
        probation_failed_names = []
    else:
        failed_df = nj_df[nj_df["probation_status"].str.lower() == "failed"]
        probation_failed = len(failed_df)
        probation_failed_names = [
            f"{row['first_name']} {row['last_name']}"
            for _, row in failed_df.iterrows()
        ]

    return {
        "poor_performers_count": poor_count,
        "exceed_expectations_pct": round(exceed_pct, 2),
        "top_performer_name": top_name,
        "probation_failed_count": probation_failed,
        "probation_failed_names": probation_failed_names,
    }