from .config import *
import pymysql
import requests
import zipfile

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
    
def query_table(conn, table, fields=['*'], conditions=[]):
    cursor = conn.cursor()
    cursor.execute(f"""
                   SELECT {', '.join(fields)} FROM {table} WHERE {'AND '.join(conditions)}; 
                   """)
    conn.commit()
    result = cursor.fetchall()
    cursor.close()
    return result