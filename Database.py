import traceback

import pymysql
from flask import jsonify

connection = pymysql.connect(
    host="localhost",
    user="root",
    password="qwertyuiop",
    db="glo_2005_webapp_2023",
    autocommit=True
)

cursor = connection.cursor()


if __name__ == '__main__':
    print("we")