import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="Bird Species Observation Analysis",
    page_icon="🦅",
    layout="wide"
)

# Custom CSS for UI Match
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    div[data-testid="stMetricValue"] { font-size: 28px; font-weight: bold; }
    .stCallout { border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Load Data
# ---------------------------------------------------------
@st.cache_data
def load_data():
    # File name fallback: SQL or CSV
    try:
        conn = sqlite3.connect('bird_biodiversity.db')
        df = pd.read_sql("SELECT * FROM bird_observations", conn)
        conn.close()
    except:
        df = pd.read_csv('cleaned_bird_data.csv')
        
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Month_Name'] = df['Date'].dt.month_name()
    return df

df = load_data()

# ---------------------------------------------------------
# Sidebar Controls
# ---------------------------------------------------------
st.sidebar.title("🎛️ Dashboard Controls")
st.sidebar.caption("Use the filters to explore the bird observation dataset.")

# 1. Habitat Filter
habitats = list(df['Location_Type'].dropna().unique()) if 'Location_Type' in df.columns else ['Forest', 'Grassland']
selected_habitat = st.sidebar.multiselect("Habitat", habitats, default=habitats)

# 2. Administrative Unit Filter
admin_units = list(df['Admin_Unit_Code'].dropna().unique()) if 'Admin_Unit_Code' in df.columns else []
selected_admin = st.sidebar.multiselect("Administrative Unit", admin_units, default=admin_units)

# 3. Species Filter (Optional Multi-Select)
species_list = list(df['Common_Name'].dropna().unique()) if 'Common_Name' in df.columns else []
selected_species = st.sidebar.multiselect("Species", species_list, default=[])

# 4. Month Filter
months = ["May", "June", "July"]
selected_months = st.sidebar.multiselect("Month", months, default=months)

# 5. Visit Filter
visits = list(df['Visit'].dropna().unique()) if 'Visit' in df.columns else [1, 2, 3]
selected_visits = st.sidebar.multiselect("Visit", visits, default=visits)

st.sidebar.markdown("---")
# 6. Top species slider
top_n = st.sidebar.slider("Top species to display", min_value=5, max_value=20, value=15)

st.sidebar.caption("Dashboard source: bird_observations_cleaned.csv")

# ---------------------------------------------------------
# Filter Dataset
# ---------------------------------------------------------
filtered_df = df.copy()

if 'Location_Type' in filtered_df.columns and selected_habitat:
    filtered_df = filtered_df[filtered_df['Location_Type'].isin(selected_habitat)]

if 'Admin_Unit_Code' in filtered_df.columns and selected_admin:
    filtered_df = filtered_df[filtered_df['Admin_Unit_Code'].isin(selected_admin)]

if selected_species and 'Common_Name' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['Common_Name'].isin(selected_species)]

if 'Month_Name' in filtered_df.columns and selected_months:
    filtered_df = filtered_df[filtered_df['Month_Name'].isin(selected_months)]

if 'Visit' in filtered_df.columns and selected_visits:
    filtered_df = filtered_df[filtered_df['Visit'].isin(selected_visits)]

# ---------------------------------------------------------
# Main Header & Metric Summary
# ---------------------------------------------------------
st.title("Bird Species Observation Analysis")
st.caption("Explore bird diversity, habitat patterns, temporal trends, environmental conditions, and conservation indicators across forest and grassland observations.")

st.info(f"Showing {len(filtered_df):,} observations from {len(df):,} total records after applying the selected filters.")

# Metric Cards Row
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Observations", f"{len(filtered_df):,}", "Filtered records")
m2.metric("Unique Species", filtered_df['Common_Name'].nunique() if 'Common_Name' in filtered_df.columns else 0, "Scientific names")
m3.metric("Habitats", filtered_df['Location_Type'].nunique() if 'Location_Type' in filtered_df.columns else 0, "Forest / Grassland")
m4.metric("Admin Units", filtered_df['Admin_Unit_Code'].nunique() if 'Admin_Unit_Code' in filtered_df.columns else 0, "Observation areas")
m5.metric("Plots", filtered_df['Plot_Name'].nunique() if 'Plot_Name' in filtered_df.columns else 0, "Observation plots")

st.markdown("---")

# ---------------------------------------------------------
# Tabs Section
# ---------------------------------------------------------
tab_names = ["👁️ Overview", "🦜 Species & Habitat", "📅 Temporal", "🌤️ Environment", "🛡️ Conservation & Location"]
tab1, tab2, tab3, tab4, tab5 = st.tabs(tab_names)

