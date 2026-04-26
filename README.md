# 🌧️ AquaScan – Interactive Soil Moisture Viewer for Irish Planning

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://aquascan.streamlit.app) *(replace with your deployed URL)*

AquaScan is a **decision‑support prototype** for Irish planning authorities. It helps planning officers quickly assess soil moisture conditions over a proposed development site using **satellite‑derived Copernicus data** (exported as an RGB GeoTIFF from QGIS) and **interactive map drawing**.

The app classifies the area into **dry**, **moderate**, and **wet** zones, displays a **blue intensity map**, and generates **draft planning conditions** based on Irish regulations (BRE365, GDSDS, OPW guidelines).

---

## 📖 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [How It Works](#how-it-works)
- [Data Requirements](#data-requirements)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [Methodology & Regulatory Context](#methodology--regulatory-context)
- [Project Structure](#project-structure)
- [Future Improvements](#future-improvements)
- [License](#license)

---

## Overview

Irish planning authorities often lack independent, real‑time environmental data when assessing planning applications. AquaScan demonstrates how **space technology** (Copernicus Sentinel‑1/2, CLMS) can provide immediate, objective soil moisture information.

This version uses a **pre‑processed RGB GeoTIFF** (exported from QGIS) where:

- **Red** = dry areas  
- **Green** = moderate moisture  
- **Blue** = wet areas  

By drawing a polygon on an interactive map, the user obtains:

- **Percentage** of dry/moderate/wet pixels in the selected area.
- A **blue‑scale moisture map** (light blue = drier, dark blue = wetter).
- A **risk level** (LOW / MEDIUM / HIGH) and a **draft planning condition** referencing Irish standards (BRE365, GDSDS).

---

## Features

✅ **Interactive map** – Draw any polygon (development site boundary).  
✅ **Local GeoTIFF support** – Upload your own RGB moisture map (exported from QGIS).  
✅ **Automatic CRS handling** – Supports EPSG:3857 (Web Mercator) and reprojects user polygons accordingly.  
✅ **Colour‑based classification** – Each pixel classified as dry (red‑dominant), moderate (green‑dominant), or wet (blue‑dominant).  
✅ **Continuous blue output map** – Light blue (dry) → dark blue (wet), with a numeric colourbar.  
✅ **Risk & condition generation** – Outputs a draft planning condition based on wet area percentage and Irish regulations.  
✅ **Raster footprint overlay** – Shows where your data covers on the map, avoiding out‑of‑range errors.  
✅ **Manual bounding box** – Fallback if drawing is not possible.

---

## How It Works

1. **Upload** an RGB GeoTIFF (e.g., from Copernicus CLMS styled in QGIS).
2. **Draw** a polygon on the map (or enter manual coordinates).
3. The app **clips** the raster to the polygon (after transforming coordinates to the raster’s CRS).
4. **Pixel classification** – Each pixel is labelled dry/moderate/wet by comparing RGB channel dominance.
5. **Numeric mapping** – Dry → 150, Moderate → 200, Wet → 250 (for the blue colourbar).
6. **Display**:
   - Percentage breakdown of classes.
   - Blue‑scale image of the clipped area with a colourbar.
   - Risk level and draft planning condition.
7. (Optional) The raster footprint (red rectangle) helps you see where data exists.

---

## Data Requirements

- **Input**: A **3‑band RGB GeoTIFF** (GeoTIFF with 3 colour bands) where:
  - Red channel dominates in dry areas.
  - Green channel dominates in moderate areas.
  - Blue channel dominates in wet areas.
- Typical sources:
  - Copernicus CLMS Surface Soil Moisture (SSM) or Soil Water Index (SWI) exported from QGIS with a **colour‑stretched style** (red‑dry, green‑moderate, blue‑wet).
  - Any RGB map where colours correspond to moisture classes (even a hand‑drawn overlay).

> ⚠️ This prototype works with **colour visualisations**, not raw single‑band numerical rasters. For real soil moisture in m³/m³, please use the original Copernicus numerical products.

---

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/aquascan.git
cd aquascan# aquahub_soil_moisture
