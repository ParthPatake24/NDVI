# 🌱 NDVI Analysis and Visualization Platform

## 📌 Overview

This project is a **web-based system for automated vegetation analysis**, using the Normalized Difference Vegetation Index (NDVI), along with EVI and SAVI. It integrates:

* **Sentinel Hub**: to dynamically fetch Sentinel-2 satellite imagery.
* **OpenStreetMap (OSM)**: for intuitive, interactive geographic location selection.
* **Streamlit**: for building an interactive dashboard.
* **SQLite**: for temporary structured data storage.

Users can select locations on a map, compute vegetation indices in real-time, visualize results (NDVI, EVI, SAVI), explore histograms, heatmaps, KDE plots, 3D surface plots, and download CSV reports.

---

## 🎯 Features

✅ **Dynamic satellite imagery retrieval** (Sentinel-2 via Sentinel Hub API).
✅ **Interactive map interface** (OSM for easy location selection).
✅ **Multi-index computation**:

* NDVI = (NIR - Red) / (NIR + Red)
* EVI = G \* (NIR - Red) / (NIR + C1*Red - C2*Blue + L)
* SAVI = (NIR - Red) / (NIR + Red + L) × (1 + L)

✅ **Data visualizations**:

* True Color, Infrared, NDVI raster plots
* Histograms, KDE probability density plots
* Heatmaps on OSM
* 3D surface plots of vegetation indices

✅ **Session-based SQLite storage** for query data & plots.
✅ **CSV download** of computed results.

---

## 🚀 How it works

1. **User selects a region** on an OpenStreetMap interface.
2. **Sentinel Hub API** fetches satellite imagery (bands B2, B4, B8).
3. **Vegetation indices** (NDVI, EVI, SAVI) are computed on-the-fly.
4. **Streamlit dashboard** visualizes:

   * Color-coded index maps
   * Histograms, KDE plots, heatmaps, 3D surfaces
5. **SQLite stores session data**; users can export results as CSV.

---

## 🔧 Tech Stack

* **Backend**: Python (Pandas, Numpy, Requests)
* **Satellite processing**: Sentinel Hub API (Sentinel-2)
* **Database**: SQLite (for session storage)
* **Visualization**: Streamlit, Matplotlib, Plotly, Folium
* **Map / Geocoding**: OpenStreetMap Nominatim
* **Deployment (future scope)**: Cloud platform (AWS/GCP/Azure)

---

## 📈 Future Enhancements

* Move from local SQLite to a **full-scale relational database** for persistent user report storage.
* **Secure user authentication** & dashboards to track historical vegetation data.
* **Cloud deployment** for high-speed, real-time large-scale processing.
* Support more indices (GCI, ARVI) for advanced environmental studies.

---

## 📝 Running the project

```bash
pip install streamlit pandas numpy requests folium matplotlib plotly sqlite3
streamlit run app.py
```

Replace `app.py` with your Streamlit entry file.

