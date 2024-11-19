from imports import *  # Mengimpor semua pustaka dari imports.py

# Fungsi untuk memuat data dari file JSON
@st.cache_data
def load_shelter_data(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return pd.DataFrame(data['data'])
    except (FileNotFoundError, KeyError):
        return pd.DataFrame(columns=["No.", "Name", "Capacity People", "Capacity Livestock", "Latitude", "Longitude", "Province Name"])

# Memuat data shelter dari file JSON
if "shelter_df" not in st.session_state:
    st.session_state.shelter_df = load_shelter_data('data_shelter.json')

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
            file_name=f"shelter_page_{current_page}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"download_page_{current_page}"
        )
    with col5:
        st.download_button(
            label="Download all data as Excel",
            data=convert_df_to_excel(df),
            file_name="shelter_all_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_all_data"
        )

    st.dataframe(paginated_df)

    col6, col7, col8 = st.columns([1, 2, 1])
    with col6:
        if st.button("Previous", key="prev_button_shelter") and current_page > 1:
            st.session_state.current_page = current_page - 1
    with col8:
        if st.button("Next", key="next_button_shelter") and current_page < total_pages:
            st.session_state.current_page = current_page + 1

# Fungsi untuk menampilkan peta interaktif dengan folium
def show_interactive_map():
    st.write("### Shelter Locations Map")

    if "shelter_df" not in st.session_state or st.session_state.shelter_df.empty:
        st.error("Data Shelter tidak ditemukan atau kosong.")
        return

    if "Latitude" not in st.session_state.shelter_df.columns or "Longitude" not in st.session_state.shelter_df.columns:
        st.error("Data Shelter tidak memiliki kolom 'Latitude' atau 'Longitude'.")
        st.write("Kolom yang tersedia saat ini:", st.session_state.shelter_df.columns)
        return

    map_center = [st.session_state.shelter_df["Latitude"].mean(), st.session_state.shelter_df["Longitude"].mean()]
    m = folium.Map(location=map_center, zoom_start=6, tiles="CartoDB Positron")

    for _, row in st.session_state.shelter_df.iterrows():
        popup_text = (f"<b>Name:</b> {row['Name']}<br>"
                      f"<b>Capacity People:</b> {row['Capacity People']}<br>"
                      f"<b>Capacity Livestock:</b> {row['Capacity Livestock']}<br>"
                      f"<b>Province:</b> {row['Province Name']}")
        
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=folium.Popup(popup_text, max_width=300),
            tooltip=row["Name"]
        ).add_to(m)

    st_folium(m, width=700, height=500)

# Fungsi utama untuk menampilkan halaman shelters dan fitur CRUD
def show_shelters():
    st.markdown("<h1 style='color: white;'>List of Shelters</h1>", unsafe_allow_html=True)

    show_interactive_map()

    uploaded_csv_file = st.file_uploader("Import CSV", type=["csv"], key="shelter_csv_upload")
    if uploaded_csv_file is not None:
        st.session_state.shelter_df = pd.read_csv(uploaded_csv_file)
        st.success("File CSV berhasil diunggah dan data ditampilkan.")

    uploaded_json_file = st.file_uploader("Import JSON", type=["json"], key="shelter_json_upload")
    if uploaded_json_file is not None:
        try:
            json_data = json.load(uploaded_json_file)
            st.session_state.shelter_df = pd.DataFrame(json_data['data'])
            st.success("File JSON berhasil diunggah dan data ditampilkan.")
        except Exception as e:
            st.error(f"Error loading JSON: {e}")

    search_keyword = st.text_input("Keywords", placeholder="Search...", key="shelter_search")

    if search_keyword:
        filtered_df = st.session_state.shelter_df[
            st.session_state.shelter_df.apply(lambda row: row.astype(str).str.contains(search_keyword, case=False).any(), axis=1)
        ]
        st.write(f"Menampilkan hasil pencarian untuk kata kunci: **{search_keyword}**")
    else:
        filtered_df = st.session_state.shelter_df
        st.write("Menampilkan semua data")

    st.write("### Shelter Data")
    compatible_df = ensure_arrow_compatibility(filtered_df)
    paginate_dataframe(compatible_df, page_size=10)

    with st.expander("➕ Add New Shelter", expanded=False):
        st.write("Fill out the form below to add a new shelter:")

        if not st.session_state.shelter_df.empty:
            new_no = st.session_state.shelter_df["No."].max() + 1
        else:
            new_no = 1

        new_name = st.text_input("Name")
        new_capacity_people = st.number_input("Capacity People", min_value=0, step=1)
        new_capacity_livestock = st.number_input("Capacity Livestock", min_value=0, step=1)
        new_latitude = st.number_input("Latitude", format="%.6f")
        new_longitude = st.number_input("Longitude", format="%.6f")
        new_province_name = st.text_input("Province Name")

        if st.button("Add New Shelter", key="add_new_shelter_button"):
            new_data = {
                "No.": new_no,
                "Name": new_name,
                "Capacity People": new_capacity_people,
                "Capacity Livestock": new_capacity_livestock,
                "Latitude": new_latitude,
                "Longitude": new_longitude,
                "Province Name": new_province_name
            }
            st.session_state.shelter_df = pd.concat([st.session_state.shelter_df, pd.DataFrame([new_data])], ignore_index=True)
            st.success("New shelter added successfully!")

    selected_row_index = st.selectbox("Select Shelter to View or Update", options=compatible_df.index, format_func=lambda x: compatible_df.at[x, 'Name'])
    
    st.write("### Shelter Details")
    st.write(compatible_df.loc[selected_row_index])

    with st.expander("✏️ Update Shelter", expanded=False):
        shelter_details = compatible_df.loc[selected_row_index]
        updated_name = st.text_input("Name", value=shelter_details["Name"], key=f"name_{selected_row_index}")
        updated_capacity_people = st.number_input("Capacity People", value=shelter_details["Capacity People"], key=f"people_{selected_row_index}")
        updated_capacity_livestock = st.number_input("Capacity Livestock", value=shelter_details["Capacity Livestock"], key=f"livestock_{selected_row_index}")
        updated_latitude = st.number_input("Latitude", value=shelter_details["Latitude"], key=f"lat_{selected_row_index}")
        updated_longitude = st.number_input("Longitude", value=shelter_details["Longitude"], key=f"long_{selected_row_index}")
        updated_province_name = st.text_input("Province Name", value=shelter_details["Province Name"], key=f"province_{selected_row_index}")

        if st.button("Update Shelter", key=f"update_button_{selected_row_index}"):
            st.session_state.shelter_df.at[selected_row_index, "Name"] = updated_name
            st.session_state.shelter_df.at[selected_row_index, "Capacity People"] = updated_capacity_people
            st.session_state.shelter_df.at[selected_row_index, "Capacity Livestock"] = updated_capacity_livestock
            st.session_state.shelter_df.at[selected_row_index, "Latitude"] = updated_latitude
            st.session_state.shelter_df.at[selected_row_index, "Longitude"] = updated_longitude
            st.session_state.shelter_df.at[selected_row_index, "Province Name"] = updated_province_name
            st.success("Shelter updated successfully!")

    selected_rows = st.multiselect("Select rows to delete:", options=compatible_df.index, format_func=lambda x: f"{compatible_df.at[x, 'Name']}")

    if st.button("🗑️ Drop Selected", key="drop_selected_shelter_button"):
        if selected_rows:
            st.session_state.shelter_df.drop(selected_rows, inplace=True)
            st.session_state.shelter_df.reset_index(drop=True, inplace=True)
            st.success("Selected rows have been deleted.")
