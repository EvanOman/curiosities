# Northern Cities Analysis

Geographic data analysis and visualization exploring global city populations with a focus on northern hemisphere cities and their relationship to latitude.

## Overview

This project analyzes the GeoNames cities1000 dataset to explore patterns in global urban population distribution, with specialized analysis on:

1. **Northern cities** - Population vs distance from North Pole
2. **Global latitude distribution** - How population varies by latitude bands
3. **Global longitude distribution** - How population varies by longitude bands  
4. **Pareto frontier analysis** - Cities that are optimally large and northern

## Data Source

Uses the [GeoNames cities1000 dataset](http://download.geonames.org/export/dump/) (`cities1000.txt`), which contains all cities with population > 1000.

## Scripts

### `main.py`
Analyzes the top 20 most populous northern hemisphere cities and their distance from the North Pole.

**Features:**
- Filters for northern hemisphere cities (latitude > 0)
- Creates bar chart showing population vs distance from North Pole
- Displays summary statistics including northernmost/southernmost cities
- Saves visualization as `northern_cities_visualization.png`

**Run:** `python main.py`

### `latitude_population.py`
Analyzes global population distribution across latitude bands.

**Features:**
- Groups cities into 1-degree latitude bins
- Shows population concentration by climate zones (tropical, temperate, arctic)
- Highlights major latitude lines (equator, tropics, arctic circles)
- Compares northern vs southern hemisphere populations
- Saves visualization as `latitude_population_visualization.png`

**Run:** `python latitude_population.py`

### `longitude_population.py`
Analyzes global population distribution across longitude bands.

**Features:**
- Groups cities into 1-degree longitude bins
- Identifies major population centers by longitude (Asia, Europe, Americas)
- Shows concentration patterns across different regions
- Saves visualization as `longitude_population_visualization.png`

**Run:** `python longitude_population.py`

### `pareto_cities.py`
Finds cities on the Pareto frontier for size vs northern latitude.

**Features:**
- Identifies cities where no other city is both larger AND further north
- Uses logarithmic scale to show population range
- Demonstrates economic concept of Pareto efficiency applied to geography
- Saves visualization as `pareto_cities_visualization.png`

**Run:** `python pareto_cities.py`

## Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Download the cities1000 dataset:
   ```bash
   wget http://download.geonames.org/export/dump/cities1000.zip
   unzip cities1000.zip
   ```

3. Run any of the analysis scripts:
   ```bash
   python main.py
   python latitude_population.py
   python longitude_population.py
   python pareto_cities.py
   ```

## Output

Each script generates:
- Interactive matplotlib visualization
- High-resolution PNG image (300 DPI)
- Summary statistics printed to console

## Key Insights

The analysis reveals interesting patterns in global urbanization:
- Strong northern hemisphere bias in population distribution
- Concentration of population in temperate latitudes (20-60°N)
- Major population centers align with historical trade routes and agricultural regions
- Pareto frontier shows trade-offs between city size and northern latitude