from flask import Flask, render_template, url_for, Response, request
import pymysql
import json
import config
import re

app = Flask(__name__)

db = pymysql.connect("localhost", "root", "root", "san")
cursor = db.cursor()


def get_data(sql):
    db.ping()

    cursor.execute(sql)
    results = cursor.fetchall()
    index = cursor.description
    headers = [title[0] for title in index]
    mysql_data = []
    for data in results:
        mid_data = dict(zip(headers, data))
        mysql_data.append(mid_data)
    return mysql_data


@app.route('/show', methods=['POST', 'GET'])
def sql_show():
    if request.json != None:
        data = request.json.get('data')
        value = data.get('search').get('value')
        index = data.get('page').get('index')
        size = data.get('page').get('size')
        sql = "select * from switch_device"
        text_cond = and_or(value)
        # ['devicename like "%wq%" OR ip like "%wq%" OR location like "%wq%"' AND ("","","")]
        if text_cond:
            sql = sql + ' where ' + text_cond
        sql = count_rows(sql)
        db.ping()
        count = cursor.execute(sql)
        sql = sql + ' limit ' + str(size) + ' offset ' + str(size * (index - 1))
    mysql_data = get_data(sql)
    return json.dumps(dict(total=count, data=mysql_data))


def and_or(value):
    mid_values = value.split()
    columns = config.columns
    and_cond = []
    text_cond = ''
    for mid_value in mid_values:
        or_cond = []
        for col in columns:
            or_cond.append(col + ' like "%' + mid_value + '%"')
        if or_cond:
            and_cond.append(' OR '.join(or_cond))
    if and_cond:
        text_cond = '(' + ') AND ('.join(and_cond) + ')'
    return text_cond


@app.route('/insert', methods=['POST', 'GET'])
def insert():
    data = request.json['data']
    placeholders = ', '.join(['%s'] * len(data))
    values = list(request.json['data'].values())
    columns = ', '.join(data.keys())
    sql = "INSERT INTO switch_device ( %s ) VALUES ( %s )" % (columns, placeholders)
    cursor.execute(sql, values)
    db.commit()
    return ''


@app.route('/delete', methods=['POST', 'GET'])
def delete():
    id = request.json.get('id')
    sql = 'delete from switch_device where id = %s' % id
    db.ping()
    cursor.execute(sql)
    db.commit()
    return ''


@app.route('/edit', methods=['POST', 'GET'])
def edit():
    id = request.json['data'].get('id')
    values = list(request.json['data'].values())
    values.pop(0)
    values.append(id)
    sql = 'update switch_device set devicename=%s,ip=%s,location=%s,area=%s,hardware=%s,platform=%s,version=%s,sn=%s,' \
          'slot0=%s,memory=%s, bootflash=%s WHERE id=%s'
    db.ping()
    cursor.execute(sql, values)
    db.commit()
    return ''


def count_rows(sql):
    sql = re.sub('SELECT.+FROM', 'SELECT COUNT(*) FROM', sql, re.I)
    sql = re.sub('LIMIT\s+\d+(\s+OFFSET\s+\d+)?', '', sql, re.I)
    return sql


@app.route('/', methods=['POST', 'GET'])
def data_show():
    return render_template('Switch_table.html')


if __name__ == '__main__':
    app.run(debug=True)
