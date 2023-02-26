from flask import Flask, render_template, request, redirect, url_for
from sqlite3 import connect
from collections import deque
import os

class Database:

    def __init__(self, db_file, table):
        self.abs_path = f"{os.path.dirname(os.path.abspath(__file__))}/{db_file}"
        self._table_name = table
        self._db_connect = connect(self.abs_path, check_same_thread=False)
        self._db = self._db_connect.cursor()
        self._get_data()

    def _get_data(self):
        self._db.execute(f"select * from {self._table_name}")
        return self._db.fetchall()

    def delete(self, index):
        # Query: delete from {table} where {column}={data} and {column}={data} and ...;
        
        # Find the necessary row
        row_to_delete = None
        for row in self.data:
            if row[0] == index:
                row_to_delete = row
                
        # Remove the index from values to create a query string
        if row_to_delete is not None: row_to_delete.pop(0)
        else: return

        # Prepare the string with arguments
        headers = self.headers
        headers.pop(0)

        query = f'delete from {self._table_name} where '
        for idx in range(0, len(headers)):
            query += f"{headers[idx]}='{row_to_delete[idx]}'"
            if idx != len(headers) - 1: query += ' and '
            else: query += ';'

        self._db.execute(query)
        self._db_connect.commit()


    def update(self, values):
        # Query: insert into {table} values({0},{1},...)
        prepared_values = [f'"{value}"' for value in values]
        self._db.execute(f"insert into {self._table_name} values({','.join(prepared_values)});")
        self._db_connect.commit()

    @property
    def data(self):
        init_data = self._get_data()
        prepared_data = []
        for idx in range(0, len(init_data)):
            el = deque(init_data[idx])
            el.appendleft(idx+1)
            prepared_data.append(list(el))
        return prepared_data

    @property
    def headers(self):
        headers = deque([description[0] for description in self._db.description])
        headers.appendleft('IDX')
        return list(headers)


app = Flask(__name__)
db = Database('database/test.db', 'employees')


@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/engineering', methods=['POST', 'GET'])
def engineering_page():
    if request.method == 'POST':
        data = list(request.form.to_dict().values())
        data.pop(-1) # Delete the "index" value
        db.update(data)
        return redirect(url_for('engineering_page'))
    elif request.method == 'GET':
        return render_template('engineering_dep.html', rows=db.data, headers=db.headers)

@app.route('/engineering/delete/<idx>')
def engineering_delete(idx):
    db.delete(int(idx))
    return redirect(url_for('engineering_page'))

@app.route('/marketing')
def marketing_page():
    return render_template('marketing_dep.html')

@app.route('/search')
def search_page():
    return render_template('search.html')
    

if __name__ == '__main__':
    app.run(debug=True)