# ai_logic.py

from openai import OpenAI
from prompt import ceo_prompt
from data import (
    fetch_employee_data,
    fetch_performance_risks,
    fetch_former_employees,
    fetch_employee_details,   # uses employees table
)
import pandas as pd


client = OpenAI()
MODEL = "gpt-4o-mini"


def build_hr_overview():
    """
    Build a compact HR overview dictionary that the CEO prompt can use.
    This assumes fetch_employee_data() already returns keys such as:
      - total_employees, active_employees, former_employees
      - attrition_rate, monthly_payroll_qr (fallback here if missing)
      - turnover_last_year, turnover_breakdown
      - top_turnover_department, top_turnover_pct
      - turnover_main_reasons, turnover_cost_qr
      - engagement_score, new_joiners_2023_2024, on_probation
      - top_nationality, top_nationality_pct, contract_split
      - avg_pass_rate, avg_rating, top_instructor
    and fetch_performance_risks() returns:
      - poor_performers_count, exceed_expectations_pct
      - top_performer_name, probation_failed_count, probation_failed_names
    """
    m = fetch_employee_data()
    p = fetch_performance_risks()
    employees_df = fetch_employee_details()
    former_df = fetch_former_employees()

    print("EMPLOYEES_DF COLUMNS:", employees_df.columns.tolist())
    print(employees_df.head(3).to_dict(orient="records"))
    print("FORMER_DF COLUMNS:", former_df.columns.tolist())
    print(former_df.head(3).to_dict(orient="records"))

    # ---------- Workforce KPIs derived from employees_df ----------
    # Monthly payroll (QAR) – if not already in m
    monthly_payroll_qr = m.get("monthly_payroll_qr")
    if (monthly_payroll_qr is None or monthly_payroll_qr == 0) and employees_df is not None:
        if "total_salary" in employees_df.columns:
            monthly_payroll_qr = float(employees_df["total_salary"].sum())
        else:
            monthly_payroll_qr = 0.0

    # Average tenure (years)
    avg_tenure_years = m.get("avg_tenure_years")
    if (avg_tenure_years is None or avg_tenure_years == 0) and employees_df is not None:
        if "date_of_joining" in employees_df.columns:
            tmp = employees_df.copy()
            tmp["doj"] = pd.to_datetime(tmp["date_of_joining"])
            tmp["tenure_years"] = (pd.Timestamp("today") - tmp["doj"]).dt.days / 365
            avg_tenure_years = round(tmp["tenure_years"].mean(), 1)
        else:
            avg_tenure_years = 0.0

    # Nationality mix (dict)
    nationality_split = m.get("nationality_split")
    if (not nationality_split) and employees_df is not None:
        if "nationality" in employees_df.columns:
            nationality_split = (
                employees_df["nationality"]
                .value_counts(normalize=True)
                .mul(100)
                .round(1)
                .to_dict()
            )
        else:
            nationality_split = {}

    # Contract status (married vs single)
    married_pct = m.get("married_pct")
    single_pct = m.get("single_pct")
    if (married_pct is None or single_pct is None) and employees_df is not None:
        if "contract_type" in employees_df.columns:
            ct = (
                employees_df["contract_type"]
                .value_counts(normalize=True)
                .mul(100)
                .round(1)
            )
            married_pct = float(ct.get("Married", 0))
            single_pct = float(ct.get("Single", 0))
        else:
            married_pct = 0.0
            single_pct = 0.0

    # ---------- Turnover metrics from former_df ----------
    turnover_last_year = m.get("turnover_last_year")
    turnover_breakdown = m.get("turnover_breakdown")
    top_turnover_department = m.get("top_turnover_department")
    top_turnover_pct = m.get("top_turnover_pct")
    turnover_main_reasons = m.get("turnover_main_reasons")

    if (former_df is not None) and (not former_df.empty):
        total_leavers = len(former_df)

        # Last year turnover (by leaving year)
        if "dateofleaving" in former_df.columns:
            fd = former_df.copy()
            fd["dol"] = pd.to_datetime(fd["dateofleaving"])
            last_year = pd.Timestamp("today").year - 1
            last_year_leavers = fd[fd["dol"].dt.year == last_year]
            turnover_last_year = len(last_year_leavers)
        else:
            turnover_last_year = total_leavers

        # Terminations vs resignations
        termination_count = resignation_count = 0
        if "terminationtype" in former_df.columns:
            termination_count = int((former_df["terminationtype"] == "Termination").sum())
            resignation_count = int((former_df["terminationtype"] == "Resignation").sum())
        turnover_breakdown = {
            "terminations": termination_count,
            "resignations": resignation_count,
            "total_leavers": total_leavers,
        }

        # Top turnover department
        if "department" in former_df.columns:
            dept_counts = former_df["department"].value_counts()
            if not dept_counts.empty:
                top_turnover_department = dept_counts.index[0]
                top_turnover_pct = round(
                    (dept_counts.iloc[0] / total_leavers) * 100, 1
                )

        # Main resignation reasons (top 3)
        if "terminationsubreason" in former_df.columns and "terminationtype" in former_df.columns:
            reason_counts = (
                former_df[former_df["terminationtype"] == "Resignation"]
                .groupby("terminationsubreason")
                .size()
                .sort_values(ascending=False)
            )
            turnover_main_reasons = [
                f"{reason}: {count} resignations"
                for reason, count in reason_counts.head(3).items()
            ]

    # ---------- Turnover cost (salary-based estimate) ----------
    turnover_cost_qr = m.get("turnover_cost_qr")
    if (
        (turnover_cost_qr is None or turnover_cost_qr == 0)
        and former_df is not None
        and not former_df.empty
        and employees_df is not None
        and "employee_number" in former_df.columns
        and "employee_number" in employees_df.columns
        and "total_salary" in employees_df.columns
    ):
        sal = employees_df[["employee_number", "total_salary"]].drop_duplicates()
        leavers = former_df.merge(sal, on="employee_number", how="left")

        leavers["annual_salary"] = leavers["total_salary"].fillna(0) * 12
        leavers["turnover_cost_est"] = leavers["annual_salary"] * 0.3  # 30% factor

        turnover_cost_qr = float(leavers["turnover_cost_est"].sum())
    elif turnover_cost_qr is None:
        turnover_cost_qr = 0.0

    return {
        # Core HR metrics
        "total_employees": m.get("total_employees"),
        "active_employees": m.get("active_employees"),
        "former_employees": m.get("former_employees"),
        "attrition_rate": m.get("attrition_rate"),
        "monthly_payroll_qr": monthly_payroll_qr,

        # Turnover metrics (driven from formeremployees table)
        "turnover_last_year": turnover_last_year,
        "turnover_breakdown": turnover_breakdown,
        "top_turnover_department": top_turnover_department,
        "top_turnover_pct": top_turnover_pct,
        "turnover_main_reasons": turnover_main_reasons,
        "turnover_cost_qr": turnover_cost_qr,

        # Engagement / pipeline
        "engagement_score": m.get("engagement_score"),
        "new_joiners_2023_2024": m.get("new_joiners_2023_2024"),
        "on_probation": m.get("on_probation"),

        # Workforce composition (existing fields)
        "top_nationality": m.get("top_nationality"),
        "top_nationality_pct": m.get("top_nationality_pct"),
        "contract_split": m.get("contract_split"),
        "avg_pass_rate": m.get("avg_pass_rate"),
        "avg_rating": m.get("avg_rating"),
        "top_instructor": m.get("top_instructor"),

        # New derived composition fields (for CEO answers)
        "nationality_split": nationality_split,
        "married_pct": married_pct,
        "single_pct": single_pct,
        "avg_tenure_years": avg_tenure_years,

        # Performance risk metrics
        "poor_performers_count": p.get("poor_performers_count"),
        "exceed_expectations_pct": p.get("exceed_expectations_pct"),
        "top_performer_name": p.get("top_performer_name"),
        "probation_failed_count": p.get("probation_failed_count"),
        "probation_failed_names": p.get("probation_failed_names"),
    }


