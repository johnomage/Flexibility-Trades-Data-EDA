# import packages

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import locale
from preprocessor import preprocess_and_engineer_features


# ++++++++++++++++++++++++++++++++++++++++++ Configure page and Properties +++++++++++++++++++++++++++++++++++++++++
st.set_page_config(
    page_title="📊Flexibility Trades Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "mailto:john.e.omage@gmail.com",
        "Report a bug": "mailto:john.e.omage@gmail.com",
        "About": "# Want to reach out?!",
    },
)


# set page title
st.title(":bulb: UK Flexibility Trades Data Visualisation: 2024 - 2029")


# ++++++++++++++++++++++++++++++++++++++++++ cache data for quick loading ++++++++++++++++++++++++++++++++++++++++
@st.cache_data
def load_data():
    return pd.read_csv("datastore/trade_results.csv")

# load data
data = preprocess_and_engineer_features(load_data())

# ++++++++++++++++++++++++++++++++++++++++ Sidebars +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# sidebar for company filter
def create_sidebar(label, feature, placeholder):
    return st.sidebar.multiselect(
                                label=label,
                                options=data[feature].unique(),
                                default=data[feature].unique(),
                                placeholder=placeholder)

st.sidebar.header("Global Filters")

company_name_sidebar = create_sidebar("Select Flexibility Service Provider(s)", "Company Name", "choose company name")

# create sidebar for tech type filter
technology_type_sidebar = create_sidebar("Select Technology type(s)", "Technology Type", "choose tech type")

# create sidebar for trade outcome filter
trade_outcome_sidebar = create_sidebar("Select Trade Outcome(s)", "Trade Outcome", "choose trade outcome")

trade_restore_avail = create_sidebar('Select Restore Availability', 'Available for Restore', 'can restore?')

# data on sidebar filters to update display on main page
selected_data = data[(data["Company Name"].isin(company_name_sidebar)
                        & data["Technology Type"].isin(technology_type_sidebar)
                        & data["Trade Outcome"].isin(trade_outcome_sidebar)
                        & data["Available for Restore"].isin(trade_restore_avail))]

"---"  # Add line separator

# +++++++++++++++++++++++++++++++++++++++++++++++++++ Metrics Container ++++++++++++++++++++++++++++++++++++++++++

# Function to format Capacity as KW or MW
def format_KW_MW(capacity: float, feature):
    """
    Format and display capacity in KW or MW using based on capacity's value.

    Converts the input value to MW if it's 1000 or greater,
    otherwise displays it in KW. Uses Streamlit to render
    the formatted capacity with HTML styling.

    Args:
        value (float): Capacity value in KW
        feature (string): Name of capacity feature to convert
    """
    cap_value = capacity / 1000
    if cap_value < 1:  # Display in KW
        st.markdown(f"<b>{feature}</b><h3>{capacity:.2f}KW</h3>", unsafe_allow_html=True,)
    else:  # Display in MW
        st.markdown(f"<b>{feature}</b><h3>{cap_value:.4f}MW</h3>", unsafe_allow_html=True)


# get local region currency symbol
locale.setlocale(locale.LC_ALL, '')
# Function to format price in GBP with thousand separator
def format_as_currency(price: float, feature: str):
    try:
        price_value = locale.currency(price, grouping=True)
        st.markdown(f"<b>{feature}</b><h3>{price_value}</h3>", unsafe_allow_html=True)
    except ValueError:
        st.markdown(f"<b>{feature}</b><h3>£{price:,.2f}</h3>", unsafe_allow_html=True)


st.markdown("<h5 style='text-align: center;'>💷Total Price Metrics💷</h5>", unsafe_allow_html=True)
# create metrics with columns and populate
total_records_col, awarded_util_price_col, awarded_avail_col,  restore_price_col, offered_price_col = st.columns(5)

# total records
total_records = selected_data.shape[0]

# ##################### add metrics to dashboard
with total_records_col:
    st.markdown(f"<b>Trade Records<h3>{total_records}</b></h3>", unsafe_allow_html=True)

with awarded_util_price_col:
    # Format the price with the GBP symbol using locale settings
    format_as_currency(selected_data["Awarded Utilisation Price"].sum(), 'Awarded Utilisation Price')

with awarded_avail_col:
    format_as_currency(selected_data['Awarded Availability Price'].sum(), "Total Awarded Availability")

with restore_price_col:
    format_as_currency(selected_data['Restore Price'].sum(), 'Total Restore Price')

with offered_price_col:
    format_as_currency(selected_data['Offered Availability Price'].sum(), 'Total Offered Availability')

st.write('\n')

# ###################################### Add metrics for capacity
st.markdown("<h5 style='text-align: center;'>⚡Total Capacity Metrics⚡</h5>", unsafe_allow_html=True)

total_ass_cap_col, tendered_cap_col, offered_cap_col, awarded_cap_col = st.columns(4)

with total_ass_cap_col:
    format_KW_MW(selected_data['Total Asset Installed Capacity'].sum(), 'Total Asset Installed Capacity')

