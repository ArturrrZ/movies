from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from cs50 import SQL
import os
import qrcode
import random
from search import get_random_movies
import requests
app = Flask(__name__)
app.config['SECRET_KEY']=os.environ.get('SECRET_KEY')
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///votes.db")

active_votings = {}
genres = [{'id': 28, 'name': 'Action'},
          {'id': 12, 'name': 'Adventure'},
          {'id': 16, 'name': 'Animation'},
          {'id': 35, 'name': 'Comedy'},
          {'id': 80, 'name': 'Crime'},
          {'id': 99, 'name': 'Documentary'},
          {'id': 18, 'name': 'Drama'},
          {'id': 10751, 'name': 'Family'},
          {'id': 14, 'name': 'Fantasy'},
          {'id': 36, 'name': 'History'},
          {'id': 27, 'name': 'Horror'},
          {'id': 10402, 'name': 'Music'},
          {'id': 9648, 'name': 'Mystery'},
          {'id': 10749, 'name': 'Romance'},
          {'id': 878, 'name': 'Science Fiction'},
          {'id': 10770, 'name': 'TV Movie'},
          {'id': 53, 'name': 'Thriller'},
          {'id': 10752, 'name': 'War'},
          {'id': 37, 'name': 'Western'}]
@app.route("/")
def index():
    for voting in active_votings:
        print(voting)
    return render_template("index.html")

@app.route("/search", methods = ['GET', 'POST'])
def search():
    if request.method == 'POST':
        category = request.form.get("category")
        people = request.form.get("people")
        genre_id = None
        # print(category, people)
        # check number of people
        try:
            people = int(people)
            if people < 1:
                error = "At least 1 person"
                return render_template("search.html",categories=genres, error=error)
        except ValueError as e:
            print(e)
            error = "Invalid data types"
            return render_template("search.html",categories=genres, error=error)
        # search for genre
        for genre in genres:
            if genre["name"].lower() == category.lower():
                print("found")
                genre_id = genre['id']
                print(genre_id)
                print("----------")
                break
        else:
            error = "No such genre"
            return render_template("search.html", categories=genres, error=error)
        # DATA IS VALID
        random_movies = get_random_movies(genre_id)
        for movie in random_movies:
            movie['genre_ids'] = [x for x in movie['genre_ids']]
            for i in range(len(movie['genre_ids'])):
                for genre in genres:
                    if genre['id'] == movie['genre_ids'][i]:
                        movie['genre_ids'][i] = genre['name']
                        break
        voting_id = random.randint(1111,9999)
        votings_ids = db.execute("SELECT voting_id FROM votes GROUP BY voting_id")
        votings_ids = [x['voting_id'] for x in votings_ids]
        while voting_id in votings_ids:
            voting_id = random.randint(1111, 9999)
        active_votings[voting_id] = {
            'max_users': people,
            'current_users': 0,
            'movies': random_movies,
        }
        session['voting_id'] = voting_id
        for movie in random_movies:
            db.execute("INSERT INTO votes (voting_id, movie_name, movie_id, likes, dislikes)"
                       "VALUES (?, ?, ?, ?, ?)", voting_id, movie['title'], movie['id'], 0, 0)
        return redirect(url_for("create_voting", voting_id=voting_id))
    return render_template("search.html", categories=genres)

@app.route("/create_voting/<int:voting_id>")
def create_voting(voting_id):
    url = request.url.split('create_voting')
    base_url = url[0]
    voting_url = f"{base_url}voting/{voting_id}"
    img = qrcode.make(voting_url)
    img.save(f"static/qrs/{voting_id}.png")
    return render_template("link.html", voting_url=voting_url, voting_id=voting_id)

@app.route("/voting/<voting_id>")
def voting(voting_id):
    try:
        voting_id = int(voting_id)
    except ValueError:
        return render_template("error.html", error="No such voting")
    if voting_id in active_votings:
        # if reload
        if active_votings[voting_id]['current_users'] < active_votings[voting_id]['max_users']:
            #enough space
            active_votings[voting_id]['current_users'] += 1
            movies = active_votings[voting_id]['movies']
            print(movies[0]['genre_ids'])
            return render_template("voting.html", movies=movies, voting_id=voting_id)
        else:
            return render_template("error.html", error="Maximum people already")
    else:
        return render_template("error.html", error="No such voting")
    return "goodd"

@app.route("/results/<voting_id>")
def results(voting_id):
    try:
        voting_id = int(voting_id)
    except ValueError:
        return render_template("error.html", error="No such voting")
    rows = db.execute("SELECT * FROM votes WHERE voting_id = ? ORDER BY likes DESC", voting_id)
    place = 1
    if voting_id not in active_votings:
        return render_template("error.html", error="Voting is no longer active")
    movies_data = active_votings[voting_id]['movies']
    if rows[0]['is_finished'] == 1:
        for row in rows:
            row['place'] = place
            place += 1
            for movie in movies_data:
                if movie['id'] == row['movie_id']:
                    row['genre_ids'] = movie['genre_ids']
                    row['poster_path'] = movie['poster_path']
                    row['title'] = movie['title']
                    row['release_date'] = movie['release_date']
                    row['poster_path'] = movie['poster_path']
                    row['overview'] = movie['overview']
        return render_template("results.html", movies=rows)
    else:
        return render_template("error.html", error="no finish")

@app.route("/api/vote", methods=['POST'])
def vote():
    data = request.get_json()
    movie = db.execute("SELECT * from votes WHERE voting_id = ? AND movie_id = ?", data['voting_id'], data['movie_id'])
    if movie[0]['is_finished'] == 1:
        return jsonify({"is_finished": True})
    likes = movie[0]['likes']
    dislikes = movie[0]['dislikes']
    if data['type'] == "like":
        likes += 1
        db.execute("UPDATE votes SET likes = ? WHERE voting_id = ? AND movie_id = ?", likes, data['voting_id'], data['movie_id'])
    else:
        dislikes += 1
        db.execute("UPDATE votes SET dislikes = ? WHERE voting_id = ? AND movie_id = ?", dislikes, data['voting_id'], data['movie_id'])
    return jsonify({"ok":" Ok"})
@app.route("/api/ask_for_end")
def ask_for_end():
    voting_id = request.args.get("voting_id")
    type = request.args.get("type", "ask")
    voting = active_votings[int(voting_id)]
    max_total = voting['max_users'] * len(voting['movies'])
    rows = db.execute("SELECT SUM(likes + dislikes) as total, is_finished FROM votes WHERE voting_id = ?", voting_id)
    if max_total == rows[0]['total']:
        db.execute("UPDATE votes SET is_finished = true WHERE voting_id = ?", voting_id)
        return jsonify({"is_finished": True})
    if type == "ask":
        if rows[0]['is_finished'] == 0:
            return jsonify({"is_finished": False, "total": rows[0]['total']})
        else:
            return jsonify({"is_finished": True})
    else:
        db.execute("UPDATE votes SET is_finished = true WHERE voting_id = ?", voting_id)

@app.route("/<anything>")
def anything(anything):
    return render_template("error.html", error="Route does not exist"), 404
if __name__ == '__main__':
    app.run(debug=False)