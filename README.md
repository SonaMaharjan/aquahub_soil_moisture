# 🌧️ AquaScan: Soil Moisture Spatial Analysis for Irish Planning

AquaScan is a technical prototype designed for Irish planning authorities to evaluate soil moisture conditions on proposed development sites. It utilizes satellite-derived imagery (Copernicus) to classify land into moisture zones and generate regulatory-aligned planning conditions.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://aquaappsoilmoisture-4ffds6yaknqk6ajzu8dgh9.streamlit.app/)

## 📖 Table of Contents
* [Overview](#overview)
* [Technical Features](#technical-features)
* [Methodology](#methodology)
* [Risk Assessment Logic](#risk-assessment-logic)
* [Data Requirements](#data-requirements)
* [Installation & Setup](#installation--setup)

---

## Overview
Irish planning authorities often lack independent, real-time environmental data for site assessments. AquaScan demonstrates how **Copernicus Sentinel data** can provide immediate, objective moisture information. The tool processes pre-styled RGB GeoTIFFs to provide quantitative metrics for specific land parcels.

## Technical Features
* **Interactive Geometry:** Site boundary definition via `streamlit-folium`.
* **CRS Synchronisation:** Automated handling of **EPSG:3857** and raster-specific coordinate systems for precise clipping.
* **Pixel Classification Engine:** Quantitative analysis of RGB channel dominance for land characterisation.
* **Raster Footprint Mapping:** Dynamic calculation of data bounds to prevent out-of-range errors.
* **Regulatory Alignment:** Automated draft conditions based on **GDSDS** and **BRE365** standards.

## Methodology
The tool operates through a four-stage pipeline:
1.  **Coordinate Transformation:** Converts user-drawn WGS84 polygons into the Raster's native Projection.
2.  **Spatial Clipping:** Uses `rasterio` to mask the GeoTIFF to the user's defined site boundary.
3.  **Classification Logic:**
    * **Dry:** $Red > Green$ and $Red > Blue$
    * **Moderate:** $Green > Red$ and $Green > Blue$
    * **Wet:** $Blue > Red$ and $Blue > Green$
4.  **Reporting:** Outputs a blue-scale moisture map and categorical risk level.

## Risk Assessment Logic
Risk is determined by the density of "Wet" pixels within the clipped area.

| Wet Pixel % | Risk Level | Recommended Planning Condition |
| :--- | :--- | :--- |
| **> 50%** | **HIGH** | Infiltration unlikely. Engineered drainage systems required. |
| **25% - 50%** | **MEDIUM** | BRE365 soakaway or percolation test recommended. |
| **< 25%** | **LOW** | Standard surface water drainage protocols acceptable. |

## Data Requirements
Input files must meet the following specifications:
* **Format:** 3-band RGB GeoTIFF.
* **Styling:** Exported from QGIS/ArcGIS using a discrete colour-stretched style (Red: Dry, Green: Moderate, Blue: Wet).
* **Source:** Typically derived from Copernicus CLMS Surface Soil Moisture (SSM) or Soil Water Index (SWI) products.

## Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/aquascan.git
    cd aquascan
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the application:**
    ```bash
    streamlit run app.py
    ```

## Project Structure
* `app.py`: Main Streamlit application logic.
* `requirements.txt`: Python dependencies (Rasterio, Folium, Geopandas, etc.).
* `data/`: Directory for sample GeoTIFF files.

---

**Regulatory Context:** This tool references **BRE Digest 365** (Soakaway design), **GDSDS** (Greater Dublin Strategic Drainage Study), and **OPW** flood risk management guidelines.
