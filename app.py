from flask import Flask, render_template

app = Flask(__name__)

# Define routes for three pages
@app.route('/')
def index():
    return 'This is the homepage'

@app.route('/admin')
def about():
    return 'This is the admin page'

@app.route('/reservations')
def contact():
    return 'This is the reservations page'

if __name__ == '__main__':
    app.run(debug=True)
