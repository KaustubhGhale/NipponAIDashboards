# erp_salesdatagen.py
import pandas as pd
import sqlite3
from flask import Flask, request, jsonify
import os

app = Flask(__name__)
DB = 'erp_sales.db'
TABLE = 'sales_data'

def init_db():
    conn = sqlite3.connect(DB)
    conn.execute(f'''
      CREATE TABLE IF NOT EXISTS {TABLE} (
        state_name TEXT, city_name TEXT, Party_Name TEXT, item_name TEXT,
        qty INTEGER, Taxable_Value REAL, cgst_amount REAL, sgst_amount REAL,
        igst_amount REAL, tcs_amount REAL, invoice_value REAL,
        t_code TEXT, location_code TEXT, invoice_date TEXT
      )
    ''')
    conn.commit(); conn.close()

@app.route('/upload', methods=['POST'])
def upload_csv():
    # 1) Receive CSV
    f = request.files.get('file')
    if not f:
        return jsonify({'error':'No file uploaded'}),400
    df = pd.read_csv(f)

    # 2) Write to SQLite
    conn = sqlite3.connect(DB)
    df.to_sql(TABLE, conn, if_exists='replace', index=False)
    conn.close()
    return jsonify({'status':'OK, data loaded to DB'}),200

@app.route('/gen_csv', methods=['GET'])
def gen_csv():
    # 3) Parameterized SQL
    sql = "SELECT * FROM sales_data WHERE 1=1 "
    for p in ('t_code','location_code','from_date','to_date'):
        v = request.args.get(p)
        if v:
            if p in ('from_date','to_date'):
                op = '>=' if p=='from_date' else '<='
                sql += f" AND date(invoice_date){op}date('{v}') "
            else:
                sql += f" AND {p}='{v}' "
    # 4) Export CSV
    conn = sqlite3.connect(DB)
    df = pd.read_sql(sql, conn)
    conn.close()
    df.to_csv('erp_sales_data.csv', index=False)
    return jsonify({'rows':len(df)}),200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5050)))

