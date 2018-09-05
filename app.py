from flask import Flask, render_template, request, redirect
import quandl


quandl.ApiConfig.api_key = 'YarQnKztTjms_zWSmMZy'
quandl.ApiConfig.api_version = '2015-04-09'
app = Flask(__name__)


@app.route('/')
def index():
  return render_template('index.html')


@app.route('/about')
def about():
  quandl.Database('WIKI/PRICES').bulk_download_to_file('wikip.dat')
  return render_template('about.html')


if __name__ == '__main__':
  app.run(port=33507)
