# app.py
from flask import Flask, render_template, send_file
app = Flask(__name__)

@app.route('/')
def index():
   return '<h2>Conveyor Packaging System — UI Placeholder</h2><p>Use CLI measure_and_recommend.py for now.</p>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)