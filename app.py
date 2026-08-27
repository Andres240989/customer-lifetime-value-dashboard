import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Customer Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# =========================================================
# TITLE
# =========================================================

st.title("Customer Analytics Dashboard")

st.write(
    "Interactive dashboard for monitoring customer value, "
    "revenue and retention opportunities."
)

# =========================================================
# LOAD DATA
# =========================================================

df = pd.read_csv("data/customer_segmented.csv")

# =========================================================
# FILTERS
# =========================================================

st.subheader("Filters")

channel_selected = st.selectbox(
    "Channel",
    ["All"] + sorted(df["channel"].unique().tolist())
)


# =========================================================
# APPLY FILTERS
# =========================================================

filtered_df = df.copy()

if channel_selected != "All":

    filtered_df = filtered_df[
        filtered_df["channel"] == channel_selected
    ]


# =========================================================
# KPI CALCULATIONS
# =========================================================

total_customers = filtered_df["customer_id"].nunique()

total_revenue = filtered_df["revenue"].sum()

clientes_low_values = (filtered_df["customer_segment"] == "Low Value").sum()

average_conversion_rate = filtered_df["conversion_rate"].mean()

# =========================================================
# KPI WIDGETS
# =========================================================

st.subheader("Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        label="Customers",
        value=f"{total_customers:,}"
    )

with col2:

    st.metric(
        label="Revenue",
        value=f"${total_revenue / 1000000:,.2f}M"
    )

with col3:
    st.metric(
        label="Low Value Customers",
        value=f"{clientes_low_values:,}"
    )
    

with col4:

    st.metric(
        label="Avg. Conversion Rate",
        value=f"{average_conversion_rate:.1%}"
    )

# =========================================================
# REVENUE BY CHANNEL
# =========================================================

st.subheader("Revenue por canal")

revenue_by_channel = (
    df
    .groupby("channel", as_index=False)["revenue"]
    .sum()
    .sort_values("revenue", ascending=False)
)

fig_channel = px.bar(
    revenue_by_channel,
    x="channel",
    y="revenue",
    color="channel",
    title="Revenue by Channel",
    labels={
        "channel": "Channel",
        "revenue": "Revenue"
    }
)

st.plotly_chart(
    fig_channel,
    use_container_width=True
)

# =========================================================
# REVENUE BY CUSTOMER SEGMENT
# =========================================================

st.subheader('Revenue por segmento')

revenue_by_segment = (
    filtered_df
    .groupby("customer_segment", as_index=False)["revenue"]
    .sum()
    .sort_values("revenue", ascending=False)
)

fig_segment_revenue = px.bar(
    revenue_by_segment,
    x="customer_segment",
    y="revenue",
    color='customer_segment',
    title="Revenue by Customer Segment",
    labels={
        "customer_segment": "Customer Segment",
        "revenue": "Revenue"
    }
)

st.plotly_chart(
    fig_segment_revenue,
    use_container_width=True
)

# =========================================================
# CUSTOMERS BY SEGMENT
# =========================================================

st.subheader("Número de clientes por segmento")

customers_by_segment = (
    filtered_df
    .groupby("customer_segment", as_index=False)["customer_id"]
    .nunique()
    .rename(columns={"customer_id": "customers"})
    .sort_values("customers", ascending=False)
)

fig_customers_segment = px.bar(
    customers_by_segment,
    x="customer_segment",
    y="customers",
    color = 'customer_segment',
    title="Customers by Customer Segment",
    labels={
        "customer_segment": "Customer Segment",
        "customers": "Customers"
    }
)

st.plotly_chart(
    fig_customers_segment,
    use_container_width=True
)

# =========================================================
# 4. RETENTION WARNING AND CUSTOMER ID
# =========================================================
 
# =========================================================
# 4. CUSTOMER RETENTION ALERT
# =========================================================

st.subheader("Customer Retention Alert")

customer_id_selected = st.number_input(
    "Enter Customer ID",
    min_value=int(df["customer_id"].min()),
    max_value=int(df["customer_id"].max()),
    step=1
)

customer = df[df["customer_id"] == customer_id_selected]

if not customer.empty:

    # Customer information
    customer_channel = customer["channel"].iloc[0]
    customer_revenue = customer["revenue"].iloc[0]
    customer_cost = customer["cost"].iloc[0]
    customer_net_value = customer["net_value"].iloc[0]
    customer_score = customer["customer_value_score_net"].iloc[0]
    customer_segment = customer["customer_segment"].iloc[0]

    # -----------------------------------------------------
    # CUSTOMER PROFILE
    # -----------------------------------------------------

    st.write(f"### Customer #{customer_id_selected}")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Revenue",
            f"${customer_revenue:,.0f}"
        )

    with col2:
        st.metric(
            "Net Value",
            f"${customer_net_value:,.0f}"
        )


    with col3:
            st.metric(
                "Customer_Segment",
                 customer_segment
            )

    with col4:
                st.metric(
                    "Cost",
                    f"{customer_cost:.4}"
                )

    st.write(f"**Channel:** {customer_channel}")

    # -----------------------------------------------------
    # RETENTION ALERT
    # -----------------------------------------------------

    if customer_segment == "Low Value":

        st.error(
            "🔴 RETENTION RISK: Low Value Customer"
        )

        st.warning(
            f"""
            **Customer #{customer_id_selected} requires attention.**

            This customer belongs to the **Low Value** segment.

            **Recommended Strategy:**
            - Launch a targeted retention campaign.
            - Increase customer engagement.
            - Offer personalized incentives.
            - Monitor future revenue and conversion.
            """
        )

    elif customer_segment == "High Value - Standard Efficiency":

        st.success(
            "🟢 HIGH VALUE CUSTOMER"
        )

        st.info(
            """
            **Recommended Strategy:**
            - Prioritize customer retention.
            - Explore cross-selling opportunities.
            - Maintain personalized communication.
            - Avoid unnecessary discounts.
            """
        )

    elif customer_segment == "Cost Efficient - Potential Value":

        st.warning(
            "🟡 GROWTH OPPORTUNITY"
        )

        st.info(
            """
            **Recommended Strategy:**
            - Increase customer engagement.
            - Explore opportunities to increase revenue.
            - Consider personalized offers.
            - Monitor customer evolution toward higher-value segments.
            """
        )

    else:

        st.info(
            "🔵 CUSTOMER MONITORING"
        )

        st.info(
            """
            **Recommended Strategy:**
            - Monitor customer performance.
            - Track revenue and conversion.
            - Identify opportunities to increase customer value.
            """
        )

else:

    st.warning(
        "Customer ID not found."
    )
# =========================================================
# LOW VALUE CUSTOMERS AT RISK
# =========================================================

low_value_customers = filtered_df[
    filtered_df["customer_segment"] == "Low Value"
].copy()

low_value_count = low_value_customers["customer_id"].nunique()

st.subheader(
    f"Clientes Low Value en riesgo ({low_value_count})"
)

if low_value_count > 0:

    low_value_display = (
        low_value_customers[
            [
                "customer_id",
                "revenue",
                "channel",
                "cost"
                
            ]
        ]
        .sort_values("revenue", ascending=False)
        .rename(
            columns={
                "customer_id": "Customer ID",
                "revenue": "Revenue",
                "channel": "Channel",
                "customer_value_score_net": "Customer Score",
                "cost" : "Cost"
            }
        )
    )

    st.dataframe(
        low_value_display,
        use_container_width=True,
        hide_index=True
    )

else:

    st.success(
        "No Low Value customers found for the selected channel."
    )