import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import calendar
import plotly.express as px

# --- PAGE SETUP ---
st.set_page_config(layout="wide", page_title="Pizza Sales BI Portfolio")

# --- IMPORTANT FUNCTIONS ---
def style_ticks(ax, x_labelsize=9, y_labelsize=9, x_labelcolor='black', y_labelcolor='black', tick_length=0):
    ax.tick_params(axis='x', labelsize=x_labelsize, labelcolor=x_labelcolor, length=tick_length)
    ax.tick_params(axis='y', labelsize=y_labelsize, labelcolor=y_labelcolor, length=tick_length)

def style_labels_and_title(ax, x_label=None, xcolor='black', xbold=None, y_label=None, ycolor='black', ybold=None, title=None, tcolor='black', tsize=15, tbold=None):
    if x_label: ax.set_xlabel(x_label, fontsize=9, color=xcolor, fontweight=xbold)
    if y_label: ax.set_ylabel(y_label, fontsize=9, color=ycolor, fontweight=ybold)
    if title: ax.set_title(title, fontsize=tsize, color=tcolor, pad=20, fontweight=tbold)

def remove_spines(ax, spines=["top", "right", "left", "bottom"]):
    for spine in spines: ax.spines[spine].set_visible(False)

# --- DATA LOADING & PREPARATION ---
df = pd.read_csv('pizza_sales.csv')
df['order_date'] = pd.to_datetime(df['order_date'], dayfirst=True)
df['order_time'] = pd.to_datetime(df['order_time'], format='%H:%M:%S')
df['order_hour'] = df['order_time'].dt.hour
df['day_name'] = df['order_date'].dt.day_name()
df['month_name'] = df['order_date'].dt.month_name()

st.sidebar.header("Dashboard Filters")
# Download Button for the filtered data
st.sidebar.markdown("---")
csv = df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="Download Filtered Data as CSV",
    data=csv,
    file_name='filtered_pizza_sales.csv',
    mime='text/csv',
)
# --- SIDEBAR FILTERS ---
st.sidebar.header("Filter Your Data")

# Month Filter
month_list = list(calendar.month_name)[1:]
selected_months = st.sidebar.multiselect("Select Months", options=month_list, default=month_list)

# 1. Category Filter
categories = st.sidebar.multiselect(
    "Select Pizza Category:",
    options=df["pizza_category"].unique(),
    default=df["pizza_category"].unique()
)

# 2. Size Filter
sizes = st.sidebar.multiselect(
    "Select Pizza Size:",
    options=df["pizza_size"].unique(),
    default=df["pizza_size"].unique()
)

# Apply filters to the dataframe
df = df[df['month_name'].isin(selected_months) & df["pizza_category"].isin(categories) & df["pizza_size"].isin(sizes)]

# KPI Calculations
total_revenue = df['total_price'].sum()
total_pizza_sold = df['quantity'].sum()
total_orders = df['order_id'].nunique()
avg_order_value = total_revenue / total_orders 
avg_pizza_per_order = total_pizza_sold / total_orders

# --- DASHBOARD HEADER ---
st.title("🍕 Pizza Sales Business Intelligence Report")
st.markdown("---")

# KPI Metrics Row
col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
col_m1.metric("Total Revenue", f"${total_revenue:,.0f}")
col_m2.metric("Pizzas Sold", f"{total_pizza_sold:,}")
col_m3.metric("Total Orders", f"{total_orders:,}")
col_m4.metric("Avg Order Value", f"${avg_order_value:,.2f}")
col_m5.metric("Average Pizza Per Order", f"{avg_pizza_per_order:,.2f}")



st.markdown("---")
# --- TOP SECTION ---

# Top 10 Most Popular Pizza Ingredients
# --- TOP SECTION: INGREDIENT ANALYSIS ---
st.header("Inventory and Ingredient Analysis")

# Professional 3-line explanation placed above the chart
st.markdown("""
This analysis identifies the core components of the menu to assist in high-level inventory forecasting. 
By visualizing ingredient frequency, we can isolate the most critical items for daily operations, 
where the <span style='color:#780909; font-weight:bold;'>volume of the bubbles</span> represents the scale of demand.
""", unsafe_allow_html=True)

# Data logic remains the same, but we use the result for the chart only
ingredient = (df['pizza_ingredients']
              .str.split(',')
              .explode()
              .str.strip()
              .value_counts()
              .reset_index())
