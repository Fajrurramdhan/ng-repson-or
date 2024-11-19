import streamlit as st
import time

# Fungsi untuk menampilkan modul Network Generation
def show_network_generation():
    # Using "with" notation
    with st.sidebar:
        st.button("Network Generation", type="primary")
    
    # Title
    st.title("Integrate Module Network Generation")

    # Layout with two main columns
    col1, col2 = st.columns([2, 3])

    province = ["Aceh", "Sumatra Utara", "Sumatra Barat",
                "Riau", "Kepulauan Riau", "Jambi", "Sumatra Selatan", "Bengkulu",
                "Lampung", "Bangka Belitung", "DKI Jakarta", "Banten", "Jawa Barat",
                "Jawa Tengah", "Jawa Timur", "DI Yogyakarta", "Kalimantan Barat",
                "Kalimatan Tengah", "Kalimantan Selatan", "Kalimantan Timur",
                "Kalimantan Utara", "Sulawesi Utara", "Gorontalo", "Sulawesi Tengah",
                "Sulawesi Selatan", "Sulawesi Barat", "Nusa Tenggara Barat",
                "Nusa Tenggara Timur", "Bali", "Maluku", "Maluku Utara",
                "Papua Barat", "Papua", "Papua Barat Daya", "Papua Tengah",
                "Papua Pegunungan", "Papua Selatan"]
    
    # Left column (Input Data)
    with col1:
        st.header("Input Data")
        base_area = st.selectbox("Base Area (Province)", ["Select Area"] + province)
        directory_name = st.text_input("Directory Name")
        st.subheader("Master Files")
        tab1, tab2 = st.tabs(["Locations", "Settings"])
        with tab1:
            st.markdown("**Master Locations (Point Of Interest)**")
            st.button("View Input")

    # Right column (Execute Process)
    with col2:
        st.header("Execute Process")
        directory_input = st.text_input("Directory Input", "not created yet", disabled=True)
        directory_output = st.text_input("Directory Output", "not created yet", disabled=True)
        status_file_input = st.text_input("Status File Input", "not provided yet", disabled=True)
    
    # Additional guide button
    st.button("Need Guide?", key="guide_button")

# Hanya untuk debugging saat menjalankan file ini secara mandiri
if __name__ == "__main__":
    show_network_generation()
