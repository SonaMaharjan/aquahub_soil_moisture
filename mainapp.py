import streamlit as st
import folium
from folium.plugins import Draw
from streamlit_folium import st_folium
import rasterio
from rasterio.mask import mask
from shapely.geometry import Polygon, box
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import tempfile
import os
from pyproj import Transformer

st.set_page_config(page_title="AquaHub – Soil Moisture Map", layout="wide")
st.title("🌧️ AquaHub - Soil Moisture")
st.markdown("Draw a polygon to see the moisture intensity map (150 = dry, 200 = moderate, 250 = wet).")

# ---------- Helper functions ----------
def transform_coords(coords, from_crs, to_crs):
    transformer = Transformer.from_crs(from_crs, to_crs, always_xy=True)
    return [list(transformer.transform(x, y)) for x, y in coords]

def get_raster_footprint_4326(raster_path):
    with rasterio.open(raster_path) as src:
        bounds = src.bounds
        raster_crs = src.crs
        if raster_crs is None:
            st.error("Raster has no CRS.")
            return None
        transformer = Transformer.from_crs(raster_crs, "EPSG:4326", always_xy=True)
        corners = [
            (bounds.left, bounds.bottom), (bounds.right, bounds.bottom),
            (bounds.right, bounds.top), (bounds.left, bounds.top),
            (bounds.left, bounds.bottom)
        ]
        corners_4326 = [transformer.transform(x, y) for x, y in corners]
        return Polygon(corners_4326)

def classify_and_get_numeric(r, g, b):
    """
    Classify pixel and return a numeric value:
    dry -> 150, moderate -> 200, wet -> 250
    """
    if r > 1 or g > 1 or b > 1:
        r, g, b = r/255.0, g/255.0, b/255.0
    
    # Dry (red-dominant)
    if r > g and r > b and r > 0.4:
        return 150
    # Wet (blue-dominant)
    elif b > g and b > r and b > 0.4:
        return 250
    # Moderate (green-dominant or mixed)
    else:
        return 200

def clip_and_create_numeric_map(raster_path, polygon_coords_4326):
    """Clip RGB raster and create a numeric map (150,200,250)."""
    if not polygon_coords_4326 or len(polygon_coords_4326) < 3:
        return None, None, None

    with rasterio.open(raster_path) as src:
        raster_crs = src.crs
        if raster_crs is None:
            st.error("Raster has no CRS.")
            return None, None, None
        raster_crs_str = raster_crs.to_string() if hasattr(raster_crs, 'to_string') else str(raster_crs)
        
        transformed_coords = transform_coords(polygon_coords_4326, "EPSG:4326", raster_crs_str)
        poly = Polygon(transformed_coords)
        
        # Check overlap
        raster_bounds = src.bounds
        poly_bounds = poly.bounds
        if not (poly_bounds[0] < raster_bounds[2] and poly_bounds[2] > raster_bounds[0] and
                poly_bounds[1] < raster_bounds[3] and poly_bounds[3] > raster_bounds[1]):
            st.error("❌ Polygon does not overlap raster extent.")
            return None, None, None
        
        out_image, out_transform = mask(src, [poly], crop=True)
        if out_image.shape[0] < 3:
            st.error(f"Raster has {out_image.shape[0]} bands – expected 3 (RGB).")
            return None, None, None
        
        r_band = out_image[0]
        g_band = out_image[1]
        b_band = out_image[2]
        h, w = r_band.shape
        
        # Create numeric map
        numeric_map = np.zeros((h, w), dtype=np.uint8)
        dry = wet = mod = 0
        
        for i in range(h):
            for j in range(w):
                val = classify_and_get_numeric(r_band[i,j], g_band[i,j], b_band[i,j])
                numeric_map[i,j] = val
                if val == 150:
                    dry += 1
                elif val == 200:
                    mod += 1
                else:  # 250
                    wet += 1
        
        total = dry + mod + wet
        if total == 0:
            return None, None, None
        
        dry_pct = dry / total * 100
        mod_pct = mod / total * 100
        wet_pct = wet / total * 100
        
        return numeric_map, (dry_pct, mod_pct, wet_pct), (dry, mod, wet)

# ---------- Raster file selection ----------
st.sidebar.header("📁 Upload RGB GeoTIFF")
uploaded_file = st.sidebar.file_uploader("Upload GeoTIFF (.tif)", type=["tif", "tiff"])

raster_path = None
raster_footprint = None

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tif") as tmp:
        tmp.write(uploaded_file.getvalue())
        raster_path = tmp.name
    st.sidebar.success("Raster loaded")
    raster_footprint = get_raster_footprint_4326(raster_path)
else:
    DEFAULT_RASTER_PATH = "soil_moisture_rgb.tif"
    if os.path.exists(DEFAULT_RASTER_PATH):
        raster_path = DEFAULT_RASTER_PATH
        st.sidebar.success(f"Using default: {DEFAULT_RASTER_PATH}")
        raster_footprint = get_raster_footprint_4326(raster_path)
    else:
        st.sidebar.error("Please upload an RGB GeoTIFF.")

# ---------- Map with drawing and footprint ----------
st.sidebar.markdown("---")
st.sidebar.markdown("## 🗺️ Draw Polygon")
st.sidebar.info("Draw polygon, double‑click to finish.")

