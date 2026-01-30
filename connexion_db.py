from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g

import pymysql.cursors

import os

import pymysql.cursors
import os

def get_db():
    db = pymysql.connect(
        host=os.environ.get('MYSQLHOST'),
        user=os.environ.get('MYSQLUSER'),
        password=os.environ.get('MYSQLPASSWORD'),
        database=os.environ.get('MYSQLDATABASE'),
        port=int(os.environ.get('MYSQLPORT', 3306)),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return db
