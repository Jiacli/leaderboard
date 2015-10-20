# -*- coding: utf-8 -*-
import os
from flask import Flask, url_for, render_template, request
from werkzeug import secure_filename
from modules.online_test import evaluate_rmse
from modules.database import connect_db, add_record
from config import *


app = Flask(__name__)


@app.route("/")
def home():
    return render_template('index.html')

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
    testfile = request.files['testfile']
    checkbox = request.form.get('checkbox')

    context = dict(
        name=name,
        id=andrewid,
        show_result=True,
        result=None
    )

    # data validation checks
    if not andrewid:
        context['result'] = 'Your Andrew ID is required.'
    elif not name:
        context['result'] = 'A nickname is required.'
    elif not testfile:
        context['result'] = 'No result file submitted.'
    elif andrewid not in app.config['ID_SET']:
        context['result'] = 'Andrew ID is not valid.'

    if context['result']:
        return render_template('online_test.html', context=context)

    # store file locally
    filename = secure_filename(testfile.filename)
    saved_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    testfile.save(saved_path)

    if checkbox == None:
        # evaluate on the dev set
        status, result = evaluate_rmse(saved_path, app.config['DEV_SET'])
        if not status:
            context['result'] = result
        else:
            if result == 0.0:
                context['result'] = 'Please do not submit golden standard file.'
                return render_template('online_test.html', context=context)

            context['result'] = 'The RMSE of your result is {0}.'.format(result)
            # add record in database
            db = connect_db(app.config['DB_PATH'])
            add_record(db, db.dev_table, andrewid, name, result)
            db.disconnect()
    else:
        # evaluate on the test set (for grading)
        status, result = evaluate_rmse(saved_path, app.config['TEST_SET'])
        if not status:
            context['result'] = result
        else:
            context['result'] = 'Your result file has successfully submitted. Good luck!'
            # add record in database
            db = connect_db(app.config['DB_PATH'])
            add_record(db, db.test_table, andrewid, name, result)
            db.disconnect()        

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
            rmse=record[2],
            submission=record[3],
            timestamp=record[4]
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


@app.errorhandler(404)
def not_found(error):
    return render_template('page_not_found.html'), 404


def initialize():
    app.config['AUTH_TOKEN'] = auth_token
    app.config['UPLOAD_FOLDER'] = folder_path['upload_hw4']
    app.config['DEV_SET'] = dataset_path['dev_set']
    app.config['TEST_SET'] = dataset_path['test_set']
    app.config['DB_PATH'] = database_path['db_hw4']
    app.config['ID_SET'] = stu_ids


if __name__ == "__main__":
    initialize()

    db = connect_db(app.config['DB_PATH'])
    db.ensure_tables()
    db.disconnect()

    app.run(debug=True) # host='0.0.0.0'