ingredient.columns = ['Ingredient', 'Count']

# Creating the Bubble Chart with Top 30 ingredients to fill the space better
fig_ing = px.scatter(ingredient.head(30), 
                     x="Ingredient", 
                     y="Count",
                     size="Count", 
                     color="Count",
                     hover_name="Ingredient",
                     color_continuous_scale='YlOrRd_r', 
                     size_max=80) # Increased size_max for full-width impact

# Full-width styling
fig_ing.update_layout(
    xaxis_visible=False, 
    yaxis_visible=False,
    showlegend=False,
    height=450, # Fixed height to keep it clean
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=10, r=10, t=0, b=0)
)

# Displaying the chart across the full page width
st.plotly_chart(fig_ing, use_container_width=True, config={'displayModeBar': False})
st.divider()

# Statistical Analysis 
with st.expander("🔬 Deep Dive: Statistical Analysis"):
    # --- SECTION Metrics ---
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("CV: Coefficient of Variation", "26.38%")
        st.caption("Since **CV < 30%**, prices are consistent; most customers purchase similar items.")
    with col2:
        st.metric("Kurtosis", "8.90")
        st.caption("High Kurtosis (> 3.0) indicates a 'Leptokurtic' distribution—a clear gap between regular and bulk orders.")
    with col3:
        st.metric("Outlier Revenue Impact", "2.90%")
        st.caption("Outliers only account for **2.9%** of revenue; the business is stable and not 'whale-dependent'.")

    st.divider()

    # --- SECTION 2: Visualizations with Markdown ---
    tab1, tab2, tab3 = st.tabs(["📦 Outlier Detection", "📊 Distribution Shape", "🔗 Correlations"])

    with tab1:
        st.markdown("""
            The transactional data shows that the majority of orders are concentrated between 
            <span style='color:#780909; font-weight:bold;'>12 and 20</span>, establishing a highly stable 
            revenue base. Orders exceeding <span style='color:#780909; font-weight:bold;'>$32</span> are 
            identified as outliers, representing specialized bulk purchases that deviate from daily 
            consumer patterns.
            """, unsafe_allow_html=True)
        fig1, ax1 = plt.subplots(figsize=(9, 3.5)) # Reduced height
        sns.boxplot(x=df['total_price'], color="#C02626", flierprops={'markerfacecolor':"blue"}, ax=ax1)
        style_labels_and_title(ax1, x_label='Total Price', title='Outlier Detection for Pizza Order Totals', tsize=14)
        remove_spines(ax1); style_ticks(ax1)
        st.pyplot(fig1)
        

    with tab2:
        st.markdown("""
            The revenue distribution exhibits a <span style='color:#780909; font-weight:bold;'>Strong Right-Skew (1.73)</span>, 
            indicating that high-value transactions are inflating the overall average. While the 
            <span style='color:#780909; font-weight:bold;'>median price of $16</span> represents typical consumer behavior, 
            the mean is pulled significantly to the right by premium bulk orders.
            """, unsafe_allow_html=True)
        fig2, ax2 = plt.subplots(figsize=(9, 4))
        sns.kdeplot(df['total_price'], fill=True, color='#780909', ax=ax2)
        plt.axvline(df['total_price'].mean(), color='blue', linestyle='--', label='Mean')
        plt.axvline(df['total_price'].median(), color='green', linestyle='-', label='Median')
        style_labels_and_title(ax2, title=f"Price Distribution (Skewness: 1.73)", x_label='Total Price', y_label='Density', tsize=14)
        style_ticks(ax2)
        remove_spines(ax2)
        plt.legend()
        st.pyplot(fig2)
        

with tab3:
        # We use columns here to make the heatmap physically smaller on the screen
        map_col1, map_col2 = st.columns([1.5, 1]) 
        
        with map_col1:
            numerical_df = df.select_dtypes(include=['number']).drop(columns=['order_id', 'pizza_id'], errors='ignore')
            fig3, ax3 = plt.subplots(figsize=(5, 4)) # Small figsize
            sns.heatmap(numerical_df.corr(), annot=True, cmap='YlOrRd_r', center=0, linewidths=0.5, ax=ax3, cbar=False)
            ax3.tick_params(axis='y', pad=10)
            plt.yticks(rotation=45)
            plt.title('Correlation Heatmap', fontsize=12)
            style_ticks(ax3)
            st.pyplot(fig3)
        
        with map_col2:
            st.markdown("### Key Correlation")
            st.info("""
            **Unit Price (0.84)** has a much **stronger relationship** with the Total Price than **Quantity (0.54)** does. 
            
            This suggests that *what* people buy (premium vs standard) impacts your revenue more than *how many* items they buy.
            """)
