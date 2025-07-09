from modules.lib import *
from database import *
from sentinelhub import SHConfig

# Streamlit app configuration
st.set_page_config(page_title="NDVI Analysis Dashboard", layout="wide")


if "first_load" not in st.session_state:
    st.session_state.first_load = True


if st.session_state.first_load:
    # Show a loading message when the app first loads
    loading_placeholder = st.empty()
    loading_placeholder.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600&display=swap');

            .loading-container {
                position: fixed;
                top: 33%;
                left: 50%;
                transform: translate(-50%, -50%);
                text-align: center;
                z-index: 9999;
            }

            .loading-text {
                font-size: 25px;
                font-family: 'Orbitron', sans-serif;
                color: #D4E7F5;  /* Light blue text */
                padding: 12px;
                backdrop-filter: blur(8px);
                box-shadow: 0 4px 12px rgba(70, 130, 180, 0.3);  /* Soft blue glow */
                display: inline-block;
            }
        </style>
        <div class='loading-container'>
            <div class='loading-text'>🔍 Zooming into Earth's greenery... Just a sec!</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # progress bar animation 
    progress_bar = st.progress(0)
    status_text = st.empty()

    for percent in range(1, 101, 3): 
        time.sleep(0.03)  
        status_text.markdown(
            f"<h4 style='text-align: center; color: lightblue;'>{percent}% </h4>",
            unsafe_allow_html=True,
        )
        progress_bar.progress(percent)

    # Clear progress bar after loading
    loading_placeholder.empty()
    progress_bar.empty()
    status_text.empty()

    # Mark first load as done so it doesn’t show again on internal reruns
    st.session_state.first_load = False


