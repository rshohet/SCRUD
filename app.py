from flask import Flask, render_template, request, redirect, url_for, session
import pymysql

app = Flask(__name__)
app.secret_key = 'your secret key'


@app.route('/')
def hello_world():  # put application's code here
    return render_template('index.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    print('in login 1')
    msg = ''
    print("rf: ")
    for x in request.form: print(x)
    print(request.method)
    for y in request.args: print(y)
    print('in if')
    conn = pymysql.connections.Connection(host="localhost", user="root", passwd="rachel12", db="udb")
    cursor = conn.cursor()

    if request.method == 'POST' and 'login' in request.form and 'password' in request.form:
        if request.form['host']:
            typed_host = request.form['host']
        else:
            typed_host = "localhost"
        if request.form['port']:
            typed_port = request.form['port']
        else:
            typed_port = "3306"
        if request.form['database']:
            typed_database = request.form['database']
        else:
            typed_database = "udb"
        if request.form['login']:
            typed_login = request.form['login']
        else:
            typed_login = "root"
        typed_password = request.form['password']

        query = "SELECT * FROM users WHERE login = '" + typed_login + "' AND password = '" + typed_password + "'"
        print(query)
        cursor.execute(query)
        user_row = cursor.fetchone()
        print(user_row)
        if user_row:
            session['loggedin'] = True
            session['user_id'] = user_row[0]
            session['login'] = user_row[1]
            session['host'] = typed_host
            session['database'] = typed_database
            session['port'] = typed_port
            session['password'] = typed_password

            msg = 'Logged in successfully !'
            return render_template('index.html', msg=msg)
        else:
            msg = 'Incorrect login / password !'

    return render_template('login.html', msg=msg)


@app.route('/table/<name>', methods=['POST', 'GET'])
def table(name):
    print('in table name ')
    for x in request.form: print("form", x)
    print("method", request.method)
    for y in request.args: print("args", y)
    password = "rachel12"
    conn = pymysql.connections.Connection(host="localhost", user="root", passwd=password, db="udb")
    cursor = conn.cursor()

    # get the list of columns for the specified table
    query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{name}'"
    cursor.execute(query)
    columns = cursor.fetchall()
    # print("col", columns)
    for column in columns:
        print("col", column)
    if request.method == 'GET':
        return render_template('scrud.html', name=name, columns=columns)
        for x in request.form: print("form", x)
        print("method", request.method)
        for y in request.args: print("args", y)

    elif request.method == 'POST':
        for x in request.form: print("form", x)
        print("method", request.method)
        for y in request.args: print("args", y)
        print("in post to search")

        # Construct query based on search form input
        search_params = []
        if 'search' in request.form:
            query = "SELECT * FROM {} WHERE ".format(name)

        elif 'create' in request.form:
            query = "INSERT INTO {} ".format(name)

        elif 'delete' in request.form:
            query = "DELETE FROM {} WHERE ".format(name)

        cols = []
        for column in columns:
            col_name = column[0]
            value = request.form[col_name]
            print("val", value)
            print("col_name", col_name)

            if value:
                cols.append(col_name)
                search_params.append(value)
                print("search param", search_params)
                if 'search' in request.form or 'delete' in request.form:
                    query += f"{col_name}=%s AND "
                elif 'update' in request.form:
                    query += f"{col_name}=%s, "

        if search_params:
            if 'search' in request.form or 'delete' in request.form:
                query = query[:-5]  # Remove the final 'AND' and trailing space
            elif 'create' in request.form:
                all_cols = ','.join(cols)
                query += f"({all_cols}) VALUES ("
                for v in search_params:
                    print(v)
                    query += "'" + v + "',"
                query = query[:-1]  # delete final comma
                query += ")"

            print("query", query)

            if 'search' in request.form or 'delete' in request.form:
                cursor.execute(query, search_params)
                if 'search' in request.form:  # store the second half of the query in case client wants to update the results of search row
                    final_query = cursor.mogrify(query, search_params).split("WHERE")[1][1:]
                    # update_param = final_query.split("WHERE")[1][1:].replace(" AND ", ",")
                    # print("up param 2", update_param)
                    print("FINAL QUERY", final_query)
            elif 'create' in request.form:
                cursor.execute(query)

            results = cursor.fetchall()
            conn.commit()

            if 'search' in request.form:
                res = []
                headers = [i[0] for i in cursor.description]
                res.append(headers)
                data = []
                for row in results:
                    curData = []
                    for col in row:
                        curData.append(str(col))
                    res.append(curData)
                print("res", res)
                return render_template('res.html', name=name, final_query=final_query, results=res)
            elif 'delete' in request.form or 'create' in request.form:
                return render_template('index.html')


@app.route('/update/<name>/<final_query>', methods=['POST', 'GET'])
def update(name, final_query):
    print("HHHHHHH", name, final_query)

    conn = pymysql.connections.Connection(host="localhost", user="root", passwd="rachel12", db="udb")
    cursor = conn.cursor()

    # get the list of columns for the specified table
    query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{name}'"
    cursor.execute(query)
    all_columns = cursor.fetchall()

    for x in request.form: print("FORM", x)
    print("METHOD", request.method)
    print("METHOD", request.form)

    if request.method == 'GET':
        return render_template('update.html', name=name, final_query=final_query, all_columns=all_columns)

    elif request.method == 'POST':
        for x in request.form: print("form", x)
        print("method", request.method)
        for y in request.args: print("args", y)
        print("in post to update")

        query = "UPDATE {} SET".format(name)
        print("before loop", all_columns)
        for col in all_columns:
            print("after loop", col)
            if request.form[col[0]]:
                print("COLS NAME", col)
                query += f" {col[0]}='{request.form[col[0]]}',"
        query = query[
                :-1] + f" WHERE {final_query}"  # delete trailing comma and space and include the where clause from search query
        print("query", query)
        cursor.execute(query)
        conn.commit()
        return render_template('index.html')


if __name__ == '__main__':
    app.run()
