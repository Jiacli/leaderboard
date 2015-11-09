# -*- coding: utf-8 -*-
import os
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from werkzeug import secure_filename
from modules.online_test import evaluate
from modules.database import connect_db, add_record
#from config import *


app = Flask(__name__)



@app.route("/")
def home():
    return render_template('index.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('fiveChooseOne'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('home'))



@app.route('/fiveChooseOne')
def fiveChooseOne():
    return '5 choose 1'

@app.route('/similarUsers')
def similarUsers():
    return 'similar users'

@app.route('/similarSongs')
def similarSongs():
    return 'similar songs'

@app.route("/online_test")
def online_test():
    context = dict(
        name=None,
        id=None
    )
    return render_template('online_test.html', context=context)


@app.route("/eval", methods=['POST'])
def eval():
    name = request.form['name']
    andrewid = request.form['andrewid']

    context = dict(
        name=name,
        id=andrewid,
        show_result=True,
        result=None
    )

 
    if not andrewid:
        context['result'] = 'Your Andrew ID is required.'
    elif not name:
        context['result'] = 'A nickname is required.'
    else:
        context['result']='Hello'   

    return render_template('online_test.html', context=context)



@app.route("/leader_board")
def leader_board():
    db = connect_db(app.config['DB_PATH'])
    records = []
    for row in db.get_all_records(db.dev_table):
        records.append(row)
    db.disconnect()

    context = dict(records=[])
    
    records = sorted(records, key=lambda x:x[2])
    for rank, record in enumerate(records):
        context['records'].append(dict(
            rank=rank+1,
            nickname=record[1],
            accuracy=record[2],
            rmse=record[3],
            submission=record[4],
            timestamp=record[5]
        ))

    return render_template('leader_board.html', context=context)

@app.route("/test_board/<token>")
def leader_board_admin(token):
    if token != app.config['AUTH_TOKEN']:
        return render_template('page_not_found.html'), 404
    db = connect_db(app.config['DB_PATH'])
    records = []
    for row in db.get_all_records(db.test_table):
        records.append(row)
    db.disconnect()

    context = dict(records=[])
    
    records = sorted(records, key=lambda x:x[2])
    for rank, record in enumerate(records):
        context['records'].append(dict(
            rank=rank+1,
            nickname=record[1],
            rmse=record[2],
            submission=record[3],
            timestamp=record[4]
        ))

    return render_template('leader_board.html', context=context)


@app.route("/file_format")
def file_format():
    return send_file('data/file_format.txt')


@app.errorhandler(404)
def not_found(error):
    return render_template('page_not_found.html'), 404


if __name__ == "__main__":
    app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
    ))



    '''
    app.config.update(dict(
        AUTH_TOKEN=auth_token,
        UPLOAD_FOLDER=folder_path['upload_hw5'],
        DEV_SET=dev_results,
        TEST_SET=test_results,
        DB_PATH=database_path['db_hw5'],
        ID_SET=stu_ids,
        HOST_IP=host_ip,
        PORT=port,
        DEBUG=debug
    ))
    '''
    #db = connect_db(app.config['DB_PATH'])
    #db.ensure_tables()
    #db.disconnect()

    app.run()
