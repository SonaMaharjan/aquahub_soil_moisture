# AquaScan: Soil Moisture Spatial Analysis for Irish Planning

AquaScan is a technical prototype designed for Irish planning authorities to evaluate soil moisture conditions on proposed development sites. It uses satellite-derived imagery (Copernicus) to classify land into moisture zones and generate regulatory-aligned planning conditions.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://aquaappsoilmoisture-4ffds6yaknqk6ajzu8dgh9.streamlit.app/)

## Table of Contents
* [Overview](#overview)
* [How it Works (Methodology)](#how-it-works-methodology)
* [Risk Assessment Logic](#risk-assessment-logic)
* [Data Requirements](#data-requirements)
* [Future Expansion](#future-expansion)
* [Installation & Setup](#installation--setup)

---

## Overview
Irish planning authorities often lack real-time environmental data for site assessments. AquaScan demonstrates how **Copernicus Sentinel data** can provide immediate, objective moisture information. The tool processes pre-styled RGB GeoTIFFs to provide quantitative metrics for specific land areas.

## How it Works (Methodology)
The app follows a four-step process to turn satellite images into a planning report:

1.  **Aligning the Maps:** When you draw a shape on the interactive map, the app converts the coordinates of your drawing into the specific grid system used by the satellite image.
2.  **Cutting the Data:** The app uses your drawn boundary, "clipping" out only the relevant portion of the image and discarding the rest.
3.  **Sorting the Colours:** The app looks at every individual pixel in your selected area from the RGB GeoTIFF file and checks which colour is the strongest:
    * **Red is strongest:** Classified as **Dry**.
    * **Green is strongest:** Classified as **Moderate**.
    * **Blue is strongest:** Classified as **Wet**.
4.  **Final Report:** The app calculates the percentage of each category to provide a risk level, and produce a blue-scale map of wet spots, and recommendations.

## Risk Assessment Logic
Risk is determined by the density of "Wet" pixels within the clipped area. For the scope of this prototype, we came up with the following conditions.

| Wet Pixel % | Risk Level | Conditions |
| :--- | :--- | :--- |
| **> 50%** | **HIGH** | Infiltration unlikely. Engineered drainage systems required. |
| **25% - 50%** | **MEDIUM** | BRE365 soakaway or percolation test recommended. |
| **< 25%** | **LOW** | Standard surface water drainage protocols acceptable. |

## Data Requirements
Input files must meet the following specifications:
* **Format:** 3-band RGB GeoTIFF.
* **Styling:** Exported from QGIS using a discrete colour-stretched style (Red: Dry, Green: Moderate, Blue: Wet).
* **Source:** Derived from Copernicus CLMS Surface Soil Moisture (SSM) or Soil Water Index (SWI) products.

## Future Expansion
Currently, this prototype relies exclusively on the Soil Moisture Index to assess site suitability. To provide a more comprehensive environmental risk profile, future versions will integrate the following datasets:

* **Flood Risks:** High-resolution monitoring via Copernicus Sentinel-1 (GRD).

* **Evapotranspiration:** Water-cycle data from Copernicus CLMS Global Land Service.

* **Soil Sealing:** Land permeability metrics from Copernicus CLMS High Resolution Layer (HRL).

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
