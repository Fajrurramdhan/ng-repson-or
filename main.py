from imports import *  # Menggunakan semua impor dari imports.py
from app_zones import load_zone_data

def initialize_data():
    """Initialize data for shelters and zones in Streamlit's session state."""
    if "shelter_df" not in st.session_state:
        try:
            st.session_state.shelter_df = load_shelter_data('data_shelter.json')
        except FileNotFoundError:
            st.session_state.shelter_df = pd.DataFrame(columns=[
                "No.", "Name", "Capacity People", "Capacity Livestock", 
                "Latitude", "Longitude", "Province Name"
            ])

    if "zone_df" not in st.session_state:
        try:
            st.session_state.zone_df = load_zone_data('data_zone.json')
        except FileNotFoundError:
            st.session_state.zone_df = pd.DataFrame(columns=[
                "No.", "Name", "Population Of People", "Population Of Livestock", 
                "Latitude", "Longitude", "Province"
            ])

def render_sidebar():
    """Render the sidebar with navigation and additional actions."""
    # Sidebar styling
    st.markdown("""
        <style>
        /* Styling sidebar */
        [data-testid="stSidebar"] {
            background-color: #2e3b4e;
            padding: 20px;
        }
        .sidebar-title {
            color: #ffffff;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .stRadio > label {
            font-size: 16px;
            font-weight: bold;
            color: #ffffff;
        }
        .custom-divider {
            margin: 20px 0;
            height: 1px;
            background-color: #6c7a89;
        }
        </style>
    """, unsafe_allow_html=True)

    # Sidebar title
    st.sidebar.markdown("<div class='sidebar-title'>📋 Master Data</div>", unsafe_allow_html=True)

    # Navigation radio buttons
    page_options = ["📦 Depots", "🏠 Shelters", "🗺️ Zones", "🔗 Network Generation"]
    selected_page = st.sidebar.radio("Navigation", page_options, index=0, key="navigation_radio")

    # Map selected page to session state
    page_mapping = {
        "📦 Depots": "Depots",
        "🏠 Shelters": "Shelters",
        "🗺️ Zones": "Zones",
        "🔗 Network Generation": "Network Generation"
    }
    st.session_state.page = page_mapping[selected_page]

    # Divider
    st.sidebar.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

    # Run Network Generation button
    if st.sidebar.button("🚀 Run Network Generation", key="run_network_generation"):
        st.success("Network Generation in progress...")

def display_page():
    """Display the main content based on the selected page in the sidebar."""
    page = st.session_state.get("page", "Depots")
    if page == "Depots":
        show_depots()
    elif page == "Shelters":
        show_shelters()
    elif page == "Zones":
        show_zones()
    elif page == "Network Generation":
        show_network_generation()
    else:
        st.error("Invalid page selected.")

def main():
    """Main function to run the app."""
    initialize_data()
    render_sidebar()
    display_page()

if __name__ == "__main__":
    main()
