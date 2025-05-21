from flask import Flask, render_template, request, redirect, url_for, flash
from utils.downloader import download_disclosures

app = Flask(__name__)
app.secret_key = "supersecretkey"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    year = request.form['year']
    success, message = download_disclosures(year)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
