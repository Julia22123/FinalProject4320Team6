from flask import Flask, render_template, render_template, url_for,flash, redirect, abort


app = Flask(__name__)
app.config["DEBUG"] = True

# Define routes for three pages
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template("admin.html")


@app.route('/reservations')
def reservations():
    return render_template("reservations.html")


app.run(host="0.0.0.0")
