from .config import *
import pymysql
import requests
import zipfile
import pandas as pd
from time import time
import csv

"""These are the types of import we might expect in this file
import httplib2
import oauth2
import tables
import mongodb
import sqlite"""

# This file accesses the data

"""Place commands in this file to access the data electronically. Don't remove any missing values, or deal with outliers. Make sure you have legalities correct, both intellectual property and personal data privacy rights. Beyond the legal side also think about the ethical issues around this data. """

def data():
    """Read the data from the web or local file, returning structured format such as a data frame"""
    raise NotImplementedError

def create_connection(user, password, host, port, database=None):
    """ Create a database connection to the MariaDB database
        specified by the host url and database name.
    :param user: username
    :param password: password
    :param host: host url
    :param database: database
    :param port: port number
    :return: Connection object or None
    """
    try:
        if database is None:
            conn = pymysql.connect(user=user,
                                passwd=password,
                                host=host,
                                port=port,
                                local_infile=1,
                                )
        else:
            conn = pymysql.connect(user=user,
                                passwd=password,
                                host=host,
                                port=port,
                                local_infile=1,
                                db=database,
                                )
    except Exception as e:
        print(f"Error connecting to the MariaDB Server: {e}")
    return conn

# General function to download csv files and extract zip files if neccessary
def download_csv(url, filename, target_dir="", extract=False):
    file_path = f"{target_dir}/{filename}"
    try:
        req = requests.get(url)
        url_content = req.content
        target_file = open(file_path, 'wb')
        target_file.write(url_content)
        if extract:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(target_dir)
            os.remove(file_path)
        else:
            target_file.close()
    except Exception as e:
        print(f"Error downloading file from: {url}\n{e}")
        
