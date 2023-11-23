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
import statsmodels.api as sm
from sklearn.decomposition import PCA
import access, assess

TAGS = [("amenity", "school")]


def predict_price(latitude, longitude, date, property_type):
    samples = get_training_samples(latitude, longitude, date, property_type, limit=100)
    target_id = samples[(samples.latitude == latitude) & (samples.longitude == longitude) & (samples.date == date) & (samples.property_type == property_type)]
    # TODO: Remove price to predict from training data
    pois_by_features = []
    for i in range(len(samples)):
        pois_by_features.append(assess.count_pois_by_features(assess.get_pois(float(samples.iloc[i].latitude), float(samples.iloc[i].longitude), 
                                                                              assess.KEYS_DICT, box_height=1/69, box_width=1/69), assess.KEYS_DICT, TAGS))
    encoded_property_features = property_feature_map(samples)
    features = convert_to_principle_components(pois_by_features, encoded_property_features)
    target_features = features[target_id]
    features = np.delete(features, target_id)
    prices = samples['price'].to_numpy()
    target_price = prices[target_id]
    prices = np.delete(prices, target_id)
    m_linear = sm.OLS(prices, features)
    results = m_linear.fit()
    prediction = results.get_prediction(target_features).summary_frame(alpha=0.05)['mean']
    percentage_error = 100 * abs(prediction) / target_price
    if percentage_error > 0.1:
        print("Poor model perfromance")
    print(f"Predicted: {prediction}, Actual: {target_price}, Percentage error: {percentage_error}%")
    return (prediction, target_price)
    
    
# get relevant training samples
from dateutil.relativedelta import relativedelta
# will include the target so make sure to remove that before training
def get_training_samples(latitude, longitude, date, property_type, date_range=2, area_range=2/69, limit=1000):
    credentials = access.get_credentials("credentials.yaml")
    conn = access.create_connection(user=credentials["username"], password=credentials["password"], host=credentials["url"], port=credentials["port"], database=credentials["db_name"])
    conditions = [
                  access.greater_equal_condition('latitude', latitude-area_range), access.greater_equal_condition(latitude+area_range, 'latitude'),
                  access.greater_equal_condition('longitude', longitude-area_range), access.greater_equal_condition(longitude+area_range, 'longitude'),
                  access.greater_equal_condition('date_of_transfer', f"'{date-relativedelta(years=date_range)}'"), access.greater_equal_condition(f"'{date+relativedelta(years=date_range)}'", 'date_of_transfer'),
                  access.equal_condition('property_type', property_type)
                  ]
    samples = access.price_coordinates_data_to_df(access.query_table(conn, 'prices_coordinates_data', conditions=conditions, limit=limit))
    conn.close()
    return samples

def convert_to_principle_components(pois_by_features, encoded_property_features, threshold=0.95):
    df = pd.DataFrame(pois_by_features)
    df = pd.concat(df, encoded_property_features)
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

def property_feature_map(training_rows):
    replacements = {'new_build_flag': {'N': 0, 'Y' :1}, 'tenure_type': {'L': 0, 'F': 1}}
    # one_hot = {'F': [1,0,0,0,0], 'S': [0,1,0,0,0], 'T': [0,0,1,0,0], 'D': [0,0,0,1,0], 'O': [0,0,0,0,1]}
    res = training_rows[['new_build_flag', 'tenure_type']]
    res = res.replace(replacements) # Not sure this needs to be here
    res.rename(columns={"tenure_type": 'freehold_flag'})
    # res['property_type'] = res['property_type'].map(one_hot)
    return res
        
def convert_property_to_feature_vec(property_feature):
    return np.concatenate((property_feature[0],[property_feature[1], property_feature[2]]))