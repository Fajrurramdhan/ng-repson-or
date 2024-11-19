from imports import *  # Mengimpor semua pustaka dari imports.py


# Fungsi untuk memuat data dari file JSON
@st.cache_data
def load_Depot_data(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return pd.DataFrame(data['data'])
    except (FileNotFoundError, KeyError):
        # Jika file tidak ditemukan atau data tidak memiliki struktur yang diharapkan
        return pd.DataFrame(columns=["No.", "Name", "Latitude", "Longitude", "Province Name"])


# Fungsi inisialisasi data untuk memastikan Depot_df selalu ada di session state
def initialize_data():
    """Initialize Depot data."""
    if "Depot_df" not in st.session_state:
        st.session_state.Depot_df = load_Depot_data('data_depot.json')
        # Jika file tidak ditemukan atau kosong, buat DataFrame kosong dengan kolom yang benar
        if st.session_state.Depot_df.empty:
            st.session_state.Depot_df = pd.DataFrame(columns=["No.", "Name", "Latitude", "Longitude", "Province Name"])


# Pastikan initialize_data() dipanggil di awal aplikasi
initialize_data()

# Fungsi untuk memastikan kolom memiliki tipe data yang konsisten
def ensure_arrow_compatibility(df):
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str)
        elif pd.api.types.is_numeric_dtype(df[col]):
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

# Fungsi untuk mengonversi DataFrame ke Excel
@st.cache_data
def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

# Fungsi pagination untuk menampilkan tabel
def paginate_dataframe(df, page_size=10):
    total_pages = len(df) // page_size + (1 if len(df) % page_size > 0 else 0)
    current_page = st.session_state.get("current_page", 1)

    if current_page > total_pages:
        current_page = total_pages

    start_idx = (current_page - 1) * page_size
    end_idx = start_idx + page_size

    paginated_df = df.iloc[start_idx:end_idx]

    col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 2, 2])
    with col1:
        st.write(f"Page {current_page} of {total_pages}")
    with col4:
        st.download_button(
            label="Download current page as Excel",
            data=convert_df_to_excel(paginated_df),
            file_name=f"Depot_page_{current_page}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"download_page_{current_page}"
        )
    with col5:
        st.download_button(
            label="Download all data as Excel",
            data=convert_df_to_excel(df),
            file_name="Depot_all_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_all_data"
        )

    st.dataframe(paginated_df, use_container_width=True)

    col6, col7, col8 = st.columns([1, 2, 1])
    with col6:
        if st.button("Previous", key="prev_button_depot") and current_page > 1:
            st.session_state.current_page = current_page - 1
    with col8:
        if st.button("Next", key="next_button_depot") and current_page < total_pages:
            st.session_state.current_page = current_page + 1

# Fungsi untuk menampilkan peta interaktif dengan folium
def show_interactive_map():
    st.write("### Depot Locations Map")

    # Validasi apakah Depot_df memiliki data dan kolom yang diperlukan
    if "Depot_df" not in st.session_state or st.session_state.Depot_df.empty:
        st.error("Data Depot tidak ditemukan atau kosong.")
        return

    if "Latitude" not in st.session_state.Depot_df.columns or "Longitude" not in st.session_state.Depot_df.columns:
        st.error("Data Depot tidak memiliki kolom 'Latitude' atau 'Longitude'. Pastikan data memiliki kolom yang sesuai.")
        st.write("Kolom yang tersedia saat ini:", st.session_state.Depot_df.columns)
        return

    # Tentukan pusat peta
    map_center = [st.session_state.Depot_df["Latitude"].mean(), st.session_state.Depot_df["Longitude"].mean()]
    
    # Inisialisasi peta
    m = folium.Map(location=map_center, zoom_start=6, tiles="CartoDB Positron")

    # Tambahkan marker untuk setiap Depot
    for _, row in st.session_state.Depot_df.iterrows():
        popup_text = (f"<b>Name:</b> {row['Name']}<br>"
                      f"<b>Latitude:</b> {row['Latitude']}<br>"
                      f"<b>Longitude:</b> {row['Longitude']}<br>"
                      f"<b>Province:</b> {row['Province Name']}")
        
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=folium.Popup(popup_text, max_width=300),
            tooltip=row["Name"]
        ).add_to(m)

    # Render peta menggunakan streamlit-folium
    st_folium(m, width=700, height=500)