def create_pp_data(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS pp_data;")
        cursor.execute("""
                    CREATE TABLE `pp_data` (
                    `transaction_unique_identifier` tinytext COLLATE utf8_bin NOT NULL,
                    `price` int(10) unsigned NOT NULL,
                    `date_of_transfer` date NOT NULL,
                    `postcode` varchar(8) COLLATE utf8_bin NOT NULL,
                    `property_type` varchar(1) COLLATE utf8_bin NOT NULL,
                    `new_build_flag` varchar(1) COLLATE utf8_bin NOT NULL,
                    `tenure_type` varchar(1) COLLATE utf8_bin NOT NULL,
                    `primary_addressable_object_name` tinytext COLLATE utf8_bin NOT NULL,
                    `secondary_addressable_object_name` tinytext COLLATE utf8_bin NOT NULL,
                    `street` tinytext COLLATE utf8_bin NOT NULL,
                    `locality` tinytext COLLATE utf8_bin NOT NULL,
                    `town_city` tinytext COLLATE utf8_bin NOT NULL,
                    `district` tinytext COLLATE utf8_bin NOT NULL,
                    `county` tinytext COLLATE utf8_bin NOT NULL,
                    `ppd_category_type` varchar(2) COLLATE utf8_bin NOT NULL,
                    `record_status` varchar(2) COLLATE utf8_bin NOT NULL,
                    `db_id` bigint(20) unsigned NOT NULL
                    ) DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=1 ;
                    """)
        cursor.execute("""
                    ALTER TABLE pp_data
                    ADD PRIMARY KEY (`db_id`);
                    """)
        cursor.execute("""
                    ALTER TABLE pp_data
                    MODIFY db_id bigint(20) unsigned NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;
                    """)
        conn.commit()
        cursor.close()
    except Exception as e:
        print(f"Error creating pp_data table: {e}")
        
def create_postcode_data(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS postcode_data;")
        cursor.execute("""
                        CREATE TABLE `postcode_data` (
                        `postcode` varchar(8) COLLATE utf8_bin NOT NULL,
                        `status` enum('live','terminated') NOT NULL,
                        `usertype` enum('small', 'large') NOT NULL,
                        `easting` int unsigned,
                        `northing` int unsigned,
                        `positional_quality_indicator` int NOT NULL,
                        `country` enum('England', 'Wales', 'Scotland', 'Northern Ireland', 'Channel Islands', 'Isle of Man') NOT NULL,
                        `latitude` decimal(11,8) NOT NULL,
                        `longitude` decimal(10,8) NOT NULL,
                        `postcode_no_space` tinytext COLLATE utf8_bin NOT NULL,
                        `postcode_fixed_width_seven` varchar(7) COLLATE utf8_bin NOT NULL,
                        `postcode_fixed_width_eight` varchar(8) COLLATE utf8_bin NOT NULL,
                        `postcode_area` varchar(2) COLLATE utf8_bin NOT NULL,
                        `postcode_district` varchar(4) COLLATE utf8_bin NOT NULL,
                        `postcode_sector` varchar(6) COLLATE utf8_bin NOT NULL,
                        `outcode` varchar(4) COLLATE utf8_bin NOT NULL,
                        `incode` varchar(3)  COLLATE utf8_bin NOT NULL,
                        `db_id` bigint(20) unsigned NOT NULL
                        ) DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
                    """)
        cursor.execute("""
                    ALTER TABLE postcode_data
                    ADD PRIMARY KEY (`db_id`);
                    """)
        cursor.execute("""
                    ALTER TABLE postcode_data
                    MODIFY `db_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=1;
                    """)
        conn.commit()
        cursor.close()
    except Exception as e:
        print(f"Error creating postcode_data table: {e}")
    
def create_prices_coordinates_data(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS prices_coordinates_data;")
        cursor.execute("""
                        CREATE TABLE `prices_coordinates_data` (
                        `price` int(10) unsigned NOT NULL,
                        `date_of_transfer` date NOT NULL,
                        `postcode` varchar(8) COLLATE utf8_bin NOT NULL,
                        `property_type` varchar(1) COLLATE utf8_bin NOT NULL,
                        `new_build_flag` varchar(1) COLLATE utf8_bin NOT NULL,
                        `tenure_type` varchar(1) COLLATE utf8_bin NOT NULL,
                        `locality` tinytext COLLATE utf8_bin NOT NULL,
                        `town_city` tinytext COLLATE utf8_bin NOT NULL,
                        `district` tinytext COLLATE utf8_bin NOT NULL,
                        `county` tinytext COLLATE utf8_bin NOT NULL,
                        `country` enum('England', 'Wales', 'Scotland', 'Northern Ireland', 'Channel Islands', 'Isle of Man') NOT NULL,
                        `latitude` decimal(11,8) NOT NULL,
                        `longitude` decimal(10,8) NOT NULL,
                        `db_id` bigint(20) unsigned NOT NULL
                    ) DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=1;
                    """)
        cursor.execute("""
                    ALTER TABLE prices_coordinates_data
                    ADD PRIMARY KEY (`db_id`);
                    """)
        cursor.execute("""
                    ALTER TABLE prices_coordinates_data
                    MODIFY `db_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=1;
                    """)
        conn.commit()
        cursor.close()
    except Exception as e:
        print(f"Error creating prices_coordinates_data table: {e}")
        
def index_pp_data(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""
                    CREATE INDEX index_postcode ON pp_data(postcode);
                    """)
        cursor.execute("""
                    CREATE INDEX index_date ON pp_data(date_of_transfer);
                    """)
        conn.commit()
        cursor.close()
    except Exception as e:
        print(f"Error indexing pp_data table: {e}")
        
def create_index(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""
                    CREATE INDEX index_postcode ON postcode_data(postcode);
                    """)
        conn.commit()
        cursor.close()
    except Exception as e:
        print(f"Error indexing postcode_data table: {e}")
    
def populate_table(conn, filename, table):
    cursor = conn.cursor()
    cursor.execute(f"""
                   LOAD DATA LOCAL INFILE '{filename}' INTO TABLE {table}
                   FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED by '"'
                   LINES STARTING BY '' TERMINATED BY '\n';
                   """)
    conn.commit()
    cursor.close()
    
def equal_condition(field1, field2):
    return f"{field1}={field2}"

def not_equal_condition(field1, field2):
    return f"{field1}!={field2}"

def greater_equal_condition(field1, field2):
    return f"{field1}>={field2}"

def greater_condition(field1, field2):
    return f"{field1}>{field2}"
    
def query_table(conn, table, fields=['*'], conditions=[], limit=10):
    try:
        cursor = conn.cursor()
        cursor.execute(f"""
                    SELECT {', '.join(['*'])} FROM {'prices_coordinates_data'} {('WHERE ' if conditions != [] else '') + 'AND '.join(conditions)} LIMIT {limit}; 
                    """)
        conn.commit()
        result = cursor.fetchall()
        cursor.close()
        return result
    except Exception as e:
        print(f"The following error occured in the query to {table}: {e}")

def store_joined_data(conn, year):
    cursor = conn.cursor()
    start = time()
    cursor.execute(f"""
                SELECT price, date_of_transfer, prices.postcode, property_type, new_build_flag, tenure_type, locality, town_city, district, county, country, latitude, longitude
                FROM (SELECT price, date_of_transfer, postcode, property_type, new_build_flag, tenure_type, locality, town_city, district, county
                    FROM pp_data WHERE (date_of_transfer >= '{year}-01-01' AND date_of_transfer <= '{year}-12-31')) prices
                INNER JOIN (SELECT country, latitude, longitude, postcode
                            FROM postcode_data) postcodes
                ON prices.postcode = postcodes.postcode;
                """)
    rows = cursor.fetchall()
    file_path = f'joined_data/{year}.csv' 
    with open(file_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in rows:
                csvwriter.writerow(row)
    cursor.close()
    end = time()
    print(f"{year} took: {end-start} seconds")
        
def price_coordinates_data_to_df(records):
    return pd.DataFrame(records, columns =['price', 'date_of_transfer', 'postcode', 'property_type', 'new_build_flag', 'tenure_type', 
                                         'locality', 'town_city', 'district', 'county', 'country', 'latitude', 'longitude', 'db_id'])