with tendered_cap_col:
    format_KW_MW(selected_data['Tendered Capacity [kW]'].sum(), 'Total Tendered Capacity')

with offered_cap_col:
    format_KW_MW(selected_data['Offered Capacity [kW]'].sum(), 'Total Offered Capacity')

with awarded_cap_col:
    format_KW_MW(selected_data['Accepted Capacity [kW]'].sum(), 'Total Accepted Capacity')



st.write("---")

# +++++++++++++++++++++++++++++++++++++++++++ Charts Container ++++++++++++++++++++++++++++++++++++++++++++++++++++

# barcharts on capacity
def plug_in_barchart(feature, title, grouping="Company Name"):
    grouped = selected_data.groupby(grouping)[feature].sum().sort_values()
    custom_cmap = ["#2a52be", "#33FF57", "#3357FF", "#F0E68C", "#E9967A", "#8A2BE2", "#FF1493"]
    grouped_fig = px.bar(
        data_frame=grouped,
        x=feature,
        y=grouped.index,
        orientation="h",
        title=title,
        # color=grouped,
        template="plotly_white",
        color_discrete_sequence=custom_cmap,
    )
    grouped_fig.update_layout(plot_bgcolor="rgba(0,0,0,0.3)", xaxis=dict(showgrid=True))
    st.plotly_chart(grouped_fig, use_container_width=True)


inst_cap_barchart_col, accp_cap_barchart_col, tech_cap_barchart_col = st.columns(3)

# Horizontal Bar Chart - companies installed total asset capacity
with inst_cap_barchart_col:
    plug_in_barchart(
        "Total Asset Installed Capacity",
        "<b>Total Asset Installed Capacity of FSPs [KW]</b>",
    )

with accp_cap_barchart_col:
    plug_in_barchart(
        "Accepted Capacity [kW]", "<b>Total Accepted Capacity by FSPs [KW]</b>"
    )

with tech_cap_barchart_col:
    plug_in_barchart(
        "Accepted Capacity [kW]",
        "<b>Total Accepted Capacity by Tech Type [KW]</b>",
        "Technology Type",
    )


