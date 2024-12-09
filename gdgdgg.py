import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
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

    # Fusionner avec les données des quartiers pour les visualisations
    return quartiers_gdf.merge(
        moyennes_quartiers.groupby('name').agg({'intensity': 'mean'}).reset_index(),
        on='name',
        how='left'
    )

# Calculer les intensités pour 2023 et 2024
quartiers_gdf_2022 = calculer_intensite_moyenne('6_2022.json', quartiers_gdf.copy())
quartiers_gdf_2024 = calculer_intensite_moyenne('6_2024.json', quartiers_gdf.copy())

#print(quartiers_gdf_2022)
#print(quartiers_gdf_2024)
# Trouver la plage commune des intensités
intensite_min = min(quartiers_gdf_2022['intensity'].min(), quartiers_gdf_2024['intensity'].min())
intensite_max = max(quartiers_gdf_2022['intensity'].max(), quartiers_gdf_2024['intensity'].max())

# Création de la figure avec deux sous-cartes
fig, axes = plt.subplots(1, 2, figsize=(18, 8), subplot_kw={'aspect': 'equal'})

# Visualisation des intensités pour 2022
quartiers_gdf_2022.plot(
    column='intensity',
    cmap='Reds',
    legend=False,  # Désactiver la légende ici
    ax=axes[0],
    vmin=intensite_min,
    vmax=intensite_max
)
axes[0].set_title("Intensité moyenne du trafic - 2022")
for x, y, label in zip(
    quartiers_gdf_2022.geometry.centroid.x,
    quartiers_gdf_2022.geometry.centroid.y,
    quartiers_gdf_2022['name']
):
    axes[0].text(x, y, label, fontsize=8, ha='center', color='black')

# Visualisation des intensités pour 2024
quartiers_gdf_2024.plot(
    column='intensity',
    cmap='Reds',
    legend=False,  # Désactiver la légende ici
    ax=axes[1],
    vmin=intensite_min,
    vmax=intensite_max
)
axes[1].set_title("Intensité moyenne du trafic - 2024")
for x, y, label in zip(
    quartiers_gdf_2024.geometry.centroid.x,
    quartiers_gdf_2024.geometry.centroid.y,
    quartiers_gdf_2024['name']
):
    axes[1].text(x, y, label, fontsize=8, ha='center', color='black')

# Ajouter une légende commune
cbar_ax = fig.add_axes([0.92, 0, 0.02, 0.95])  # Position de la barre de couleur
sm = plt.cm.ScalarMappable(cmap='Reds', norm=plt.Normalize(vmin=intensite_min, vmax=intensite_max))
cbar = fig.colorbar(sm, cax=cbar_ax)
cbar.set_label("Intensité moyenne", fontsize=12)

plt.tight_layout(rect=[0, 0, 0.9, 1])  # Ajuster pour laisser la place à la légende

# Sauvegarder l'image de la carte
plt.savefig('intensite_traffics_map.png', dpi=300)
plt.close()
