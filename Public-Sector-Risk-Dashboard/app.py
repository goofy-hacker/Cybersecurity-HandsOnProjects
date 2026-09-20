import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime

# --------------------------------------------------
# Page Config
# --------------------------------------------------

st.set_page_config(
    page_title="Public Sector Strategic Risk & Resilience Dashboard",
    page_icon="",
    layout="wide"
)

# --------------------------------------------------
# Custom CSS - Minimal Professional Theme
# --------------------------------------------------

st.markdown(
    """
    <style>
    :root {
        --primary-navy: #0f172a;
        --secondary-navy: #1e293b;
        --accent-blue: #2563eb;
        --soft-blue: #dbeafe;
        --border-color: #334155;
        --muted-text: #cbd5e1;
        --light-text: #f8fafc;
    }

    .hero {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 70%, #334155 100%);
        padding: 34px;
        border-radius: 10px;
        color: white;
        margin-bottom: 28px;
        border: 1px solid #334155;
    }

    .hero h1 {
        font-size: 34px;
        margin-bottom: 10px;
        color: white;
        font-weight: 800;
        letter-spacing: -0.4px;
    }

    .hero p {
        font-size: 16px;
        line-height: 1.55;
        color: #cbd5e1;
        max-width: 1100px;
    }

    .section-label {
        font-size: 13px;
        color: #93c5fd;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 4px;
    }

    div[data-testid="stMetric"] {
        background: #111827;
        padding: 18px;
        border-radius: 10px;
        border: 1px solid #334155;
    }

    div[data-testid="stMetricLabel"] {
        color: #cbd5e1;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        color: #ffffff;
        font-size: 30px;
        font-weight: 800;
    }

    section[data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #334155;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label {
        color: #e5e7eb !important;
    }

    .sidebar-box {
        background-color: #111827;
        padding: 16px;
        border-radius: 10px;
        border: 1px solid #334155;
        margin-bottom: 18px;
    }

    .sidebar-title {
        font-size: 21px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 6px;
    }

    .sidebar-subtitle {
        font-size: 14px;
        color: #cbd5e1;
        line-height: 1.45;
    }

    .filter-note {
        font-size: 13px;
        color: #94a3b8;
        margin-bottom: 8px;
    }

    .badge {
        padding: 5px 10px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 700;
        display: inline-block;
        border: 1px solid transparent;
    }

    .badge-critical {
        background-color: #3f1d1d;
        color: #fecaca;
        border-color: #7f1d1d;
    }

    .badge-high {
        background-color: #422006;
        color: #fed7aa;
        border-color: #9a3412;
    }

    .badge-medium {
        background-color: #3f3a12;
        color: #fef3c7;
        border-color: #854d0e;
    }

    .badge-low {
        background-color: #10291c;
        color: #bbf7d0;
        border-color: #166534;
    }

    .badge-blue {
        background-color: #172554;
        color: #dbeafe;
        border-color: #1d4ed8;
    }

    .badge-purple {
        background-color: #2e1065;
        color: #ede9fe;
        border-color: #6d28d9;
    }

    .small-note {
        color: #cbd5e1;
        font-size: 14px;
        line-height: 1.5;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    hr {
        border-color: #334155;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# Header
# --------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <h1>Public Sector Strategic Risk & Resilience Dashboard</h1>
        <p>
        Enterprise risk management prototype for translating public-sector technology modernization priorities
        into measurable strategic risk, maturity gaps, key risk indicators, risk appetite, and POA&M-style remediation tracking.
        </p>
        <p>
        Focus areas include cybersecurity posture, disaster recovery, AI governance, data strategy, vendor risk,
        privacy, IT modernization, constituent experience, and operational resilience.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# Load Data
# --------------------------------------------------

DATA_PATH = "data/strategic_risk_register.csv"
OUTPUT_PATH = "outputs/processed_strategic_risks.csv"

try:
    df = pd.read_csv(DATA_PATH)
except FileNotFoundError:
    st.error("Could not find data/strategic_risk_register.csv. Please confirm the CSV file exists in the data folder.")
    st.stop()

# --------------------------------------------------
# Helper Functions
# --------------------------------------------------

def classify_risk(score):
    if score >= 17:
        return "Critical"
    elif score >= 10:
        return "High"
    elif score >= 5:
        return "Medium"
    else:
        return "Low"


def maturity_label(level):
    labels = {
        1: "Ad Hoc",
        2: "Developing",
        3: "Maturing",
        4: "Scaling",
        5: "Optimizing"
    }
    return labels.get(int(level), "Unknown")


def appetite_status(score):
    return "Above Appetite" if score > 10 else "Within Appetite"


def kri_severity(row):
    current = row["Current KRI Value"]
    threshold = row["KRI Threshold"]

    if threshold == 0:
        return "Critical" if current > 0 else "Within Threshold"

    ratio = current / threshold

    if ratio <= 1:
        return "Within Threshold"
    elif ratio <= 1.25:
        return "Warning"
    elif ratio <= 1.75:
        return "Elevated"
    else:
        return "Critical"


def treatment_decision(row):
    residual = row["Residual Risk Score"]
    maturity_gap = row["Maturity Gap"]
    kri = row["KRI Severity"]

    if residual >= 17 or kri == "Critical":
        return "Executive Review Required"
    elif residual > 10 and maturity_gap >= 2:
        return "Prioritize Remediation"
    elif residual > 10:
        return "Remediate / Risk Acceptance Needed"
    elif maturity_gap >= 2:
        return "Monitor and Improve Maturity"
    else:
        return "Monitor"


def remediation_priority(row):
    residual = row["Residual Risk Score"]
    maturity_gap = row["Maturity Gap"]
    kri = row["KRI Severity"]

    if residual >= 17 or kri == "Critical":
        return "Priority 1 - Immediate"
    elif residual >= 10 and maturity_gap >= 2:
        return "Priority 2 - High"
    elif residual >= 10:
        return "Priority 3 - Medium"
    else:
        return "Priority 4 - Monitor"


def days_until_target(date_value):
    try:
        target = pd.to_datetime(date_value)
        today = pd.to_datetime(datetime.today().date())
        return (target - today).days
    except Exception:
        return None


def timeline_status(row):
    days = row["Days Until Target"]
    status = row["Status"]

    if pd.isna(days):
        return "Unknown"

    if status == "Completed":
        return "Completed"

    if days < 0:
        return "Overdue"
    elif days <= 14:
        return "Due Soon"
    else:
        return "On Track"


def badge_html(value):
    badge_map = {
        "Critical": "badge-critical",
        "High": "badge-high",
        "Medium": "badge-medium",
        "Low": "badge-low",
        "Above Appetite": "badge-critical",
        "Within Appetite": "badge-low",
        "Executive Review Required": "badge-critical",
        "Prioritize Remediation": "badge-high",
        "Remediate / Risk Acceptance Needed": "badge-medium",
        "Monitor and Improve Maturity": "badge-purple",
        "Monitor": "badge-blue",
        "Elevated": "badge-high",
        "Warning": "badge-medium",
        "Within Threshold": "badge-low",
        "Overdue": "badge-critical",
        "Due Soon": "badge-medium",
        "On Track": "badge-low",
        "Completed": "badge-blue",
    }

    badge_class = badge_map.get(value, "badge-blue")
    return f'<span class="badge {badge_class}">{value}</span>'


def make_bar_chart(series, title, xlabel, ylabel):
    fig, ax = plt.subplots(figsize=(8, 4))
    series.plot(kind="bar", ax=ax)

    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=35)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    return fig


# --------------------------------------------------
# Calculations
# --------------------------------------------------

df["Inherent Risk Score"] = df["Likelihood"] * df["Impact"]

df["Control Effectiveness Decimal"] = df["Control Effectiveness %"] / 100

df["Residual Risk Score"] = (
    df["Inherent Risk Score"] * (1 - df["Control Effectiveness Decimal"])
).round(1)

df["Residual Risk Level"] = df["Residual Risk Score"].apply(classify_risk)

df["Risk Appetite Status"] = df["Residual Risk Score"].apply(appetite_status)

df["Maturity Gap"] = df["Target Maturity"] - df["Current Maturity"]

df["Current Maturity Label"] = df["Current Maturity"].apply(maturity_label)

df["Target Maturity Label"] = df["Target Maturity"].apply(maturity_label)

df["KRI Severity"] = df.apply(kri_severity, axis=1)

df["KRI Status"] = df["KRI Severity"].apply(
    lambda x: "Threshold Breached" if x in ["Warning", "Elevated", "Critical"] else "Within Threshold"
)

df["Risk Treatment Decision"] = df.apply(treatment_decision, axis=1)

df["Remediation Priority"] = df.apply(remediation_priority, axis=1)

df["Days Until Target"] = df["Target Date"].apply(days_until_target)

df["Timeline Status"] = df.apply(timeline_status, axis=1)

df.to_csv(OUTPUT_PATH, index=False)

# --------------------------------------------------
# Sidebar - Visible Checkbox Filters
# --------------------------------------------------

st.sidebar.markdown(
    """
    <div class="sidebar-box">
        <div class="sidebar-title">Dashboard Controls</div>
        <div class="sidebar-subtitle">
            All categories remain visible. Select or clear items to focus the dashboard view.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


def visible_checkbox_filter(title, options, key_prefix):
    st.sidebar.markdown(f"### {title}")
    st.sidebar.markdown(
        '<div class="filter-note">Selected items are included in the dashboard.</div>',
        unsafe_allow_html=True
    )

    selected = []

    for option in sorted(options):
        checked = st.sidebar.checkbox(
            option,
            value=True,
            key=f"{key_prefix}_{option}"
        )

        if checked:
            selected.append(option)

    st.sidebar.markdown("---")
    return selected


pillar_filter = visible_checkbox_filter(
    "01 Strategic Area",
    df["Pillar"].unique(),
    "pillar"
)

domain_filter = visible_checkbox_filter(
    "02 Risk Category",
    df["Risk Domain"].unique(),
    "domain"
)

appetite_filter = visible_checkbox_filter(
    "03 Risk Appetite",
    df["Risk Appetite Status"].unique(),
    "appetite"
)

decision_filter = visible_checkbox_filter(
    "04 Executive Decision",
    df["Risk Treatment Decision"].unique(),
    "decision"
)

st.sidebar.markdown(
    """
    <div class="sidebar-box">
        <div class="sidebar-title">Reading Guide</div>
        <div class="sidebar-subtitle">
            <b>Above Appetite</b> means residual risk exceeds the accepted threshold.<br><br>
            <b>KRI Breach</b> means a key risk indicator exceeded its limit.<br><br>
            <b>Executive Review</b> means the risk may need leadership attention.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

filtered_df = df[
    (df["Pillar"].isin(pillar_filter)) &
    (df["Risk Domain"].isin(domain_filter)) &
    (df["Risk Appetite Status"].isin(appetite_filter)) &
    (df["Risk Treatment Decision"].isin(decision_filter))
]

if filtered_df.empty:
    st.warning("No records match the selected filters. Adjust the sidebar checkboxes.")
    st.stop()

# --------------------------------------------------
# Executive Metrics
# --------------------------------------------------

st.markdown('<div class="section-label">Overview</div>', unsafe_allow_html=True)
st.subheader("Executive Summary Metrics")

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("Total Risks", len(filtered_df))

with col2:
    st.metric(
        "Above Appetite",
        len(filtered_df[filtered_df["Risk Appetite Status"] == "Above Appetite"])
    )

with col3:
    st.metric(
        "High / Critical",
        len(filtered_df[filtered_df["Residual Risk Level"].isin(["High", "Critical"])])
    )

with col4:
    st.metric(
        "Avg Residual Risk",
        round(filtered_df["Residual Risk Score"].mean(), 1)
    )

with col5:
    st.metric(
        "KRI Breaches",
        len(filtered_df[filtered_df["KRI Status"] == "Threshold Breached"])
    )

with col6:
    st.metric(
        "Exec Review",
        len(filtered_df[filtered_df["Risk Treatment Decision"] == "Executive Review Required"])
    )

# --------------------------------------------------
# Tabs
# --------------------------------------------------

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "01 Executive Overview",
        "02 Top Risks",
        "03 Maturity",
        "04 KRI Monitoring",
        "05 POA&M Tracker",
        "06 Risk Narrative"
    ]
)

# --------------------------------------------------
# Tab 1: Executive Overview
# --------------------------------------------------

with tab1:
    st.markdown('<div class="section-label">01 Executive Overview</div>', unsafe_allow_html=True)
    st.subheader("Executive Strategic Risk Register")

    executive_cols = [
        "Risk ID",
        "Strategic Priority",
        "Pillar",
        "Risk Domain",
        "Business Impact",
        "Inherent Risk Score",
        "Residual Risk Score",
        "Residual Risk Level",
        "Risk Appetite Status",
        "KRI Severity",
        "Maturity Gap",
        "Risk Treatment Decision",
        "Remediation Priority",
        "Owner",
        "Status"
    ]

    st.dataframe(
        filtered_df[executive_cols].sort_values("Residual Risk Score", ascending=False),
        use_container_width=True,
        height=430
    )

    col7, col8 = st.columns(2)

    with col7:
        st.subheader("Residual Risk Level Distribution")
        fig = make_bar_chart(
            filtered_df["Residual Risk Level"].value_counts(),
            "Residual Risk Levels",
            "Risk Level",
            "Count"
        )
        st.pyplot(fig)

    with col8:
        st.subheader("Risk Appetite Status")
        fig = make_bar_chart(
            filtered_df["Risk Appetite Status"].value_counts(),
            "Risk Appetite Status",
            "Appetite Status",
            "Count"
        )
        st.pyplot(fig)

    col9, col10 = st.columns(2)

    with col9:
        st.subheader("Risks by Strategic Pillar")
        fig = make_bar_chart(
            filtered_df["Pillar"].value_counts(),
            "Risks by Pillar",
            "Strategic Pillar",
            "Count"
        )
        st.pyplot(fig)

    with col10:
        st.subheader("Risk Treatment Decisions")
        fig = make_bar_chart(
            filtered_df["Risk Treatment Decision"].value_counts(),
            "Treatment Decisions",
            "Decision",
            "Count"
        )
        st.pyplot(fig)

# --------------------------------------------------
# Tab 2: Top Risks
# --------------------------------------------------

with tab2:
    st.markdown('<div class="section-label">02 Top Risks</div>', unsafe_allow_html=True)
    st.subheader("Top Strategic Risks by Residual Risk and Maturity Gap")

    top_risks = filtered_df.sort_values(
        ["Residual Risk Score", "Maturity Gap"],
        ascending=[False, False]
    ).head(10)

    st.dataframe(
        top_risks[
            [
                "Risk ID",
                "Strategic Priority",
                "Risk Domain",
                "Risk Description",
                "Business Impact",
                "Inherent Risk Score",
                "Residual Risk Score",
                "Residual Risk Level",
                "Risk Appetite Status",
                "KRI Severity",
                "Maturity Gap",
                "Risk Treatment Decision",
                "Remediation Plan",
            ]
        ],
        use_container_width=True,
        height=420
    )

    st.markdown(
        """
        <p class="small-note">
        This view ranks risks using residual exposure, maturity gap, and KRI severity.
        It helps identify where risk reduction or executive attention is most urgent.
        </p>
        """,
        unsafe_allow_html=True
    )

    col11, col12 = st.columns(2)

    with col11:
        st.subheader("Top Risk Residual Scores")
        top_score_view = top_risks.set_index("Risk ID")["Residual Risk Score"]
        fig = make_bar_chart(
            top_score_view,
            "Top Residual Risk Scores",
            "Risk ID",
            "Residual Risk Score"
        )
        st.pyplot(fig)

    with col12:
        st.subheader("Remediation Priority")
        fig = make_bar_chart(
            filtered_df["Remediation Priority"].value_counts(),
            "Remediation Priority",
            "Priority",
            "Count"
        )
        st.pyplot(fig)

# --------------------------------------------------
# Tab 3: Maturity
# --------------------------------------------------

with tab3:
    st.markdown('<div class="section-label">03 Maturity</div>', unsafe_allow_html=True)
    st.subheader("Strategic Maturity Gap Dashboard")

    col13, col14, col15, col16 = st.columns(4)

    with col13:
        st.metric("Avg Current Maturity", round(filtered_df["Current Maturity"].mean(), 1))

    with col14:
        st.metric("Avg Target Maturity", round(filtered_df["Target Maturity"].mean(), 1))

    with col15:
        st.metric("Largest Gap", filtered_df["Maturity Gap"].max())

    with col16:
        st.metric("Areas Below Target", len(filtered_df[filtered_df["Maturity Gap"] > 0]))

    maturity_cols = [
        "Risk ID",
        "Strategic Priority",
        "Pillar",
        "Current Maturity",
        "Current Maturity Label",
        "Target Maturity",
        "Target Maturity Label",
        "Maturity Gap",
        "Risk Treatment Decision"
    ]

    st.dataframe(
        filtered_df[maturity_cols].sort_values("Maturity Gap", ascending=False),
        use_container_width=True,
        height=360
    )

    st.subheader("Maturity Gap by Strategic Priority")

    maturity_view = filtered_df.sort_values("Maturity Gap", ascending=False)
    fig, ax = plt.subplots(figsize=(10, 5))
    maturity_view.set_index("Strategic Priority")["Maturity Gap"].plot(kind="bar", ax=ax)
    ax.set_xlabel("Strategic Priority")
    ax.set_ylabel("Maturity Gap")
    ax.set_title("Current vs Target Maturity Gap", fontsize=13, fontweight="bold")
    ax.tick_params(axis="x", rotation=55)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)

# --------------------------------------------------
# Tab 4: KRI Monitoring
# --------------------------------------------------

with tab4:
    st.markdown('<div class="section-label">04 KRI Monitoring</div>', unsafe_allow_html=True)
    st.subheader("KRI & Risk Appetite Monitoring")

    col17, col18, col19, col20 = st.columns(4)

    with col17:
        st.metric("Total KRIs", len(filtered_df))

    with col18:
        st.metric(
            "Threshold Breached",
            len(filtered_df[filtered_df["KRI Status"] == "Threshold Breached"])
        )

    with col19:
        st.metric(
            "Critical KRIs",
            len(filtered_df[filtered_df["KRI Severity"] == "Critical"])
        )

    with col20:
        st.metric(
            "Within Threshold",
            len(filtered_df[filtered_df["KRI Status"] == "Within Threshold"])
        )

    kri_cols = [
        "Risk ID",
        "Strategic Priority",
        "Risk Domain",
        "Key Risk Indicator",
        "Current KRI Value",
        "KRI Threshold",
        "KRI Severity",
        "KRI Status",
        "Risk Appetite Status"
    ]

    st.dataframe(
        filtered_df[kri_cols],
        use_container_width=True,
        height=360
    )

    col21, col22 = st.columns(2)

    with col21:
        st.subheader("KRI Severity Distribution")
        fig = make_bar_chart(
            filtered_df["KRI Severity"].value_counts(),
            "KRI Severity",
            "Severity",
            "Count"
        )
        st.pyplot(fig)

    with col22:
        st.subheader("Risk Appetite by Pillar")
        appetite_by_pillar = filtered_df.groupby(
            ["Pillar", "Risk Appetite Status"]
        ).size().unstack(fill_value=0)

        fig, ax = plt.subplots(figsize=(8, 4))
        appetite_by_pillar.plot(kind="bar", ax=ax)
        ax.set_xlabel("Pillar")
        ax.set_ylabel("Count")
        ax.set_title("Risk Appetite by Strategic Pillar", fontsize=13, fontweight="bold")
        ax.tick_params(axis="x", rotation=35)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)

# --------------------------------------------------
# Tab 5: POA&M Tracker
# --------------------------------------------------

with tab5:
    st.markdown('<div class="section-label">05 POA&M Tracker</div>', unsafe_allow_html=True)
    st.subheader("Remediation and POA&M Tracker")

    poam_cols = [
        "Risk ID",
        "Strategic Priority",
        "Owner",
        "Remediation Plan",
        "Target Date",
        "Days Until Target",
        "Timeline Status",
        "Status",
        "Residual Risk Score",
        "Risk Appetite Status",
        "Remediation Priority"
    ]

    st.dataframe(
        filtered_df[poam_cols].sort_values(
            ["Remediation Priority", "Days Until Target"],
            ascending=[True, True]
        ),
        use_container_width=True,
        height=420
    )

    st.markdown(
        """
        <p class="small-note">
        POA&M-style tracking connects risk findings to owners, target dates, remediation actions,
        status, and timeline health.
        </p>
        """,
        unsafe_allow_html=True
    )

    col23, col24 = st.columns(2)

    with col23:
        st.subheader("Remediation Status")
        fig = make_bar_chart(
            filtered_df["Status"].value_counts(),
            "Remediation Status",
            "Status",
            "Count"
        )
        st.pyplot(fig)

    with col24:
        st.subheader("Timeline Status")
        fig = make_bar_chart(
            filtered_df["Timeline Status"].value_counts(),
            "Timeline Status",
            "Timeline Status",
            "Count"
        )
        st.pyplot(fig)

# --------------------------------------------------
# Tab 6: Risk Narrative
# --------------------------------------------------

with tab6:
    st.markdown('<div class="section-label">06 Risk Narrative</div>', unsafe_allow_html=True)
    st.subheader("Detailed Risk Narrative")

    selected_risk = st.selectbox(
        "Select a risk to view detailed narrative",
        options=filtered_df["Risk ID"].tolist()
    )

    risk_row = filtered_df[filtered_df["Risk ID"] == selected_risk].iloc[0]

    st.markdown(f"### {risk_row['Risk ID']} — {risk_row['Strategic Priority']}")

    col25, col26, col27 = st.columns(3)

    with col25:
        st.markdown("**Residual Risk Level**")
        st.markdown(badge_html(risk_row["Residual Risk Level"]), unsafe_allow_html=True)

    with col26:
        st.markdown("**Risk Appetite**")
        st.markdown(badge_html(risk_row["Risk Appetite Status"]), unsafe_allow_html=True)

    with col27:
        st.markdown("**Recommended Decision**")
        st.markdown(badge_html(risk_row["Risk Treatment Decision"]), unsafe_allow_html=True)

    st.write("")

    col28, col29 = st.columns(2)

    with col28:
        st.markdown("#### Risk Context")
        st.write("**Pillar:**", risk_row["Pillar"])
        st.write("**Risk Domain:**", risk_row["Risk Domain"])
        st.write("**Risk Description:**", risk_row["Risk Description"])
        st.write("**Business Impact:**", risk_row["Business Impact"])
        st.write("**Owner:**", risk_row["Owner"])

    with col29:
        st.markdown("#### Risk Scoring")
        st.write("**Likelihood:**", risk_row["Likelihood"])
        st.write("**Impact:**", risk_row["Impact"])
        st.write("**Inherent Risk Score:**", risk_row["Inherent Risk Score"])
        st.write("**Control Effectiveness:**", f"{risk_row['Control Effectiveness %']}%")
        st.write("**Residual Risk Score:**", risk_row["Residual Risk Score"])

    st.markdown("#### Maturity and KRI")

    col30, col31 = st.columns(2)

    with col30:
        st.write("**Current Maturity:**", f"{risk_row['Current Maturity']} - {risk_row['Current Maturity Label']}")
        st.write("**Target Maturity:**", f"{risk_row['Target Maturity']} - {risk_row['Target Maturity Label']}")
        st.write("**Maturity Gap:**", risk_row["Maturity Gap"])

    with col31:
        st.write("**Key Risk Indicator:**", risk_row["Key Risk Indicator"])
        st.write("**Current KRI Value:**", risk_row["Current KRI Value"])
        st.write("**KRI Threshold:**", risk_row["KRI Threshold"])
        st.write("**KRI Severity:**", risk_row["KRI Severity"])

    st.markdown("#### Remediation")
    st.write("**Remediation Plan:**", risk_row["Remediation Plan"])
    st.write("**Target Date:**", risk_row["Target Date"])
    st.write("**Timeline Status:**", risk_row["Timeline Status"])
    st.write("**Remediation Priority:**", risk_row["Remediation Priority"])
    st.write("**Current Status:**", risk_row["Status"])

# --------------------------------------------------
# Download
# --------------------------------------------------

st.divider()

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Processed Strategic Risk Register",
    data=csv,
    file_name="processed_strategic_risk_register.csv",
    mime="text/csv",
)

st.caption(
    "Prototype dashboard using mock/sample data for public-sector strategic risk, maturity, KRI, and remediation reporting."
)