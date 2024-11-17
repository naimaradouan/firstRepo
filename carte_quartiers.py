import geopandas as gpd
import folium
import random

# Load the JSON file
gdf = gpd.read_file('VilleMTP_MTP_Quartiers.json')

# Initialize the map centered around Montpellier
m = folium.Map(location=[43.6117, 3.8767], zoom_start=12)

# Loop through each neighborhood and plot it with a random color
for _, row in gdf.iterrows():
    # Generate a random color
    color = "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    
    # Add neighborhood to map
    folium.GeoJson(
        row['geometry'],
        style_function=lambda x, color=color: {'fillColor': color, 'color': color, 'weight': 0.5, 'fillOpacity': 0.5}
    ).add_to(m)

# Save map as HTML
m.save("les quartiers de montpellier.html")
