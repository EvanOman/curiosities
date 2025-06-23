import matplotlib.pyplot as plt
import pandas as pd
import math

def calculate_miles_from_north_pole(latitude):
    """Calculate miles from North Pole given latitude in degrees"""
    miles_per_degree = 24901 / 360
    distance_miles = (90 - latitude) * miles_per_degree
    return distance_miles

def find_pareto_cities(df):
    """Find cities on the Pareto frontier: largest-northernmost cities"""
    # Sort by latitude descending (northernmost first)
    df_sorted = df.sort_values('latitude', ascending=False).copy()
    
    pareto_cities = []
    max_population_so_far = 0
    
    for _, city in df_sorted.iterrows():
        # If this city has a larger population than any city further north, include it
        if city['population'] > max_population_so_far:
            pareto_cities.append(city)
            max_population_so_far = city['population']
    
    return pd.DataFrame(pareto_cities)

def main():
    # Read the GeoNames cities1000 dataset
    column_names = ['geonameid', 'name', 'asciiname', 'alternatenames', 'latitude', 'longitude',
                   'feature_class', 'feature_code', 'country_code', 'cc2', 'admin1_code', 
                   'admin2_code', 'admin3_code', 'admin4_code', 'population', 'elevation', 
                   'dem', 'timezone', 'modification_date']
    
    df = pd.read_csv('cities1000.txt', sep='\t', names=column_names, low_memory=False)
    
    # Filter for northern hemisphere cities only (latitude > 0)
    df = df[df['latitude'] > 0]
    
    # Remove cities with missing or zero population
    df = df[df['population'].notna() & (df['population'] > 0)]
    
    # Find Pareto frontier cities (largest-northernmost)
    pareto_df = find_pareto_cities(df)
    
    # Calculate miles from North Pole
    pareto_df['miles_from_north_pole'] = pareto_df['latitude'].apply(calculate_miles_from_north_pole)
    
    # Create city labels with country
    pareto_df['city_label'] = pareto_df['asciiname'] + ', ' + pareto_df['country_code']
    
    # Sort by miles from North Pole (closest to farthest) for visualization
    pareto_df = pareto_df.sort_values('miles_from_north_pole', ascending=True)
    
    # Create bar chart with population on y-axis and miles from North Pole on x-axis
    plt.figure(figsize=(16, 10))
    bars = plt.bar(range(len(pareto_df)), pareto_df['population'], color='darkgreen', alpha=0.7)
    
    # Customize the plot
    plt.title('Largest-Northernmost Cities: Pareto Frontier\n(No city is both larger and further north)', fontsize=16, fontweight='bold')
    plt.xlabel('Cities (Ordered by Distance from North Pole)', fontsize=12)
    plt.ylabel('Population', fontsize=12)
    
    # Set x-axis labels with city names and miles from North Pole
    labels = []
    for _, row in pareto_df.iterrows():
        miles = row['miles_from_north_pole']
        lat = row['latitude']
        labels.append(f"{row['city_label']}\n({miles:.0f} mi, {lat:.1f}°N)")
    
    plt.xticks(range(len(pareto_df)), labels, rotation=45, ha='right')
    
    # Format y-axis to show population in thousands/millions
    def format_population(x, pos):
        if x >= 1000000:
            return f'{x/1000000:.1f}M'
        elif x >= 1000:
            return f'{x/1000:.0f}K'
        else:
            return f'{int(x)}'
    
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(format_population))
    
    # Set y-axis to log scale first
    plt.yscale('log')
    
    # Add value labels on top of bars (population) - adjusted for log scale
    for i, (bar, pop) in enumerate(zip(bars, pareto_df['population'])):
        if pop >= 1000000:
            label = f'{pop/1000000:.1f}M'
        elif pop >= 1000:
            label = f'{pop/1000:.0f}K'
        else:
            label = str(int(pop))
        # For log scale, add a small multiplier instead of fixed offset
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() * 1.1,
                 label, ha='center', va='bottom', fontsize=9)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Add grid for better readability
    plt.grid(axis='y', alpha=0.3)
    
    # Show the plot
    plt.show()
    
    # Save the plot
    plt.savefig('pareto_cities_visualization.png', dpi=300, bbox_inches='tight')
    print("Visualization saved as 'pareto_cities_visualization.png'")
    
    # Display summary statistics
    print(f"\nPareto Frontier Cities (Largest-Northernmost):")
    print(f"Total cities on frontier: {len(pareto_df)}")
    print(f"Northernmost city: {pareto_df.iloc[0]['city_label']} at {pareto_df.iloc[0]['latitude']:.2f}°N ({pareto_df.iloc[0]['miles_from_north_pole']:.0f} miles from North Pole)")
    print(f"Largest city: {pareto_df.loc[pareto_df['population'].idxmax(), 'city_label']} with {pareto_df['population'].max():,} people")
    print(f"Population range: {pareto_df['population'].min():,} to {pareto_df['population'].max():,}")
    
    print(f"\nCities on the frontier:")
    for _, city in pareto_df.sort_values('latitude', ascending=False).iterrows():
        print(f"  {city['city_label']}: {city['population']:,} people at {city['latitude']:.2f}°N ({city['miles_from_north_pole']:.0f} mi)")

if __name__ == "__main__":
    main()