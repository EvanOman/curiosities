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
    
    # Create longitude bins (1-degree intervals from -180 to 180)
    longitude_bins = np.arange(-180, 181, 1)
    df['longitude_bin'] = pd.cut(df['longitude'], bins=longitude_bins, labels=longitude_bins[:-1], include_lowest=True)
    
    # Group by longitude bin and sum population
    longitude_pop = df.groupby('longitude_bin', observed=True)['population'].sum().reset_index()
    longitude_pop['longitude_bin'] = longitude_pop['longitude_bin'].astype(float)
    
    # Sort by longitude
    longitude_pop = longitude_pop.sort_values('longitude_bin')
    
    # Filter out bins with zero population for cleaner visualization
    longitude_pop = longitude_pop[longitude_pop['population'] > 0]
    
    # Create bar chart
    plt.figure(figsize=(20, 10))
    bars = plt.bar(longitude_pop['longitude_bin'], longitude_pop['population'], 
                   width=0.8, color='coral', alpha=0.7, edgecolor='darkred', linewidth=0.5)
    
    # Customize the plot
    plt.title('Global Population Distribution by Longitude\n(Total Population per Degree of Longitude)', 
              fontsize=16, fontweight='bold')
    plt.xlabel('Longitude (Degrees East/West)', fontsize=12)
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
    major_ticks = np.arange(-180, 181, 30)
    plt.xticks(major_ticks)
    
    # Add vertical lines for major longitude references
    for lon in [-180, -120, -60, 0, 60, 120, 180]:
        plt.axvline(x=lon, color='gray', linestyle='--', alpha=0.3)
    
    # Add text annotations for major regions
    plt.text(0, max(longitude_pop['population']) * 0.9, 'Prime Meridian', 
             ha='center', va='bottom', rotation=90, fontsize=10, alpha=0.7)
    plt.text(-75, max(longitude_pop['population']) * 0.9, 'Americas', 
             ha='center', va='bottom', rotation=90, fontsize=10, alpha=0.7)
    plt.text(30, max(longitude_pop['population']) * 0.9, 'Europe/Africa', 
             ha='center', va='bottom', rotation=90, fontsize=10, alpha=0.7)
    plt.text(120, max(longitude_pop['population']) * 0.9, 'Asia/Pacific', 
             ha='center', va='bottom', rotation=90, fontsize=10, alpha=0.7)
    
    # Adjust layout
    plt.tight_layout()
    
    # Add grid for better readability
    plt.grid(axis='y', alpha=0.3)
    
    # Show the plot
    plt.show()
    
    # Save the plot
    plt.savefig('longitude_population_visualization.png', dpi=300, bbox_inches='tight')
    print("Visualization saved as 'longitude_population_visualization.png'")
    
    # Display summary statistics
    top_longitudes = longitude_pop.nlargest(10, 'population')
    
    print(f"\nPopulation Distribution by Longitude:")
    print(f"Total longitude bins with population: {len(longitude_pop)}")
    print(f"Total global population (in dataset): {longitude_pop['population'].sum():,}")
    print(f"Average population per longitude degree: {longitude_pop['population'].mean():.0f}")
    
    print(f"\nTop 10 Most Populated Longitude Degrees:")
    for _, row in top_longitudes.iterrows():
        pop_millions = row['population'] / 1000000
        print(f"  {row['longitude_bin']:+.0f}°: {pop_millions:.1f}M people")
    
    # Find longitude ranges with highest concentrations
    print(f"\nLongitude ranges with highest population concentrations:")
    asia_pop = longitude_pop[(longitude_pop['longitude_bin'] >= 60) & 
                           (longitude_pop['longitude_bin'] <= 140)]['population'].sum()
    europe_pop = longitude_pop[(longitude_pop['longitude_bin'] >= -10) & 
                             (longitude_pop['longitude_bin'] <= 60)]['population'].sum()
    americas_pop = longitude_pop[(longitude_pop['longitude_bin'] >= -120) & 
                               (longitude_pop['longitude_bin'] <= -60)]['population'].sum()
    
    print(f"  Asia/Pacific (60°E to 140°E): {asia_pop/1000000:.0f}M people")
    print(f"  Europe/Africa (-10°E to 60°E): {europe_pop/1000000:.0f}M people")
    print(f"  Americas (-120°W to -60°W): {americas_pop/1000000:.0f}M people")

if __name__ == "__main__":
    main()