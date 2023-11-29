from .config import *
from . import access
import osmnx as ox
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from IPython.display import display

"""These are the types of import we might expect in this file
import pandas
import bokeh
import seaborn
import matplotlib.pyplot as plt
import sklearn.decomposition as decomposition
import sklearn.feature_extraction"""

"""Place commands in this file to assess the data you have downloaded. How are missing values encoded, how are outliers encoded? What do columns represent, makes rure they are correctly labeled. How is the data indexed. Crete visualisation routines to assess the data (e.g. in bokeh). Ensure that date formats are correct and correctly timezoned."""

KEYS_DICT = {
        "public_transport": True,
        "amenity": True, 
        "leisure": True, 
        "natural": True, 
        "landuse:residential": True,
        "shop": True,
        "tourism": True,
        "historic": True,
        "aeroway": True,
        "healthcare": True,
        "industrial": True,
        "flood_prone": True,
        "highway": True,
        "waste": True
        }

KEYS = ["public_transport", "amenity", "leisure", "natural", "shop", "tourism", 
             "historic", "aeroway", "healthcare", "industrial", "flood_prone", "highway", "waste"]

TAGS = [("amenity", "school")]

LOCATIONS = [(51.5316, -0.1236, "Kings Cross, London"), (50.2660, -5.0527, "Cornwall, England"), (52.1951, 0.1313, "Cambridge, England")]

COLOURS = ['black', 'red', 'darkorange', 'gold', 'yellow', 'darkolivegreen', 'lime', 'silver',
           'aquamarine', 'dodgerblue', 'purple', 'fuchsia', 'lightpink', 'peru']

def view(num_rows=100, seed=1):
    """Provide a view of the data that allows the user to verify some aspect of its quality."""
    visualise_pois_by_key(LOCATIONS, KEYS)
    visualise_pois_by_key(LOCATIONS, TAGS, tag_version=True)
    credentials = access.get_credentials("credentials.yaml")
    conn = access.create_connection(user=credentials["username"], password=credentials["password"], host=credentials["url"], port=credentials["port"], database=credentials["name"])
    rows = access.get_random_rows(conn, num_rows, seed)
    pois_by_features = get_pois_for_rows(rows)
    visualise_feature_dist(pois_by_features)
    corr, princ_compt = conduct_PCA(pois_by_features)
    vis_PCA1(corr, princ_compt)
    vis_PCA2(corr, princ_compt)
    vis_PCA3(corr, princ_compt)

def get_pois_for_rows(rows):
    pois_by_features = []
    for i in range(len(rows)):
        count_pois = count_pois_by_features(get_pois(float(rows.iloc[i].latitude), float(rows.iloc[i].longitude), KEYS_DICT), KEYS, TAGS)
        count_pois['price'] = rows.iloc[i].price
        pois_by_features.append(count_pois)
    return pois_by_features

def conduct_PCA(pois_by_features):
    df = pd.DataFrame(pois_by_features)
    corr = df.corr()
    display(corr.style.background_gradient(cmap='Reds'))
    corr = corr.drop('price')
    corr = corr.drop('price', axis=1)
    pca = PCA(n_components=len(corr))
    princ_compt = pca.fit_transform(corr)
    explained_variance = np.concatenate([np.array([0]), np.cumsum(pca.explained_variance_ratio_)])
    cutoff = np.argmax(explained_variance > 0.95)
    for i in range(1, cutoff + 1):
        print(f"The explained variance with {i} principle componnts is: {explained_variance[i]}")
    plt.ylabel('Explained variance')
    plt.xlabel('Number of principle components')
    plt.yticks(np.arange(0, 1.1, 0.1))
    plt.plot(explained_variance)
    plt.show()
    return corr, princ_compt
    
def vis_PCA1(corr, princ_compt):
    for i, col in enumerate(corr.columns):
        plt.scatter(princ_compt[i,0], [0], c=COLOURS[i], label=col)
    plt.title("1 Principle component")
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.yticks([])
    plt.show()
    
def vis_PCA2(corr, princ_compt):
    for i, col in enumerate(corr.columns):
        plt.scatter(princ_compt[i,0], princ_compt[i,1], c=COLOURS[i], label=col)
    plt.title("2 Principle components")
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.xlabel("Principle component 1")
    plt.ylabel("Principle component 2")
    plt.show()

