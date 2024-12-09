import plotly.express as px
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

# Charger les données des quartiers (GeoJSON ou shapefile)
quartiers_gdf = gpd.read_file('VilleMTP_MTP_Quartiers.json')

def calculer_intensite_moyenne(file_path, quartiers_gdf):
    # Charger les données de vélo avec les intensités et dates
    df_velo = pd.read_json(file_path)

    # Extraire les coordonnées de latitude et longitude des points
    df_velo['longitude'] = df_velo['location'].apply(lambda x: x['coordinates'][0])
    df_velo['latitude'] = df_velo['location'].apply(lambda x: x['coordinates'][1])

    # Créer la colonne geometry pour le GeoDataFrame
    geometry = [Point(xy) for xy in zip(df_velo['longitude'], df_velo['latitude'])]
    gdf_velo = gpd.GeoDataFrame(df_velo, geometry=geometry, crs=quartiers_gdf.crs)

    # Associer les points de vélo aux quartiers
    gdf_joined = gpd.sjoin(gdf_velo, quartiers_gdf, how="inner", predicate="intersects")

    # Calculer la moyenne journalière par quartier et par date
    gdf_joined['start_date'] = gdf_joined['dateObserved'].apply(lambda x: x.split('/')[0])
    gdf_joined['start_date'] = pd.to_datetime(gdf_joined['start_date'])

    moyennes_quartiers = (
        gdf_joined.groupby(['name', 'start_date'])
        .agg({'intensity': 'mean'})
        .reset_index()
    )

    return quartiers_gdf.merge(
        moyennes_quartiers.groupby('name').agg({'intensity': 'mean'}).reset_index(),
        on='name',
        how='left'
    )

# Calculer les intensités pour 2023 et 2024
quartiers_gdf_2023 = calculer_intensite_moyenne('6_2024.json', quartiers_gdf.copy())
quartiers_gdf_2024 = calculer_intensite_moyenne('6_2022.json', quartiers_gdf.copy())

# Trouver la plage commune des intensités
intensite_min = min(quartiers_gdf_2023['intensity'].min(), quartiers_gdf_2024['intensity'].min())
intensite_max = max(quartiers_gdf_2023['intensity'].max(), quartiers_gdf_2024['intensity'].max())

# Créer une carte interactive pour 2023
fig_2023 = px.choropleth(
    quartiers_gdf_2023,
    geojson=quartiers_gdf_2023.geometry,
    locations=quartiers_gdf_2023.index,
    color='intensity',
    color_continuous_scale="Reds",
    range_color=[intensite_min, intensite_max],
    hover_name='name',
    title="Intensité moyenne du trafic - 2023"
)

# Ajuster la géométrie de la carte
fig_2023.update_geos(fitbounds="locations", visible=False)

# Créer une carte interactive pour 2024
fig_2024 = px.choropleth(
    quartiers_gdf_2024,
    geojson=quartiers_gdf_2024.geometry,
    locations=quartiers_gdf_2024.index,
    color='intensity',
    color_continuous_scale="Reds",
    range_color=[intensite_min, intensite_max],
    hover_name='name',
    title="Intensité moyenne du trafic - 2024"
)

# Ajuster la géométrie de la carte
fig_2024.update_geos(fitbounds="locations", visible=False)

# Créer un fichier HTML avec les deux cartes
html_content = f"""
<html>
<head>
    <title>Cartes de l'intensité du trafic</title>
    <style>
        .chart-container {{
            display: flex;
            justify-content: space-between;
            padding: 20px;
        }}
        .chart {{
            width: 48%;
            height: 600px;
        }}
    </style>
</head>
<body>
    <h1>Intensité moyenne du trafic de vélos</h1>
    <div class="chart-container">
        <div class="chart" id="carte_2023">{fig_2023.to_html(full_html=False)}</div>
        <div class="chart" id="carte_2024">{fig_2024.to_html(full_html=False)}</div>
    </div>
</body>
</html>
"""

# Sauvegarder le fichier HTML
with open("cartes_intensite_traffic.html", "w") as f:
    f.write(html_content)

print("Le fichier HTML a été sauvegardé sous 'cartes_intensite_traffic.html'.")