# --- SECTION 1: WEEKLY TRENDS ---
st.header('Daily and Hourly Sales Trends 📈')

col1, col2 = st.columns(2)

with col1:
    # 1. Total Orders by Day
    st.markdown("""
        Weekly transaction volume identifies <span style='color:#780909; font-weight:bold;'>Friday</span> as the peak 
        operational day, followed closely by the Thursday and Saturday window. Demand reaches its 
        <span style='color:#780909; font-weight:bold;'>lowest point on Sundays and Mondays</span>, indicating a 
        strategic opportunity for targeted mid-week promotions to balance inventory flow.
        """, unsafe_allow_html=True)

    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df['day_name'] = pd.Categorical(df['day_name'], categories=weekday_order, ordered=True)
    orders_by_day = df.groupby('day_name', observed=False)['order_id'].nunique()
    fig, ax = plt.subplots()
    orders_by_day.plot(kind='bar', color=sns.color_palette("YlOrRd_r", len(orders_by_day)), ax=ax)
    style_labels_and_title(ax, x_label=' ', y_label='Number of Orders', ycolor='#d62828', ybold='bold', title='Total Orders by Day of Week', tbold='bold', tsize=11)
    style_ticks(ax); plt.xticks(rotation=45); remove_spines(ax)
    for i, val in enumerate(orders_by_day):
        ax.text(i, val+5, f'{val/total_orders * 100:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)

with col2:
    # 2. Weekly Revenue Breakdown
    st.markdown("""
        Revenue analysis confirms that <span style='color:#780909; font-weight:bold;'>Friday</span> contributes the 
        highest financial share to the weekly total. The data indicates a 
        <span style='color:#780909; font-weight:bold;'>stable revenue flow</span> through the weekend, suggesting 
        that operational capacity and premium offerings should be maximized during these high-traffic periods.
        """, unsafe_allow_html=True)

    price_by_day = df.groupby('day_name', observed=False)['total_price'].sum()
    fig, ax = plt.subplots()
    colors = sns.color_palette("YlOrRd", len(price_by_day))
    for i, (day, val) in enumerate(price_by_day.items()):
        ax.vlines(x=day, ymin=0, ymax=val, color=colors[i], alpha=0.6, linewidth=3)
    ax.scatter(price_by_day.index, price_by_day.values, s=120, color=colors, edgecolors='black', linewidth=1, zorder=3)
    for i, val in enumerate(price_by_day):
        ax.text(i, val + (price_by_day.max()*0.05), f'{val/total_revenue * 100:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold', color='#7b2c17')
    style_labels_and_title(ax, x_label=' ', y_label='Total Revenue ($)', ycolor='#d62828', ybold='bold', title='Total Revenue by Day of Weak', tsize=11, tbold='bold')
    style_ticks(ax); plt.xticks(rotation=45); remove_spines(ax)
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
st.markdown("---")

# --- 3. Weekly Pizza Volume (The Sales Wave) ---
col3, col4 = st.columns([1.2,1], gap='small')
with col3:
        st.markdown("""
            The sales volume demonstrates a clear <span style='color:#780909; font-weight:bold;'>27% surge</span> 
            in demand from the start of the week toward the Friday peak. While Friday requires 
            <span style='color:#780909; font-weight:bold;'>maximum operational capacity</span>, the dip observed 
            on Sunday represents a natural cooling period essential for inventory and staff reset.
    """, unsafe_allow_html=True)
        quantity_by_day = df.groupby('day_name', observed=False)['quantity'].sum()
        fig, ax = plt.subplots(figsize=(7,5)) 
        ax.plot(quantity_by_day.index, quantity_by_day.values, color="#780909", marker='o', linewidth=2, markersize=6, markerfacecolor='white', markeredgewidth=2)
        ax.fill_between(quantity_by_day.index, quantity_by_day.values, color='#fcbf49', alpha=0.3)
        for i, val in enumerate(quantity_by_day):
            ax.text(i, val + (max(quantity_by_day)*0.03), f'{int(val)}', ha='center', va='bottom', fontsize=9, fontweight='bold', color="#780909")
        style_labels_and_title(ax, x_label=' ', y_label='Total Pizzas Sold', ycolor='#780909', ybold='bold', title='Total Pizza Sales Volume by Day of Week', tsize=11, tbold='bold', tcolor='black')
        style_ticks(ax); remove_spines(ax); plt.xticks(rotation=45)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)

