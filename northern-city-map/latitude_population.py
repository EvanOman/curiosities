import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def main():
    # Read the GeoNames cities1000 dataset
    column_names = ['geonameid', 'name', 'asciiname', 'alternatenames', 'latitude', 'longitude',
                   'feature_class', 'feature_code', 'country_code', 'cc2', 'admin1_code', 
                   'admin2_code', 'admin3_code', 'admin4_code', 'population', 'elevation', 
                   'dem', 'timezone', 'modification_date']
    
    df = pd.read_csv('cities1000.txt', sep='\t', names=column_names, low_memory=False)
    
    # Remove cities with missing or zero population
    df = df[df['population'].notna() & (df['population'] > 0)]
    
    # Create latitude bins (1-degree intervals from -90 to 90)
    latitude_bins = np.arange(-90, 91, 1)
    df['latitude_bin'] = pd.cut(df['latitude'], bins=latitude_bins, labels=latitude_bins[:-1], include_lowest=True)
    
    # Group by latitude bin and sum population
    latitude_pop = df.groupby('latitude_bin', observed=True)['population'].sum().reset_index()
    latitude_pop['latitude_bin'] = latitude_pop['latitude_bin'].astype(float)
    
    # Sort by latitude
    latitude_pop = latitude_pop.sort_values('latitude_bin')
    
    # Filter out bins with zero population for cleaner visualization
    latitude_pop = latitude_pop[latitude_pop['population'] > 0]
    
    # Create bar chart
    plt.figure(figsize=(16, 12))
    bars = plt.bar(latitude_pop['latitude_bin'], latitude_pop['population'], 
                   width=0.8, color='lightseagreen', alpha=0.7, edgecolor='teal', linewidth=0.5)
    
    # Customize the plot
    plt.title('Global Population Distribution by Latitude\n(Total Population per Degree of Latitude)', 
              fontsize=16, fontweight='bold')
    plt.xlabel('Latitude (Degrees North/South)', fontsize=12)
    plt.ylabel('Total Population', fontsize=12)
    
    # Format y-axis to show population in millions/billions
    def format_population(x, pos):
        if x >= 1000000000:
            return f'{x/1000000000:.1f}B'
        elif x >= 1000000:
            return f'{x/1000000:.0f}M'
        elif x >= 1000:
            return f'{x/1000:.0f}K'
        else:
            return f'{int(x)}'
    
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(format_population))
    
    # Set x-axis ticks and labels
    major_ticks = np.arange(-90, 91, 15)
    plt.xticks(major_ticks)
    
    # Add vertical lines for major latitude references
    important_lats = [0, 23.5, -23.5, 66.5, -66.5]  # Equator, Tropics, Arctic/Antarctic circles
    lat_labels = ['Equator', 'Tropic of Cancer', 'Tropic of Capricorn', 'Arctic Circle', 'Antarctic Circle']
    
    for lat, label in zip(important_lats, lat_labels):
        plt.axvline(x=lat, color='red', linestyle='--', alpha=0.5)
        # Position labels to the right of the line to avoid overlap
        plt.text(lat + 2, max(latitude_pop['population']) * 0.85, label, 
                 ha='left', va='center', fontsize=9, alpha=0.8, 
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
    
    # Add horizontal line at equator for reference
    plt.axvline(x=0, color='red', linestyle='-', alpha=0.7, linewidth=2)
    
    # Adjust layout
    plt.tight_layout()
    
    # Add grid for better readability
    plt.grid(axis='y', alpha=0.3)
    
    # Show the plot
    plt.show()
    
    # Save the plot
    plt.savefig('latitude_population_visualization.png', dpi=300, bbox_inches='tight')
    print("Visualization saved as 'latitude_population_visualization.png'")
    
    # Display summary statistics
    top_latitudes = latitude_pop.nlargest(10, 'population')
    
    print(f"\nPopulation Distribution by Latitude:")
    print(f"Total latitude bins with population: {len(latitude_pop)}")
    print(f"Total global population (in dataset): {latitude_pop['population'].sum():,}")
    print(f"Average population per latitude degree: {latitude_pop['population'].mean():.0f}")
    
    print(f"\nTop 10 Most Populated Latitude Degrees:")
    for _, row in top_latitudes.iterrows():
        pop_millions = row['population'] / 1000000
        hemisphere = "N" if row['latitude_bin'] >= 0 else "S"
        print(f"  {abs(row['latitude_bin']):.0f}°{hemisphere}: {pop_millions:.1f}M people")
    
    # Analyze population by hemisphere and climate zones
    northern_pop = latitude_pop[latitude_pop['latitude_bin'] >= 0]['population'].sum()
    southern_pop = latitude_pop[latitude_pop['latitude_bin'] < 0]['population'].sum()
    
    tropical_pop = latitude_pop[(latitude_pop['latitude_bin'] >= -23.5) & 
                               (latitude_pop['latitude_bin'] <= 23.5)]['population'].sum()
    temperate_north_pop = latitude_pop[(latitude_pop['latitude_bin'] > 23.5) & 
                                      (latitude_pop['latitude_bin'] < 66.5)]['population'].sum()
    temperate_south_pop = latitude_pop[(latitude_pop['latitude_bin'] < -23.5) & 
                                      (latitude_pop['latitude_bin'] > -66.5)]['population'].sum()
    arctic_pop = latitude_pop[latitude_pop['latitude_bin'] >= 66.5]['population'].sum()
    antarctic_pop = latitude_pop[latitude_pop['latitude_bin'] <= -66.5]['population'].sum()
    
    print(f"\nPopulation by Hemisphere:")
    print(f"  Northern Hemisphere: {northern_pop/1000000:.0f}M people ({northern_pop/(northern_pop+southern_pop)*100:.1f}%)")
    print(f"  Southern Hemisphere: {southern_pop/1000000:.0f}M people ({southern_pop/(northern_pop+southern_pop)*100:.1f}%)")
    
    print(f"\nPopulation by Climate Zones:")
    print(f"  Tropical (23.5°S to 23.5°N): {tropical_pop/1000000:.0f}M people")
    print(f"  Northern Temperate (23.5°N to 66.5°N): {temperate_north_pop/1000000:.0f}M people")
    print(f"  Southern Temperate (23.5°S to 66.5°S): {temperate_south_pop/1000000:.0f}M people")
    print(f"  Arctic (above 66.5°N): {arctic_pop/1000000:.1f}M people")
    print(f"  Antarctic (below 66.5°S): {antarctic_pop/1000000:.1f}M people")

if __name__ == "__main__":
    main()