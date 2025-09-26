import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(
    page_title="12-Bed Spa Profitability Dashboard",
    page_icon="💆",
    layout="wide",
    initial_sidebar_state="collapsed"  # Start collapsed for button-based interface
)

# Custom CSS for better styling and mobile responsiveness
st.markdown("""
    <style>
    /* Mobile-first responsive design */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        flex-wrap: wrap;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        padding: 8px 12px;
        background-color: #f0f2f6;
        border-radius: 8px;
        font-size: 14px;
        min-width: 80px;
        text-align: center;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
    }
    .metric-container {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 12px;
        margin: 8px 0;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* Mobile responsive adjustments */
    @media (max-width: 768px) {
        .stTabs [data-baseweb="tab"] {
            font-size: 12px;
            padding: 6px 8px;
            height: 40px;
        }
        .metric-container {
            padding: 12px;
            margin: 6px 0;
        }
        .stMetric {
            text-align: center;
        }
        .plot-container {
            height: 300px !important;
        }
    }

    /* Improve readability */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #2c3e50;
    }

    .stSidebar {
        background-color: #f8f9fa;
    }

    /* Enhanced metric styling */
    .stMetric {
        background-color: white;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    /* Button styling for mobile */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        padding: 8px 4px;
        font-size: 14px;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* Mobile button adjustments */
    @media (max-width: 768px) {
        .stButton > button {
            font-size: 12px;
            padding: 6px 2px;
            min-height: 40px;
        }
    }

    /* Collapsible sections */
    .collapsible {
        background-color: #f1f3f4;
        color: #444;
        cursor: pointer;
        padding: 12px;
        width: 100%;
        border: none;
        text-align: left;
        outline: none;
        font-size: 16px;
        border-radius: 8px;
        margin: 5px 0;
    }

    .collapsible:hover {
        background-color: #e2e6ea;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description with mobile-friendly layout
st.title("🏢 12-Bed Spa Profitability Dashboard - Mumbai")
st.markdown("### Interactive Analysis Tool for Spa Business Planning")


# Constants
MAX_CAPACITY = 1560  # 12 beds × 5 treatments × 26 days
WORKING_DAYS = 26

# One-time capital expenditure
INTERIOR_CAPEX = 10000000  # ₹1 crore for interior setup

# Fixed costs (updated values)
FIXED_COSTS = {
    'Rent (displacement)': 200000,
    'Salary (5 staff)': 425000,
    'Electricity': 45000,
    'Marketing': 125000,
    'IISC': 10000,
    'Accommodation': 100000,
    'Snacks (26 days)': 5200
}

TOTAL_FIXED = sum(FIXED_COSTS.values())

# Variable costs per customer
VARIABLE_PER_CUSTOMER = {
    'Laundry': 35,
    'Bathrobe': 50,
    'Disposal': 10,
    'Disposal U': 20,
    'Incentive': 200
}

TOTAL_VARIABLE_PER_CUSTOMER = sum(VARIABLE_PER_CUSTOMER.values())

# Initialize session state for persistent selections
if 'treatment_cost' not in st.session_state:
    st.session_state.treatment_cost = 5000
if 'num_customers' not in st.session_state:
    st.session_state.num_customers = 468
if 'product_cost_pct' not in st.session_state:
    st.session_state.product_cost_pct = 5.0

# Interactive Button Controls
st.markdown("## ⚙️ Quick Controls")

# Treatment Cost Buttons
st.markdown("### 💰 Treatment Cost (₹)")
cost_col1, cost_col2, cost_col3, cost_col4, cost_col5, cost_col6 = st.columns(6)

cost_options = [3000, 3500, 4000, 4500, 5000, 5500]
cost_labels = ["₹3,000", "₹3,500", "₹4,000", "₹4,500", "₹5,000", "₹5,500"]

for i, (col, cost, label) in enumerate(zip([cost_col1, cost_col2, cost_col3, cost_col4, cost_col5, cost_col6], cost_options, cost_labels)):
    with col:
        button_type = "primary" if st.session_state.treatment_cost == cost else "secondary"
        if st.button(label, key=f"cost_{cost}", type=button_type):
            st.session_state.treatment_cost = cost
            st.rerun()

treatment_cost = st.session_state.treatment_cost

# Customer Count Buttons
st.markdown("### 👥 Number of Customers per Month")
cust_col1, cust_col2, cust_col3, cust_col4, cust_col5, cust_col6 = st.columns(6)

customer_options = [156, 312, 468, 624, 780]
customer_labels = ["156 (10%)", "312 (20%)", "468 (30%)", "624 (40%)", "780 (50%)"]

for i, (col, customers, label) in enumerate(zip([cust_col1, cust_col2, cust_col3, cust_col4, cust_col5], customer_options, customer_labels)):
    with col:
        button_type = "primary" if st.session_state.num_customers == customers else "secondary"
        if st.button(label, key=f"cust_{customers}", type=button_type):
            st.session_state.num_customers = customers
            st.rerun()

with cust_col6:
    if st.button("Custom", key="cust_custom"):
        st.session_state.show_custom_input = True
        st.rerun()

# Custom customer input
if hasattr(st.session_state, 'show_custom_input') and st.session_state.show_custom_input:
    custom_customers = st.number_input("Enter custom number of customers:", min_value=50, max_value=1560, value=st.session_state.num_customers, step=10, key="custom_input")
    if st.button("Apply Custom Value", key="apply_custom"):
        st.session_state.num_customers = custom_customers
        st.session_state.show_custom_input = False
        st.rerun()

num_customers = st.session_state.num_customers

# Calculate current utilization
current_utilization = (num_customers / MAX_CAPACITY) * 100

# Product Cost Percentage Buttons
st.markdown("### 📦 Product Cost (% of Revenue)")
prod_col1, prod_col2, prod_col3, prod_col4, prod_col5 = st.columns(5)

product_options = [2.0, 3.0, 4.0, 5.0, 6.0]
product_labels = ["2%", "3%", "4%", "5%", "6%"]

for i, (col, pct, label) in enumerate(zip([prod_col1, prod_col2, prod_col3, prod_col4, prod_col5], product_options, product_labels)):
    with col:
        button_type = "primary" if st.session_state.product_cost_pct == pct else "secondary"
        if st.button(label, key=f"prod_{pct}", type=button_type):
            st.session_state.product_cost_pct = pct
            st.rerun()

product_cost_pct = st.session_state.product_cost_pct

# Display current selections
st.info(f"🎯 **Current Selection**: ₹{treatment_cost:,} per treatment | {num_customers} customers ({current_utilization:.1f}% utilization) | {product_cost_pct}% product cost")

# Optional: Advanced Settings in Sidebar (collapsed by default)
with st.sidebar:
    st.header("🔧 Advanced Settings")
    modify_fixed = st.checkbox("Modify Fixed Costs")

    if modify_fixed:
        rent = st.number_input("Rent (displacement)", value=FIXED_COSTS['Rent (displacement)'], step=10000)
        salary = st.number_input("Salary", value=FIXED_COSTS['Salary (5 staff)'], step=5000)
        electricity = st.number_input("Electricity", value=FIXED_COSTS['Electricity'], step=1000)
        marketing = st.number_input("Marketing", value=FIXED_COSTS['Marketing'], step=5000)

        FIXED_COSTS['Rent (displacement)'] = rent
        FIXED_COSTS['Salary (5 staff)'] = salary
        FIXED_COSTS['Electricity'] = electricity
        FIXED_COSTS['Marketing'] = marketing
        TOTAL_FIXED = sum(FIXED_COSTS.values())

# Quick summary for mobile users
if st.checkbox("📱 Show Quick Summary", value=False):
    current_metrics = calculate_metrics(num_customers, treatment_cost, product_cost_pct)

    col1, col2 = st.columns(2)
    with col1:
        status = "✅ Profitable" if current_metrics['net_profit'] > 0 else "❌ Loss"
        st.info(f"**Status**: {status}")
        st.info(f"**Utilization**: {current_metrics['utilization']:.1f}%")

    with col2:
        st.info(f"**Monthly Profit**: ₹{current_metrics['net_profit']:,.0f}")
        st.info(f"**Break-even**: {current_metrics['break_even_customers']:.0f} customers")

    st.markdown("---")

# Quick utilization tabs
tab_labels = ["📊 Custom", "10%", "20%", "30%", "40%", "50%"]
tabs = st.tabs(tab_labels)

def calculate_metrics(customers, price, product_pct=5.0):
    """Calculate all financial metrics with enhanced KPIs"""
    revenue = customers * price
    product_cost = revenue * (product_pct / 100)
    variable_costs = (TOTAL_VARIABLE_PER_CUSTOMER * customers) + product_cost
    total_expenses = TOTAL_FIXED + variable_costs
    net_profit = revenue - total_expenses
    margin = (net_profit / revenue * 100) if revenue > 0 else 0
    utilization = (customers / MAX_CAPACITY) * 100
    daily_avg = customers / WORKING_DAYS

    # Enhanced KPIs
    revenue_per_bed = revenue / 12 if revenue > 0 else 0
    profit_per_customer = net_profit / customers if customers > 0 else 0
    break_even_customers = TOTAL_FIXED / (price - TOTAL_VARIABLE_PER_CUSTOMER - (price * product_pct / 100)) if price > (TOTAL_VARIABLE_PER_CUSTOMER + (price * product_pct / 100)) else 0
    break_even_utilization = (break_even_customers / MAX_CAPACITY) * 100 if break_even_customers <= MAX_CAPACITY else 100
    roi_monthly = (net_profit / total_expenses * 100) if total_expenses > 0 else 0
    roi_annual = roi_monthly * 12

    # Cost ratios
    fixed_cost_ratio = (TOTAL_FIXED / revenue * 100) if revenue > 0 else 0
    variable_cost_ratio = (variable_costs / revenue * 100) if revenue > 0 else 0

    # Efficiency metrics
    revenue_per_treatment = price
    cost_per_treatment = total_expenses / customers if customers > 0 else 0
    contribution_margin = price - (TOTAL_VARIABLE_PER_CUSTOMER + (price * product_pct / 100))
    contribution_margin_ratio = (contribution_margin / price * 100) if price > 0 else 0

    # CAPEX payback analysis
    capex_payback_months = INTERIOR_CAPEX / net_profit if net_profit > 0 else float('inf')
    capex_payback_years = capex_payback_months / 12 if net_profit > 0 else float('inf')
    annual_profit = net_profit * 12
    capex_roi_annual = (annual_profit / INTERIOR_CAPEX * 100) if INTERIOR_CAPEX > 0 else 0

    return {
        'revenue': revenue,
        'fixed_costs': TOTAL_FIXED,
        'variable_costs': variable_costs,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'margin': margin,
        'utilization': utilization,
        'daily_avg': daily_avg,
        'break_even': net_profit >= 0,
        'revenue_per_bed': revenue_per_bed,
        'profit_per_customer': profit_per_customer,
        'break_even_customers': break_even_customers,
        'break_even_utilization': break_even_utilization,
        'roi_monthly': roi_monthly,
        'roi_annual': roi_annual,
        'fixed_cost_ratio': fixed_cost_ratio,
        'variable_cost_ratio': variable_cost_ratio,
        'revenue_per_treatment': revenue_per_treatment,
        'cost_per_treatment': cost_per_treatment,
        'contribution_margin': contribution_margin,
        'contribution_margin_ratio': contribution_margin_ratio,
        'capex_payback_months': capex_payback_months,
        'capex_payback_years': capex_payback_years,
        'annual_profit': annual_profit,
        'capex_roi_annual': capex_roi_annual
    }

# Business Parameters Header
st.markdown("---")
st.markdown("## 📋 Business Parameters Overview")

# Display key business constants in organized sections
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🏢 **Facility Specifications**")
    st.markdown(f"""
    - **Beds**: 12 treatment beds
    - **Treatments per bed/day**: 5
    - **Working days/month**: {WORKING_DAYS}
    - **Maximum capacity**: {MAX_CAPACITY:,} treatments/month
    - **Interior CAPEX**: ₹{INTERIOR_CAPEX/10000000:.1f} Crore
    """)

with col2:
    st.markdown("### 💰 **Fixed Costs (Monthly)**")
    st.markdown(f"""
    - **Rent (displacement)**: ₹{FIXED_COSTS['Rent (displacement)']:,}
    - **Salary (5 staff)**: ₹{FIXED_COSTS['Salary (5 staff)']:,}
    - **Electricity**: ₹{FIXED_COSTS['Electricity']:,}
    - **Marketing**: ₹{FIXED_COSTS['Marketing']:,}
    - **IISC**: ₹{FIXED_COSTS['IISC']:,}
    - **Accommodation**: ₹{FIXED_COSTS['Accommodation']:,}
    - **Snacks**: ₹{FIXED_COSTS['Snacks (26 days)']:,}
    - **📊 Total Fixed**: ₹{TOTAL_FIXED:,}
    """)

with col3:
    st.markdown("### 🛍️ **Variable Costs (Per Customer)**")
    st.markdown(f"""
    - **Laundry**: ₹{VARIABLE_PER_CUSTOMER['Laundry']}
    - **Bathrobe**: ₹{VARIABLE_PER_CUSTOMER['Bathrobe']}
    - **Disposal**: ₹{VARIABLE_PER_CUSTOMER['Disposal']}
    - **Disposal U**: ₹{VARIABLE_PER_CUSTOMER['Disposal U']}
    - **Incentive**: ₹{VARIABLE_PER_CUSTOMER['Incentive']}
    - **📊 Total Variable**: ₹{TOTAL_VARIABLE_PER_CUSTOMER}
    - **Product Cost**: 2-6% of revenue (adjustable)
    """)

# Summary metrics in a highlighted box
st.markdown("### 🎯 **Key Business Ratios**")
current_metrics_display = calculate_metrics(468, 5000, 5.0)  # Default values for display
break_even_util = (current_metrics_display['break_even_customers'] / MAX_CAPACITY) * 100

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.info(f"**Break-even Point**\n{current_metrics_display['break_even_customers']:.0f} customers\n({break_even_util:.1f}% utilization)")
with col2:
    st.info(f"**CAPEX Payback**\n₹{INTERIOR_CAPEX/1000000:.0f}M investment\n{current_metrics_display['capex_payback_years']:.1f} years @ default")
with col3:
    st.info(f"**Cost Structure**\nFixed: ₹{TOTAL_FIXED:,}/month\nVariable: ₹{TOTAL_VARIABLE_PER_CUSTOMER}/customer")
with col4:
    st.info(f"**Capacity Planning**\n{MAX_CAPACITY:,} max treatments\n{MAX_CAPACITY/WORKING_DAYS:.0f} per day")

st.markdown("---")

# Function to display metrics
def display_metrics(customers, price, tab_name="Custom"):
    metrics = calculate_metrics(customers, price, product_cost_pct)

    # Row 1: Primary KPIs (responsive columns)
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        st.metric(
            "Utilization Rate",
            f"{metrics['utilization']:.1f}%",
            f"{customers} customers",
            delta_color="normal"
        )

    with col2:
        st.metric(
            "Daily Average",
            f"{metrics['daily_avg']:.0f} customers",
            f"{metrics['daily_avg']/12:.1f} per bed",
            delta_color="normal"
        )

    with col3:
        st.metric(
            "Monthly Revenue",
            f"₹{metrics['revenue']:,.0f}",
            f"₹{price} per treatment"
        )

    with col4:
        profit_color = "normal" if metrics['net_profit'] >= 0 else "inverse"
        st.metric(
            "Net Profit",
            f"₹{metrics['net_profit']:,.0f}",
            f"{metrics['margin']:.1f}% margin",
            delta_color=profit_color
        )

    # Row 2: Enhanced Business Metrics
    st.markdown("### 📊 Enhanced Business Metrics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Revenue per Bed",
            f"₹{metrics['revenue_per_bed']:,.0f}",
            "Monthly per bed"
        )

    with col2:
        st.metric(
            "Profit per Customer",
            f"₹{metrics['profit_per_customer']:,.0f}",
            "Per treatment"
        )

    with col3:
        roi_color = "normal" if metrics['roi_monthly'] > 0 else "inverse"
        st.metric(
            "Monthly ROI",
            f"{metrics['roi_monthly']:.1f}%",
            f"{metrics['roi_annual']:.1f}% annual",
            delta_color=roi_color
        )

    with col4:
        st.metric(
            "Contribution Margin",
            f"₹{metrics['contribution_margin']:.0f}",
            f"{metrics['contribution_margin_ratio']:.1f}% ratio"
        )

    # Row 3: Break-even Analysis
    st.markdown("### ⚖️ Break-even Analysis")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        be_color = "normal" if customers >= metrics['break_even_customers'] else "inverse"
        st.metric(
            "Break-even Customers",
            f"{metrics['break_even_customers']:.0f}",
            f"Need {max(0, metrics['break_even_customers'] - customers):.0f} more" if customers < metrics['break_even_customers'] else "✅ Achieved",
            delta_color=be_color
        )

    with col2:
        st.metric(
            "Break-even Utilization",
            f"{metrics['break_even_utilization']:.1f}%",
            "Minimum required"
        )

    with col3:
        st.metric(
            "Fixed Cost Ratio",
            f"{metrics['fixed_cost_ratio']:.1f}%",
            "Of total revenue"
        )

    with col4:
        st.metric(
            "Variable Cost Ratio",
            f"{metrics['variable_cost_ratio']:.1f}%",
            "Of total revenue"
        )

    # Row 4: CAPEX Analysis
    st.markdown("### 🏗️ CAPEX Payback Analysis")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Interior Investment",
            f"₹{INTERIOR_CAPEX/10000000:.1f} Cr",
            "One-time setup cost"
        )

    with col2:
        payback_color = "normal" if metrics['capex_payback_years'] <= 5 else "inverse"
        payback_text = f"{metrics['capex_payback_years']:.1f} years" if metrics['capex_payback_years'] != float('inf') else "No payback"
        st.metric(
            "Payback Period",
            payback_text,
            f"{metrics['capex_payback_months']:.0f} months" if metrics['capex_payback_months'] != float('inf') else "Loss making",
            delta_color=payback_color
        )

    with col3:
        capex_roi_color = "normal" if metrics['capex_roi_annual'] > 20 else "inverse"
        st.metric(
            "CAPEX ROI (Annual)",
            f"{metrics['capex_roi_annual']:.1f}%",
            "Return on investment",
            delta_color=capex_roi_color
        )

    with col4:
        st.metric(
            "Annual Profit",
            f"₹{metrics['annual_profit']:,.0f}",
            f"₹{metrics['annual_profit']/10000000:.2f} Cr/year"
        )
    
    # Row 4: Visual Analysis
    st.markdown("### 📈 Visual Analysis")

    # Use responsive layout for mobile
    use_single_column = st.checkbox("📱 Single Column View (Mobile Friendly)", value=False, key=f"mobile_view_{tab_name}")

    if use_single_column:
        # Single column layout for mobile
        # Pie chart for cost breakdown
        fig_pie = go.Figure(data=[go.Pie(
            labels=['Fixed Costs', 'Variable Costs', 'Profit' if metrics['net_profit'] > 0 else 'Loss'],
            values=[
                metrics['fixed_costs'],
                metrics['variable_costs'],
                abs(metrics['net_profit'])
            ],
            hole=.3,
            marker_colors=['#FF6B6B', '#4ECDC4', '#95E77E' if metrics['net_profit'] > 0 else '#FFB6C1'],
            textinfo='label+percent',
            textfont_size=12
        )])

        fig_pie.update_layout(
            title={"text": "Cost & Profit Distribution", "x": 0.5, "font": {"size": 16}},
            height=350,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(t=50, b=50, l=20, r=20)
        )
        st.plotly_chart(fig_pie, use_container_width=True, key=f"pie_chart_{tab_name}")

        # Waterfall chart for profit calculation
        fig_waterfall = go.Figure(go.Waterfall(
            name = "Profit Calculation",
            orientation = "v",
            measure = ["absolute", "relative", "relative", "total"],
            x = ["Revenue", "Fixed Costs", "Variable Costs", "Net Profit"],
            y = [metrics['revenue'], -metrics['fixed_costs'], -metrics['variable_costs'], metrics['net_profit']],
            textposition = "outside",
            text = [f"₹{metrics['revenue']/1000:.0f}K",
                   f"-₹{metrics['fixed_costs']/1000:.0f}K",
                   f"-₹{metrics['variable_costs']/1000:.0f}K",
                   f"₹{metrics['net_profit']/1000:.0f}K"],
            connector = {"line":{"color":"rgb(63, 63, 63)"}},
            textfont_size=10
        ))

        fig_waterfall.update_layout(
            title = {"text": "Profit Waterfall (₹ in thousands)", "x": 0.5, "font": {"size": 16}},
            height=350,
            showlegend = False,
            margin=dict(t=50, b=50, l=20, r=20),
            xaxis=dict(tickfont=dict(size=10)),
            yaxis=dict(tickfont=dict(size=10))
        )
        st.plotly_chart(fig_waterfall, use_container_width=True, key=f"waterfall_chart_{tab_name}")
    else:
        # Two column layout for desktop
        col1, col2 = st.columns(2)

        with col1:
            # Pie chart for cost breakdown
            fig_pie = go.Figure(data=[go.Pie(
                labels=['Fixed Costs', 'Variable Costs', 'Profit' if metrics['net_profit'] > 0 else 'Loss'],
                values=[
                    metrics['fixed_costs'],
                    metrics['variable_costs'],
                    abs(metrics['net_profit'])
                ],
                hole=.3,
                marker_colors=['#FF6B6B', '#4ECDC4', '#95E77E' if metrics['net_profit'] > 0 else '#FFB6C1']
            )])

            fig_pie.update_layout(
                title="Cost & Profit Distribution",
                height=400,
                showlegend=True
            )
            st.plotly_chart(fig_pie, use_container_width=True, key=f"pie_chart_{tab_name}")

        with col2:
            # Waterfall chart for profit calculation
            fig_waterfall = go.Figure(go.Waterfall(
                name = "Profit Calculation",
                orientation = "v",
                measure = ["absolute", "relative", "relative", "total"],
                x = ["Revenue", "Fixed Costs", "Variable Costs", "Net Profit"],
                y = [metrics['revenue'], -metrics['fixed_costs'], -metrics['variable_costs'], metrics['net_profit']],
                textposition = "outside",
                text = [f"₹{metrics['revenue']:,.0f}",
                       f"-₹{metrics['fixed_costs']:,.0f}",
                       f"-₹{metrics['variable_costs']:,.0f}",
                       f"₹{metrics['net_profit']:,.0f}"],
                connector = {"line":{"color":"rgb(63, 63, 63)"}},
            ))

            fig_waterfall.update_layout(
                title = "Profit Waterfall",
                height=400,
                showlegend = False
            )
            st.plotly_chart(fig_waterfall, use_container_width=True, key=f"waterfall_chart_{tab_name}")
    
    return metrics

# Display for each tab
with tabs[0]:  # Custom tab
    st.subheader(f"Custom Analysis: {num_customers} customers @ ₹{treatment_cost}")
    custom_metrics = display_metrics(num_customers, treatment_cost)

# Predefined utilization tabs
utilization_rates = [0.10, 0.20, 0.30, 0.40, 0.50]

for i, util_rate in enumerate(utilization_rates, 1):
    with tabs[i]:
        customers_at_util = int(util_rate * MAX_CAPACITY)
        st.subheader(f"{int(util_rate*100)}% Utilization: {customers_at_util} customers @ ₹{treatment_cost}")
        display_metrics(customers_at_util, treatment_cost, f"{int(util_rate*100)}%")

# Comparison Analysis Section
st.markdown("---")
st.header("📈 Comparative Analysis")

# Mobile-friendly comparison charts
mobile_charts = st.checkbox("📱 Mobile-Friendly Charts", value=False, key="mobile_charts_comparison")

if mobile_charts:
    # Single column layout for mobile
    st.markdown("#### 📊 Profit vs Utilization Analysis")
    utilization_range = np.arange(0.05, 0.55, 0.05)
    customers_range = [int(u * MAX_CAPACITY) for u in utilization_range]

    profits = []
    margins = []
    for c in customers_range:
        m = calculate_metrics(c, treatment_cost, product_cost_pct)
        profits.append(m['net_profit'])
        margins.append(m['margin'])

    fig_profit = go.Figure()
    fig_profit.add_trace(go.Scatter(
        x=[u*100 for u in utilization_range],
        y=profits,
        mode='lines+markers',
        name='Net Profit',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=6)
    ))

    fig_profit.add_hline(y=0, line_dash="dash", line_color="red",
                        annotation_text="Break-even")

    # Add current position marker
    current_metrics = calculate_metrics(num_customers, treatment_cost, product_cost_pct)
    fig_profit.add_trace(go.Scatter(
        x=[current_utilization],
        y=[current_metrics['net_profit']],
        mode='markers',
        name='Current Position',
        marker=dict(size=12, color='red', symbol='star')
    ))

    fig_profit.update_layout(
        title={"text": f"Profit vs Utilization @ ₹{treatment_cost}", "x": 0.5, "font": {"size": 14}},
        xaxis_title="Utilization %",
        yaxis_title="Net Profit (₹)",
        height=300,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
        margin=dict(t=50, b=80, l=50, r=50),
        font=dict(size=10)
    )
    st.plotly_chart(fig_profit, use_container_width=True, key="profit_utilization_chart")

    st.markdown("#### 💰 Price Sensitivity Analysis")
    # Simplified price sensitivity for mobile
    price_range = range(3000, 6100, 500)

    fig_price = go.Figure()

    for util in [0.20, 0.30, 0.40]:  # Fewer lines for mobile clarity
        customers_at_util = int(util * MAX_CAPACITY)
        profits_at_prices = []

        for price in price_range:
            m = calculate_metrics(customers_at_util, price, product_cost_pct)
            profits_at_prices.append(m['net_profit'])

        fig_price.add_trace(go.Scatter(
            x=list(price_range),
            y=profits_at_prices,
            mode='lines+markers',
            name=f'{int(util*100)}%',
            line=dict(width=2),
            marker=dict(size=4)
        ))

    fig_price.add_hline(y=0, line_dash="dash", line_color="red")

    fig_price.update_layout(
        title={"text": "Price Sensitivity Analysis", "x": 0.5, "font": {"size": 14}},
        xaxis_title="Treatment Price (₹)",
        yaxis_title="Net Profit (₹)",
        height=300,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
        margin=dict(t=50, b=80, l=50, r=50),
        font=dict(size=10)
    )
    st.plotly_chart(fig_price, use_container_width=True, key="price_sensitivity_chart")

else:
    # Desktop two-column layout
    col1, col2 = st.columns(2)

    with col1:
        # Profitability across different utilization rates
        utilization_range = np.arange(0.05, 0.55, 0.05)
        customers_range = [int(u * MAX_CAPACITY) for u in utilization_range]

        profits = []
        margins = []
        for c in customers_range:
            m = calculate_metrics(c, treatment_cost, product_cost_pct)
            profits.append(m['net_profit'])
            margins.append(m['margin'])

        fig_profit = go.Figure()
        fig_profit.add_trace(go.Scatter(
            x=[u*100 for u in utilization_range],
            y=profits,
            mode='lines+markers',
            name='Net Profit',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8)
        ))

        fig_profit.add_hline(y=0, line_dash="dash", line_color="red",
                            annotation_text="Break-even")

        # Add current position marker
        current_metrics = calculate_metrics(num_customers, treatment_cost, product_cost_pct)
        fig_profit.add_trace(go.Scatter(
            x=[current_utilization],
            y=[current_metrics['net_profit']],
            mode='markers',
            name='Current Position',
            marker=dict(size=15, color='red', symbol='star')
        ))

        fig_profit.update_layout(
            title=f"Profit vs Utilization @ ₹{treatment_cost}",
            xaxis_title="Utilization %",
            yaxis_title="Net Profit (₹)",
            height=400,
            showlegend=True
        )
        st.plotly_chart(fig_profit, use_container_width=True, key="profit_utilization_chart")

    with col2:
        # Price sensitivity analysis
        price_range = range(2000, 6100, 500)

        fig_price = go.Figure()

        for util in [0.10, 0.20, 0.30, 0.40, 0.50]:
            customers_at_util = int(util * MAX_CAPACITY)
            profits_at_prices = []

            for price in price_range:
                m = calculate_metrics(customers_at_util, price, product_cost_pct)
                profits_at_prices.append(m['net_profit'])

            fig_price.add_trace(go.Scatter(
                x=list(price_range),
                y=profits_at_prices,
                mode='lines+markers',
                name=f'{int(util*100)}% Utilization',
                line=dict(width=2)
            ))

        fig_price.add_hline(y=0, line_dash="dash", line_color="red")

        fig_price.update_layout(
            title="Price Sensitivity Analysis",
            xaxis_title="Treatment Price (₹)",
            yaxis_title="Net Profit (₹)",
            height=400,
            showlegend=True
        )
        st.plotly_chart(fig_price, use_container_width=True, key="price_sensitivity_chart")

# Detailed breakdown table
st.markdown("---")

# Create expandable sections for better mobile navigation
with st.expander("📋 Detailed Financial Breakdown", expanded=False):
    st.markdown("### Complete cost and revenue analysis")

    # Create detailed breakdown
    breakdown_data = {
        'Item': [],
        'Amount (₹)': [],
        'Per Customer (₹)': [],
        '% of Revenue': []
    }

    current_metrics = calculate_metrics(num_customers, treatment_cost, product_cost_pct)

    # Add revenue
    breakdown_data['Item'].append('REVENUE')
    breakdown_data['Amount (₹)'].append(current_metrics['revenue'])
    breakdown_data['Per Customer (₹)'].append(treatment_cost)
    breakdown_data['% of Revenue'].append(100.0)

    # Add fixed costs
    breakdown_data['Item'].append('FIXED COSTS')
    breakdown_data['Amount (₹)'].append(None)
    breakdown_data['Per Customer (₹)'].append(None)
    breakdown_data['% of Revenue'].append(None)

    for item, amount in FIXED_COSTS.items():
        breakdown_data['Item'].append(f"  {item}")
        breakdown_data['Amount (₹)'].append(amount)
        breakdown_data['Per Customer (₹)'].append(round(amount/num_customers))
        breakdown_data['% of Revenue'].append(round(amount/current_metrics['revenue']*100, 1))

    # Add variable costs
    breakdown_data['Item'].append('VARIABLE COSTS')
    breakdown_data['Amount (₹)'].append(None)
    breakdown_data['Per Customer (₹)'].append(None)
    breakdown_data['% of Revenue'].append(None)

    for item, amount in VARIABLE_PER_CUSTOMER.items():
        total_amount = amount * num_customers
        breakdown_data['Item'].append(f"  {item}")
        breakdown_data['Amount (₹)'].append(total_amount)
        breakdown_data['Per Customer (₹)'].append(amount)
        breakdown_data['% of Revenue'].append(round(total_amount/current_metrics['revenue']*100, 1))

    # Add product cost
    product_total = current_metrics['revenue'] * (product_cost_pct/100)
    breakdown_data['Item'].append(f"  Product ({product_cost_pct}%)")
    breakdown_data['Amount (₹)'].append(round(product_total))
    breakdown_data['Per Customer (₹)'].append(round(product_total/num_customers))
    breakdown_data['% of Revenue'].append(product_cost_pct)

    # Add totals
    breakdown_data['Item'].append('TOTAL EXPENSES')
    breakdown_data['Amount (₹)'].append(round(current_metrics['total_expenses']))
    breakdown_data['Per Customer (₹)'].append(round(current_metrics['total_expenses']/num_customers))
    breakdown_data['% of Revenue'].append(round(current_metrics['total_expenses']/current_metrics['revenue']*100, 1))

    breakdown_data['Item'].append('NET PROFIT')
    breakdown_data['Amount (₹)'].append(round(current_metrics['net_profit']))
    breakdown_data['Per Customer (₹)'].append(round(current_metrics['net_profit']/num_customers))
    breakdown_data['% of Revenue'].append(round(current_metrics['margin'], 1))

    # Add CAPEX analysis
    breakdown_data['Item'].append('CAPEX ANALYSIS')
    breakdown_data['Amount (₹)'].append(None)
    breakdown_data['Per Customer (₹)'].append(None)
    breakdown_data['% of Revenue'].append(None)

    breakdown_data['Item'].append('  Interior Investment')
    breakdown_data['Amount (₹)'].append(INTERIOR_CAPEX)
    breakdown_data['Per Customer (₹)'].append(round(INTERIOR_CAPEX/num_customers))
    breakdown_data['% of Revenue'].append(round(INTERIOR_CAPEX/current_metrics['revenue']*100, 1))

    breakdown_data['Item'].append('  Annual Profit')
    breakdown_data['Amount (₹)'].append(round(current_metrics['annual_profit']))
    breakdown_data['Per Customer (₹)'].append(round(current_metrics['annual_profit']/num_customers/12))
    breakdown_data['% of Revenue'].append(round(current_metrics['annual_profit']/(current_metrics['revenue']*12)*100, 1))

    payback_text = f"{current_metrics['capex_payback_years']:.1f} years" if current_metrics['capex_payback_years'] != float('inf') else "No payback"
    breakdown_data['Item'].append(f"  Payback Period: {payback_text}")
    breakdown_data['Amount (₹)'].append(None)
    breakdown_data['Per Customer (₹)'].append(None)
    breakdown_data['% of Revenue'].append(round(current_metrics['capex_roi_annual'], 1))

    # Display table
    df_breakdown = pd.DataFrame(breakdown_data)
    st.dataframe(df_breakdown, use_container_width=True)

# Recommendations section
st.markdown("---")

with st.expander("💡 Business Recommendations & Insights", expanded=True):
    st.markdown("### Strategic guidance for optimal spa performance")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🎯 Target Metrics")
        if current_utilization < 20:
            st.error("⚠️ Utilization too low! Target minimum 20%")
        elif current_utilization < 30:
            st.warning("📊 Good start! Aim for 30-40%")
        else:
            st.success("✅ Excellent utilization!")

        st.markdown(f"""
        - **Current**: {current_utilization:.1f}%
        - **Minimum Target**: 20% (312 customers)
        - **Optimal Target**: 30-35% (468-546)
        - **Excellent**: 40%+ (624+)
        """)

    with col2:
        st.markdown("### 💰 Pricing Strategy")
        if treatment_cost < 4000:
            st.warning("⚠️ Consider raising prices")
        elif treatment_cost < 5000:
            st.info("📈 Good pricing, room to grow")
        else:
            st.success("✅ Premium pricing achieved")

        st.markdown(f"""
        - **Current**: ₹{treatment_cost}
        - **Break-even at 10%**: ₹4,900
        - **Recommended**: ₹5,000-5,500
        - **Premium**: ₹5,500+
        """)

    with col3:
        st.markdown("### 📉 Cost Optimization")
        current_metrics = calculate_metrics(num_customers, treatment_cost, product_cost_pct)
        rent_percent = (FIXED_COSTS['Rent (displacement)'] / current_metrics['revenue'] * 100) if current_metrics['revenue'] > 0 else 0

        if rent_percent > 40:
            st.error(f"⚠️ Rent is {rent_percent:.0f}% of revenue!")
        elif rent_percent > 25:
            st.warning(f"📊 Rent is {rent_percent:.0f}% of revenue")
        else:
            st.success(f"✅ Rent is {rent_percent:.0f}% of revenue")

        st.markdown(f"""
        - **Fixed Costs**: ₹{TOTAL_FIXED:,}
        - **Per Customer**: ₹{TOTAL_FIXED/num_customers:.0f}
        - **Consider**: Revenue share model
        - **Target**: <25% of revenue
        """)

# Footer
st.markdown("---")
st.caption("💆 12-Bed Spa Profitability Dashboard | Built with Streamlit | Data as of September 2025")