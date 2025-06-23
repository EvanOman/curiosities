import matplotlib.pyplot as plt
import pandas as pd
import math

def calculate_miles_from_north_pole(latitude):
    """Calculate miles from North Pole given latitude in degrees"""
    # Earth's circumference is approximately 24,901 miles
    # Distance from North Pole (90°) to any latitude = (90 - latitude) * (circumference / 360)
    miles_per_degree = 24901 / 360
    distance_miles = (90 - latitude) * miles_per_degree
    return distance_miles

def main():
    # Read the GeoNames cities1000 dataset
    # Format: geonameid, name, asciiname, alternatenames, latitude, longitude, feature_class, 
    # feature_code, country_code, cc2, admin1_code, admin2_code, admin3_code, admin4_code, 
    # population, elevation, dem, timezone, modification_date
    
    column_names = ['geonameid', 'name', 'asciiname', 'alternatenames', 'latitude', 'longitude',
                   'feature_class', 'feature_code', 'country_code', 'cc2', 'admin1_code', 
                   'admin2_code', 'admin3_code', 'admin4_code', 'population', 'elevation', 
                   'dem', 'timezone', 'modification_date']
    
    df = pd.read_csv('cities1000.txt', sep='\t', names=column_names, low_memory=False)
    
    # Filter for northern hemisphere cities only (latitude > 0)
    df = df[df['latitude'] > 0]
    
    # Remove cities with missing or zero population
    df = df[df['population'].notna() & (df['population'] > 0)]
    
    # Sort by population (increasing order as requested)
    df = df.sort_values('population', ascending=True)
    
    # Take top 20 cities by population for visualization
    df = df.tail(20).copy()
    
    # Calculate miles from North Pole
    df['miles_from_north_pole'] = df['latitude'].apply(calculate_miles_from_north_pole)
    
    # Create city labels with country
    df['city_label'] = df['asciiname'] + ', ' + df['country_code']

    # Sort by miles from North Pole for x-axis (closest to farthest)
    df = df.sort_values('miles_from_north_pole', ascending=True)

    # Create bar chart with population on y-axis and miles from North Pole on x-axis
    plt.figure(figsize=(16, 10))
    bars = plt.bar(range(len(df)), df['population'], color='steelblue', alpha=0.7)

    # Customize the plot
    plt.title('Northern Cities: Population vs Distance from North Pole', fontsize=16, fontweight='bold')
    plt.xlabel('Cities (Ordered by Distance from North Pole)', fontsize=12)
    plt.ylabel('Population', fontsize=12)

    # Set x-axis labels with city names and miles from North Pole
    labels = []
    for _, row in df.iterrows():
        miles = row['miles_from_north_pole']
        labels.append(f"{row['city_label']}\n({miles:.0f} mi)")
    
    plt.xticks(range(len(df)), labels, rotation=45, ha='right')

    # Format y-axis to show population in thousands/millions
    def format_population(x, pos):
        if x >= 1000000:
            return f'{x/1000000:.1f}M'
        elif x >= 1000:
            return f'{x/1000:.0f}K'
        else:
            return f'{int(x)}'

    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(format_population))

    # Add value labels on top of bars (population)
    for i, (bar, pop) in enumerate(zip(bars, df['population'])):
        if pop >= 1000000:
            label = f'{pop/1000000:.1f}M'
        elif pop >= 1000:
            label = f'{pop/1000:.0f}K'
        else:
            label = str(int(pop))
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(df['population'])*0.01,
                 label, ha='center', va='bottom', fontsize=9)

    # Adjust layout to prevent label cutoff
    plt.tight_layout()

    # Add grid for better readability
    plt.grid(axis='y', alpha=0.3)

    # Show the plot
    plt.show()

    # Save the plot
    plt.savefig('northern_cities_visualization.png', dpi=300, bbox_inches='tight')
    print("Visualization saved as 'northern_cities_visualization.png'")

    # Display summary statistics
    print("\nSummary of Northern Cities Data (Top 20 by Population):")
    print(f"Total cities analyzed: {len(df)}")
    print(f"Northernmost city: {df.loc[df['latitude'].idxmax(), 'city_label']} at {df['latitude'].max():.2f}°N ({df['miles_from_north_pole'].min():.0f} miles from North Pole)")
    print(f"Southernmost city: {df.loc[df['latitude'].idxmin(), 'city_label']} at {df['latitude'].min():.2f}°N ({df['miles_from_north_pole'].max():.0f} miles from North Pole)")
    print(f"Largest city by population: {df.loc[df['population'].idxmax(), 'city_label']} with {df['population'].max():,} people")
    print(f"Smallest city by population: {df.loc[df['population'].idxmin(), 'city_label']} with {df['population'].min():,} people")
    print(f"Average distance from North Pole: {df['miles_from_north_pole'].mean():.0f} miles")


if __name__ == "__main__":
    main()
