import math

import numpy as np
import pandas as pd
from alive_progress import alive_it
from sqlalchemy import create_engine, insert, Table, MetaData, Column, Integer, Double, String
from sqlalchemy.sql import text
from sqlalchemy.engine import URL

BULK_SIZE = 1000

# return if x is numeric and nan
def isnan(x):
    try:
        return math.isnan(float(x))
    except:
        return False
    
# return if string is a number, built in function returns false for decimals so it should actually be called isInteger not isNumeric
def is_numeric(x):
    if x.lower() == 'infinity':
        return False
    
    try:
        float(x)
    except:
        return False
    return True

def escape_string(x):
    return x.replace("'", "''")

def build_insert(table_name, value_dict):
    columns = ','.join([str(x) for x in value_dict])
    values = [str(value_dict[x]) for x in value_dict]
    values = ','.join([x if is_numeric(x) else f"'%s'" % escape_string(x.lower()) for x in values])
    result = f'INSERT INTO %s (%s) VALUES (%s)' % (table_name, columns, values)
    return result

def get_column_type(dtype):
    if dtype == np.float64 or dtype == np.float32 or dtype == np.float16:
        return Double
    elif dtype == np.int64 or dtype == np.int32 or dtype == np.int8:
        return Integer
    else:
        return String

# Insert a csv into a table, create it if not exists
# requires the DB exists
# if primary key == None, then create and autoincrement ID column, requires id not present
def csv_to_psql(dataframe, database, table_name, primary_key=None):
    column_names = [x.lower() for x in dataframe.columns]
    types = list(dataframe.dtypes)

    if primary_key is None and 'id' in column_names:
        raise Exception('No primary key is specified yet id column is present. Either specify a primary key or remove id column')
    
    if primary_key is not None and primary_key not in column_names:
        raise Exception('Specified primary key is not in columns')

    url = URL.create(
        drivername='postgresql',
        username='postgres',
        database=database
    )

    engine = create_engine(url)
    meta = MetaData()

    with engine.connect() as connection:
        # Create table if not exists, infer types
        table = None
        if not engine.dialect.has_table(connection, table_name):
            columns = []
            if primary_key is not None:
                primary_key_index = np.argwhere(column_names == primary_key)
                columns.append(Column(column_names.pop(primary_key_index), get_column_type(types.pop(primary_key_index)), primary_key=True))
            else:
                columns.append(Column('id', Integer, primary_key=True, autoincrement=True))

            for i in range(len(column_names)):
                columns.append(Column(column_names[i], get_column_type(types[i])))

            table = Table(table_name, meta, *columns)
            meta.create_all(engine)
        else:
            table = Table('horses', meta, autoload_with=engine)

        # Perform inserts
        # TODO look into bulk inserts, they might be faster
        inserts = []
        for i in alive_it(range(len(dataframe))):
            values = dict([x for x in zip(column_names, dataframe.iloc[i]) if not isnan(x[1])])
            statement = build_insert(table_name, values)
            inserts.append(statement)

            if i % BULK_SIZE == BULK_SIZE - 1:
                connection.execute(text(';'.join(inserts)))
                inserts = []
        if len(inserts) > 0:
            connection.execute(text(';'.join(inserts)))
        connection.commit()