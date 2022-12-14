import numpy as np
from flask import Flask, render_template, request, Response, flash, url_for, redirect
import pandas as pd
from Youtube import Youtube
from datetime import datetime


 ####### Start of the App

app = Flask(__name__, static_folder = "./static")
app.config['SECRET_KEY'] = 'your secret key'


@app.route("/")
def index():
    return redirect(url_for('youtube_videos_search'))



# keyword search
@app.route("/youtube-videos-search")
def youtube_videos_search():
	return render_template('youtube-videos-search.html')

@app.route("/search-youtube-results", methods = ['POST'])
def search_youtube_results():

    keywords = request.form['keywords']
    api_key = request.form['key']
    no_of_results = request.form['noOfSearchResults']

    if not keywords:
        flash('Keyword(s) are required!')
    elif not api_key:
        flash('api_key is required!')
    elif not no_of_results:
        flash('Define number of results you want in your search!')
    else:
        search = Youtube(api_key, no_of_results)
        search.search_videos(keywords)
        return Response(
            datetime.today().strftime("%d %B %Y") + "\n\n" + search.Data.to_csv(index=False),
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=search-data.csv"}
                    )

    return redirect(url_for('youtube_videos_search'))



# channel search
@app.route("/youtube-channel-search")
def youtube_channel_search():
    return render_template('youtube-channels-search.html')

@app.route("/channel-search-youtube-results", methods = ['POST'])
def channel_search_youtube_results():

    channel_urls = request.form['channel-urls']
    api_key = request.form['key']
    no_of_results = request.form['noOfSearchResults']

    if not channel_urls:
        flash('Url(s) are required!')
    elif not api_key:
        flash('api_key is required!')
    elif not no_of_results:
        # flash('Define number of results you want in your search!')
        no_of_results = 50
    else:
        search = Youtube(api_key, no_of_results)
        search.search_channel_videos(channel_urls)
        return Response(
            datetime.today().strftime("%d %B %Y") + "\n\n" + search.Data.to_csv(index=False),
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=search-data.csv"}
                    )

    return redirect(url_for('youtube_channel_search'))

# Rank Tracker
@app.route("/youtube-rank-tracker")
def youtube_rank_tracker():
    return render_template('youtube-rank-tracker.html')

@app.route("/youtube-rank-tracker-results", methods = ['POST'])
def youtube_rank_tracker_results():

    keywords = request.form['keywords']
    channel_handle = request.form['Channel-Handle']
    api_key = request.form['key']
    no_of_results = request.form['noOfSearchResults']

    if not keywords:
        flash('Keyword(s) are required!')
    elif not channel_handle:
        flash('Your channel handle is required!')
    elif not api_key:
        flash('api_key is required!')
    elif not no_of_results:
        # flash('Define number of results you want in your search!')
        no_of_results = 10
    else:
        search = Youtube(api_key, no_of_results)
        search.rank_tracker(keywords, channel_handle)
        return Response(
            datetime.today().strftime("%d %B %Y") + "\n\n" + search.Data.to_csv(index=False),
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=search-data.csv"}
                    )

    return redirect(url_for('youtube_rank_tracker'))


if __name__ == '__main__':
	app.run()