# Fungsi utama untuk menampilkan halaman Depots dan fitur CRUD
def show_depots():
    initialize_data()  # Pastikan data diinisialisasi ulang jika perlu
    st.markdown("<h1 style='color: white;'>List of Depots</h1>", unsafe_allow_html=True)
    # Menampilkan peta interaktif
    show_interactive_map()

    # Tombol untuk mengimpor CSV
    uploaded_csv_file = st.file_uploader("Import CSV", type=["csv"], key="Depot_upload")
    if uploaded_csv_file is not None:
        st.session_state.Depot_df = pd.read_csv(uploaded_csv_file)
        st.success("File CSV berhasil diunggah dan data ditampilkan di bawah.")
    
    # Tombol untuk mengimpor JSON
    uploaded_json_file = st.file_uploader("Import JSON", type=["json"], key="Depot_json_upload")
    if uploaded_json_file is not None:
        try:
            json_data = json.load(uploaded_json_file)
            st.session_state.Depot_df = pd.DataFrame(json_data['data'])
            st.success("File JSON berhasil diunggah dan data ditampilkan di bawah.")
        except json.JSONDecodeError as e:
            st.error(f"Error decoding JSON: {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")

    # Input untuk pencarian kata kunci
    search_keyword = st.text_input("Keywords", placeholder="Search...", key="Depot_search")

    # Filter data berdasarkan kata kunci
    if search_keyword:
        filtered_df = st.session_state.Depot_df[
            st.session_state.Depot_df.apply(lambda row: row.astype(str).str.contains(search_keyword, case=False).any(), axis=1)
        ]
        st.write(f"Menampilkan hasil pencarian untuk kata kunci: **{search_keyword}**")
    else:
        filtered_df = st.session_state.Depot_df
        st.write("Menampilkan semua data")

    # Menampilkan tabel Depot data dengan pagination
    st.write("### Depot Data")
    compatible_df = ensure_arrow_compatibility(filtered_df)  # Pastikan kompatibilitas tipe data
    paginate_dataframe(compatible_df, page_size=10)

    # Menambahkan fitur New untuk menambahkan data baru
    with st.expander("➕ Add New Depot", expanded=False):
        st.write("Fill out the form below to add a new Depot:")

        if not st.session_state.Depot_df.empty:
            new_no = st.session_state.Depot_df["No."].max() + 1
        else:
            new_no = 1

        st.write(f"Next available No.: {new_no}")

        new_name = st.text_input("Name")
        new_latitude = st.number_input("Latitude", format="%.6f")
        new_longitude = st.number_input("Longitude", format="%.6f")
        new_province_name = st.text_input("Province Name")

        if st.button("Add New Depot", key="add_new_depot_button"):
            new_data = {
                "No.": new_no,
                "Name": new_name,
                "Latitude": new_latitude,
                "Longitude": new_longitude,
                "Province Name": new_province_name
            }
            st.session_state.Depot_df = pd.concat([st.session_state.Depot_df, pd.DataFrame([new_data])], ignore_index=True)
            st.success("New Depot added successfully!")

    # Menangani aksi View dan Update berdasarkan pemilihan
    selected_row_index = st.selectbox("Select Depot to View or Update", options=compatible_df.index, format_func=lambda x: compatible_df.at[x, 'Name'])
    
    st.write("### Depot Details")
    st.write(compatible_df.loc[selected_row_index])

    # Tombol Update dengan expander untuk form update
    with st.expander("✏️ Update Depot", expanded=False):
        st.write(f"Updating Depot - {compatible_df.at[selected_row_index, 'Name']}")
        depot_details = compatible_df.loc[selected_row_index]
        updated_name = st.text_input("Name", value=depot_details["Name"], key=f"name_{selected_row_index}")
        updated_latitude = st.number_input("Latitude", value=depot_details["Latitude"], key=f"lat_{selected_row_index}")
        updated_longitude = st.number_input("Longitude", value=depot_details["Longitude"], key=f"long_{selected_row_index}")
        updated_province_name = st.text_input("Province Name", value=depot_details["Province Name"], key=f"province_{selected_row_index}")

        if st.button("Update Depot", key=f"update_button_{selected_row_index}"):
            st.session_state.Depot_df.at[selected_row_index, "Name"] = updated_name
            st.session_state.Depot_df.at[selected_row_index, "Latitude"] = updated_latitude
            st.session_state.Depot_df.at[selected_row_index, "Longitude"] = updated_longitude
            st.session_state.Depot_df.at[selected_row_index, "Province Name"] = updated_province_name
            st.success("Depot updated successfully!")

    # Opsi untuk memilih baris yang akan dihapus
    selected_rows = st.multiselect("Select rows to delete:", options=compatible_df.index, format_func=lambda x: f"{compatible_df.at[x, 'Name']}")

    if st.button("🗑️ Drop Selected", key="drop_selected_depot_button"):
        if selected_rows:
            st.session_state.Depot_df.drop(selected_rows, inplace=True)
            st.session_state.Depot_df.reset_index(drop=True, inplace=True)
            st.success("Selected rows have been deleted.")