# SECTION 2: HOURLY ANALYSIS ---
with col4:
        st.markdown("""
            The hourly revenue pulse identifies a <span style='color:#780909; font-weight:bold;'>minimal activity window</span> 
            during early morning hours, followed by a significant surge during the lunch and dinner peaks. 
            Revenue is most heavily concentrated between <span style='color:#780909; font-weight:bold;'>12:00 PM – 1:00 PM</span> 
            and <span style='color:#780909; font-weight:bold;'>4:00 PM – 7:00 PM</span>, mapping the primary demand cycles.
    """, unsafe_allow_html=True)
        total_revenue_by_hour = df.groupby('order_hour', observed=False)['total_price'].sum()
        full_hours = pd.Series(0, index=range(24))
        hours = total_revenue_by_hour.index.tolist()
        values = total_revenue_by_hour.values.tolist()
        hours += [hours[0]]; values += [values[0]]
        angles = np.linspace(0, 2 * np.pi, len(hours), endpoint=True)
        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
        ax.plot(angles, values, color='#780909', linewidth=2)
        ax.fill(angles, values, color='#fcbf49', alpha=0.4)
        ax.set_theta_offset(np.pi / 2); ax.set_theta_direction(-1)
        ax.set_xticks(angles[:-1]); ax.set_xticklabels([f"{h}:00" for h in hours[:-1]], fontsize=9); ax.set_yticklabels([])
        ax.spines['polar'].set_visible(False)
        plt.title('Hourly Revenue Pulse', size=9, color="#780909", weight='bold', pad=30)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
st.markdown("---")

# 4. Total Orders by Hour
coll,colm,colr = st.columns([1,10,1])
with colm:
    st.markdown("""
        The hourly distribution identifies a clear <span style='color:#780909; font-weight:bold;'>bimodal demand pattern</span>, 
        with volume peaks concentrated during traditional lunch and dinner windows. A mid-afternoon 
        <span style='color:#780909; font-weight:bold;'>operational lull</span> occurs between 2:00 PM and 3:00 PM, 
        offering a strategic window for staff transitions before the evening surge.
        """, unsafe_allow_html=True)

    fig, ax = plt.subplots()
    orders_by_hour = df.groupby('order_hour', observed=False)['order_id'].nunique()
    ax = orders_by_hour.plot(kind='bar', color=sns.color_palette('YlOrRd_r', len(orders_by_hour)), figsize=(10,5))
    style_labels_and_title(ax, x_label='Order Hour (24-Hour Format)', xcolor="#000000FF", y_label='Number Of Orders', ycolor="#000000FF", title='Total Orders by Hour of Day', tcolor="#060606ff", tbold='bold', tsize=11)
    remove_spines(ax); style_ticks(ax); plt.xticks(rotation=0)
    for i, val in enumerate(orders_by_hour):
        plt.text(i, val + 6, str(val), ha='center', va='bottom', fontweight='bold', color='black')
    st.pyplot(fig)
st.markdown("---")


# 6. Hourly Quantity Distribution (Bubble)
st.markdown("""
This visualization illustrates the <span style='color:#780909; font-weight:bold;'>intensity of product volume</span> 
throughout the day. The scaling of the indicators clearly isolates the 
<span style='color:#780909; font-weight:bold;'>12:00 PM – 1:00 PM lunch surge</span> as the period of 
maximum throughput, requiring optimized kitchen performance.
""", unsafe_allow_html=True)
quantity_by_hour = df.groupby('order_hour', observed=False)['quantity'].sum()
fig, ax = plt.subplots(figsize=(16, 4))
ax.scatter(quantity_by_hour.index, [1]*len(quantity_by_hour.index), s=quantity_by_hour.values*0.7, c=quantity_by_hour.values, cmap='YlOrRd', alpha=0.9, edgecolors='black', linewidth=1.5)
for hour, val in quantity_by_hour.items():
    ax.text(hour, 1.1, f'{int(val)}', ha='center', va='bottom', fontsize=10, fontweight='bold', color='#7b2c17')