if raster_footprint is not None:
    center_lat = raster_footprint.centroid.y
    center_lon = raster_footprint.centroid.x
else:
    center_lat, center_lon = 53.3498, -6.2603

m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles="CartoDB positron")

if raster_footprint is not None:
    folium.GeoJson(
        data=raster_footprint.__geo_interface__,
        style_function=lambda x: {'color': 'red', 'weight': 2, 'fillOpacity': 0.1},
        name="Raster Footprint"
    ).add_to(m)

draw = Draw(draw_options={"polygon": {"allowIntersection": False}})
draw.add_to(m)
map_output = st_folium(m, width=800, height=500)

polygon_coords_4326 = None
if map_output and map_output.get("last_active_drawing"):
    geom = map_output["last_active_drawing"]["geometry"]
    if geom["type"] == "Polygon":
        polygon_coords_4326 = geom["coordinates"][0]
        lats = [p[1] for p in polygon_coords_4326]
        lngs = [p[0] for p in polygon_coords_4326]
        clat, clng = sum(lats)/len(lats), sum(lngs)/len(lngs)
        st.sidebar.success(f"Polygon centroid: {clat:.5f}, {clng:.5f}")

# ---------- Manual override ----------
st.sidebar.markdown("---")
use_manual = st.sidebar.checkbox("Use manual bounding box")
if use_manual:
    col1, col2 = st.sidebar.columns(2)
    with col1:
        minx = st.number_input("West (lon)", -6.35, format="%.5f")
        miny = st.number_input("South (lat)", 53.30, format="%.5f")
    with col2:
        maxx = st.number_input("East (lon)", -6.20, format="%.5f")
        maxy = st.number_input("North (lat)", 53.40, format="%.5f")
    polygon_coords_4326 = [[minx, miny], [maxx, miny], [maxx, maxy], [minx, maxy], [minx, miny]]

# ---------- Run analysis ----------
if st.sidebar.button("💧 Extract Soil Moisture", type="primary", use_container_width=True):
    if raster_path is None:
        st.error("No raster file.")
    elif polygon_coords_4326 is None:
        st.error("Draw a polygon or enable manual bbox.")
    else:
        with st.spinner("Creating numeric moisture map..."):
            num_map, percentages, counts = clip_and_create_numeric_map(raster_path, polygon_coords_4326)
            if num_map is not None:
                dry_pct, mod_pct, wet_pct = percentages
                dry_cnt, mod_cnt, wet_cnt = counts
                st.session_state['num_map'] = num_map
                st.session_state['dry_pct'] = dry_pct
                st.session_state['mod_pct'] = mod_pct
                st.session_state['wet_pct'] = wet_pct
                st.session_state['dry_cnt'] = dry_cnt
                st.session_state['mod_cnt'] = mod_cnt
                st.session_state['wet_cnt'] = wet_cnt
                st.success("Map generated!")
            else:
                st.error("Processing failed.")

# ---------- Display results ----------
if 'num_map' in st.session_state:
    num_map = st.session_state['num_map']
    dry_pct = st.session_state['dry_pct']
    mod_pct = st.session_state['mod_pct']
    wet_pct = st.session_state['wet_pct']
    dry_cnt = st.session_state['dry_cnt']
    mod_cnt = st.session_state['mod_cnt']
    wet_cnt = st.session_state['wet_cnt']
    
    st.markdown("---")
    st.subheader("📊 Soil Moisture Index")
    col1, col2, col3 = st.columns(3)
    col1.metric("💧 Wet (250)", f"{wet_pct:.1f}%", f"{wet_cnt} pixels")
    col2.metric("🌿 Moderate (200)", f"{mod_pct:.1f}%", f"{mod_cnt} pixels")
    col3.metric("🏜️ Dry (150)", f"{dry_pct:.1f}%", f"{dry_cnt} pixels")
    
    # Risk classification
    if wet_pct > 50:
        risk = "HIGH"
        condition = "High soil moisture -> infiltration unlikely. Engineered drainage required."
        color = "red"
    elif wet_pct > 25:
        risk = "MEDIUM"
        condition = "Moderate moisture –> BRE365 soakaway test (or percolation test) test recommended."
        color = "orange"
    else:
        risk = "LOW"
        condition = "Low moisture –> standard surface water drainage acceptable."
        color = "green"
    
    st.markdown(f"### Risk Level: <span style='color:{color}; font-weight:bold'>{risk}</span>", unsafe_allow_html=True)
    st.info(f"📌 **Draft Planning Condition:** {condition}")
    
    # Display the blue map with numeric colorbar
    st.subheader("🗺️ Clipped Soil Moisture Layer")
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(num_map, cmap='Blues', vmin=150, vmax=250, interpolation='nearest')
    cbar = plt.colorbar(im, ax=ax, ticks=[150, 200, 250])
    cbar.set_label('Soil moisture index (unitless)')
    ax.set_title("Soil Moisture over selected area")
    ax.axis('off')
    st.pyplot(fig)
    
    st.caption("Blue shade: lighter = drier (150), darker = wetter (250). Based on RGB classification.")
else:
    st.info("👈 Upload an RGB GeoTIFF, draw a polygon, then click 'Generate Blue Map'.")