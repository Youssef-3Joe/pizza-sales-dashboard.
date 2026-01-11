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

# --- SECTION 1: WEEKLY TRENDS ---
st.header('Daily and Hourly Sales Trends 📈')

col1, col2 = st.columns(2)

with col1:
    # 1. Total Orders by Day
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
    st.markdown("**Friday** is our **'Golden Day'** with the highest number of orders, followed closely by **Thursday** and **Saturday**. Orders hit the lowest point on **Sundays** and **Mondays**, which is a great time to run some 'Mid-week Offers' to boost sales!")

with col2:
    # 2. Weekly Revenue Breakdown
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
    st.markdown("**Friday** is our **'Money Maker'** with the highest revenue, while we see a steady flow through the **weekend—Time** to capitalize on those high-traffic days!")

# --- 3. Weekly Pizza Volume (The Sales Wave) ---
col3, col4 = st.columns([1.2,1], gap='small')
with col3:
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
        st.markdown("Friday takes the lead as our ultimate peak, pushing out a record 8,242 pizzas that keep our ovens running at maximum capacity to satisfy the weekend rush. This momentum builds steadily throughout the week, showing a significant 27% surge in volume from the Monday start to the Friday high. While the weekends sizzle, Sunday marks a natural 'cool down' period with volume dipping to 6,035 pizzas, allowing the team to reset before the cycle begins again.")# --- SECTION 2: HOURLY ANALYSIS ---


with col4:
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
        st.markdown("We hit a **'Dead Zone'** between **9-11 AM** with zero revenue, before surging into peak performance during the **12-1 PM** and **4-7 PM** power hours!")

# 4. Total Orders by Hour
coll,colm,colr = st.columns([1,10,1])
with colm:
    fig, ax = plt.subplots()
    orders_by_hour = df.groupby('order_hour', observed=False)['order_id'].nunique()
    ax = orders_by_hour.plot(kind='bar', color=sns.color_palette('YlOrRd_r', len(orders_by_hour)), figsize=(10,5))
    style_labels_and_title(ax, x_label='Order Hour (24-Hour Format)', xcolor="#000000FF", y_label='Number Of Orders', ycolor="#000000FF", title='Total Orders by Hour of Day', tcolor="#060606ff", tbold='bold', tsize=11)
    remove_spines(ax); style_ticks(ax); plt.xticks(rotation=0)
    for i, val in enumerate(orders_by_hour):
        plt.text(i, val + 6, str(val), ha='center', va='bottom', fontweight='bold', color='black')
    st.pyplot(fig)
    st.markdown("From **11 to 1 afternoon**, the pizza order is high, and it goes down at **2 to 3 in the evening**, and rise up again from **4 till 6**, and then goes down again.")


# 6. Hourly Quantity Distribution (Bubble)
quantity_by_hour = df.groupby('order_hour', observed=False)['quantity'].sum()
fig, ax = plt.subplots(figsize=(16, 4))
ax.scatter(quantity_by_hour.index, [1]*len(quantity_by_hour.index), s=quantity_by_hour.values*0.7, c=quantity_by_hour.values, cmap='YlOrRd', alpha=0.9, edgecolors='black', linewidth=1.5)
for hour, val in quantity_by_hour.items():
    ax.text(hour, 1.1, f'{int(val)}', ha='center', va='bottom', fontsize=10, fontweight='bold', color='#7b2c17')
style_labels_and_title(ax, x_label='Hour of Day', xcolor="#FF0000FF", xbold='bold', title='Hourly Quantity Distribution', tsize=13, tbold='bold')
ax.get_yaxis().set_visible(False); remove_spines(ax); style_ticks(ax); ax.set_xticks(quantity_by_hour.index); ax.set_ylim(0.7, 1.3)
st.pyplot(fig)
st.markdown("This is clearly highlighting the **12:00 PM - 1:00 PM** rush.")
st.markdown("---")

#############################################################################################
#############################################################################################
#############################################################################################

# --- SECTION 3: PRODUCT MIX & CATEGORIES ---
st.header("🍕 Category & Product Insights")
col5, col6 = st.columns([0.8,1], gap='small')

with col5:
        # 7. Percentage of Sales by Category (Pie)
        category_sales = df.groupby('pizza_category')['total_price'].sum()
        category_pct = category_sales / category_sales.sum()*100
        fig, ax = plt.subplots()
        ax.pie(category_pct, labels=category_pct.index, autopct='%1.1f%%', colors=plt.get_cmap('tab20').colors, startangle=90, wedgeprops={'edgecolor': 'black', 'width':0.4}, radius=0.8)
        plt.title('Percentage of Sales by Pizza Category', fontweight='bold', fontsize=10)
        st.pyplot(fig, use_container_width=False)
        st.markdown("The percentages of sales by pizza categories are closed, there is **no big difference**.")

