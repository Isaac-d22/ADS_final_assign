from .config import *
from . import access
import osmnx as ox
import matplotlib.pyplot as plt

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
        # "amenity": "school", # There will be a correlation between amenity and school as an amenity is classed as a school (but my prior is that schools are such abn important field when it comes to house prices that they should be their own feature)
        "amenity": True, #Used to get other amenities eg. cinema, fast food etc. that have not been given a dedicate feature (need to remove other feature already account for)
        "leisure": True, #May want to split this up further into park, playground etc.
        "natural": True, #Proximity t nature may be helpful but may need to split further as tree counts here
        "residential": True,
        "landuse:residential": True,
        # "landuse": "residential", #TODO: Figure out how to break this down into rural/urban etc.
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

def data():
    """Load the data from access and ensure missing values are correctly encoded as well as indices correct, column names informative, date and times correctly formatted. Return a structured data structure such as a data frame."""
    df = access.data()
    raise NotImplementedError

def query(data):
    """Request user input for some aspect of the data."""
    raise NotImplementedError

def view(data):
    """Provide a view of the data that allows the user to verify some aspect of its quality."""
    raise NotImplementedError

def labelled(data):
    """Provide a labelled set of data ready for supervised learning."""
    raise NotImplementedError

def get_pois(latitude, longitude, tags, box_height=0.02, box_width=0.02):
    north = latitude + box_height/2
    south = latitude - box_height/2
    west = longitude - box_width/2
    east = longitude + box_width/2
    return ox.geometries_from_bbox(north, south, east, west, tags)

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
    
    fig, ax = plt.subplots(len(keys), len(locations), figsize=(len(locations[0][2]), (len(keys)) * 4))

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