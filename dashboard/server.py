import MySQLdb
import json
from datetime import datetime

import sys
from flask import Flask
from flask import Response
from flask import render_template

app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('index.html')

@app.route('/update/')
def update():
    # sudo apt-get install python-mysqldb
    db = MySQLdb.connect(host="127.0.0.1", user="root", passwd="", db="hpc_project")

    # By date
    sentiment_detail_hourly_keys = set()
    sentiment_detail_hourly = {'positive': {}, 'negative': {}, 'neutral': {}}

    cur = db.cursor()
    cur.execute('SELECT DATE(status_time), HOUR(status_time), sentiment, count(*) FROM trump_executive_order '
                'GROUP BY DATE(status_time), HOUR(status_time), sentiment')
    for date, hour, sent, count in cur.fetchall():
        hour_ts = int((datetime(date.year, date.month, date.day, int(hour)) -
                       datetime(1970, 1, 1)).total_seconds() * 1000)
        sentiment_detail_hourly_keys.add(hour_ts)

        if sent.lower() == 'positive':
            sentiment_detail_hourly['positive'][hour_ts] = int(count)
        elif sent.lower() == 'negative':
            sentiment_detail_hourly['negative'][hour_ts] = int(count)
        elif sent.lower() == 'neutral':
            sentiment_detail_hourly['neutral'][hour_ts] = int(count)
    cur.close()

    for ts in sentiment_detail_hourly_keys:
        if ts not in sentiment_detail_hourly['positive']:
            sentiment_detail_hourly['positive'][ts] = 0
        elif ts not in sentiment_detail_hourly['negative']:
            sentiment_detail_hourly['negative'][ts] = 0
        elif ts not in sentiment_detail_hourly['neutral']:
            sentiment_detail_hourly['neutral'][ts] = 0

    sentiment_detail_hourly['positive'] = sorted([[k, v] for k, v in sentiment_detail_hourly['positive'].items()])
    sentiment_detail_hourly['negative'] = sorted([[k, v] for k, v in sentiment_detail_hourly['negative'].items()])
    sentiment_detail_hourly['neutral'] = sorted([[k, v] for k, v in sentiment_detail_hourly['neutral'].items()])

    # By sentiment
    sentiment = {'positive': 0, 'negative': 0, 'neutral': 0}

    cur = db.cursor()
    cur.execute('SELECT sentiment, count(*) FROM trump_executive_order GROUP BY sentiment')
    for sent, count in cur.fetchall():
        sentiment[sent.lower()] = int(count)
    cur.close()

    num_data = sum(sentiment.values())
    if num_data > 0:
        for sent in sentiment:
            sentiment[sent] = float(sentiment[sent]) / num_data * 100

    # By hashtag
    hashtags = []
    hashtag_total = 0
    cur = db.cursor()
    cur.execute('SELECT hashtag, count(*) as freq FROM trump_executive_order_hashtag GROUP BY hashtag ORDER BY freq desc')
    for hashtag, count in cur.fetchall():
        hashtags.append((hashtag.lower(), int(count)))
        hashtag_total += int(count)
    cur.close()

    for i, (t, c) in enumerate(hashtags):
        hashtags[i] = (t, c, float(c)/hashtag_total * 100)

    hashtags = hashtags[:5]

    # By terms
    terms = []
    term_total = 0
    cur = db.cursor()
    cur.execute(
        'SELECT term, count(*) as freq FROM trump_executive_order_term GROUP BY term ORDER BY freq desc')
    for term, count in cur.fetchall():
        terms.append((term.lower(), int(count)))
        term_total += int(count)
    cur.close()

    for i, (t, c) in enumerate(terms):
        terms[i] = (t, c, float(c)/term_total * 100)

    terms = terms[:5]

    # By batch
    batch_status_count = []
    batch_time_windows = []

    last_timestamp = None
    cur = db.cursor()
    cur.execute('SELECT process_time, status_count FROM trump_executive_order_summary')
    for process_time, status_count in cur.fetchall():
        batch_status_count.append(int(status_count))
        if last_timestamp:
            batch_time_windows.append((process_time - last_timestamp).total_seconds())
        last_timestamp = process_time
    cur.close()

    return Response(response=json.dumps([
        {'num_processed': num_data, 'num_batch': len(batch_status_count),
         'avg_time_window': int(sum(batch_time_windows)/len(batch_time_windows)) if len(batch_time_windows) > 0 else 0},
        sentiment, sentiment_detail_hourly, hashtags, terms]), status=200, mimetype='application/json')

if __name__ == "__main__":
    args = sys.argv
    if len(args) < 2:
        args[1] = 80
    app.run(host='0.0.0.0', port=args[1])