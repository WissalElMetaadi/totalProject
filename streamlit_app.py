import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import io
import altair as alt
import tempfile
import os
from PyPDF2 import PdfReader, PdfWriter

import matplotlib.pyplot as plt

plt.rcParams.update({
    'axes.titlesize': 7,
    'axes.labelsize': 7,
    'xtick.labelsize': 6,
    'ytick.labelsize': 6,
    'legend.fontsize': 6,
    'font.size': 7
})


# Configure the application's theme
st.set_page_config(page_title='Interactive Data Dashboard', layout='wide')

# Load the Excel file
file_path = './DATA.xlsx'
data = pd.read_excel(file_path)

# Convert date columns to datetime
data['date d\'entrée'] = pd.to_datetime(data['date d\'entrée'])
data['date de sortie'] = pd.to_datetime(data['date de sortie'])

# Apply CSS styles for better presentation
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
        padding: 20px;
    }
    .header {
        text-align: center;
        padding: 20px;
        background-color: #007bff;
        color: white;
        margin-bottom: 20px;
        border-radius: 8px;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f1f1f1;
        color: black;
        text-align: center;
        padding: 10px;
    }
    .section {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Display the application's title
st.markdown('<div class="header"><h1>Interactive Data Dashboard</h1></div>', unsafe_allow_html=True)

# Organize filters, the filtered table, charts, and statistics on the same page
st.markdown('<div class="section">', unsafe_allow_html=True)

st.header('Filters')

# Use columns for filters
col1, col2, col3 = st.columns([2, 2, 2])

with col1:
    classes = st.multiselect('Vehicle Class', options=data['class'].unique(), default=data['class'].unique())

with col2:
    zones = st.multiselect('Zone', options=data['ZoneTotal'].unique(), default=data['ZoneTotal'].unique())

with col3:
    filter_option = st.text_input('Filter by Keyword', '')

# Date filters
date_filter_type = st.radio("Type of Date Filter", ('Day', 'Week'))

if date_filter_type == 'Day':
    date_selected = st.date_input("Select Date", value=pd.to_datetime("2024-04-01"))
    filtered_data = data[data['date d\'entrée'].dt.date == date_selected]
else:
    start_date = st.date_input("Start Date", value=pd.to_datetime("2024-04-01"))
    end_date = st.date_input("End Date", value=pd.to_datetime("2024-04-07"))
    if start_date <= end_date:
        filtered_data = data[(data['date d\'entrée'].dt.date >= start_date) & (data['date d\'entrée'].dt.date <= end_date)]
    else:
        st.error("The start date must be before the end date.")

# Filter data according to selected options
filtered_data = filtered_data[(filtered_data['class'].isin(classes)) & (filtered_data['ZoneTotal'].isin(zones))]
if filter_option:
    filtered_data = filtered_data[filtered_data.apply(lambda row: row.astype(str).str.contains(filter_option, case=False).any(), axis=1)]

st.markdown('</div>', unsafe_allow_html=True)

# Display the filtered table
st.markdown('<div class="section">', unsafe_allow_html=True)
st.header('Filtered Table')
st.dataframe(filtered_data)
st.markdown('</div>', unsafe_allow_html=True)

# Display descriptive statistics for the filtered data
st.markdown('<div class="section">', unsafe_allow_html=True)
st.header('Descriptive Statistics')
st.write('Descriptive Statistics for Filtered Data')
st.write(filtered_data.describe(include='all'))

# Add additional metrics
total_vehicles = filtered_data['class'].count()
unique_zones = filtered_data['ZoneTotal'].nunique()

col1, col2 = st.columns(2)
col1.metric("Total Vehicles", total_vehicles)
col2.metric("Number of Unique Zones", unique_zones)

# Statistics for vehicles by class
st.write('Statistics for Vehicles by Class')
vehicles_by_class = filtered_data['class'].value_counts().reset_index()
vehicles_by_class.columns = ['Vehicle Class', 'Number of Vehicles']
st.write(vehicles_by_class)
st.markdown('</div>', unsafe_allow_html=True)

# Add additional charts
st.markdown('<div class="section">', unsafe_allow_html=True)
st.header('Graphical Analysis')
# Ajouter des graphiques supplémentaires
st.markdown('<div class="section">', unsafe_allow_html=True)
st.header('Analyse Graphique')

chart1 = alt.Chart(filtered_data).mark_bar().encode(
    x='class:N',
    y='count():Q',
    color='class:N',
    tooltip=['class', 'count()']
).interactive()

st.altair_chart(chart1, use_container_width=True)

# Supprimer les valeurs nulles pour la colonne 'pompes_info' avant de créer le graphique
filtered_data_no_nulls = filtered_data.dropna(subset=['pompes_info'])

chart2 = alt.Chart(filtered_data_no_nulls).mark_bar().encode(
    x='pompes_info:N',
    y='count():Q',
    color='pompes_info:N',
    tooltip=['pompes_info', 'count()']
).interactive()

st.altair_chart(chart2, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)
def create_seaborn_chart(data, x_column, y_column, title, color_palette, width=8, height=6):
    fig, ax = plt.subplots(figsize=(width, height))
    sns.barplot(x=x_column, y=y_column, data=data, ax=ax, palette=color_palette)
    ax.set_title(title)
    return fig



# Chart 1: Number of Vehicles by Class
chart1 = create_seaborn_chart(vehicles_by_class, 'Vehicle Class', 'Number of Vehicles', 'Number of Vehicles by Class', 'Blues', width=6, height=4)
st.pyplot(chart1)

# Save the matplotlib chart as a temporary image
chart1_path = os.path.join(tempfile.gettempdir(), 'chart1.png')
chart1.savefig(chart1_path)

# Remove null values for the 'pumps_info' column before creating the chart
filtered_data_no_nulls = filtered_data.dropna(subset=['pompes_info'])

# Chart 2: Number of Pumps by Inf
pumps_info_counts = filtered_data_no_nulls['pompes_info'].value_counts().reset_index()
pumps_info_counts.columns = ['Pump Info', 'Number']
chart2 = create_seaborn_chart(pumps_info_counts, 'Pump Info', 'Number', 'Number of Pumps by Info', 'Greens', width=5, height=3)
st.pyplot(chart2)

# Save the matplotlib chart as a temporary image
chart2_path = os.path.join(tempfile.gettempdir(), 'chart2.png')
chart2.savefig(chart2_path)

st.markdown('</div>', unsafe_allow_html=True)

# Generate the analysis table by weight category and zone
filtered_data['weight_category'] = filtered_data['class'].apply(lambda x: 'Heavy Weight' if x in ['Big Truck', 'Construction Machine'] else 'Light Weight')
analysis_table = filtered_data.pivot_table(index='ZoneTotal', columns='weight_category', aggfunc='size', fill_value=0)
st.write(analysis_table)

# Function to generate the PDF report
import matplotlib.patches as patches

def generate_pdf(date_filter_type, date_selected=None, start_date=None, end_date=None, figsize=(11.69, 8.27)):
    buffer = io.BytesIO()
    with PdfPages(buffer) as pdf:
        # Create a function to add a border to a figure
        def add_border(fig, ax, color='blue', thickness=5, padding=0):
            # Ajouter une bordure autour de toute la figure avec un padding optionnel
            fig_width, fig_height = fig.get_size_inches()
            rect = patches.Rectangle(
                (-padding / fig_width, -padding / fig_height),
                1 + 2 * padding / fig_width,
                1 + 2 * padding / fig_height,
                transform=fig.transFigure,
                linewidth=thickness,
                edgecolor=color,
                facecolor='none',
                clip_on=False
            )
            fig.patches.append(rect)


        # Report title
        fig, ax = plt.subplots(figsize=figsize)
        ax.axis('off')
        if date_filter_type == 'Day':
            title = f"Daily Report for {date_selected.strftime('%Y-%m-%d')}"
        else:
            title = f"Weekly Report from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        ax.text(0.5, 0.5, title, transform=ax.transAxes, ha="center", fontsize=20)
        add_border(fig, ax)
        pdf.savefig(fig)
        plt.close(fig)

        # Chart 1: Number of Vehicles by Class
        fig1 = create_seaborn_chart(vehicles_by_class, 'Vehicle Class', 'Number of Vehicles', 'Number of Vehicles by Class', 'Blues', width=6, height=4)
        add_border(fig1, fig1.axes[0])
        pdf.savefig(fig1)
        plt.close(fig1)
        
        # Chart 2: Number of Pumps by Info
        fig2 = create_seaborn_chart(pumps_info_counts, 'Pump Info', 'Number', 'Number of Pumps by Info', 'Greens', width=6, height=4)
        add_border(fig2, fig2.axes[0])
        pdf.savefig(fig2)
        plt.close(fig2)

        # Chart for weight categories
        fig3, ax3 = plt.subplots(figsize=(figsize[0], figsize[1]))
        weight_totals = filtered_data['weight_category'].value_counts()
        weight_avg_wait_times = filtered_data.groupby('weight_category')['wait_time'].mean()
        weight_summary_table = pd.DataFrame({
            'Total Count': weight_totals,
            'Average Wait Time': weight_avg_wait_times
        })

        ax3.bar(weight_summary_table.index, weight_summary_table['Total Count'], color='blue', alpha=0.6, label='Total Count')
        ax3.set_ylabel('Total Count', color='blue')
        ax3.tick_params(axis='y', labelcolor='blue')
        ax4 = ax3.twinx()
        ax4.plot(weight_summary_table.index, weight_summary_table['Average Wait Time'], color='red', marker='o', linestyle='-', linewidth=2, markersize=10, label='Average Wait Time')
        ax4.set_ylabel('Average Wait Time (seconds)', color='red')
        ax4.tick_params(axis='y', labelcolor='red')
        ax3.set_title('Heavy and Light Weight - Total Count and Average Wait Time')
        fig3.tight_layout()
        add_border(fig3, ax3)
        pdf.savefig(fig3)
        plt.close(fig3)

        # Add the saved chart images to the report
        for chart_path in [chart1_path, chart2_path]:
            image = plt.imread(chart_path)
            fig, ax = plt.subplots(figsize=figsize)
            ax.imshow(image)
            ax.axis('off')
            add_border(fig, ax)
            pdf.savefig(fig)
            plt.close(fig)

        # Descriptive Statistics for weight categories
        fig4, ax5 = plt.subplots(figsize=figsize)
        ax5.axis('off')
        table_data = weight_summary_table.reset_index().values
        table = ax5.table(cellText=table_data, colLabels=weight_summary_table.reset_index().columns, loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.2)
        ax5.set_title('Descriptive Statistics for Weight Categories')
        add_border(fig4, ax5)
        pdf.savefig(fig4)
        plt.close(fig4)
        
        # Analysis by Zone and Weight Category
        fig5, ax6 = plt.subplots(figsize=figsize)
        ax6.axis('off')
        table_data = analysis_table.reset_index().values
        table = ax6.table(cellText=table_data, colLabels=analysis_table.reset_index().columns, loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.2)
        ax6.set_title('Analysis by Zone and Weight Category')
        add_border(fig5, ax6)
        pdf.savefig(fig5)
        plt.close(fig5)

    buffer.seek(0)
    return buffer


def merge_pdfs(cover_page_path, report_buffer):
    cover_pdf = PdfReader(cover_page_path)
    report_pdf = PdfReader(report_buffer)
    writer = PdfWriter()

    # Add cover page
    for page in cover_pdf.pages:
        writer.add_page(page)

    # Add report pages
    for page in report_pdf.pages:
        writer.add_page(page)

    output_buffer = io.BytesIO()
    writer.write(output_buffer)
    output_buffer.seek(0)
    return output_buffer

# Add a button to download the report
if st.button('Download Report'):
    if date_filter_type == 'Day':
        report_buffer = generate_pdf(date_filter_type, date_selected=date_selected)
    else:
        report_buffer = generate_pdf(date_filter_type, start_date=start_date, end_date=end_date)
    
    cover_page_path = 'first_page.pdf'
    final_report_buffer = merge_pdfs(cover_page_path, report_buffer)
    st.download_button(label="Download PDF Report", data=final_report_buffer, file_name="report_with_cover.pdf", mime="application/pdf")

# Add a footer
st.markdown(
    """
    <div class="footer">
        <p>Developed by Metaadi Wissal</p>
    </div>
    """,
    unsafe_allow_html=True
)
