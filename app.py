from cryptography.fernet import Fernet
from flask import Flask, render_template, request
import csv
import io
import pandas as pd
import mysql.connector as db

app = Flask(__name__)

# GETTING CSV FILE


@app.route('/')
def upload():
    return render_template("index.html")

# READING CSV FILE


@app.route('/success', methods=['POST'])
def success():
    if request.method == 'POST':
        file = request.files['file']
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        reader = csv.reader(stream)
        f = file.filename
        file.save(f)

        datas = []
        for row in reader:
            datas.append(row)

        datas = pd.DataFrame(datas)
        print(datas)

        # DATABASE CONNECTIVITY

        connection = db.connect(
            host='localhost', database='csvdata', user='root', password='')

        if connection.is_connected():
            db_Info = connection.get_server_info()
            print("Connected to MySQL Server version ", db_Info)
            cursor = connection.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            print("Database Connectivity is Successful : ", record)
        else:
            print("Something went Wrong....")

        # GETTING COLUMN NAMES

        names = []
        for x in range(len(datas.columns)):
            names.append(datas[x][0])
        print(names)

        # DYNAMICALLY CREATING TABLE

        sql = """CREATE TABLE %s""" % f[:-4] + "(\n" + ",\n".join(
            [("%s varchar(255)" % name.replace(" ", "")) for name in names]) + "\n);"
        print(sql)
        cursor.execute(sql)

        # INSERTING ELEMENTS FROM CSV TO TABLE

        ele = []
        for x in range(1, len(datas.index)):
            ele.clear()
            for y in range(0, len(datas.columns)):
                ele.append(datas[y][x])
            sql_insert = "INSERT INTO %s" % f[:-4]+" ("+",".join([("%s" % name.replace(
                " ", "")) for name in names])+")" + " VALUES ("+",".join([("'%s'" % elem) for elem in ele])+");"
            print(sql_insert)
            cursor.execute(sql_insert)
            connection.commit()

        # SUCCESSFULLY INSERTED...

        return render_template("success.html", name=f[:-4])


if __name__ == '__main__':
    app.run(debug=True)
