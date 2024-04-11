from flask import Flask, render_template, request
import pymysql, pymysql.cursors
from passlib.hash import sha256_crypt

app = Flask(__name__)

if __name__ == "__main__":
    app.run()