# --- TAB 1: OVERVIEW ---
with tab1:
    st.subheader("Overview")
    st.caption("High-level view of observation volume and biodiversity across the selected data.")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("**Observation Share by Habitat**")
        if 'Location_Type' in filtered_df.columns:
            hab_counts = filtered_df['Location_Type'].value_counts().reset_index()
            hab_counts.columns = ['Habitat', 'Count']
            fig_hab = px.pie(
                hab_counts, values='Count', names='Habitat', hole=0.55,
                color='Habitat', color_discrete_map={'Forest': '#2ECC71', 'Grassland': '#F1C40F'}
            )
            fig_hab.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_hab, use_container_width=True)

    with col_right:
        st.markdown("**Species Richness by Habitat**")
        if 'Location_Type' in filtered_df.columns and 'Common_Name' in filtered_df.columns:
            richness = filtered_df.groupby('Location_Type')['Common_Name'].nunique().reset_index()
            richness.columns = ['Habitat', 'Unique Species']
            fig_rich = px.bar(
                richness, x='Habitat', y='Unique Species', color='Habitat',
                text='Unique Species', color_discrete_map={'Forest': '#2ECC71', 'Grassland': '#F1C40F'}
            )
            st.plotly_chart(fig_rich, use_container_width=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(f"**Top {top_n} Most Observed Species**")
        if 'Common_Name' in filtered_df.columns:
            top_spec = filtered_df['Common_Name'].value_counts().head(top_n).reset_index()
            top_spec.columns = ['Common Name', 'Count']
            fig_top = px.bar(top_spec, x='Count', y='Common Name', orientation='h', color='Count', color_continuous_scale='Turbo')
            fig_top.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_top, use_container_width=True)

    with c2:
        st.markdown("**Observation Volume by Administrative Unit**")
        if 'Admin_Unit_Code' in filtered_df.columns:
            admin_counts = filtered_df['Admin_Unit_Code'].value_counts().reset_index()
            admin_counts.columns = ['Admin Unit', 'Count']
            fig_admin = px.bar(admin_counts, x='Count', y='Admin Unit', orientation='h', color='Admin Unit', color_discrete_sequence=px.colors.qualitative.Prism)
            fig_admin.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_admin, use_container_width=True)

    # Dynamic Insight Banner
    if 'Location_Type' in filtered_df.columns and len(filtered_df) > 0:
        forest_pct = (len(filtered_df[filtered_df['Location_Type'] == 'Forest']) / len(filtered_df)) * 100
        st.warning(f"💡 **Observation insight:** Forest accounts for **{forest_pct:.1f}%** of the filtered observations ({len(filtered_df):,} records). This describes observation volume, not necessarily habitat preference.")

# --- TAB 2: SPECIES & HABITAT ---
with tab2:
    st.subheader("Species Distribution across Habitats")
    if 'Common_Name' in filtered_df.columns and 'Location_Type' in filtered_df.columns:
        spec_hab = filtered_df.groupby(['Common_Name', 'Location_Type']).size().reset_index(name='Count')
        top_spec_list = filtered_df['Common_Name'].value_counts().head(top_n).index
        spec_hab_filtered = spec_hab[spec_hab['Common_Name'].isin(top_spec_list)]
        
        fig_spec_hab = px.bar(spec_hab_filtered, x='Count', y='Common_Name', color='Location_Type', barmode='stack', title="Top Species Breakdown by Habitat")
        fig_spec_hab.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_spec_hab, use_container_width=True)

# --- TAB 3: TEMPORAL ---
with tab3:
    st.subheader("Temporal Trends")
    if 'Year' in filtered_df.columns:
        yearly = filtered_df.groupby('Year').size().reset_index(name='Observations')
        fig_year = px.line(yearly, x='Year', y='Observations', markers=True, title="Observations Over Years")
        st.plotly_chart(fig_year, use_container_width=True)

# --- TAB 4: ENVIRONMENT ---
with tab4:
    st.subheader("Environmental Factors")
    if 'Temperature' in filtered_df.columns:
        fig_temp = px.histogram(filtered_df, x="Temperature", color="Location_Type" if 'Location_Type' in filtered_df.columns else None, title="Temperature Spread")
        st.plotly_chart(fig_temp, use_container_width=True)

# --- TAB 5: CONSERVATION & LOCATION ---
with tab5:
    st.subheader("Conservation Status")
    if 'PIF_Watchlist_Status' in filtered_df.columns:
        watch_counts = filtered_df['PIF_Watchlist_Status'].astype(str).value_counts().reset_index()
        watch_counts.columns = ['Watchlist Status', 'Count']
        fig_watch = px.pie(watch_counts, values='Count', names='Watchlist Status', title="PIF Watchlist Species Ratio")
        st.plotly_chart(fig_watch, use_container_width=True)