# Create barchart for FSP Service Availability by Day of Week
# barchart for FSP service availablity days
# group by 'Company Name' and sum service counts for each day of the week
"---"
title_format = {"x": 0.5, "xanchor": "center", "yanchor": "top"}  # Center the title
service_days_count = (
    selected_data.groupby("Company Name")[["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]]
                        .sum()
                        .reset_index()
)

# Convert the dataframe to long format with pd.melt()
service_days_long = pd.melt(
                            service_days_count,
                            id_vars=["Company Name"],
                            value_vars=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                            var_name="Day of Week",
                            value_name="Service Count",
                        )

service_days_fig = px.bar(service_days_long,
                          x="Company Name",
                          y="Service Count",
                          color="Day of Week",
                          title="FSP Service Availability by Day of Week",
                          labels={"Service Count": "Count", "Company Name": "Company Name"},
                          barmode="stack").update_layout(title=title_format)
st.plotly_chart(service_days_fig, use_container_width=True)


company_tech_util_price = selected_data.groupby(
    ["Company Name", "Technology Type"], as_index=False
)["Awarded Utilisation Price"].agg("sum")

# Create the grouped bar plot using Plotly Express
company_tech_util_price_fig = px.bar(
                         company_tech_util_price,
                                    x="Company Name",
                                    y="Awarded Utilisation Price",
                                    color="Technology Type",  # Different colors for each Technology Type
                                    barmode="stack",  # stacked bars
                                    title="Total Awarded Utilisation Price by Company and Technology Type (£)",
                                ).update_layout(title=title_format)
st.plotly_chart(company_tech_util_price_fig)


# +++++++++++++++++++++++++++ linecharts for Utilisation Price and Start dates and times +++++++++++++++++++++++++++++++++++++++

# Group by 'Delivery Start Date' and 'Company Name', calculate median utilisation price
company_delivery_date = (
    selected_data.groupby(["Delivery Start Date", "Company Name", "Delivery Period", "Accepted Capacity [kW]"])["Offered Utilisation Price"]
                .min()
                .reset_index())

# Group by 'Delivery Start Time' and 'Company Name', calculate median utilisation price
company_delivery_time = (selected_data.groupby(["Delivery Start Time", "Company Name", "Accepted Capacity [kW]"])["Offered Utilisation Price"]
    .min()
    .reset_index()
)

# Get unique companies
companies = company_delivery_date["Company Name"].unique()

# Create subplots with two rows (one for date, one for time)
fig_utilPr_dt_tm = make_subplots(rows=2, cols=1,
                                 subplot_titles=("Offered Utilisation Price by Delivery Start Date",
                                                "Offered Utilisation Price by Delivery Start Time",),
                                 shared_yaxes=True,
                            )

# Add traces for each company for the Delivery Start Date subplot (row 1)
for company in companies:
    company_data = company_delivery_date[company_delivery_date["Company Name"] == company]
    fig_utilPr_dt_tm.add_trace(
                          go.Scatter(
                                x=company_data["Delivery Start Date"],
                                y=company_data["Offered Utilisation Price"],
                                name=company,  # Single name for the legend
                                mode="lines+markers",
                                # Hover template with Date, Accepted Capacity, Delivery Period, and Offered Utilisation Price
                                hovertemplate="<b>Accepted Capacity:</b> %{customdata[0]:.2f} kW<br>"
                                              + "<b>Delivery Period (days):</b> %{customdata[1]}<br>"
                                              + "<b>Minimum Price:</b> £%{y:.2f}<extra></extra>",
                                customdata=company_data[["Accepted Capacity [kW]", "Delivery Period"]].values,  # Passing both Accepted Capacity and Delivery Period
                            ),
                            row=1, col=1)
# Add traces for each company for the Delivery Start Time subplot (row 2)
for company in companies:
    company_data = company_delivery_time[company_delivery_time["Company Name"] == company]
    fig_utilPr_dt_tm.add_trace(
                        go.Scatter(
                                        x=company_data["Delivery Start Time"],
                                        y=company_data["Offered Utilisation Price"],
                                        name=company,  # Same name, but no duplicate in the legend
                                        mode="lines+markers",
                                        hovertemplate="<b>FSP:</b> %{customdata[0]}<br>"
                                                        + "<b>Offered Utilisation Price:</b> £%{y:.2f}<br>"
                                                        + "<b>Accepted Capacity:</b> %{customdata[1]:.2f} kW<br>"
                                                        + "<b>Minimum Price:</b> £%{y:.2f}<extra></extra>",
                                        customdata=company_data[["Company Name", "Accepted Capacity [kW]"]].values,  # Passing both Accepted Capacity and Delivery Period
                                        showlegend=False,  # Avoid duplicate legends
                                    ),
                             row=2, col=1)
# Update layout for the entire figure
fig_utilPr_dt_tm.update_layout(title=str.format("Minimum Offered Utilisation Price Over Delivery Date and Time by Company", title_format),
                               hovermode="x unified",
                               legend_title="Company Name")
# Add x-axis titles for both subplots
fig_utilPr_dt_tm.update_xaxes(title_text="Delivery Start Date", row=1, col=1)
fig_utilPr_dt_tm.update_xaxes(title_text="Delivery Start Time", row=2, col=1)
# Add y-axis title (shared across subplots)
fig_utilPr_dt_tm.update_yaxes(title_text="Offered Utilisation Price", row=1, col=1)

st.plotly_chart(fig_utilPr_dt_tm, use_container_width=True)


# ++++++++++++++++++++++++++++++++++++++++ Other Stuffs +++++++++++++++++++++++++++++++++++++++++++++++++++
cap_flex_bar_col, flex_pie_col = st.columns(2)

with cap_flex_bar_col:
    flex_capacity = selected_data.groupby(['Company Name', 'Flexibility Product'])['Accepted Capacity [kW]'].sum().reset_index()
    cap_flex_bar_fig = px.bar(flex_capacity, 
                            x='Company Name', 
                            y='Accepted Capacity [kW]', 
                            color='Flexibility Product', 
                            barmode='stack',
                            title='Accepted Capacity by Company and Flexibility Product')
    st.plotly_chart(cap_flex_bar_fig)

with flex_pie_col:
    flex = selected_data.groupby('Flexibility Product').agg(
                        Awarded_Availability_Price=('Awarded Availability Price', 'sum'),
                        # Total_Tendered_Capacity=('Tendered Capacity [kW]', 'sum'),  # Sum of capacities
                        Company_Names=('Company Name', lambda x: ', '.join(x.unique())),  # Concatenate company names
                        Total_Accepted_Capacity=('Accepted Capacity [kW]', 'sum')  # Total capacity per product
                        ).reset_index()

    # Create a doughnut chart
    flex_fig = px.pie(flex,
                                 names='Flexibility Product',
                                 values='Total_Accepted_Capacity',
                                 hole=0.4,  # This creates the doughnut effect
                                 hover_data={'Flexibility Product': True,
                                             'Total_Accepted_Capacity': True,
                                             'Awarded_Availability_Price': True,
                                             'Company_Names': True},
                                 title='Distribution of Flexibility Products by Total Accepted Capacity'
                            )

    # Update hover template to include the company names and total capacity
    flex_fig.update_traces(hovertemplate="<b>Flexibility Product:</b> %{label}<br>" +
                          "<b>Total Accepted Capacity:</b> %{value} kW<br>" +
                          "<b>Awarded Availability Price:</b> £%{value:,.2f}<br>" +
                        #   "<b>Total Asset Installed Capacity:</b> %{value} kW<br>" +
                          "<b>Companies:</b> %{customdata[0]}<extra></extra>",
                          customdata=flex[['Company_Names']].values)  # Pass company names to customdata
    st.plotly_chart(flex_fig)



"---"
st.write(f'Trade Data Table showing {selected_data.shape[0]} records')
st.dataframe(selected_data)
# st.write(data.columns.sort_values())


# if not available
if selected_data.empty:
    st.warning("Selection not found ⚠️")
    st.stop()
