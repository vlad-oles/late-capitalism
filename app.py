from flask import Flask, render_template, request, redirect, url_for, session
import numpy as np
import quandl
from datetime import datetime, timedelta
import calendar
from bokeh.plotting import figure
from bokeh.models import Legend
from bokeh.embed import components


app = Flask(__name__)

quandl.ApiConfig.api_key = 'YarQnKztTjms_zWSmMZy'
quandl.ApiConfig.api_version = '2015-04-09'

months = [calendar.month_name[month] for month in range(1, 13)]
years = [2018, 2017, 2016, 2015, 2014]
date_column = 'date'
close_column = 'close'
adjusted_close_column = 'adj_close'
day_index_column = 'day_index'


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ticker = request.form['ticker']
        if not ticker:
            ticker = '-'
        year = request.form['year']
        month = months.index(request.form['month']) + 1
        try:
            showing_close = request.form['close'] == 'on'
        except KeyError:
            showing_close = False
        try:
            showing_adjusted_close = request.form['adj_close'] == 'on'
        except KeyError:
            showing_adjusted_close = False
        return redirect(url_for('graph', ticker=ticker, month=month, year=year,
                                showing_close=showing_close,
                                showing_adjusted_close=showing_adjusted_close))
    else:
        return render_template('index.html', months=months, years=years)



@app.route('/graph/<ticker>/<int:month>/<int:year>/<int:showing_close>/<int:showing_adjusted_close>')
def graph(ticker, month, year, showing_close, showing_adjusted_close):
    _, n_days = calendar.monthrange(year, month)
    month_first_day = datetime(year, month, 1)
    month_last_day = datetime(year, month, n_days)
    date_from = month_first_day - timedelta(days=5)
    date_to = month_last_day + timedelta(days=5)
    date_from_str = date_from.strftime('%Y-%m-%d')
    date_to_str = date_to.strftime('%Y-%m-%d')
    all_columns = [date_column, close_column, adjusted_close_column]
    columns_mask = [True, showing_close, showing_adjusted_close]
    columns = [column for column, flag in zip(all_columns, columns_mask) if flag]

    # Fetch, sort, and enrich data.
    df = quandl.get_table('WIKI/PRICES', ticker=ticker, qopts={'columns': columns},
                          date={'gte': date_from_str, 'lte': date_to_str}, paginate=True)
    df.sort_values(date_column, inplace=True)
    df[day_index_column] = [time_diff.days for time_diff in df[date_column] - month_first_day]

    # Plot.
    plot_title = "Quandl WIKI/{} stock prices, {} {}".format(
        ticker, calendar.month_name[month], year)
    plot = figure(title=plot_title, width=800, height=400)
    legend_items = []
    X = list(range(n_days))
    if showing_close:
        Y = np.interp(X, df[day_index_column].values, df[close_column].values)
        legend_items.append(("closing price", [plot.line(X, Y)]))
    if showing_adjusted_close:
        Y = np.interp(X, df[day_index_column].values, df[adjusted_close_column].values)
        legend_items.append(("adjusted closing price", [plot.line(X, Y)]))
    plot.add_layout(Legend(items=legend_items), 'right')
    plot.xaxis.axis_label = 'date'
    plot.yaxis.axis_label = 'price, $'
    plot.xaxis.major_label_overrides = {x: (month_first_day + timedelta(days=x)).strftime('%d %b')
                                        for x in X}
    plot.xaxis.major_label_orientation = np.pi / 4
    script, div = components(plot)

    return render_template('graph.html', script=script, div=div, ticker=ticker)


if __name__ == '__main__':
  app.run(port=33507)