def vis_PCA3(corr, princ_compt):
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    for i, col in enumerate(corr.columns):
        ax.scatter(princ_compt[i,0], princ_compt[i,1], princ_compt[i,2], c=COLOURS[i], label=col)
    ax.set_title("3 Principle components")
    ax.legend(loc='center left', bbox_to_anchor=(1.25, 0.5))
    ax.set_xlabel("Principle component 1")
    ax.set_ylabel("Principle component 2")
    ax.set_zlabel("Principle component 3")
    plt.show()


def get_pois(latitude, longitude, tags, box_height=0.02, box_width=0.02):
    north = latitude + box_height/2
    south = latitude - box_height/2
    west = longitude - box_width/2
    east = longitude + box_width/2
    return ox.features_from_bbox(north, south, east, west, tags)

def get_graph(latitude, longitude, box_height=0.02, box_width=0.02):
    north = latitude + box_height/2
    south = latitude - box_height/2
    west = longitude - box_width/2
    east = longitude + box_width/2
    return ox.graph_from_bbox(north, south, east, west)

def get_box(latitude, longitude, box_height=0.02, box_width=0.02):
    north = latitude + box_height/2
    south = latitude - box_height/2
    west = longitude - box_width/2
    east = longitude + box_width/2
    return north, south, west, east

def count_pois_by_features(pois, keys, tags):
    count_by_features = {}
    for key in keys:
        try:
            count_by_features[key] = len(pois[pois[key].isna() == False])
        except:
            count_by_features[key] = 0
    for key, tag in tags:
        try:
            count_by_features[tag] = len(pois[pois[key] == tag])
        except:
            count_by_features[tag] = 0
        if key in count_by_features:
            count_by_features[key] -= count_by_features[tag]
    return count_by_features

def visualise_pois_by_key(locations, keys, box_height=0.02, box_width=0.02, tag_version=False):
    pois = []
    graphs = []

    for loc in locations:
        pois.append(get_pois(loc[0], loc[1], KEYS_DICT, box_height, box_width))
        graphs.append(get_graph(loc[0], loc[1], box_height, box_width))
    
    _, ax = plt.subplots(len(keys), len(locations), figsize=(len(locations[0][2]), (len(keys)) * 4))

    for i, loc in enumerate(locations):
        for j, key in enumerate(keys):
            try:        
                # Retrieve nodes and edges
                _, edges = ox.graph_to_gdfs(graphs[i])
                
                # Get place boundary related to the place name as a geodataframe
                area = ox.geocode_to_gdf(loc[2], which_result=1)

                # Plot the footprint
                if len(keys) > 1:
                    sub_ax = ax[j][i]
                else:
                    sub_ax = ax[i]
                area.plot(ax=sub_ax, facecolor="white")

                # Plot street edges
                edges.plot(ax=sub_ax, linewidth=1, edgecolor="dimgray")
                
                north, south, west, east = get_box(loc[0], loc[1], box_height, box_width)
                sub_ax.set_xlim([west, east])
                sub_ax.set_ylim([south, north])
                sub_ax.set_xlabel("longitude")
                sub_ax.set_ylabel("latitude")
                # Plot all POIs
                # Get POIS
                if tag_version:
                    sub_ax.set_title(f"{loc[2]} {key[0]}={key[1]}")
                    pois_subset = pois[i][pois[i][key[0]] == key[1]]
                else:
                    sub_ax.set_title(f"{loc[2]} {key}")
                    pois_subset = pois[i][pois[i][key].isna() == False]
                pois_subset.plot(ax=sub_ax, color="blue", alpha=0.7, markersize=10)
            except KeyError:
                print(f"{loc[2]} has no {key} keys")
            plt.tight_layout()
    plt.show()
            
def visualise_feature_dist(pois_by_features, bins=10):
    features = {}
    for key in pois_by_features[0].keys():
        for pois in pois_by_features:
            features[key] = features.get(key, []) + [pois[key]]
    _, ax = plt.subplots(len(features)//3 + 1, 3, figsize=(len(next(iter(features.keys()))), len(features) * 1.5))
    for i, feature in enumerate(features.items()):
        sub_ax = ax[i//3][i%3]
        sub_ax.set_title(feature[0])
        sub_ax.hist(feature[1], bins=bins)
    plt.show()