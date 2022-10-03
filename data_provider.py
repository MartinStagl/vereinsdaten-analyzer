import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def query_database(query,database='verbands.db'):
    '''
    Load data from database
    :param query: Specifies in an SQL Select statement which data to load
    :return: Pandas Dataframe of resultset
    '''
    cnx = sqlite3.connect(database)
    df = pd.read_sql_query(query, cnx)
    cnx.commit()
    cnx.close()
    return df

def print_more(query):
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(query_database(query))