with col6:
    # 8. Sales by Category and Size (Heatmap)
    sales_pivot = df.pivot_table(index='pizza_category', columns='pizza_size', values='total_price', aggfunc='sum', fill_value=0)
    sales_pct = sales_pivot / sales_pivot.sum().sum()*100
    fig, ax = plt.subplots()
    sns.heatmap(sales_pct, annot=True, fmt='.1f', cmap='YlOrRd', linewidths=0.5, ax=ax)
    style_labels_and_title(ax, x_label='Pizza Size', xbold='bold', y_label='Pizza Category', ybold='bold', title='% of Sales by Pizza Category and Size', tbold='bold', tsize=11)
    fig.tight_layout()
    st.pyplot(fig)
    st.markdown("**Veggie** with L size and **Chicken** with L size and in general in L size, all the pizzas are sold at higher level, and the second highest will be all the pizza categories with medium size, **but XL and XXL pizzas** those are very least sold and sometimes they are not sold at all.")


# 9. Total Pizza Sold by Category (Barh)
coll,colm,colr = st.columns([1,2,1])
with colm:
    pizza_by_category = df.groupby('pizza_category')['quantity'].sum()
    fig, ax = plt.subplots()
    pizza_by_category.plot(kind='barh', color=list(plt.get_cmap('tab20').colors[:len(pizza_by_category)]), edgecolor='black', ax=ax)
    style_labels_and_title(ax, x_label='Total Pizza Sold', xbold='bold', y_label='Pizza Category', ybold='bold', title='Total Pizza Sold by Pizza Category', tbold='bold', tsize=11)
    remove_spines(ax); style_ticks(ax)
    for i, val in enumerate(pizza_by_category):
        ax.text(val+1000, i, str(val), ha='center', va='bottom', fontweight='bold')
    st.pyplot(fig)
    st.markdown("We can see that **Classic pizzas** are the most pizzas getting sold, so we have to create more of it.")

# --- SECTION 5: SEASONAL HEATMAP ---
st.header("🌡️ Seasonal Intensity")
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
st.markdown("A lot of people order on **July**.")

st.markdown("---")
# --- SECTION 4: THE TOP LEADERS (TREEMAPS) ---
st.header("🏆 The Champions: Top 5 Pizzas")
col7, col8, col9 = st.columns(3, gap='small')

with col7:
    # 10. Top 5 by Revenue
    p_rev = df.groupby('pizza_name')['total_price'].sum().reset_index()
    top5_rev = p_rev.sort_values(by='total_price', ascending=False).head(5)
    fig_rev = px.treemap(top5_rev, path=['pizza_name'], values='total_price', color='total_price', color_continuous_scale='Cividis')
    fig_rev.update_layout(template='plotly_dark', title="💰 Top 5 by Revenue", margin=dict(t=50, l=10, r=10, b=10))
    fig_rev.update_traces(texttemplate="<b>%{label}</b><br>$%{value:,.0f}")
    st.plotly_chart(fig_rev, use_container_width=True, config={'displayModeBar': False})

with col8:
    # 11. Top 5 by Quantity
    p_qty = df.groupby('pizza_name')['quantity'].sum().reset_index()
    top5_qty = p_qty.sort_values(by='quantity', ascending=False).head(5)
    fig_qty = px.treemap(top5_qty, path=['pizza_name'], values='quantity', color='quantity', color_continuous_scale='Sunsetdark')
    fig_qty.update_layout(template='plotly_dark', title="🏆 Top 5 by Quantity Sold", margin=dict(t=50, l=10, r=10, b=10))
    st.plotly_chart(fig_qty, use_container_width=True, config={'displayModeBar': False})

with col9:
    # 12. Top 5 by Order Count
    p_ord = df.groupby('pizza_name')['order_id'].nunique().reset_index()
    top5_ord = p_ord.sort_values(by='order_id', ascending=False).head(5)
    fig_ord = px.treemap(top5_ord, path=['pizza_name'], values='order_id', color='order_id', color_continuous_scale='Aggrnyl')
    fig_ord.update_layout(template='plotly_dark', title="🔝 Top 5 by Order Count", margin=dict(t=50, l=10, r=10, b=10))
    st.plotly_chart(fig_ord, use_container_width=True, config={'displayModeBar': False})
