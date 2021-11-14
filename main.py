from flask import Flask, render_template, request, flash, redirect, url_for
import cs304dbi as dbi

app = Flask(__name__)
app.secret_key = "hello"


dbi.conf(db='wmdb')
conn = dbi.connect()
curs = dbi.cursor(conn)  

@app.route("/")
def index():
    return render_template("base.html")


@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/insert", methods=["GET", "POST"])
def insertMovie():

    if request.method == "GET":
        return render_template("insertMovie.html")

    data = request.form
    movieId = data["movieID"]
    movieTitle = data["movieTitle"]
    releaseYear = data["movieReleaseYear"]

    # Check if input is valid
    if (not movieId) or (not movieId.isnumeric()) or (not releaseYear.isnumeric()) or (len(releaseYear)> 4) or (not movieTitle) or (not releaseYear):
        if not movieId:
            flash("Missing input: TT is missing", "info")
        elif not movieId.isnumeric():
            flash("TT is not numeric", "info")
        
        if not movieTitle:
            flash("Missing input: Title is missing", "info")
        
        if not releaseYear:
            flash("Missing input: Release year is missing", "info")

        elif (not releaseYear.isnumeric()) or (len(releaseYear)> 4):
            flash("Enter a valid release year")
        
        return render_template("insertMovie.html")

    # Check if the movie is existed in DB
    isMovieExisted = curs.execute('select * from movie where tt = %s',[movieId])
    if isMovieExisted:
        flash(f"Error: Movie exists; Movie with tt = {movieId} is already in the database.")
        return render_template("insertMovie.html")

    # Insert Data Into DB
    curs.execute('INSERT INTO movie (tt, title, `release`) VALUES (%s, %s, %s);',[int(movieId), str(movieTitle), str(releaseYear)])
    conn.commit()

    curs.execute("SELECT * FROM movie WHERE tt = %s;", [movieId])
    movie = curs.fetchone()
    flash(f"Movie {movieTitle} inserted.")
    return redirect(url_for('updateMovie', tt=movie[0]))


@app.route("/search")
def searchByTitle():
    return render_template("search-by-title.html")


@app.route("/incompleteMovies")
def showIncompleteMovies():
    curs.execute("SELECT tt, title FROM movie WHERE (`release` IS NULL OR director IS NULL) AND title <> '';")
    incompleteMovies = curs.fetchall()
    return render_template("incomplete-movies.html", movies = incompleteMovies)


@app.route("/update-movie/<tt>", methods=["GET", "POST"])
def updateMovie(tt):
    if request.method == "GET":
        curs.execute("SELECT * FROM movie WHERE tt = %s;", [tt])
        movie = curs.fetchone()
        return render_template("update-movie.html", movie=movie)

    else:
        if "update" in request.form:
            newMovieId = request.form["movieId"]
            curs.execute("SELECT * FROM movie WHERE tt = %s;", [newMovieId])
            movie = curs.fetchone()

            # Update movie id
            if movie and newMovieId != tt :
                curs.execute("SELECT * FROM movie WHERE tt = %s;", [tt])
                movie = curs.fetchone()
                flash("The movie id already exists in the DB")
                return render_template("update-movie.html", movie=movie)

            # Update movie title
            newTitle = request.form["title"]
            oldTitle = movie[1]
            if newTitle != oldTitle:
                curs.execute("UPDATE movie SET title=%s WHERE tt=%s", [newTitle, tt])


            # Update release year
            newReleaseYear = request.form["releaseYear"]
            oldReleaseYear = movie[2]
            if newReleaseYear != oldReleaseYear:
                if newReleaseYear.isnumeric() and len(newReleaseYear) <= 4:
                    if newReleaseYear != oldReleaseYear:
                        curs.execute("UPDATE movie SET `release`=%s WHERE tt=%s", [newReleaseYear, tt])
                else:
                    flash("The release year has to be numeric and valid")
                    return render_template("update-movie.html", movie=movie)


            # Update added by
            newAddedBy = request.form["addedBy"]
            oldAddedBy = movie[4]
            if str(newAddedBy) != str(oldAddedBy):
                if newAddedBy.isnumeric():
                    if newAddedBy != oldAddedBy:
                        curs.execute("UPDATE movie SET addedby=%s WHERE tt=%s", [newAddedBy, tt])
                else:
                    flash("The Added By has to be numeric")
                    return render_template("update-movie.html", movie=movie)


            # Update director Id
            newDirectorId = request.form["directorId"]
            oldDirectorId = movie[3]
            if str(newDirectorId) != str(oldDirectorId):
                if newDirectorId.isnumeric():
                    if newDirectorId != oldDirectorId:
                        curs.execute("UPDATE movie SET director=%s WHERE tt=%s", [newDirectorId, tt])
                else:
                    print(oldDirectorId != oldDirectorId)
                    print(newDirectorId)
                    flash("The director ID has to be numeric")
                    return render_template("update-movie.html", movie=movie)

            conn.commit()
            curs.execute("SELECT * FROM movie WHERE tt = %s;", [newMovieId])
            movie = curs.fetchone()
            flash(f"Movie {newTitle} was updated successfully!")
            return render_template("update-movie.html", movie=movie)

        elif "delete" in request.form:
            curs.execute("SELECT title FROM movie WHERE tt = %s", [tt])
            movie = curs.fetchone()
            curs.execute("DELETE FROM movie WHERE tt = %s", [tt])
            conn.commit()
            flash(f"Movie {movie[0]} was deleted successfully!")
            return redirect(url_for('home'))
    
@app.route("/get-movie-id")
def getTT():
    tt = request.args["movie"]
    return redirect(url_for('updateMovie', tt=tt))


if __name__ == "__main__":
    app.run(debug=True)