def answer_ceo_question(question: str) -> str:
    """
    Main entry point for the CEO Q&A.
    The prompt receives:
      - hr_overview: compact metrics dict (including turnover by department and reasons)
      - employees: the full employee / HR data structure (detailed list and stats)
      - question: CEO's natural-language question
    """

    q = question.lower()

    # keywords that should use the nationality logic
    NATIONALITY_KEYWORDS = [
        "nationality",
        "nationalities",
        "indian",
        "qatari",
        "qataris",
        "nepali",
        "philippine",
        "filipino",
        "egyptian",
    ]

    # ---------- 1) Hard rule for nationality / country questions ----------
    if any(k in q for k in NATIONALITY_KEYWORDS):
        employees_df = fetch_employee_details()

        if employees_df is None or employees_df.empty or "nationality" not in employees_df.columns:
            return (
                "Nationality is captured in the core HR system, but it is not yet fully "
                "available in this analytics dataset. I cannot reliably report nationality "
                "counts by country yet."
            )

        nat_split = (
            employees_df["nationality"]
            .value_counts(normalize=True)
            .mul(100)
            .round(1)
        )

        # If specifically asking about Indian employees
        if "indian" in q:
            total_indian = (employees_df["nationality"].str.lower() == "indian").sum()
            total_emp = len(employees_df)
            pct_indian = round((total_indian / total_emp) * 100, 1) if total_emp else 0
            return (
                f"We currently have {total_indian} Indian employees, which is about "
                f"{pct_indian}% of the workforce."
            )

        # generic nationality summary
        if len(nat_split) == 0:
            return "Nationality data exists but is empty in the current snapshot."

        top_nat = nat_split.index[0]
        top_pct = nat_split.iloc[0]
        unique_nats = len(nat_split)

        return (
            f"We currently have {unique_nats} distinct nationalities in the workforce. "
            f"The largest group is {top_nat}, accounting for about {top_pct}% of employees. "
            f"You can explore the full nationality breakdown in the HR dashboard."
        )

    # ---------- 2) Existing LLM logic ----------
    hr_overview = build_hr_overview()
    employees = fetch_employee_data()

    prompt_text = ceo_prompt.format(
        hr_overview=str(hr_overview),
        employees=str(employees),
        question=question,
    )

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt_text}],
        temperature=0.1,
        max_tokens=320,
    )

    return resp.choices[0].message.content