st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600&display=swap');
        
        .glass-title {
            text-align: center; 
            font-size: 38px; 
            font-family: 'Orbitron', sans-serif;
            color: #D4E7F5; 
            padding: 15px;
            
            background: rgba(20, 20, 20, 0.5);
            box-shadow: 0 8px 32px rgba(70, 130, 180, 0.4); 
            backdrop-filter: blur(12px);
            border: 1px solid rgba(70, 130, 180, 0.5);
            width: 100%;
            margin: auto;
        }
    </style>
    <div class='glass-title'>Vegetation Index Analysis Dashboard</div>
    <br><br>
    """,
    unsafe_allow_html=True,
)


# Initialize session state for Sentinel Hub credentials
if "sh_client_id" not in st.session_state:
    st.session_state.sh_client_id = None
if "sh_client_secret" not in st.session_state:
    st.session_state.sh_client_secret = None
if "sh_instance_id" not in st.session_state:
    st.session_state.sh_instance_id = None
if "credentials_saved" not in st.session_state:
    st.session_state.credentials_saved = False
if "feedback" not in st.session_state:
    st.session_state.feedback = ""


# Function to configure Sentinel Hub
def get_sh_config():
    config = SHConfig()
    config.sh_client_id = st.session_state.sh_client_id
    config.sh_client_secret = st.session_state.sh_client_secret
    config.sh_instance_id = st.session_state.sh_instance_id
    return config


# Show Info Box & Login Form Only If NOT Logged In
if not st.session_state.credentials_saved:
    with st.expander("ℹ️ How to Get Sentinel Hub Credentials ?", expanded=False):
        st.markdown(
            """
            <style>
                .info-box {
                    background-color: rgba(32, 60, 80, 0.2); 
                    padding: 15px;
                    border-radius: 10px;
                    border-left: 5px solid #1f77b4;
                    color: #ffffff;
                }
                .info-box h4 {
                    color: #4da8da;
                    font-size: 23px;
                    margin-bottom: 10px;
                }
                .info-box li {
                    font-size: 19px;
                    padding: 5px 0;
                }
                .info-box a {
                    color: #4da8da;
                    font-weight: bold;
                    text-decoration: none;
                }
                .info-box a:hover {
                    text-decoration: underline;
                }
                .highlight {
                    color: #ff4d4d; 
                    font-weight: bold;
                }
            </style>

            <div class="info-box">
                <h4>🔑 How to Get Sentinel Hub Credentials ?</h4>
                <ol>
                    <li> Go to <a href="https://www.sentinel-hub.com/" target="_blank">Sentinel Hub 🌍</a></li>
                    <li> Sign up or log in to your account.</li>
                    <li> Navigate to the <b>dashboard</b> and generate OAuth credentials.</li>
                    <li> Copy your <span class="highlight">Client ID</span>, <span class="highlight">Client Secret</span>, and <span class="highlight">Instance ID</span>.</li>
                    <li> Enter them below and click <b>'Save Credentials'</b>.</li>
                </ol>
            </div><br>
            """,
            unsafe_allow_html=True,
        )
        # Sentinel Hub sign-in button
        st.link_button(
            "Create account on Sentinel Hub ",
            "https://apps.sentinel-hub.com/dashboard/",
        )

    # Credential Input Form
    st.subheader("🔐 Enter Your Sentinel Hub Credentials")

    client_id = st.text_input(
        "🔑 Client ID", value=st.session_state.get("sh_client_id", "")
    )
    client_secret = st.text_input(
        "🔒 Client Secret",
        type="password",
        value=st.session_state.get("sh_client_secret", ""),
    )
    instance_id = st.text_input(
        "📌 Instance ID", value=st.session_state.get("sh_instance_id", "")
    )

    if st.button("💾 Save Credentials"):
        if all([client_id, client_secret, instance_id]):
            # Save credentials to session state
            st.session_state.sh_client_id = client_id
            st.session_state.sh_client_secret = client_secret
            st.session_state.sh_instance_id = instance_id
            st.session_state.credentials_saved = True  # Mark as logged in
            st.success("✅ Credentials saved successfully! Loading dashboard...")
            st.rerun()  # Force refresh to hide the login form & info box
        else:
            st.error("⚠️ Please fill in all fields.")

else:

    # Configure Sentinel Hub
    config = get_sh_config()

    st.sidebar.markdown(
        """
    <div style="height: 1px; background: linear-gradient(to right, #ff7e5f, #feb47b); margin-bottom: 10px;"></div>
    """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');

            [data-testid="stSidebar"] {
                background: rgba(119,158,203,0.1) ;
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                /* box-shadow: 0 4px 30px rgba(212, 231, 245, 0.5);*/
                border-right: 1px solid rgba(255, 255, 255, 0.3);
            }

            .sidebar-title {
                text-align: center;
                font-size: 20px;
                font-family: 'Orbitron', sans-serif;
                color: #D4E7F5; 
                padding: 10px;
                border-radius: 10px;
                background: rgba(255, 255, 255, 0.1); /* Subtle glass effect */
                /* box-shadow: 0 8px 32px rgba(255, 255, 255, 0.2);*/
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.3);
                margin-bottom: 19px;
            }
            
        </style>
        <div class='sidebar-title'>Vegetation Index Parameters</div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        """
        <div style="height: 1px; background: linear-gradient(to right, #ff7e5f, #feb47b); margin-bottom: 10px;"></div><br>
    """,
        unsafe_allow_html=True,
    )

    # Check if credentials are properly set
    if not config.sh_client_id or not config.sh_client_secret:
        st.error(
            "Sentinel Hub Client ID and Client Secret are not set. Please enter valid credentials."
        )
    else:
        st.toast("Sentinel Hub credentials are set correctly!", icon="✅")

    # Initialize session state for location if not already initialized
    if "location_input" not in st.session_state:
        st.session_state.location_input = "New Delhi"

    def save_image_as_png(image_array):
        """
        Convert a NumPy image array to a PNG BytesIO object.
        """
        # Ensure the image is in 8-bit format
        image_8bit = (image_array * 255).astype(np.uint8)
        image_pil = Image.fromarray(image_8bit)

        # Save as PNG into BytesIO
        image_bytes = io.BytesIO()
        image_pil.save(image_bytes, format="PNG")
        image_bytes.seek(0)

        return image_bytes

    # Function to get coordinates from Nominatim
    def get_coordinates(location_name):
        url = f"https://nominatim.openstreetmap.org/search?q={location_name}&format=json&limit=1"
        response = requests.get(url, headers={"User-Agent": "Streamlit App"})
        if response.status_code == 200:
            results = response.json()
            if results:
                coords = results[0]
                return float(coords["lat"]), float(coords["lon"])
            else:
                st.error("Location not found.")
                return None, None
        else:
            st.error("Failed to connect to the Nominatim API.")
            return None, None

    # Safe division function for vegetation index calculations
    def safe_divide(numerator, denominator):
        denominator[denominator == 0] = np.nan
        return numerator / denominator

    # Functions to calculate vegetation indices
    def calculate_ndvi(nir_band, red_band):
        denominator = nir_band + red_band
        return safe_divide(nir_band - red_band, denominator)

    def calculate_evi(nir_band, red_band, green_band):
        denominator = nir_band + 6.0 * red_band - 7.5 * green_band + 1
        return safe_divide(2.5 * (nir_band - red_band), denominator)

    def calculate_savi(nir_band, red_band):
        denominator = nir_band + red_band + 0.5
        return safe_divide(nir_band - red_band, denominator) * 1.5

    # For KDE Chart separate
    def compute_and_store_indices(nir_band, red_band, green_band):
        """Compute NDVI, EVI, and SAVI, store them in session state for reuse."""

        # Compute indices
        k_ndvi_values = calculate_ndvi(nir_band, red_band)
        k_evi_values = calculate_evi(nir_band, red_band, green_band)
        k_savi_values = calculate_savi(nir_band, red_band)

        # Normalize and Clip Values
        n_ndvi_values = np.clip(k_ndvi_values, -1, 1)
        n_evi_values = np.clip(k_evi_values, -1, 1)
        n_savi_values = np.clip(k_savi_values, -1, 1)

        # Store all values in session state
        st.session_state.index_data = {
            "NDVI": n_ndvi_values.flatten(),
            "EVI": n_evi_values.flatten(),
            "SAVI": n_savi_values.flatten(),
        }

    # Function to save Graph data to the database
    def save_graph_to_db(report_name, location, data, report_type):
        conn = sqlite3.connect("Vegetation_index_DB_new.db")
        cursor = conn.cursor()

        # Insert each row into the graph_reports table
        for _, row in data.iterrows():
            cursor.execute(
                "INSERT INTO Graph_Reports (report_name, location, date, vegetation_index_value, report_type) VALUES (?, ?, ?, ?, ?)",
                (
                    report_name,
                    location,
                    row["Date"],
                    row[f"{index} Value"],
                    report_type,
                ),
            )

        conn.commit()
        conn.close()
        st.success(f"Graph Report '{report_name}' has been saved to the database.")

    def save_histogram_to_db(
        report_name,
        location,
        data,
        report_type,
        mean,
        median,
        std_dev,
        min_value,
        max_value,
    ):
        conn = sqlite3.connect("Vegetation_index_DB_new.db")
        cursor = conn.cursor()

        #  Convert DataFrame to CSV string
        csv_buffer = StringIO()
        data.to_csv(csv_buffer, index=False)
        hist_csv_content = csv_buffer.getvalue()

        # Insert into the histogram_reports table
        cursor.execute(
            "INSERT INTO histogram_reports (report_name, location, data, report_type) VALUES (?, ?, ?, ?)",
            (report_name, location, hist_csv_content, report_type),
        )

        # Insert statistics into a separate table
        cursor.execute(
            """
            INSERT INTO histogram_statistics (report_name, location, mean, median, std_dev, min_value, max_value, report_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                report_name,
                location,
                mean,
                median,
                std_dev,
                min_value,
                max_value,
                report_type,
            ),
        )

        conn.commit()
        conn.close()
        st.success(f"Histogram Report '{report_name}' and statistics have been saved.")

    # Function to save heatmap data to the database
    def save_heatmap_to_db(report_name, location, data, report_type):
        conn = sqlite3.connect("Vegetation_index_DB_new.db")
        cursor = conn.cursor()

        # Insert each row into the table
        for _, row in data.iterrows():
            cursor.execute(
                """
                INSERT INTO Heatmap_Reports(report_name, location, latitude, longitude, vegetation_index_value, report_type)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    report_name,
                    location,
                    row["Latitude"],
                    row["Longitude"],
                    row[f"{index} Value"],
                    report_type,
                ),
            )

        conn.commit()
        conn.close()
        st.success(f"Heatmap Report '{report_name}' has been saved to the database.")

    # Function to save surface data to the database
    def save_surfaceData_to_db(report_name, location, data, report_type):
        conn = sqlite3.connect("Vegetation_index_DB_new.db")
        cursor = conn.cursor()

        # Insert each row into the table
        for _, row in data.iterrows():
            cursor.execute(
                """
                INSERT INTO Surface_data_report(report_name, location, latitude, longitude, ndvi_value, report_type)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    report_name,
                    location,
                    row["Latitude"],
                    row["Longitude"],
                    row[f"{index} Value"],
                    report_type,
                ),
            )

        conn.commit()
        conn.close()
        st.success(
            f"SurfaceData Report '{report_name}' has been saved to the database."
        )

    # feedback
    def save_feedback_to_db(feedback_text):
        conn = sqlite3.connect("Vegetation_index_DB_new.db")
        cursor = conn.cursor()

        # Insert feedback
        cursor.execute(
            "INSERT INTO User_Feedback (feedback) VALUES (?)", (feedback_text,)
        )
        conn.commit()
        conn.close()

    # timestamp
    def add_timestamp(df):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df["Generated Date"] = current_time.split()[0]  # Extract date
        df["Generated Time"] = current_time.split()[1]  # Extract time
        return df.to_csv(index=False)

    def create_download_button(data, filename, button_label):
        # Convert DataFrame to CSV format
        df = pd.DataFrame(data)
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_content = csv_buffer.getvalue()

        # Create download button
        st.sidebar.download_button(
            label=button_label, data=csv_content, file_name=filename, mime="text/csv"
        )

    # Determine initial coordinates
    latitude, longitude = get_coordinates(st.session_state.location_input)
    selected_coordinates = (
        [latitude, longitude] if latitude and longitude else [28.6139, 77.2090]
    )  # Default: New Delhi

    # Location search input
    with st.sidebar.expander("📍 Location"):
        location_input = st.text_input(
            "Enter Location", st.session_state.location_input
        )

    # User inputs for date range
    with st.sidebar.expander("📅 Select Date Range"):
        start_date = st.date_input("Start Date", value=datetime.date(2023, 1, 1))
        end_date = st.date_input("End Date", value=datetime.date(2023, 1, 15))

    # Update the map if the location input changes
    if location_input != st.session_state.location_input:
        new_latitude, new_longitude = get_coordinates(location_input)
        if new_latitude and new_longitude:
            selected_coordinates = [new_latitude, new_longitude]
            st.session_state.location_input = location_input
            st.rerun()

    # Interactive map for user
    st.subheader("📌 Pinpoint the location for analysis")

    folium_map = folium.Map(location=selected_coordinates, zoom_start=6)
    marker = folium.Marker(
        selected_coordinates, popup="Selected Location", draggable=True
    )
    marker.add_to(folium_map)
    folium_map.add_child(MeasureControl())
    folium_map.add_child(MousePosition())

    map_data = st_folium(folium_map, width=1100, height=600, key="location_map")

    # Update coordinates when the user clicks on the map
    if map_data and map_data.get("last_clicked") is not None:
        new_lat, new_lon = (
            map_data["last_clicked"]["lat"],
            map_data["last_clicked"]["lng"],
        )

        # Reverse geocode to get the location name
        reverse_geocode_url = f"https://nominatim.openstreetmap.org/reverse?lat={new_lat}&lon={new_lon}&format=json"
        response = requests.get(
            reverse_geocode_url, headers={"User-Agent": "Streamlit App"}
        )

        if response.status_code == 200:
            location_info = response.json()

            # Extract city, town, or village
            new_location = (
                location_info.get("address", {}).get("city")
                or location_info.get("address", {}).get("town")
                or location_info.get("address", {}).get("village")
                or location_info.get("display_name", "Unknown Location")
            )

            # Only update the session state if the location changed
            if new_location != st.session_state.get("location_input"):
                st.session_state.location_input = new_location
                st.session_state.selected_coordinates = [new_lat, new_lon]
                st.rerun()  # Force Streamlit to refresh with new location

    # Define bounding box and request satellite image
    bbox = BBox(
        (
            selected_coordinates[1] - 0.01,
            selected_coordinates[0] - 0.01,
            selected_coordinates[1] + 0.01,
            selected_coordinates[0] + 0.01,
        ),
        CRS.WGS84,
    )

    evalscript = """
    // Script to fetch Red, NIR for NDVI, and True Color
    function setup() {
        return {
            input: ["B02", "B03", "B04", "B08"],
            output: { bands: 4 }
        };
    }

    function evaluatePixel(sample) {
        return [sample.B04, sample.B03, sample.B02, sample.B08]; // Red, Green, Blue, NIR
    }
    """
    request = SentinelHubRequest(
        evalscript=evalscript,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,
                time_interval=(str(start_date), str(end_date)),
                mosaicking_order="leastCC",
            )
        ],
        responses=[SentinelHubRequest.output_response("default", MimeType.PNG)],
        bbox=bbox,
        size=(512, 512),
        config=config,
    )

    def process_image():
        try:
            data = request.get_data()
            if not data or len(data) == 0:
                st.error("No satellite image data received.")
                return None

            image = np.array(data[0])  # Ensure it's a NumPy array

            if image.ndim < 3 or image.shape[2] != 4:
                st.error(
                    f"Retrieved image does not contain expected bands. Shape: {image.shape}"
                )
                return None

            # Normalize bands
            red_band = image[:, :, 0].astype(float) / 255.0
            green_band = image[:, :, 1].astype(float) / 255.0
            blue_band = image[:, :, 2].astype(float) / 255.0
            nir_band = image[:, :, 3].astype(float) / 255.0

            true_color = np.stack([red_band, green_band, blue_band], axis=-1)
            infrared_image = np.stack([nir_band, red_band, green_band], axis=-1)

            return true_color, infrared_image, red_band, green_band, nir_band

        except Exception as e:
            st.error(f"Error retrieving satellite image: {e}")
            return None

    # Display selected vegetation index
    if selected_coordinates[0] and selected_coordinates[1]:
        st.write("## Satellite Imagery & Vegetation Indices")
        data = process_image()

        image_descriptions = {
            "True Color": {
                "short": "Represents natural colors as seen by the human eye.",
            },
            "Infrared": {
                "short": "Highlights vegetation using near-infrared light.",
            },
            "NDVI": {
                "short": "Measures vegetation health using red and NIR bands.",
            },
            "EVI": {
                "short": "Enhanced NDVI that reduces atmospheric distortions.",
            },
            "SAVI": {
                "short": "Modified NDVI for arid regions with sparse vegetation.",
            },
        }

        if data:
            true_color, infrared_image, red_band, green_band, nir_band = data

            # Dropdowns for user selections
            with st.sidebar.expander("🖼️ Select Image Type"):
                image_type = st.selectbox("Categories:", ["True Color", "Infrared"])
            with st.sidebar.expander("🌿 Vegetation Index Selection"):
                index = st.selectbox("Indexes:", ["NDVI", "EVI", "SAVI"])

            if image_type == "True Color":
                st.markdown(
                    "<h3 style='text-align: left; color: #b2beb5;'>True Colour Image</h3>",
                    unsafe_allow_html=True,
                )
                # Image and download button placed tightly
                st.image(true_color, use_column_width=True)

                # informatin text box
                st.markdown(
                    f"<p style='font-size:21px;'><b>{image_type}: {image_descriptions[image_type]['short']}</b></p>",
                    unsafe_allow_html=True,
                )

                # Download button - True Color Image
                st.download_button(
                    label="Download True Color Image",
                    data=save_image_as_png(true_color),
                    file_name="true_color_image.png",
                    mime="image/png",
                )

            else:
                st.markdown(
                    "<h3 style='text-align: left; color: #b2beb5;'>Infrared Colour Image</h3>",
                    unsafe_allow_html=True,
                )
                st.image(infrared_image, use_column_width=True)

                # information text box
                st.markdown(
                    f"<p style='font-size:21px;'><b>{image_type}: {image_descriptions[image_type]['short']}</b></p>",
                    unsafe_allow_html=True,
                )

                # Download button - infra Color Image
                st.download_button(
                    label="Download infrared Color Image",
                    data=save_image_as_png(infrared_image),
                    file_name="infrared_color_image.png",
                    mime="image/png",
                )
            st.markdown(
                "<hr style='border: 1px solid #f0ffff; margin-top:20px; margin-bottom:20px;'>",
                unsafe_allow_html=True,
            )

            # Compute All Indices (NDVI, EVI, SAVI)
            ndvi_values = calculate_ndvi(nir_band, red_band)
            evi_values = calculate_evi(nir_band, red_band, green_band)
            savi_values = calculate_savi(nir_band, red_band)

            # store all values

            # Normalize and Clip Indices
            cal_ndvi_values = np.clip(ndvi_values, -1, 1)
            cal_evi_values = np.clip(evi_values, -1, 1)
            cal_savi_values = np.clip(savi_values, -1, 1)

            if index == "NDVI":
                vegetation_index = cal_ndvi_values
            elif index == "EVI":
                vegetation_index = cal_evi_values
            else:
                vegetation_index = cal_savi_values

            cmap = plt.cm.RdYlGn
            norm = mcolors.Normalize(vmin=-1, vmax=1)
            vegetation_index_color = cmap(norm(vegetation_index))

            # Normalize and convert vegetation index image to PNG format
            vegetation_index_8bit = (vegetation_index_color[:, :, :3] * 255).astype(
                np.uint8
            )  # Remove alpha channel
            vegetation_pil = Image.fromarray(vegetation_index_8bit)

            # Save as PNG into BytesIO object
            vegetation_bytes = io.BytesIO()
            vegetation_pil.save(vegetation_bytes, format="PNG")
            vegetation_bytes.seek(0)  # Move pointer to start

            # Display NDVI/EVI/SAVI Image
            st.markdown(
                f"<h3 style='text-align: left; color: #b2beb5;'>{index} Image </h3>",
                unsafe_allow_html=True,
            )
            st.image(vegetation_index_color, use_column_width=True)

            # Info textbox
            st.markdown(
                f"<p style='font-size:21px;'><b>{index}: {image_descriptions[index]['short']}</b></p>",
                unsafe_allow_html=True,
            )

            # Add download button directly below NDVI/EVI/SAVI Image
            st.download_button(
                label=f"Download {index} Image",
                data=vegetation_bytes,
                file_name=f"{index.lower()}_image.png",
                mime="image/png",
            )

            st.markdown(
                "<hr style='border: 1px solid #f0ffff; margin-top:20px; margin-bottom:20px;'>",
                unsafe_allow_html=True,
            )

            # --------- Time Line Graph ---------

            # Generate Date Range
            dates = [
                start_date + datetime.timedelta(days=i)
                for i in range((end_date - start_date).days + 1)
            ]
            actual_values = calculate_ndvi(nir_band, red_band).flatten()[: len(dates)]

            st.markdown(
                f"<h3 style='text-align: left; color: #b2beb5;'>{index} Time-Line Graph</h3>",
                unsafe_allow_html=True,
            )

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=actual_values,
                    mode="lines+markers",
                    line=dict(color="green", width=2),
                    marker=dict(size=8, color="red"),
                    name=f"{index} Values",
                )
            )

            fig.update_layout(
                title=dict(
                    text=f"🌿 {index} Trend for {st.session_state.location_input}",
                    font=dict(size=18, color="#4CAF50"),
                    x=0.5,
                    xanchor="center",
                ),
                xaxis_title="Date",
                yaxis_title=f"{index} Value",
                xaxis=dict(
                    tickformat="%d/%m",
                    tickangle=-45,
                    showgrid=True,
                    gridwidth=0.5,
                    gridcolor="lightgrey",
                ),
                yaxis=dict(showgrid=True, gridcolor="lightgrey"),
                legend=dict(font=dict(size=13)),
                plot_bgcolor="rgba(0,0,0,0)",
            )

            st.plotly_chart(fig, use_container_width=True)

            # Generate CSV
            graph_df = pd.DataFrame({"Date": dates, f"{index}": actual_values})
            graph_csv = add_timestamp(graph_df)
            # Add CSV download button
            st.download_button(
                label=f"Download {index} Graph Data as CSV",
                data=graph_csv,
                file_name=f"{index.lower()}_graph_data.csv",
                mime="text/csv",
            )

            # Graph DB Saving Button
            if st.button(f"Save {index} Graph Data to Database"):
                save_graph_to_db(
                    f"{index}_Graph_{st.session_state.location_input}",
                    st.session_state.location_input,
                    pd.DataFrame({"Date": dates, f"{index} Value": actual_values}),
                    report_type=index,
                )

            st.markdown(
                "<hr style='border: 1px solid #f0ffff; margin-top:20px; margin-bottom:20px;'>",
                unsafe_allow_html=True,
            )

            # --------- HISTOGRAM ---------

            st.markdown(
                f"<h3 style='text-align: left; color: #b2beb5;'>{index} Value Distribution</h3>",
                unsafe_allow_html=True,
            )

            # Frequency distribution histogram
            freq_index = vegetation_index.flatten()
            freq_index = freq_index[~np.isnan(freq_index)]  # Remove NaN values

            # Convert data to a Pandas DataFrame
            df = pd.DataFrame({f"{index} Value": freq_index})

            # Compute Histogram Statistics Before Displaying
            mean_value = np.mean(freq_index)
            median_value = np.median(freq_index)
            std_dev_value = np.std(freq_index)
            min_value = np.min(freq_index)
            max_value = np.max(freq_index)

            # Create an interactive histogram using Plotly
            fig = px.histogram(
                df, x=f"{index} Value", nbins=50, color_discrete_sequence=["green"]
            )

            fig.update_layout(
                title=dict(
                    text=f"🌿 {index} Frequency Distribution for {st.session_state.location_input} ",
                    font=dict(size=20, color="#4CAF50"),
                    x=0.5,
                    xanchor="center",
                ),
                xaxis_title=f"{index} Value",
                yaxis_title="Frequency",
                bargap=0.1,
            )
            # Display Plotly chart in Streamlit
            st.plotly_chart(fig, use_container_width=True)

            # Display computed statistics
            with st.expander(
                f"📊 {index} Frequency Distribution Statistics:", expanded=False
            ):
                st.markdown(
                    f"""
                    <style>
                        .custom-statis-box {{
                            background-color: rgba(32, 60, 80, 0.2); 
                            padding: 10px;
                            border-radius: 8px;
                            border-left: 2px solid #1f77b4;
                            color: white; /* Text color */
                            font-size: 19px;
                        }}
                        .custom-statis-box ol {{
                            padding-left: 20px;
                        }}
                        
                    </style>

                    <div class="custom-statis-box">
                        <ol>
                            <li><b>Mean {index} value = </b> {mean_value:.4f}</li>
                            <li><b>Median {index} value = </b> {median_value:.4f}</li>
                            <li><b>Standard Deviation value = </b> {std_dev_value:.4f}</li>
                            <li><b>Minimun {index} value = </b> {min_value:.4f}</li>
                            <li><b>Maximum {index} value = </b> {max_value:.4f}</li>
                        </ol>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Generate CSV
            histogram_csv = add_timestamp(df)

            # Add CSV download button for histogram
            st.download_button(
                label=f"Download {index} Histogram Data as CSV",
                data=histogram_csv,
                file_name=f"{index} histogram_data.csv",
                mime="text/csv",
            )

            # Histogram DB Saving Button
            if st.button(f"Save {index} Histogram Data to Database"):
                save_histogram_to_db(
                    f"{index}_Histogram_{st.session_state.location_input}",
                    st.session_state.location_input,
                    data=df,
                    report_type=index,
                    median=median_value,
                    mean=mean_value,
                    std_dev=std_dev_value,
                    min_value=min_value,
                    max_value=max_value,
                )

            st.markdown(
                "<hr style='border: 1px solid #f0ffff; margin-top:20px; margin-bottom:20px;'>",
                unsafe_allow_html=True,
            )

            # -----------------------------

            # Extract NDVI shape for Grid Dimensions
            height, width = vegetation_index.shape

            # Define latitude and longitude range
            lat_range = 0.05
            lon_range = 0.05

            # Set min and max values for latitude and longitude
            latitude_min, latitude_max = latitude - lat_range, latitude + lat_range
            longitude_min, longitude_max = longitude - lon_range, longitude + lon_range

            # Create Longitude and Latitude Arrays
            lon_values = np.linspace(longitude_min, longitude_max, width)
            lat_values = np.linspace(latitude_min, latitude_max, height)
            lat_values_flip = np.flip(lat_values)

            # Create Meshgrid for Proper Mapping
            lon_grid, lat_grid = np.meshgrid(lon_values, lat_values_flip)

            # Flatten the Data
            flattened_ndvi = vegetation_index.flatten()
            flattened_evi = vegetation_index.flatten()
            flattened_savi = vegetation_index.flatten()
            flattened_lat = lat_grid.flatten()
            flattened_lon = lon_grid.flatten()

            # ------------ 3D Surface Plot -----------

            st.markdown(
                f"<h3 style='text-align: left; color: #b2beb5;'>{index} 3D Surface Plot</h3>",
                unsafe_allow_html=True,
            )

            veg_data_surface = vegetation_index

            colorscale_reversed = "YlGnBu_r"

            # Create 3D Surface Plot
            fig = go.Figure(
                data=[
                    go.Surface(
                        x=lon_grid,
                        y=lat_grid,
                        z=veg_data_surface,
                        colorscale=colorscale_reversed,
                        cmin=-1,
                        cmax=1,
                    )
                ]
            )

            fig.update_layout(
                title=dict(
                    text=f"🌿 {index} 3D Surface Visualization for {st.session_state.location_input} ",
                    font=dict(size=20, color="#4CAF50"),
                    x=0.5,
                    xanchor="center",
                ),
                scene=dict(
                    xaxis=dict(
                        title=f"Longitude : {longitude}",
                        gridcolor="lightgray",
                        gridwidth=0.4,
                    ),
                    yaxis=dict(
                        title=f"Latitude : {latitude}",
                        gridcolor="lightgray",
                        gridwidth=0.4,
                    ),
                    zaxis=dict(
                        title=f"{index} Value",
                        range=[-1, 1],
                        gridcolor="lightgray",
                        gridwidth=0.4,
                    ),
                ),
                width=1000,
                height=700,
            )

            st.plotly_chart(fig, use_container_width=True)

            # Generate CSV File
            csv_data = add_timestamp(df)

            # Add CSV Download Button for 3D surface plot
            st.download_button(
                label=f"Download {index} Surface Plot Data as CSV",
                data=csv_data,
                file_name=f"{index} 3D_Surface_Plot_data.csv",
                mime="text/csv",
            )
            
            #------
            # Create DataFrame for saving to DB and exporting
            df_surface = pd.DataFrame({
                f"{index} Value": flattened_ndvi,
                "Latitude": flattened_lat,
                "Longitude": flattened_lon,
            })

            # 3D Surface Plot DB Saving Button
            if st.button(f"Save {index} Surface Plot Data to Database"):
                save_surfaceData_to_db(
                    f"{index}_3D_Surface_Plot_{st.session_state.location_input}",
                    st.session_state.location_input,
                    data=df_surface,
                    report_type=index,
                )

            st.markdown(
                "<hr style='border: 1px solid #f0ffff; margin-top:20px; margin-bottom:20px;'>",
                unsafe_allow_html=True,
            )

            # ---------- HEATMAP -----------

            st.markdown(
                f"<h3 style='text-align: left; color: #b2beb5;'>{index} Heatmap Visualizations</h3>",
                unsafe_allow_html=True,
            )

            # Create Tabs for different views
            tab1, tab2 = st.tabs(
                [
                    f"{index} Spatial Data Heatmap",
                    f"{index} Interactive spatial Heatmap",
                ]
            )

            with tab1:

                # NDVI Data
                vegetation_index = np.nan_to_num(
                    vegetation_index, nan=0
                )  # Replace NaN with 0 or -1 as dataloss may happen
                vegetation_index = np.flipud(vegetation_index)
                # ndvi_normalized = (vegetation_index + 1) / 2  # Shifts -1 to 1 → 0 to 1

                # Create a Heatmap
                fig = go.Figure(
                    data=go.Heatmap(
                        z=vegetation_index,
                        # z=ndvi_normalized,
                        colorscale=[
                            [0.0, "lightblue"],  # -1 NDVI (Water)
                            [0.3, "yellow"],  #  0 NDVI (Bare Land)
                            [0.5, "orange"],  #  0.3 NDVI (Sparse Vegetation)
                            [0.8, "green"],  #  0.6 NDVI (Moderate Vegetation)
                            [1.0, "darkgreen"],  #  1 NDVI (Dense Vegetation)
                        ],
                        colorbar=dict(title="NDVI Values Range"),
                        zmin=-1,
                        zmax=1,
                        # zmin=0, zmax=1, #normalized range
                    )
                )

                fig.update_layout(
                    title=dict(
                        text=f"{index} Heatmap for {st.session_state.location_input} ",
                        font=dict(size=21, color="white"),
                        x=0.5,  # Centers the title
                        xanchor="center",  # Ensures alignment
                    ),
                    xaxis_title=f"Longitude : {longitude}",
                    yaxis_title=f"Latitude : {latitude}",
                    height=700,
                    width=1000,
                )
                st.plotly_chart(fig, use_container_width=True)

                # Convert to Pandas DataFrame
                df = pd.DataFrame(
                    {
                        "Latitude": flattened_lat,
                        "Longitude": flattened_lon,
                        f"{index} Value": flattened_ndvi,
                    }
                )
                # Generate CSV File
                csv_data = add_timestamp(df)

                # Add CSV Download Button for heatmap
                st.download_button(
                    label=f"Download {index} Heatmap Data as CSV",
                    data=csv_data,
                    file_name=f"{index} heatmap_data.csv",
                    mime="text/csv",
                )
                # Heatmap DB Saving Button
                if st.button(f"Save {index} Heatmap Data to Database"):
                    save_heatmap_to_db(
                        f"{index}_heatmap_{st.session_state.location_input}",
                        st.session_state.location_input,
                        data=df,
                        report_type=index,
                    )

                st.markdown(
                    "<hr style='border: 1px solid #f0ffff; margin-top:20px; margin-bottom:20px;'>",
                    unsafe_allow_html=True,
                )

            with tab2:

                # -------------- Folium Heatmap -------------

                st.markdown(
                    f"<h4 style='text-align: center; color: white;'>{index} Vegetation Density Heatmap of:&nbsp {st.session_state.location_input}</h4>",
                    unsafe_allow_html=True,
                )

                # Create DataFrame
                fh_df = pd.DataFrame(
                    {
                        "Latitude": flattened_lat,
                        "Longitude": flattened_lon,
                        f"{index} Value": flattened_ndvi,
                    }
                )

                # Create Folium Map Centered on Average Lat/Lon
                m = folium.Map(
                    location=[np.mean(flattened_lat), np.mean(flattened_lon)],
                    zoom_start=12,
                )

                # Add the heatmap layer
                heat_data = list(
                    zip(fh_df["Latitude"], fh_df["Longitude"], fh_df[f"{index} Value"])
                )

                HeatMap(
                    heat_data,
                    radius=9,  # Adjust the spread of heat points
                    blur=10,  # Softens the edges for a smoother appearance
                    min_opacity=0.2,  # Sets the minimum transparency level
                    max_zoom=13,  # Improves clarity when zooming in
                ).add_to(m)

                # Show Map
                st.components.v1.html(m._repr_html_(), height=750)

                st.markdown(
                    "<hr style='border: 1px solid #f0ffff; margin-top:20px; margin-bottom:20px;'>",
                    unsafe_allow_html=True,
                )

            # ----------- KDE Chart---------------

            st.markdown(
                f"<h3 style='text-align: left; color: #b2beb5;'>{index} Kernel Density Estimation Line Chart</h3>",
                unsafe_allow_html=True,
            )

            compute_and_store_indices(nir_band, red_band, green_band)

            kde_ndvi_data = st.session_state.index_data["NDVI"]
            kde_evi_data = st.session_state.index_data["EVI"]
            kde_savi_data = st.session_state.index_data["SAVI"]

            # Function to compute KDE for smooth line charts
            def compute_kde(data):
                kde = gaussian_kde(data)
                x_vals = np.linspace(min(data), max(data), 100)  # X-axis values
                y_vals = kde(x_vals)  # Density values
                return x_vals, y_vals

            # Compute KDE for each index
            ndvi_x, ndvi_y = compute_kde(kde_ndvi_data)
            evi_x, evi_y = compute_kde(kde_evi_data)
            savi_x, savi_y = compute_kde(kde_savi_data)

            # Find peak points (highest density values)
            ndvi_peak_x = ndvi_x[ndvi_y.argmax()]
            ndvi_peak_y = max(ndvi_y)

            evi_peak_x = evi_x[evi_y.argmax()]
            evi_peak_y = max(evi_y)

            savi_peak_x = savi_x[savi_y.argmax()]
            savi_peak_y = max(savi_y)

            # Create Tabs for different views
            tab1, tab2 = st.tabs(
                [f"{index} - KDE Distribution", " Comparative Analysis"]
            )

            with tab1:

                # Display the selected index chart
                fig = go.Figure()
                if index == "NDVI":
                    fig.add_trace(
                        go.Scatter(
                            x=ndvi_x,
                            y=ndvi_y,
                            mode="lines",
                            name="NDVI",
                            line=dict(color="green", width=2),
                        )
                    )
                    fig.add_annotation(
                        x=ndvi_peak_x,
                        y=ndvi_peak_y,
                        text=f"NDVI Peak: {ndvi_peak_x:.2f}",
                        showarrow=True,
                        arrowhead=2,
                        ax=20,
                        ay=-40,
                        font=dict(color="green"),
                    )

                elif index == "EVI":
                    fig.add_trace(
                        go.Scatter(
                            x=evi_x,
                            y=evi_y,
                            mode="lines",
                            name="EVI",
                            line=dict(color="blue", width=2),
                        )
                    )
                    fig.add_annotation(
                        x=evi_peak_x,
                        y=evi_peak_y,
                        text=f"EVI Peak: {evi_peak_x:.2f}",
                        showarrow=True,
                        arrowhead=2,
                        ax=20,
                        ay=-40,
                        font=dict(color="blue"),
                    )

                else:
                    fig.add_trace(
                        go.Scatter(
                            x=savi_x,
                            y=savi_y,
                            mode="lines",
                            name="SAVI",
                            line=dict(color="red", width=2),
                        )
                    )
                    fig.add_annotation(
                        x=savi_peak_x,
                        y=savi_peak_y,
                        text=f"SAVI Peak: {savi_peak_x:.2f}",
                        showarrow=True,
                        arrowhead=2,
                        ax=20,
                        ay=-40,
                        font=dict(color="red"),
                    )

                fig.update_layout(
                    title=f"{index} Vegetation Index Distribution",
                    xaxis_title=f"{index} Index Value",
                    yaxis_title="Density",
                )
                st.plotly_chart(fig)

                st.markdown(
                    "<hr style='border: 1px solid #f0ffff; margin-top:20px; margin-bottom:20px;'>",
                    unsafe_allow_html=True,
                )
            with tab2:

                # Create figure
                fig = go.Figure()

                # Add KDE lines
                fig.add_trace(
                    go.Scatter(
                        x=ndvi_x,
                        y=ndvi_y,
                        mode="lines",
                        name="NDVI",
                        line=dict(color="green", width=2),
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x=evi_x,
                        y=evi_y,
                        mode="lines",
                        name="EVI",
                        line=dict(color="blue", width=2),
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x=savi_x,
                        y=savi_y,
                        mode="lines",
                        name="SAVI",
                        line=dict(color="red", width=2),
                    )
                )

                # Add Annotations for Peak Values
                fig.add_annotation(
                    x=ndvi_peak_x,
                    y=ndvi_peak_y,
                    text=f"NDVI Peak: {ndvi_peak_x:.2f}",
                    showarrow=True,
                    arrowhead=2,
                    ax=20,
                    ay=-40,
                    font=dict(color="green"),
                )

                fig.add_annotation(
                    x=evi_peak_x,
                    y=evi_peak_y,
                    text=f"EVI Peak: {evi_peak_x:.2f}",
                    showarrow=True,
                    arrowhead=2,
                    ax=20,
                    ay=-40,
                    font=dict(color="blue"),
                )

                fig.add_annotation(
                    x=savi_peak_x,
                    y=savi_peak_y,
                    text=f"SAVI Peak: {savi_peak_x:.2f}",
                    showarrow=True,
                    arrowhead=2,
                    ax=20,
                    ay=-40,
                    font=dict(color="red"),
                )

                # Add title and labels
                fig.update_layout(
                    title="Comparative Vegetation Index distributions of - NDVi/EVI/SAVI",
                    xaxis_title="Vegetation Index Values",
                    yaxis_title="Density",
                )

                # Show plot
                st.plotly_chart(fig)

                st.markdown(
                    "<hr style='border: 1px solid #f0ffff; margin-top:20px; margin-bottom:20px;'>",
                    unsafe_allow_html=True,
                )

    st.sidebar.markdown(
        """
        <br><div style="height: 1px; background: linear-gradient(to right, #ff7e5f, #feb47b);"></div><br>
    """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        """
        <style>
        .custom-link {
            text-align: center;
            font-size: 15px;
            color: white !important; 
            text-decoration: none !important; 
            transition: all 0.3s ease-in-out;
        }
        .custom-link:hover {
            font-size: 16px; /* Slightly bigger on hover */
            text-decoration: underline !important; /* Underline appears on hover */
            color: #FFFFFF;  /* Light green glow effect */
            text-shadow: 0px 0px 8px ##FFFFFF;
        }
        </style>
        
        <p style="text-align: center;">
            <a class="custom-link" href="https://en.wikipedia.org/wiki/Normalized_difference_vegetation_index" target="_blank">
                NDVI
            </a> 
            &nbsp;&nbsp;&nbsp;  <!-- Extra spaces -->
            | 
            &nbsp;&nbsp;&nbsp;  <!-- Extra spaces -->
            <a class="custom-link" href="https://custom-scripts.sentinel-hub.com/custom-scripts/sentinel-2/ndvi" target="_blank">
                Sentinel Hub
            </a>
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("💡 Feedback")

    feedback = st.text_area(
        "Got ideas or feedback? We'd love to hear from you—together, we can make this project even better.",
        value=st.session_state.feedback,
        key="feedback_input",
    )

    if st.button("Submit Feedback"):
        if feedback:
            st.success("Thank you for your feedback! 🙌")
            save_feedback_to_db(feedback)

            # Clear the text area after submission
            st.session_state.feedback = ""
            st.rerun()  # Force rerun to reflect the change
        else:
            st.warning("Please enter your feedback before submitting.")
