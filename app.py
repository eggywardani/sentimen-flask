from itertools import count
from flask import Flask, render_template, request, flash
import tweepy
import csv
import re
import string
import googletrans
from googletrans import Translator
from textblob import TextBlob


# Set api key


app = Flask(__name__)
app.config['SECRET_KEY'] = '12345'

analysis_result = []


def crawling_data(query,  count):
    api_key = "ov95PcX3f3y8QpqCa81vcRKwJ"
    api_secret_key = "S7tGAQdo4C2ElMLqCLeTCurxMpJ8EuVHicUPRu9Ey4WSNUzdLi"
    access_token = "1407281799340838922-aWoy2ycip5JmL8gOfoIuzzG4aDtYdl"
    access_token_secret = "vhNVUS9001OaTfvmIegFqhO9ym0soPhUHfwhtyKh5jXoT"
    # auth
    auth = tweepy.OAuthHandler(api_key, api_secret_key)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    # CSV
    file = open('static/csv/Data Mentah Twitter.csv',
                'w', newline='', encoding='utf-8')
    writer = csv.writer(file)
    # since='2021-11-01', until='2021-11-30'

    for tweet in tweepy.Cursor(api.search_tweets, q=query, lang="id").items(int(count)):
        flash('Berhasil crawling data sebanyak ' +
              str(count) + ' kali', 'success')

        tweets = [tweet.created_at, tweet.user.screen_name,
                  tweet.text.encode('utf-8')]
        writer.writerow(tweets)
        analysis_result.append(tweets)


preprocessing_result = []


def preprocessing_data():
    file = open('static/csv/Data Hasil Preprocessing.csv',
                'w', newline='', encoding='utf-8')
    writer = csv.writer(file)
    translator = Translator()

    with open("static/csv/Data Mentah Twitter.csv") as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            flash('Berhasil preprocessing data ', 'success')
            # menghapus karakter tidak penting
            clean = re.sub(r'(\\x(.){2})', '', row[2])
            clean = ' '.join(
                re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", clean).split())
            clean = clean[1:]
            clean = clean.replace('RT', '')
            clean = clean.strip()
            clean = clean.casefold()
            # labelling
            tweet = {}
            value = translator.translate(clean, dest='en')
            terjemahan = value.text
            data_label = TextBlob(terjemahan)

            if data_label.sentiment.polarity > 0.0:
                tweet['sentiment'] = "Positif"
            elif data_label.sentiment.polarity == 0.0:
                tweet['sentiment'] = "Netral"
            else:
                tweet['sentiment'] = "Negatif"

            labelling = tweet['sentiment']
            # write csv
            tweets = [row[0], row[1], row[2], clean, labelling]
            writer.writerow(tweets)
            preprocessing_result.append(tweets)
            flash('Berhasil preprocessing data ', 'success')


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/crawling', methods=['GET', 'POST'])
def crawling():
    if request.method == 'POST':
        query = request.form.get('query')
        jumlah = request.form.get('jumlah_data')

        analysis_result.clear()
        if request.form.get('crawling_btn') == 'crawling':
            crawling_data(query, jumlah)
            return render_template('crawling.html', value=analysis_result)

    elif request.method == 'GET':
        return render_template('crawling.html', value=analysis_result)

    return render_template('crawling.html')


@app.route('/preprocessing', methods=['GET', 'POST'])
def preprocessing():
    if request.method == 'POST':

        preprocessing_result.clear()
        if request.form.get('preprocessing_btn') == 'preprocessing':
            preprocessing_data()
            return render_template('preprocessing.html', value=preprocessing_result)

    elif request.method == 'GET':
        return render_template('preprocessing.html', value=preprocessing_result)

    return render_template('preprocessing.html')


@app.route('/analisa')
def analisa():
    return render_template('analisa.html')

# @app.route('/Akurasi')
# MANTAP :v
# def analisa():
#    return render_template('analisa.html')


if __name__ == '__main__':
    app.run(debug=True)