style_labels_and_title(ax, x_label='Hour of Day', xcolor="#FF0000FF", xbold='bold', title='Hourly Quantity Distribution', tsize=13, tbold='bold')
ax.get_yaxis().set_visible(False); remove_spines(ax); style_ticks(ax); ax.set_xticks(quantity_by_hour.index); ax.set_ylim(0.7, 1.3)
st.pyplot(fig)
st.markdown("---")


# --- SECTION 3: PRODUCT MIX & CATEGORIES ---
st.header("🍕 Category & Product Insights")
col5, col6 = st.columns([0.8,1], gap='small')

with col5:
        st.markdown("""
            The revenue contribution across pizza categories demonstrates a <span style='color:#780909; font-weight:bold;'>balanced market share</span>. 
            With no single category dominating the mix, the business maintains a 
            <span style='color:#780909; font-weight:bold;'>low-risk portfolio</span>, ensuring that demand is 
            distributed evenly across different customer preferences.
          """, unsafe_allow_html=True)
        # 7. Percentage of Sales by Category (Pie)
        category_sales = df.groupby('pizza_category')['total_price'].sum()
        category_pct = category_sales / category_sales.sum()*100
        fig, ax = plt.subplots()
        ax.pie(category_pct, labels=category_pct.index, autopct='%1.1f%%', colors=plt.get_cmap('tab20').colors, startangle=90, wedgeprops={'edgecolor': 'black', 'width':0.4}, radius=0.8)
        plt.title('Percentage of Sales by Pizza Category', fontweight='bold', fontsize=10)
        st.pyplot(fig, use_container_width=False)

with col6:
    st.markdown("""
        The cross-sectional analysis reveals that <span style='color:#780909; font-weight:bold;'>Large-sized pizzas</span> 
        across all categories serve as the primary revenue drivers. Conversely, the 
        <span style='color:#780909; font-weight:bold;'>XL and XXL variants</span> show negligible market 
        penetration, suggesting an opportunity to streamline the menu and reduce specialized inventory costs.
        """, unsafe_allow_html=True)
    # 8. Sales by Category and Size (Heatmap)
    sales_pivot = df.pivot_table(index='pizza_category', columns='pizza_size', values='total_price', aggfunc='sum', fill_value=0)
    sales_pct = sales_pivot / sales_pivot.sum().sum()*100
    fig, ax = plt.subplots()
    sns.heatmap(sales_pct, annot=True, fmt='.1f', cmap='YlOrRd', linewidths=0.5, ax=ax)
    style_labels_and_title(ax, x_label='Pizza Size', xbold='bold', y_label='Pizza Category', ybold='bold', title='% of Sales by Pizza Category and Size', tbold='bold', tsize=11)
    fig.tight_layout()
    st.pyplot(fig)

st.markdown("---")

st.markdown("""
The volume hierarchy identifies <span style='color:#780909; font-weight:bold;'>Classic Pizzas</span> 
as the cornerstone of the menu. This dominance suggests that expanding the 
<span style='color:#780909; font-weight:bold;'>Classic product line</span> offers the 
lowest-risk path for increasing overall transactional volume.
""", unsafe_allow_html=True)

coll, colm, colr = st.columns([1, 6, 1]) 
with colm:
    pizza_by_category = (df.groupby('pizza_category')['quantity']
                         .sum()
                         .reset_index()
                         .sort_values(by='quantity', ascending=False))
    # Using color_discrete_sequence to avoid the TypeError
    fig_funnel = px.funnel(pizza_by_category, 
                           y='pizza_category', 
                           x='quantity',
                           color='pizza_category',
                           color_discrete_sequence=px.colors.sequential.YlOrRd_r)
    fig_funnel.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=30, b=20),
        height=400,
        yaxis_title=None,
        showlegend=False
    )
    fig_funnel.update_traces(textinfo="value+percent initial", textfont_size=12)
    st.plotly_chart(fig_funnel, use_container_width=True, config={'displayModeBar': False})
st.divider()

# --- SECTION 5: SEASONAL HEATMAP ---
st.header("🌡️ Seasonal Intensity")

