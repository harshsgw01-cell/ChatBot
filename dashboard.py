import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def render_dashboard(
    employee,
    employees_df,
    new_joiners_df,
    instructor_df,
    employee_trend_df,
    former_df
):
    # Professional AI Assistant Dashboard CSS with custom fonts
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
        
        /* Global Styles */
        * {
            font-family: 'Inter', sans-serif;
        }
        
       .main {
        padding: 0rem 2rem;
        background: #000000;
        background-attachment: fixed;
              }

        
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1400px;
        }
        
        /* Glass morphism card effect */
        .glass-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.18);
            margin-bottom: 2rem;
        }
        
        /* Header Styles */
        * Header Styles */
        h1 {
            font-family: 'Space Grotesk', sans-serif !important;
            color: #000000 !important;           /* <- make title text black */
            font-size: 3rem !important;
            font-weight: 700 !important;
            margin-bottom: 0.5rem !important;
            text-shadow: none;
            letter-spacing: -1px;
        }

        /* Remove gradient text effect on first h1 */
        .main h1:first-of-type {
            background: none !important;
            -webkit-background-clip: initial !important;
            -webkit-text-fill-color: initial !important;
            background-clip: initial !important;
            color: #000000 !important;           /* ensure first title is black */
        }
        
        h2 {
            font-family: 'Space Grotesk', sans-serif !important;
            color: #1e293b !important;
            font-size: 1.75rem !important;
            font-weight: 600 !important;
            margin-top: 2.5rem !important;
            margin-bottom: 1.5rem !important;
            position: relative;
            padding-bottom: 0.75rem !important;
        }
        
        h2:after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 60px;
            height: 4px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 2px;
        }
        
        h3 {
            font-family: 'Inter', sans-serif !important;
            color: #334155 !important;
            font-size: 1.25rem !important;
            font-weight: 600 !important;
            margin-top: 1.5rem !important;
            margin-bottom: 1rem !important;
        }
        
        /* Subtitle/Caption */
        .main > div > div > div > p {
            color: rgba(255, 255, 255, 0.9) !important;
            font-size: 1.1rem !important;
            font-weight: 300 !important;
            margin-bottom: 2rem !important;
        }
        
        /* Metric Cards */
        [data-testid="stMetric"] {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            padding: 1.5rem 1.25rem;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            border: 1px solid rgba(226, 232, 240, 0.8);
            transition: all 0.3s ease;
        }
        
        [data-testid="stMetric"]:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 28px rgba(102, 126, 234, 0.25);
            border-color: rgba(102, 126, 234, 0.3);
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 0.875rem !important;
            font-weight: 500 !important;
            color: #64748b !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.5rem;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 2.25rem !important;
            font-weight: 700 !important;
            color: #1e293b !important;
            font-family: 'Space Grotesk', sans-serif !important;
        }
        
        [data-testid="stMetricDelta"] {
            font-size: 0.875rem !important;
            font-weight: 500 !important;
        }
        
        /* Info boxes */
        .stAlert {
            background: linear-gradient(135deg, #e0e7ff 0%, #f3e8ff 100%) !important;
            border: none !important;
            border-radius: 12px !important;
            color: #4c1d95 !important;
            font-weight: 500 !important;
            padding: 1rem 1.5rem !important;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15) !important;
        }
        
        /* Markdown text in sections */
        .main strong {
            color: #1e293b;
            font-weight: 600;
        }
        
        .main p {
            color: #475569;
            line-height: 1.7;
            font-size: 0.95rem;
        }
        
        /* Section containers */
        div[data-testid="column"] {
            background: transparent;
        }
        
        /* Chart containers */
        .js-plotly-plot {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
        }
        
        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(241, 245, 249, 0.5);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #5568d3 0%, #653a8a 100%);
        }
        
        /* Divider styling */
        hr {
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent 0%, rgba(226, 232, 240, 0.8) 50%, transparent 100%);
            margin: 2rem 0;
        }
        
        /* AI Assistant accent elements */
        .ai-badge {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 0.4rem 1rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 1rem;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            h1 {
                font-size: 2rem !important;
            }
            
            h2 {
                font-size: 1.5rem !important;
            }
            
            [data-testid="stMetricValue"] {
                font-size: 1.75rem !important;
            }
        }
        
        /* Animation for page load */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .main > div {
            animation: fadeInUp 0.6s ease-out;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header with AI badge
    st.markdown('<div class="ai-badge"> AI-Powered Analytics</div>', unsafe_allow_html=True)
    st.title("HR Intelligence Dashboard")
    st.caption("Real-time workforce insights powered by advanced analytics")
    st.write("")

    # Workforce Overview
    st.subheader("Workforce Overview")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Employees",
            value=f"{employee.get('total_employees', len(employees_df) if employees_df is not None else 0):,}"
        )

    with col2:
        st.metric(
            label="Active Employees",
            value=f"{employee.get('active_employees', len(employees_df) if employees_df is not None else 0):,}"
        )

    with col3:
        st.metric(
            label="Attrition Rate",
            value=f"{employee.get('attrition_rate', 0)}%"
        )

    with col4:
        st.metric(
            label="Engagement Score",
            value=f"{employee.get('engagement_score', 0)}/100"
        )

    st.write("")
    st.write("")

    # Turnover & Risk Overview
    st.subheader("Turnover & Risk Overview")

    total_headcount = employee.get(
        "total_employees",
        len(employees_df) if employees_df is not None else 0
    )

    # Former employees / turnover
    total_leavers = 0
    total_terminations = 0
    total_resignations = 0
    early_resignations = 0

    if former_df is not None and not former_df.empty:
        total_leavers = len(former_df)
        if "terminationtype" in former_df.columns:
            total_terminations = (former_df["terminationtype"] == "Termination").sum()
            total_resignations = (former_df["terminationtype"] == "Resignation").sum()
        if {"terminationtype", "dateofjoining", "dateofleaving"}.issubset(former_df.columns):
            tmp = former_df.copy()
            tmp["doj"] = pd.to_datetime(tmp["dateofjoining"])
            tmp["dol"] = pd.to_datetime(tmp["dateofleaving"])
            early_resignations = (
                (tmp["terminationtype"] == "Resignation") &
                ((tmp["dol"] - tmp["doj"]).dt.days <= 365)
            ).sum()

    annual_turnover_rate = 0
    if total_headcount:
        # simple annualized turnover approximation
        annual_turnover_rate = round((total_leavers / total_headcount) * 100, 1)

    # Probation failures from new_joiners_df
    total_new_joiners = 0
    probation_failed = 0
    probation_failure_rate = 0

    if new_joiners_df is not None and not new_joiners_df.empty and "probation_status" in new_joiners_df.columns:
        total_new_joiners = len(new_joiners_df)
        probation_failed = (new_joiners_df["probation_status"] == "Failed").sum()
        if total_new_joiners:
            probation_failure_rate = round((probation_failed / total_new_joiners) * 100, 1)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Leavers (3 yrs)", f"{total_leavers:,}")
    with col2:
        st.metric("Annual Turnover Rate", f"{annual_turnover_rate}%")
    with col3:
        st.metric("Early Resignations (<1 yr)", f"{early_resignations:,}")
    with col4:
        st.metric("Probation Failure Rate", f"{probation_failure_rate}%")

    st.write("")
    st.write("")

    # New Joiners Section
    st.subheader("New Joiners (2023-2024)")

    if new_joiners_df is not None and not new_joiners_df.empty:
        total_joiners = len(new_joiners_df)

        nationality_split = None
        if "nationality" in new_joiners_df.columns:
            nationality_split = new_joiners_df["nationality"].value_counts(normalize=True).mul(100).round(1)

        top_nationality = nationality_split.index[0] if nationality_split is not None and len(nationality_split) > 0 else "-"
        top_pct = nationality_split.iloc[0] if nationality_split is not None and len(nationality_split) > 0 else 0

        at_risk = 0
        if "probation_status" in new_joiners_df.columns:
            at_risk = (new_joiners_df["probation_status"] != "Completed").sum()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total New Joiners", f"{total_joiners:,}")
        with col2:
            st.metric("Top Nationality", top_nationality)
        with col3:
            st.metric("Top Nationality %", f"{top_pct}%")
        with col4:
            st.metric("On Probation", f"{at_risk:,}")
    else:
        st.info("No new joiner data available")

    st.write("")
    st.write("")

    # Monthly Hiring Trend
    st.subheader("Monthly Hiring Trend")

    if employee_trend_df is not None and not employee_trend_df.empty:
        fig = px.bar(
            employee_trend_df,
            x="month",
            y="monthly_new_employees",
            labels={"month": "Month", "monthly_new_employees": "New Hires"}
        )

        fig.update_traces(
            marker_color='#667eea',
            marker_line_color='#5568d3',
            marker_line_width=1.5,
            hovertemplate='<b>%{x}</b><br>New Hires: %{y}<extra></extra>'
        )

        fig.update_layout(
            height=350,
            margin=dict(l=40, r=20, t=20, b=40),
            plot_bgcolor='#fafbfc',
            paper_bgcolor='white',
            font=dict(size=12, family='Inter, sans-serif', color='#334155'),
            xaxis=dict(
                showgrid=False, 
                showline=True, 
                linewidth=2, 
                linecolor='#e2e8f0',
                tickfont=dict(size=11)
            ),
            yaxis=dict(
                showgrid=True, 
                gridwidth=1, 
                gridcolor='#e2e8f0', 
                showline=True, 
                linewidth=2, 
                linecolor='#e2e8f0',
                tickfont=dict(size=11)
            ),
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Inter, sans-serif"
            )
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No employee trend data available")

    st.write("")
    st.write("")

    # Instructor Performance
    st.subheader("Instructor Performance")

    if instructor_df is not None and not instructor_df.empty:
        avg_pass = 0
        avg_rating = 0
        top_instructor = "-"

        if "pass_rate" in instructor_df.columns:
            avg_pass = round(instructor_df["pass_rate"].mean(), 1)
            top_instructor = instructor_df.sort_values("pass_rate", ascending=False).iloc[0]["instructor_name"]

        if "rating" in instructor_df.columns:
            avg_rating = round(instructor_df["rating"].mean(), 1)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Avg Pass Rate", f"{avg_pass}%")
        with col2:
            st.metric("Avg Rating", f"{avg_rating}/5")
        with col3:
            st.metric("Top Instructor", top_instructor)
    else:
        st.info("No instructor performance data available")

    st.write("")
    st.write("")

    # Workforce Composition
    st.subheader("Workforce Composition")

    if employees_df is not None and not employees_df.empty:
        nationality_split = None
        contract_split = None

        if "nationality" in employees_df.columns:
            nationality_split = employees_df["nationality"].value_counts(normalize=True).mul(100).round(1)

        if "contract_type" in employees_df.columns:
            contract_split = employees_df["contract_type"].value_counts(normalize=True).mul(100).round(1)

        # Display basic metrics
        col1, col2 = st.columns([1, 1])

        with col1:
            if nationality_split is not None and len(nationality_split) > 0:
                st.markdown(f"**Top Nationality:** {nationality_split.index[0]} ({nationality_split.iloc[0]}%)")

            if contract_split is not None:
                married_pct = contract_split.get("Married", 0)
                single_pct = contract_split.get("Single", 0)
                st.markdown(f"**Contract Status:** Married {married_pct}% | Single {single_pct}%")

        st.write("")

        # Charts side by side
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            if contract_split is not None and len(contract_split) > 0:
                contract_df = contract_split.reset_index()
                contract_df.columns = ["Type", "Percentage"]

                fig = px.pie(
                    contract_df,
                    names="Type",
                    values="Percentage",
                    hole=0.4
                )

                fig.update_traces(
                    marker=dict(colors=['#667eea', '#764ba2', '#f093fb', '#4facfe']),
                    textfont=dict(size=12, family='Inter, sans-serif'),
                    hovertemplate='<b>%{label}</b><br>%{value:.1f}%<extra></extra>'
                )

                fig.update_layout(
                    height=300,
                    margin=dict(l=20, r=20, t=30, b=20),
                    showlegend=True,
                    legend=dict(
                        orientation="v", 
                        yanchor="middle", 
                        y=0.5, 
                        xanchor="left", 
                        x=1.05,
                        font=dict(size=11, family='Inter, sans-serif')
                    ),
                    paper_bgcolor='white',
                    font=dict(size=11, family='Inter, sans-serif', color='#334155')
                )

                st.markdown("**Contract Type Distribution**")
                st.plotly_chart(fig, use_container_width=True)

        with chart_col2:
            if nationality_split is not None and len(nationality_split) > 0:
                nat_df = nationality_split.head(10).reset_index()
                nat_df.columns = ["Nationality", "Percentage"]

                fig = px.bar(
                    nat_df,
                    x="Nationality",
                    y="Percentage",
                    labels={"Percentage": "% of Workforce"}
                )

                fig.update_traces(
                    marker_color='#10b981',
                    marker_line_color='#059669',
                    marker_line_width=1.5,
                    hovertemplate='<b>%{x}</b><br>%{y:.1f}%<extra></extra>'
                )

                fig.update_layout(
                    height=300,
                    margin=dict(l=40, r=20, t=30, b=60),
                    plot_bgcolor='#fafbfc',
                    paper_bgcolor='white',
                    font=dict(size=11, family='Inter, sans-serif', color='#334155'),
                    xaxis=dict(
                        showgrid=False, 
                        showline=True, 
                        linewidth=2, 
                        linecolor='#e2e8f0', 
                        tickangle=-45,
                        tickfont=dict(size=10)
                    ),
                    yaxis=dict(
                        showgrid=True, 
                        gridwidth=1, 
                        gridcolor='#e2e8f0', 
                        showline=True, 
                        linewidth=2, 
                        linecolor='#e2e8f0'
                    )
                )

                st.markdown("**Nationality Distribution**")
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No employee composition data available")

    st.write("")
    st.write("")

    # Detailed Analytics
    st.subheader("Employee Analytics")

    if employees_df is not None and not employees_df.empty:

        # Calculate tenure if date_of_joining exists
        if "date_of_joining" in employees_df.columns:
            employees_df["tenure_years"] = (
                (pd.Timestamp("today") - pd.to_datetime(employees_df["date_of_joining"])).dt.days / 365
            ).round(1)

        # Department headcount
        st.markdown("### Headcount by Department")
        if "department" in employees_df.columns:
            dept_counts = employees_df["department"].value_counts().reset_index()
            dept_counts.columns = ["Department", "Count"]

            fig = px.bar(
                dept_counts,
                x="Department",
                y="Count",
                text="Count"
            )

            fig.update_traces(
                marker_color='#8b5cf6',
                marker_line_color='#7c3aed',
                marker_line_width=1.5,
                textposition='outside',
                textfont=dict(size=12, family='Inter, sans-serif'),
                hovertemplate='<b>%{x}</b><br>Employees: %{y}<extra></extra>'
            )

            fig.update_layout(
                height=350,
                margin=dict(l=40, r=20, t=20, b=80),
                plot_bgcolor='#fafbfc',
                paper_bgcolor='white',
                font=dict(size=12, family='Inter, sans-serif', color='#334155'),
                xaxis=dict(
                    showgrid=False, 
                    showline=True, 
                    linewidth=2, 
                    linecolor='#e2e8f0', 
                    tickangle=-45,
                    tickfont=dict(size=11)
                ),
                yaxis=dict(
                    showgrid=True, 
                    gridwidth=1, 
                    gridcolor='#e2e8f0', 
                    showline=True, 
                    linewidth=2, 
                    linecolor='#e2e8f0'
                )
            )

            st.plotly_chart(fig, use_container_width=True)

        st.write("")

        # Salary and Tenure side by side
        analysis_col1, analysis_col2 = st.columns(2)

        with analysis_col1:
            if "total_salary" in employees_df.columns:
                st.markdown("### Salary Distribution")

                fig = px.histogram(
                    employees_df,
                    x="total_salary",
                    nbins=25,
                    labels={"total_salary": "Total Salary (QAR)"}
                )

                fig.update_traces(
                    marker_color='#f59e0b',
                    marker_line_color='#d97706',
                    marker_line_width=1.5,
                    hovertemplate='Salary Range: %{x}<br>Count: %{y}<extra></extra>'
                )

                fig.update_layout(
                    height=300,
                    margin=dict(l=40, r=20, t=20, b=40),
                    plot_bgcolor='#fafbfc',
                    paper_bgcolor='white',
                    font=dict(size=11, family='Inter, sans-serif', color='#334155'),
                    xaxis=dict(
                        showgrid=False, 
                        showline=True, 
                        linewidth=2, 
                        linecolor='#e2e8f0'
                    ),
                    yaxis=dict(
                        showgrid=True, 
                        gridwidth=1, 
                        gridcolor='#e2e8f0', 
                        showline=True, 
                        linewidth=2, 
                        linecolor='#e2e8f0', 
                        title="Count"
                    )
                )

                st.plotly_chart(fig, use_container_width=True)

        with analysis_col2:
            if "tenure_years" in employees_df.columns and employees_df["tenure_years"].notna().any():
                st.markdown("### Tenure Distribution")

                fig = px.histogram(
                    employees_df,
                    x="tenure_years",
                    nbins=20,
                    labels={"tenure_years": "Years in Company"}
                )

                fig.update_traces(
                    marker_color='#06b6d4',
                    marker_line_color='#0891b2',
                    marker_line_width=1.5,
                    hovertemplate='Tenure: %{x} years<br>Count: %{y}<extra></extra>'
                )

                fig.update_layout(
                    height=300,
                    margin=dict(l=40, r=20, t=20, b=40),
                    plot_bgcolor='#fafbfc',
                    paper_bgcolor='white',
                    font=dict(size=11, family='Inter, sans-serif', color='#334155'),
                    xaxis=dict(
                        showgrid=False, 
                        showline=True, 
                        linewidth=2, 
                        linecolor='#e2e8f0'
                    ),
                    yaxis=dict(
                        showgrid=True, 
                        gridwidth=1, 
                        gridcolor='#e2e8f0', 
                        showline=True, 
                        linewidth=2, 
                        linecolor='#e2e8f0', 
                        title="Count"
                    )
                )

                st.plotly_chart(fig, use_container_width=True)

        st.write("")

        # Nationality by Department
        if "nationality" in employees_df.columns and "department" in employees_df.columns:
            st.markdown("### Nationality Distribution by Department")

            nat_dept = employees_df.groupby(["department", "nationality"]).size().reset_index(name="count")

            fig = px.bar(
                nat_dept,
                x="department",
                y="count",
                color="nationality",
                labels={"count": "Employees", "department": "Department", "nationality": "Nationality"},
                barmode="stack"
            )

            fig.update_layout(
                height=350,
                margin=dict(l=40, r=20, t=20, b=80),
                plot_bgcolor='#fafbfc',
                paper_bgcolor='white',
                font=dict(size=12, family='Inter, sans-serif', color='#334155'),
                xaxis=dict(
                    showgrid=False, 
                    showline=True, 
                    linewidth=2, 
                    linecolor='#e2e8f0', 
                    tickangle=-45,
                    tickfont=dict(size=11)
                ),
                yaxis=dict(
                    showgrid=True, 
                    gridwidth=1, 
                    gridcolor='#e2e8f0', 
                    showline=True, 
                    linewidth=2, 
                    linecolor='#e2e8f0'
                ),
                legend=dict(
                    orientation="h", 
                    yanchor="bottom", 
                    y=-0.4, 
                    xanchor="center", 
                    x=0.5,
                    font=dict(size=10, family='Inter, sans-serif')
                ),
                hovermode='x unified'
            )

            st.plotly_chart(fig, use_container_width=True)

        st.write("")

        # Contract Type by Department
        if "contract_type" in employees_df.columns and "department" in employees_df.columns:
            st.markdown("### Contract Type by Department")

            ct_dept = employees_df.groupby(["department", "contract_type"]).size().reset_index(name="count")

            fig = px.bar(
                ct_dept,
                x="department",
                y="count",
                color="contract_type",
                labels={"count": "Employees", "department": "Department", "contract_type": "Contract Type"},
                barmode="group"
            )

            fig.update_layout(
                height=350,
                margin=dict(l=40, r=20, t=20, b=80),
                plot_bgcolor='#fafbfc',
                paper_bgcolor='white',
                font=dict(size=12, family='Inter, sans-serif', color='#334155'),
                xaxis=dict(
                    showgrid=False, 
                    showline=True, 
                    linewidth=2, 
                    linecolor='#e2e8f0', 
                    tickangle=-45,
                    tickfont=dict(size=11)
                ),
                yaxis=dict(
                    showgrid=True, 
                    gridwidth=1, 
                    gridcolor='#e2e8f0', 
                    showline=True, 
                    linewidth=2, 
                    linecolor='#e2e8f0'
                ),
                legend=dict(
                    orientation="h", 
                    yanchor="bottom", 
                    y=-0.4, 
                    xanchor="center", 
                    x=0.5,
                    font=dict(size=10, family='Inter, sans-serif')
                ),
                hovermode='x unified'
            )

            st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No employee analytics data available")

    st.write("")
    st.write("")

    # Turnover Analytics
    st.subheader("Turnover Analytics")

    if former_df is not None and not former_df.empty:
        # Department turnover
        if "department" in former_df.columns:
            dept_turnover = (
                former_df.groupby("department")
                .size()
                .reset_index(name="Leavers")
                .sort_values("Leavers", ascending=False)
            )

            fig = px.bar(
                dept_turnover,
                x="department",
                y="Leavers",
                text="Leavers",
                labels={"department": "Department", "Leavers": "Leavers (last 3 yrs)"}
            )
            fig.update_traces(
                marker_color="#ef4444",
                marker_line_color="#dc2626",
                marker_line_width=1.5,
                textposition="outside",
                textfont=dict(size=12, family='Inter, sans-serif'),
                hovertemplate='<b>%{x}</b><br>Leavers: %{y}<extra></extra>'
            )
            fig.update_layout(
                height=320,
                margin=dict(l=40, r=20, t=20, b=80),
                plot_bgcolor="#fafbfc",
                paper_bgcolor="white",
                font=dict(size=12, family='Inter, sans-serif', color='#334155'),
                xaxis=dict(
                    showgrid=False, 
                    showline=True, 
                    linewidth=2, 
                    linecolor="#e2e8f0", 
                    tickangle=-45,
                    tickfont=dict(size=11)
                ),
                yaxis=dict(
                    showgrid=True, 
                    gridwidth=1, 
                    gridcolor="#e2e8f0", 
                    showline=True, 
                    linewidth=2, 
                    linecolor="#e2e8f0"
                )
            )
            st.markdown("### Leavers by Department")
            st.plotly_chart(fig, use_container_width=True)

        # Resignation reasons (top 8)
        if "terminationsubreason" in former_df.columns and "terminationtype" in former_df.columns:
            reason_counts = (
                former_df[former_df["terminationtype"] == "Resignation"]
                .groupby("terminationsubreason")
                .size()
                .reset_index(name="Count")
                .sort_values("Count", ascending=False)
                .head(8)
            )
            if not reason_counts.empty:
                fig = px.bar(
                    reason_counts,
                    x="terminationsubreason",
                    y="Count",
                    text="Count",
                    labels={"terminationsubreason": "Resignation Reason", "Count": "Resignations"}
                )
                fig.update_traces(
                    marker_color="#f59e0b",
                    marker_line_color="#d97706",
                    marker_line_width=1.5,
                    textposition="outside",
                    textfont=dict(size=12, family='Inter, sans-serif'),
                    hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
                )
                fig.update_layout(
                    height=320,
                    margin=dict(l=40, r=20, t=20, b=120),
                    plot_bgcolor="#fafbfc",
                    paper_bgcolor="white",
                    font=dict(size=11, family='Inter, sans-serif', color='#334155'),
                    xaxis=dict(
                        showgrid=False, 
                        showline=True, 
                        linewidth=2, 
                        linecolor="#e2e8f0", 
                        tickangle=-45,
                        tickfont=dict(size=10)
                    ),
                    yaxis=dict(
                        showgrid=True, 
                        gridwidth=1, 
                        gridcolor="#e2e8f0", 
                        showline=True, 
                        linewidth=2, 
                        linecolor="#e2e8f0"
                    )
                )
                st.markdown("### Top Resignation Reasons")
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No turnover data available")