from flask import Blueprint, render_template, url_for, request, redirect, flash
from flask_login import login_user, logout_user, login_required, current_user
from .models import Users
import mysql.connector
from . import db

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def Index():
    return render_template('index.html')


@main.route('/all_users')
@login_required
def AllUsers():
    con = mysql.connector.connect(
        host='localhost',
        user='root',
        password='12345',
        database='mydb'
    )
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * from Users")
    row = cur.fetchall()
    con.close()
    return render_template('all_user.html', rows=row)