st.markdown("""
The seasonal heatmap identifies a significant <span style='color:#780909; font-weight:bold;'>mid-year peak in July</span>, 
suggesting a strong correlation between summer holiday periods and increased order volume. 
This seasonal trend allows for more precise <span style='color:#780909; font-weight:bold;'>long-term labor 
and procurement planning</span> to ensure quality during high-demand months.
""", unsafe_allow_html=True)
month_order = list(calendar.month_name)[1:]
df['month_name'] = pd.Categorical(df['month_name'], categories=month_order, ordered=True)
orders_by_month = df.groupby('month_name', observed=False)['order_id'].nunique().reset_index()
fig, ax = plt.subplots(figsize=(12, 3))
heatmap_data = np.expand_dims(orders_by_month['order_id'].values, axis=0)
im = ax.imshow(heatmap_data, cmap='YlOrRd')
ax.set_xticks(np.arange(len(month_order))); ax.set_xticklabels(month_order, fontsize=10); ax.set_yticks([])
for i, val in enumerate(orders_by_month['order_id']):
    ax.text(i, 0, val, ha='center', va='center', fontsize=10, weight='bold')
ax.set_title("Monthly Orders Heat Intensity", fontsize=11, weight='bold', pad=20)
plt.colorbar(im, orientation='horizontal', pad=0.3, label='Number of Orders')
st.pyplot(fig)

st.markdown("---")

# --- SECTION 4: PRODUCT PERFORMANCE MATRIX ---
st.header("🏆 The Champions: Product Power Matrix")

# Strategic overview above the columns
st.markdown("""
This matrix categorizes the top-performing products across three critical business metrics. 
By comparing <span style='color:#780909; font-weight:bold;'>Revenue vs. Quantity</span>, we can 
identify high-margin premium items and high-frequency volume drivers, ensuring a balanced 
inventory and marketing strategy.
""", unsafe_allow_html=True)

col7, col8, col9 = st.columns(3, gap='small')

with col7:
    # 10. Top 5 by Revenue
    p_rev = df.groupby('pizza_name')['total_price'].sum().reset_index()
    top5_rev = p_rev.sort_values(by='total_price', ascending=False).head(5)
    fig_rev = px.treemap(top5_rev, path=['pizza_name'], values='total_price', 
                         color='total_price', color_continuous_scale='YlOrRd')
    fig_rev.update_layout(template='plotly_dark', title="💰 Revenue Leaders", 
                          margin=dict(t=50, l=10, r=10, b=10))
    fig_rev.update_traces(texttemplate="<b>%{label}</b><br>$%{value:,.0f}")
    st.plotly_chart(fig_rev, use_container_width=True, config={'displayModeBar': False})

with col8:
    # 11. Top 5 by Quantity
    p_qty = df.groupby('pizza_name')['quantity'].sum().reset_index()
    top5_qty = p_qty.sort_values(by='quantity', ascending=False).head(5)
    fig_qty = px.treemap(top5_qty, path=['pizza_name'], values='quantity', 
                         color='quantity', color_continuous_scale='YlOrRd')
    fig_qty.update_layout(template='plotly_dark', title="📦 Volume Leaders", 
                          margin=dict(t=50, l=10, r=10, b=10))
    st.plotly_chart(fig_qty, use_container_width=True, config={'displayModeBar': False})

with col9:
    # 12. Top 5 by Order Count
    p_ord = df.groupby('pizza_name')['order_id'].nunique().reset_index()
    top5_ord = p_ord.sort_values(by='order_id', ascending=False).head(5)
    fig_ord = px.treemap(top5_ord, path=['pizza_name'], values='order_id', 
                         color='order_id', color_continuous_scale='YlOrRd')
    fig_ord.update_layout(template='plotly_dark', title="🔝 Demand Frequency", 
                          margin=dict(t=50, l=10, r=10, b=10))
    st.plotly_chart(fig_ord, use_container_width=True, config={'displayModeBar': False})

st.divider()

st.markdown(
    """
    <div style="text-align: center; padding: 50px;">
        <h1 style="font-family: 'serif'; font-size: 80px; font-weight: bold; letter-spacing: 10px; color: #780909;">
            THE END
        </h1>
        <p style="color: gray; letter-spacing: 2px; font-size: 18px;">Executive Pizza Sales Performance Analysis</p>
    </div>
    """, 
    unsafe_allow_html=True
)

st.balloons()