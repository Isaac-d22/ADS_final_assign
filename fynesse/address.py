# This file contains code for suporting addressing questions in the data

"""# Here are some of the imports we might expect 
import sklearn.model_selection  as ms
import sklearn.linear_model as lm
import sklearn.svm as svm
import sklearn.naive_bayes as naive_bayes
import sklearn.tree as tree

import GPy
import torch
import tensorflow as tf

# Or if it's a statistical analysis
import scipy.stats"""

"""Address a particular question that arises from the data"""

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
import access, assess


def predict_price(latitude, longitude, date, property_type):
    samples = get_training_samples(latitude, longitude, date, limit=...)
    pois_by_features = []
    for i in range(len(samples)):
        pois_by_features.append(assess.count_pois_by_features(assess.get_pois(float(samples.iloc[i].latitude), float(samples.iloc[i].longitude), 
                                                                              KEYS_DICT, box_height=1/69, box_width=1/69), KEYS, TAGS))
    osm_features = convert_to_principle_components(pois_by_features)
    encoded_property_features = one_hot_encode(samples)
    property_features = []
    for row in encoded_property_features:
        property_features.append(convert_property_to_feature_vec(row))
    feature_vec = np.concatenate((osm_features, property_features), axis=1)
    prices = samples['price'].to_numpy()
    m_linear = sm.OLS(prices, feature_vec)
    results = m_linear.fit()
    # TODO: Remove price to predict from training data
    
# get relevant training samples
from dateutil.relativedelta import relativedelta
# will include the target so make sure to remove that before training
def get_training_samples(latitude, longitude, date, date_range=2, area_range=2/69, limit=1000):
    conn = access.create_connection(user=username, password=password, host=url, port=port, database=db_name)
    conditions = [
                  access.greater_equal_condition('latitude', latitude-area_range), access.greater_equal_condition(latitude+area_range, 'latitude'),
                  access.greater_equal_condition('longitude', longitude-area_range), access.greater_equal_condition(longitude+area_range, 'longitude'),
                  access.greater_equal_condition('date_of_transfer', f"'{date-relativedelta(years=date_range)}'"), access.greater_equal_condition(f"'{date+relativedelta(years=date_range)}'", 'date_of_transfer')
                  ]
    samples = access.price_coordinates_data_to_df(access.query_table(conn, 'prices_coordinates_data', conditions=conditions, limit=limit))
    conn.close()
    return samples

def convert_to_principle_components(pois_by_features, threshold=0.95):
    df = pd.DataFrame(pois_by_features)
    corr = df.corr()
    corr = corr.dropna(how='all')
    corr = corr.dropna(axis=1, how='all')
    dropped_features = df.columns.difference(corr.columns).tolist()
    df = df.drop(columns=dropped_features)
    pca = PCA(n_components=len(corr))
    pca.fit_transform(corr)
    explained_variance = np.cumsum(pca.explained_variance_ratio_)
    cutoff = np.argmax(explained_variance > threshold) + 1
    return pca.transform(df)[:,:cutoff]

def one_hot_encode(training_rows):
    replacements = {'new_build_flag': {'N': 0, 'Y' :1}, 'tenure_type': {'L': 0, 'F': 1}}
    one_hot = {'F': [1,0,0,0,0], 'S': [0,1,0,0,0], 'T': [0,0,1,0,0], 'D': [0,0,0,1,0], 'O': [0,0,0,0,1]}
    res = training_rows[['property_type', 'new_build_flag', 'tenure_type']]
    res = res.replace(replacements) # Not sure this needs to be here
    res.rename(columns={"tenure_type": 'freehold_flag'})
    res['property_type'] = res['property_type'].map(one_hot)
    return res
        