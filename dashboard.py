"""
PhonePe Transaction Insights — Streamlit Dashboard
This script provides an interactive interface to visualize PhonePe data.
Run with: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import mysql.connector

# --- Database & External Resources ---

# MySQL database credentials
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "pass@123"
MYSQL_DB = "phonepe_pulse"

# GeoJSON URL for India state boundaries (used by Plotly choropleth)
INDIA_GEOJSON_URL = (
    "https://gist.githubusercontent.com/jbrobst/"
    "56c13bbbf9d97d187fea01ca62ea5112/raw/"
    "e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
)

# Maps DB state names → GeoJSON "ST_NM" property names
STATE_NAME_MAP = {
    "andaman-&-nicobar-islands": "Andaman & Nicobar",
    "andhra-pradesh": "Andhra Pradesh",
    "arunachal-pradesh": "Arunachal Pradesh",
    "assam": "Assam",
    "bihar": "Bihar",
    "chandigarh": "Chandigarh",
    "chhattisgarh": "Chhattisgarh",
    "dadra-&-nagar-haveli-&-daman-&-diu": "Dadra and Nagar Haveli and Daman and Diu",
    "delhi": "Delhi",
    "goa": "Goa",
    "gujarat": "Gujarat",
    "haryana": "Haryana",
    "himachal-pradesh": "Himachal Pradesh",
    "jammu-&-kashmir": "Jammu & Kashmir",
    "jharkhand": "Jharkhand",
    "karnataka": "Karnataka",
    "kerala": "Kerala",
    "ladakh": "Ladakh",
    "lakshadweep": "Lakshadweep",
    "madhya-pradesh": "Madhya Pradesh",
    "maharashtra": "Maharashtra",
    "manipur": "Manipur",
    "meghalaya": "Meghalaya",
    "mizoram": "Mizoram",
    "nagaland": "Nagaland",
    "odisha": "Odisha",
    "puducherry": "Puducherry",
    "punjab": "Punjab",
    "rajasthan": "Rajasthan",
    "sikkim": "Sikkim",
    "tamil-nadu": "Tamil Nadu",
    "telangana": "Telangana",
    "tripura": "Tripura",
    "uttar-pradesh": "Uttar Pradesh",
    "uttarakhand": "Uttarakhand",
    "west-bengal": "West Bengal",
    "andaman & nicobar islands": "Andaman & Nicobar",
    "andhra pradesh": "Andhra Pradesh",
    "arunachal pradesh": "Arunachal Pradesh",
    "dadra & nagar haveli & daman & diu": "Dadra and Nagar Haveli and Daman and Diu",
    "himachal pradesh": "Himachal Pradesh",
    "jammu & kashmir": "Jammu & Kashmir",
    "madhya pradesh": "Madhya Pradesh",
    "tamil nadu": "Tamil Nadu",
    "uttar pradesh": "Uttar Pradesh",
    "west bengal": "West Bengal",
}


# --- Helper Functions ---
def get_db_connection():
    """Create a MySQL connection."""
    return mysql.connector.connect(
        host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB,
    )

def run_query(query):
    """Execute a SQL query and return the result as a DataFrame."""
    return pd.read_sql(query, get_db_connection())

def format_num(n):
    """Format monetary values in Indian units (Cr / L)."""
    if n >= 1e7:
        return f"₹{n / 1e7:.2f} Cr"
    elif n >= 1e5:
        return f"₹{n / 1e5:.2f} L"
    return f"₹{n:,.2f}"

def format_count(n):
    """Format count values in Indian units (Cr / L)."""
    if n >= 1e7:
        return f"{n / 1e7:.2f} Cr"
    elif n >= 1e5:
        return f"{n / 1e5:.2f} L"
    return f"{n:,.2f}"

def map_state_name(name):
    """Convert a DB state name to the GeoJSON-compatible display name."""
    if name in STATE_NAME_MAP:
        return STATE_NAME_MAP[name]
    return name.replace("-", " ").title()


def display_chart(fig):
    """Display a Matplotlib chart in Streamlit and close it."""
    st.pyplot(fig)
    plt.close(fig)


def plainy(ax):
    """Prevent scientific notation on y-axis."""
    ax.ticklabel_format(style='plain', axis='y')


# --- Chart Helper Functions ---

def create_bar_chart(df, x_col, y_col, title, xlabel=None, ylabel=None,
                     color=None, colormap="viridis", figsize=(10, 5),
                     show_values=True):
    """
    Create a matplotlib bar chart and return the figure.
    Includes value labels on top of bars by default.
    """
    fig, ax = plt.subplots(figsize=figsize)
    x_vals = range(len(df))

    if color is not None and color in df.columns:
        norm = plt.Normalize(df[color].min(), df[color].max())
        cmap = plt.get_cmap(colormap)
        colors = [cmap(norm(v)) for v in df[color]]
    else:
        colors = "#6C63FF"

    bars = ax.bar(x_vals, df[y_col], color=colors)
    ax.set_xticks(x_vals)
    ax.set_xticklabels(df[x_col], rotation=45, ha='right', fontsize=8)
    plainy(ax)

    if show_values:
        for bar, val in zip(bars, df[y_col]):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                    f"{val:,.0f}", ha='center', va='bottom', fontsize=7)

    ax.set_title(title, fontsize=12, fontweight='bold')
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.tight_layout()
    return fig


def create_pie_chart(df, names_col, values_col, title, figsize=(8, 6)):
    """Create a matplotlib pie chart and return the figure."""
    fig, ax = plt.subplots(figsize=figsize)
    colors = plt.cm.Set2(range(len(df)))
    wedges, texts, autotexts = ax.pie(
        df[values_col], labels=df[names_col], autopct='%1.1f%%',
        colors=colors, startangle=140, pctdistance=0.85,
    )
    for text in texts:
        text.set_fontsize(8)
    for autotext in autotexts:
        autotext.set_fontsize(7)
    ax.set_title(title, fontsize=12, fontweight='bold')
    fig.tight_layout()
    return fig


def create_line_chart(df, x_col, y_col, title, color_col=None,
                      figsize=(10, 5), markers=True):
    """
    Create a matplotlib line chart and return the figure.
    Supports multiple series if color_col is provided.
    """
    fig, ax = plt.subplots(figsize=figsize)
    if color_col and color_col in df.columns:
        groups = df.groupby(color_col)
        colors = plt.cm.tab10(range(len(groups)))
        for (name, group), c in zip(groups, colors):
            mk = 'o' if markers else None
            ax.plot(group[x_col], group[y_col], marker=mk, label=name, color=c)
        ax.legend(fontsize=8, loc='best')
    else:
        mk = 'o' if markers else None
        ax.plot(df[x_col], df[y_col], marker=mk, color="#6C63FF")

    ax.set_title(title, fontsize=12, fontweight='bold')
    plainy(ax)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_xlabel(x_col.replace("_", " ").title())
    fig.tight_layout()
    return fig


def create_area_chart(df, x_col, y_col, color_col, title, figsize=(10, 5)):
    """Create a matplotlib stacked area chart and return the figure."""
    fig, ax = plt.subplots(figsize=figsize)
    pivot = df.pivot_table(index=x_col, columns=color_col, values=y_col,
                           aggfunc='sum').fillna(0)
    colors = plt.cm.tab10(range(len(pivot.columns)))
    ax.stackplot(pivot.index, *[pivot[col] for col in pivot.columns],
                 labels=pivot.columns, colors=colors, alpha=0.8)
    ax.legend(fontsize=8, loc='upper left')
    ax.set_title(title, fontsize=12, fontweight='bold')
    plainy(ax)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.tight_layout()
    return fig


def create_choropleth(df, state_col, value_col, title, cmap="Reds"):
    """
    Create an India choropleth map using Plotly and display it.
    Uses GeoJSON for state boundaries.
    """
    fig = px.choropleth(
        df,
        geojson=INDIA_GEOJSON_URL,
        featureidkey='properties.ST_NM',
        locations=state_col,
        color=value_col,
        color_continuous_scale=cmap,
        title=title,
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(height=600, margin={"r": 0, "t": 40, "l": 0, "b": 0})
    st.plotly_chart(fig, use_container_width=True)


# --- Application Entry Point & Sidebar ---

st.set_page_config(page_title="PhonePe Transaction Insights", page_icon="📱", layout="wide")
st.title("PhonePe-Transaction-Insights")
st.markdown("Analyze transactions, users, and insurance data from PhonePe Pulse")

# --- Sidebar Filters ---

st.sidebar.header("Filters")

years = run_query(
    "SELECT DISTINCT year FROM aggregated_transaction ORDER BY year"
)["year"].tolist()
selected_year = st.sidebar.selectbox("Select Year", years, index=len(years) - 1)
selected_quarter = st.sidebar.selectbox("Select Quarter", [1, 2, 3, 4])

section = st.sidebar.radio(
    "Dashboard Section",
    ["Overview", "Transaction Analysis", "User Analysis",
     "Insurance Analysis", "Top Charts", "Business Case Studies"],
)


# =============================================================================
# 1. OVERVIEW - General Statistics and State-wise Summary
# =============================================================================
if section == "Overview":
    st.header("Overview")

    metrics = run_query(f"""
        SELECT SUM(transaction_count) AS total_txn,
               SUM(transaction_amount) AS total_amt
        FROM aggregated_transaction
        WHERE state != 'india' AND year = {selected_year} AND quarter = {selected_quarter}
    """)
    users = run_query(f"""
        SELECT SUM(registered_users) AS total_users,
               SUM(app_opens) AS total_opens
        FROM map_user
        WHERE state = 'india' AND year = {selected_year} AND quarter = {selected_quarter}
    """)
    ins = run_query(f"""
        SELECT SUM(insurance_count) AS total_ins,
               SUM(insurance_amount) AS total_ins_amt
        FROM aggregated_insurance
        WHERE state != 'india' AND year = {selected_year} AND quarter = {selected_quarter}
    """)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Transactions", format_count(int(metrics['total_txn'].iloc[0] or 0)))
    col2.metric("Total Amount", format_num(float(metrics['total_amt'].iloc[0] or 0)))
    col3.metric("Registered Users", format_count(int(users['total_users'].iloc[0] or 0)))
    col4.metric("Insurance Policies", format_count(int(ins['total_ins'].iloc[0] or 0)))

    # India choropleth — transaction amount by state
    st.subheader(f"Transaction Amount by State — {selected_year} Q{selected_quarter}")
    map_data = run_query(f"""
        SELECT district AS state,
               ROUND(SUM(transaction_amount), 2) AS amount,
               SUM(transaction_count) AS count
        FROM map_transaction
        WHERE state = 'india' AND year = {selected_year} AND quarter = {selected_quarter}
        GROUP BY district
    """)
    if not map_data.empty:
        map_data["state_name"] = map_data["state"].apply(map_state_name)
        create_choropleth(map_data, "state_name", "amount",
                          "Transaction Amount by State", cmap="viridis")

    # Payment category pie charts
    st.subheader("Payment Category Breakdown")
    cat_data = run_query(f"""
        SELECT transaction_type,
               SUM(transaction_count) AS count,
               ROUND(SUM(transaction_amount), 2) AS amount
        FROM aggregated_transaction
        WHERE state != 'india' AND year = {selected_year} AND quarter = {selected_quarter}
        GROUP BY transaction_type
        ORDER BY count DESC
    """)
    if not cat_data.empty:
        c1, c2 = st.columns(2)
        with c1:
            fig = create_pie_chart(cat_data, "transaction_type", "count",
                                   "By Transaction Count")
            display_chart(fig)
        with c2:
            fig = create_pie_chart(cat_data, "transaction_type", "amount",
                                   "By Transaction Amount")
            display_chart(fig)


# =============================================================================
# 2. TRANSACTION ANALYSIS - Historical Trends & State Comparisons
# =============================================================================
elif section == "Transaction Analysis":
    st.header("Transaction Analysis")

    st.subheader("Yearly Transaction Trend")
    trend = run_query("""
        SELECT year, SUM(transaction_count) AS count,
               ROUND(SUM(transaction_amount), 2) AS amount
        FROM aggregated_transaction WHERE state != 'india'
        GROUP BY year ORDER BY year
    """)
    c1, c2 = st.columns(2)
    with c1:
        fig = create_bar_chart(trend, "year", "count",
                               "Transaction Count by Year")
        display_chart(fig)
    with c2:
        fig = create_bar_chart(trend, "year", "amount",
                               "Transaction Amount by Year")
        display_chart(fig)

    st.subheader("Quarter-wise Trend")
    q_trend = run_query(f"""
        SELECT quarter, SUM(transaction_count) AS count,
               ROUND(SUM(transaction_amount), 2) AS amount
        FROM aggregated_transaction
        WHERE state != 'india' AND year = {selected_year}
        GROUP BY quarter ORDER BY quarter
    """)
    fig = create_bar_chart(q_trend, "quarter", "count",
                           f"Quarterly Transactions — {selected_year}")
    display_chart(fig)

    st.subheader("Payment Type Trend Over Years")
    pt = run_query("""
        SELECT year, transaction_type, SUM(transaction_count) AS count
        FROM aggregated_transaction WHERE state != 'india'
        GROUP BY year, transaction_type ORDER BY year
    """)
    fig = create_line_chart(pt, "year", "count", "Payment Types Over Time",
                            color_col="transaction_type")
    display_chart(fig)

    st.subheader(f"Top 10 States — {selected_year} Q{selected_quarter}")
    top_states = run_query(f"""
        SELECT state, SUM(transaction_count) AS count,
               ROUND(SUM(transaction_amount), 2) AS amount
        FROM aggregated_transaction
        WHERE state != 'india' AND year = {selected_year} AND quarter = {selected_quarter}
        GROUP BY state ORDER BY count DESC LIMIT 10
    """)
    if not top_states.empty:
        top_states["state_display"] = top_states["state"].apply(
            lambda x: x.replace("-", " ").title()
        )
        fig = create_bar_chart(top_states, "state_display", "count",
                               "Top 10 States by Transaction Count",
                               xlabel="State")
        display_chart(fig)


# =============================================================================
# 3. USER ANALYSIS - Registered Users & Device Demographics
# =============================================================================
elif section == "User Analysis":
    st.header("User Analysis")

    st.subheader(f"Registered Users by State — {selected_year} Q{selected_quarter}")
    user_map = run_query(f"""
        SELECT district AS state, SUM(registered_users) AS users, SUM(app_opens) AS opens
        FROM map_user
        WHERE state = 'india' AND year = {selected_year} AND quarter = {selected_quarter}
        GROUP BY district
    """)
    if not user_map.empty:
        user_map["state_name"] = user_map["state"].apply(map_state_name)
        create_choropleth(user_map, "state_name", "users",
                          "Registered Users by State", cmap="Blues")

    st.subheader("Top Device Brands")
    brands = run_query(f"""
        SELECT brand, SUM(user_count) AS count
        FROM aggregated_user
        WHERE state != 'india' AND year = {selected_year} AND quarter = {selected_quarter}
        GROUP BY brand ORDER BY count DESC LIMIT 10
    """)
    if not brands.empty:
        c1, c2 = st.columns(2)
        with c1:
            fig = create_bar_chart(brands, "brand", "count",
                                   "Users by Device Brand")
            display_chart(fig)
        with c2:
            fig = create_pie_chart(brands, "brand", "count",
                                   "Device Brand Share")
            display_chart(fig)

    st.subheader("Device Brand Trend Over Years")
    brand_trend = run_query("""
        SELECT year, brand, SUM(user_count) AS count
        FROM aggregated_user WHERE state != 'india'
        GROUP BY year, brand ORDER BY year
    """)
    top5 = brand_trend.groupby("brand")["count"].sum().nlargest(5).index.tolist()
    brand_trend_top = brand_trend[brand_trend["brand"].isin(top5)]
    fig = create_line_chart(brand_trend_top, "year", "count",
                            "Top 5 Device Brands Over Time", color_col="brand")
    display_chart(fig)


# =============================================================================
# 4. INSURANCE ANALYSIS - Policies and State-wise Adoption
# =============================================================================
elif section == "Insurance Analysis":
    st.header("Insurance Analysis")

    st.subheader(f"Insurance Transactions by State — {selected_year} Q{selected_quarter}")
    ins_map = run_query(f"""
        SELECT district AS state, SUM(insurance_count) AS count,
               ROUND(SUM(insurance_amount), 2) AS amount
        FROM map_insurance
        WHERE state = 'india' AND year = {selected_year} AND quarter = {selected_quarter}
        GROUP BY district
    """)
    if not ins_map.empty:
        ins_map["state_name"] = ins_map["state"].apply(map_state_name)
        create_choropleth(ins_map, "state_name", "count",
                          "Insurance Policies by State", cmap="Reds")
    else:
        st.info("No insurance data available for this period.")

    st.subheader("Insurance Trend Over Time")
    ins_trend = run_query("""
        SELECT year, SUM(insurance_count) AS count,
               ROUND(SUM(insurance_amount), 2) AS amount
        FROM aggregated_insurance WHERE state != 'india'
        GROUP BY year ORDER BY year
    """)
    if not ins_trend.empty:
        c1, c2 = st.columns(2)
        with c1:
            fig = create_bar_chart(ins_trend, "year", "count",
                                   "Insurance Count by Year")
            display_chart(fig)
        with c2:
            fig = create_bar_chart(ins_trend, "year", "amount",
                                   "Insurance Amount by Year")
            display_chart(fig)

    st.subheader("Top 10 States by Insurance")
    top_ins = run_query(f"""
        SELECT state, SUM(insurance_count) AS count,
               ROUND(SUM(insurance_amount), 2) AS amount
        FROM aggregated_insurance
        WHERE state != 'india' AND year = {selected_year} AND quarter = {selected_quarter}
        GROUP BY state ORDER BY count DESC LIMIT 10
    """)
    if not top_ins.empty:
        top_ins["state_display"] = top_ins["state"].apply(
            lambda x: x.replace("-", " ").title()
        )
        fig = create_bar_chart(top_ins, "state_display", "count",
                               "Top 10 States", xlabel="State")
        display_chart(fig)
    else:
        st.info("No insurance data available for this period.")


# =============================================================================
# 5. TOP CHARTS - Leaderboards for Transactions, Users & Insurance
# =============================================================================
elif section == "Top Charts":
    st.header("Top Charts")

    top_type = st.selectbox("Select Category", ["Transactions", "Users", "Insurance"])

    if top_type == "Transactions":
        st.subheader(f"Top 10 States — {selected_year} Q{selected_quarter}")
        df = run_query(f"""
            SELECT entity_name, SUM(transaction_count) AS count,
                   ROUND(SUM(transaction_amount), 2) AS amount
            FROM top_transaction
            WHERE entity_type = 'state' AND state = 'india'
              AND year = {selected_year} AND quarter = {selected_quarter}
            GROUP BY entity_name ORDER BY count DESC LIMIT 10
        """)
        if not df.empty:
            df["entity_display"] = df["entity_name"].apply(lambda x: x.title())
            fig = create_bar_chart(df, "entity_display", "count",
                                   "Top 10 States")
            display_chart(fig)

        st.subheader(f"Top 10 Districts — {selected_year} Q{selected_quarter}")
        df = run_query(f"""
            SELECT entity_name, SUM(transaction_count) AS count,
                   ROUND(SUM(transaction_amount), 2) AS amount
            FROM top_transaction
            WHERE entity_type = 'district' AND state = 'india'
              AND year = {selected_year} AND quarter = {selected_quarter}
            GROUP BY entity_name ORDER BY count DESC LIMIT 10
        """)
        if not df.empty:
            df["entity_display"] = df["entity_name"].apply(lambda x: x.title())
            fig = create_bar_chart(df, "entity_display", "count",
                                   "Top 10 Districts")
            display_chart(fig)

    elif top_type == "Users":
        st.subheader(f"Top 10 States — {selected_year} Q{selected_quarter}")
        df = run_query(f"""
            SELECT entity_name, SUM(registered_users) AS users
            FROM top_user
            WHERE entity_type = 'state' AND state = 'india'
              AND year = {selected_year} AND quarter = {selected_quarter}
            GROUP BY entity_name ORDER BY users DESC LIMIT 10
        """)
        if not df.empty:
            df["entity_display"] = df["entity_name"].apply(lambda x: x.title())
            fig = create_bar_chart(df, "entity_display", "users",
                                   "Top 10 States by Users")
            display_chart(fig)

        st.subheader(f"Top 10 Districts — {selected_year} Q{selected_quarter}")
        df = run_query(f"""
            SELECT entity_name, SUM(registered_users) AS users
            FROM top_user
            WHERE entity_type = 'district' AND state = 'india'
              AND year = {selected_year} AND quarter = {selected_quarter}
            GROUP BY entity_name ORDER BY users DESC LIMIT 10
        """)
        if not df.empty:
            df["entity_display"] = df["entity_name"].apply(lambda x: x.title())
            fig = create_bar_chart(df, "entity_display", "users",
                                   "Top 10 Districts by Users")
            display_chart(fig)

    elif top_type == "Insurance":
        st.subheader(f"Top 10 States — {selected_year} Q{selected_quarter}")
        df = run_query(f"""
            SELECT entity_name, SUM(insurance_count) AS count,
                   ROUND(SUM(insurance_amount), 2) AS amount
            FROM top_insurance
            WHERE entity_type = 'state' AND state = 'india'
              AND year = {selected_year} AND quarter = {selected_quarter}
            GROUP BY entity_name ORDER BY count DESC LIMIT 10
        """)
        if not df.empty:
            df["entity_display"] = df["entity_name"].apply(lambda x: x.title())
            fig = create_bar_chart(df, "entity_display", "count",
                                   "Top 10 States by Insurance")
            display_chart(fig)
        else:
            st.info("No insurance data available for this period.")

        st.subheader(f"Top 10 Districts — {selected_year} Q{selected_quarter}")
        df = run_query(f"""
            SELECT entity_name, SUM(insurance_count) AS count,
                   ROUND(SUM(insurance_amount), 2) AS amount
            FROM top_insurance
            WHERE entity_type = 'district' AND state = 'india'
              AND year = {selected_year} AND quarter = {selected_quarter}
            GROUP BY entity_name ORDER BY count DESC LIMIT 10
        """)
        if not df.empty:
            df["entity_display"] = df["entity_name"].apply(lambda x: x.title())
            fig = create_bar_chart(df, "entity_display", "count",
                                   "Top 10 Districts by Insurance")
            display_chart(fig)
        else:
            st.info("No insurance data available for this period.")


# =============================================================================
# 6. BUSINESS CASE STUDIES - Deep Dives into Market Insights
# =============================================================================
elif section == "Business Case Studies":
    st.header("Business Case Studies")

    case = st.selectbox("Select Case Study", [
        "1. Decoding Transaction Dynamics",
        "2. Device Dominance & User Engagement",
        "3. Insurance Penetration & Growth",
        "4. Transaction Analysis for Market Expansion",
        "5. User Engagement & Growth Strategy",
    ])

    # Case 1: Transaction Dynamics
    if case.startswith("1"):
        st.subheader("Decoding Transaction Dynamics on PhonePe")
        st.markdown("""
        **Scenario:** PhonePe has identified significant variations in transaction behavior
        across states, quarters, and payment categories. This analysis explores those patterns.
        """)

        df = run_query("""
            SELECT year, SUM(transaction_count) AS count,
                   ROUND(SUM(transaction_amount), 2) AS amount
            FROM aggregated_transaction WHERE state != 'india'
            GROUP BY year ORDER BY year
        """)
        fig = create_line_chart(df, "year", "count",
                                "Transaction Count Growth Over Years")
        display_chart(fig)

        df = run_query("""
            SELECT year, transaction_type, SUM(transaction_count) AS count
            FROM aggregated_transaction WHERE state != 'india'
            GROUP BY year, transaction_type ORDER BY year
        """)
        fig = create_area_chart(df, "year", "count", "transaction_type",
                                "Payment Category Trends Over Years")
        display_chart(fig)

        df = run_query("""
            SELECT a.year, a.total AS current_year, b.total AS prev_year,
                   ROUND(((a.total - b.total) / b.total) * 100, 2) AS growth_pct
            FROM (SELECT year, SUM(transaction_count) AS total
                  FROM aggregated_transaction WHERE state != 'india' GROUP BY year) a
            LEFT JOIN (SELECT year, SUM(transaction_count) AS total
                       FROM aggregated_transaction WHERE state != 'india' GROUP BY year) b
              ON a.year = b.year + 1
            ORDER BY a.year
        """)
        df = df.dropna(subset=["growth_pct"])
        if not df.empty:
            fig = create_bar_chart(df, "year", "growth_pct",
                                   "Year-over-Year Growth (%)",
                                   color="growth_pct", colormap="RdYlGn")
            display_chart(fig)

        st.markdown("""
        **Key Findings:**
        - Peer-to-peer and merchant payments dominate the transaction landscape
        - Consistent year-over-year growth indicates strong platform adoption
        - Seasonal patterns visible in quarterly data suggest festival-period spikes
        """)

    # Case 2: Device Dominance
    elif case.startswith("2"):
        st.subheader("Device Dominance and User Engagement Analysis")
        st.markdown("""
        **Scenario:** Understanding device preferences helps optimize app performance
        and target users effectively across different regions.
        """)

        brand_df = run_query("""
            SELECT brand, SUM(user_count) AS count
            FROM aggregated_user WHERE state != 'india'
            GROUP BY brand ORDER BY count DESC LIMIT 10
        """)
        fig = create_bar_chart(brand_df, "brand", "count",
                               "Top 10 Device Brands (All Time)",
                               color="count", colormap="viridis")
        display_chart(fig)

        trend_df = run_query("""
            SELECT year, brand, SUM(user_count) AS count
            FROM aggregated_user WHERE state != 'india'
            GROUP BY year, brand ORDER BY year
        """)
        top5 = trend_df.groupby("brand")["count"].sum().nlargest(5).index.tolist()
        df_top = trend_df[trend_df["brand"].isin(top5)]
        fig = create_line_chart(df_top, "year", "count",
                                "Top 5 Device Brands — Growth Over Years",
                                color_col="brand")
        display_chart(fig)

        # Calculate fastest growing brand
        fastest_brand = "N/A"
        if not df_top.empty:
            years_available = sorted(df_top["year"].unique())
            if len(years_available) >= 2:
                first_yr, last_yr = years_available[0], years_available[-1]
                growth_rates = {}
                for b in top5:
                    b_data = df_top[df_top["brand"] == b]
                    first_val = b_data[b_data["year"] == first_yr]["count"].sum()
                    last_val = b_data[b_data["year"] == last_yr]["count"].sum()
                    if first_val > 0:
                        growth_rates[b] = ((last_val - first_val) / first_val) * 100
                if growth_rates:
                    fastest_brand = max(growth_rates, key=lambda x: growth_rates[x])

        state_brand_df = run_query("""
            SELECT state, brand, total_users FROM (
                SELECT state, brand, SUM(user_count) AS total_users,
                       ROW_NUMBER() OVER (PARTITION BY state ORDER BY SUM(user_count) DESC) AS rn
                FROM aggregated_user WHERE state != 'india' GROUP BY state, brand
            ) ranked
            WHERE rn = 1
            ORDER BY total_users DESC LIMIT 15
        """)
        if not state_brand_df.empty:
            state_brand_df["state_display"] = state_brand_df["state"].apply(
                lambda x: x.replace("-", " ").title()
            )
            from matplotlib.patches import Patch
            fig, ax = plt.subplots(figsize=(12, 5))
            brands_list = state_brand_df["brand"].unique()
            colors = plt.cm.tab10(range(len(brands_list)))
            brand_color_map = dict(zip(brands_list, colors))
            bar_colors = [brand_color_map[b] for b in state_brand_df["brand"]]
            x_vals = range(len(state_brand_df))
            ax.bar(x_vals, state_brand_df["total_users"], color=bar_colors)
            ax.set_xticks(x_vals)
            ax.set_xticklabels(state_brand_df["state_display"], rotation=45,
                               ha='right', fontsize=8)
            ax.set_title("Dominant Device Brand by State (Top 15)",
                         fontsize=12, fontweight='bold')
            ax.set_xlabel("State")
            plainy(ax)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            legend_elements = [Patch(facecolor=brand_color_map[b], label=b)
                               for b in brands_list]
            ax.legend(handles=legend_elements, fontsize=8, loc='upper right')
            fig.tight_layout()
            display_chart(fig)

        top1_brand = brand_df.iloc[0]["brand"] if len(brand_df) > 0 else "N/A"
        top2_brand = brand_df.iloc[1]["brand"] if len(brand_df) > 1 else "N/A"
        num_unique_dominant = state_brand_df["brand"].nunique() if not state_brand_df.empty else 0

        st.markdown(f"""
        **Key Findings:**
        - **{top1_brand}** and **{top2_brand}** are the top two dominant device brands across all states
        - **{fastest_brand}** shows the fastest growth trajectory among the top 5 brands
        - **{num_unique_dominant}** distinct brands dominate across the top 15 states, showing {'significant regional variation' if num_unique_dominant >= 3 else 'relatively uniform preferences'}
        """)

    # Case 3: Insurance Growth
    elif case.startswith("3"):
        st.subheader("Insurance Penetration and Growth Potential")
        st.markdown("""
        **Scenario:** PhonePe's insurance segment is growing. This analysis identifies
        untapped opportunities for insurance adoption at the state level.
        """)

        df = run_query("""
            SELECT year, quarter, SUM(insurance_count) AS count,
                   ROUND(SUM(insurance_amount), 2) AS amount
            FROM aggregated_insurance WHERE state != 'india'
            GROUP BY year, quarter ORDER BY year, quarter
        """)
        if not df.empty:
            df["period"] = df["year"].astype(str) + " Q" + df["quarter"].astype(str)
            fig, ax = plt.subplots(figsize=(14, 5))
            x_vals = range(len(df))
            ax.plot(x_vals, df["count"], marker='o', color="#6C63FF", linewidth=2)
            
            # Set x-axis labels with year on first line, Q{quarter} on second line
            labels = [f"{row['year']}\nQ{row['quarter']}" 
                      for _, row in df.iterrows()]
            ax.set_xticks(x_vals)
            ax.set_xticklabels(labels, fontsize=8, rotation=0)
            
            ax.set_title("Insurance Transactions Over Time", fontsize=12, fontweight='bold')
            ax.set_xlabel("Period")
            plainy(ax)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            fig.tight_layout()
            display_chart(fig)
            
            fig = create_bar_chart(df, "period", "amount",
                           "Insurance Amount Over Time")
            display_chart(fig)

        df = run_query("""
            SELECT state, SUM(insurance_count) AS count
            FROM aggregated_insurance WHERE state != 'india'
            GROUP BY state ORDER BY count DESC LIMIT 10
        """)
        if not df.empty:
            df["state_display"] = df["state"].apply(lambda x: x.replace("-", " ").title())
            fig = create_bar_chart(df, "state_display", "count",
                                   "Top 10 States by Insurance Adoption",
                                   xlabel="State")
            display_chart(fig)

        st.markdown("""
        **Key Findings:**
        - Insurance adoption is growing rapidly quarter-over-quarter
        - Southern and western states show higher insurance penetration
        - Significant untapped potential in northern and eastern states
        """)

    # Case 4: Market Expansion
    elif case.startswith("4"):
        st.subheader("Transaction Analysis for Market Expansion")
        st.markdown("""
        **Scenario:** Understanding transaction dynamics at the state level is crucial
        for identifying trends, opportunities, and potential areas for expansion.
        """)

        df = run_query("""
            SELECT state, SUM(transaction_count) AS count,
                   ROUND(SUM(transaction_amount), 2) AS amount
            FROM aggregated_transaction WHERE state != 'india'
            GROUP BY state ORDER BY count DESC
        """)
        if not df.empty:
            df["state_name"] = df["state"].apply(map_state_name)
            create_choropleth(df, "state_name", "count",
                              "Total Transactions by State (All Time)",
                              cmap="YlOrRd")

        df = run_query("""
            SELECT state, SUM(transaction_count) AS count
            FROM aggregated_transaction WHERE state != 'india'
            GROUP BY state ORDER BY count ASC LIMIT 10
        """)
        if not df.empty:
            df["state_display"] = df["state"].apply(lambda x: x.replace("-", " ").title())
            fig = create_bar_chart(df, "state_display", "count",
                                   "Bottom 10 States (Market Expansion Targets)",
                                   xlabel="State", color="count", colormap="Reds_r")
            display_chart(fig)

        st.markdown("""
        **Key Findings:**
        - Karnataka, Maharashtra, and Telangana lead in transactions
        - Northeast states and UTs represent untapped markets for expansion
        - Strategic partnerships and marketing in low-adoption states can drive growth
        """)

    # Case 5: User Engagement
    elif case.startswith("5"):
        st.subheader("User Engagement and Growth Strategy")
        st.markdown("""
        **Scenario:** Analyzing user engagement across states helps enhance market
        position and identify growth opportunities.
        """)

        df = run_query("""
            SELECT district AS state,
                   SUM(registered_users) AS users,
                   SUM(app_opens) AS opens,
                   ROUND(SUM(app_opens) / SUM(registered_users), 2) AS engagement_ratio
            FROM map_user WHERE state = 'india'
            GROUP BY district ORDER BY engagement_ratio DESC
        """)
        if not df.empty:
            df["state_name"] = df["state"].apply(map_state_name)
            create_choropleth(df, "state_name", "engagement_ratio",
                              "User Engagement Ratio (App Opens / Registered Users)",
                              cmap="Greens")

            top15 = df.nlargest(15, "engagement_ratio")
            fig = create_bar_chart(top15, "state_name", "engagement_ratio",
                                   "Top 15 States by Engagement Ratio",
                                   xlabel="State")
            display_chart(fig)

        df = run_query("""
            SELECT year, SUM(registered_users) AS users
            FROM map_user WHERE state = 'india'
            GROUP BY year ORDER BY year
        """)
        fig = create_line_chart(df, "year", "users",
                                "Registered User Growth Over Years")
        display_chart(fig)

        st.markdown("""
        **Key Findings:**
        - Southern states show highest engagement ratios (app opens per user)
        - User base is growing consistently year-over-year
        - States with high registration but low engagement need targeted retention strategies
        """)


# --- Footer ---
st.sidebar.markdown("---")
st.sidebar.markdown("Built by Manglesh Kumar Singh !")
st.sidebar.markdown("Data Source: [PhonePe Pulse](https://github.com/PhonePe/pulse)")