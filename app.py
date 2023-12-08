from flask import Flask, render_template,request, render_template, url_for,flash, redirect, abort
import pandas as pd
import numpy as np
import sys
import os
import uuid
os.environ["PYTHONUNBUFFERED"] = "0"

#creating the app
app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'ABCDEFG'

##########################################   GLOBAL VARIABLES   #########################################################################
#parsing the .txt file into a dict, these will not change
admins = pd.read_csv('passcodes.txt')
admins_dict = admins.to_dict("records")

#initializing the seating matrix
seating_matrix = [["O","O","O","O"] for row in range (12)]
#####################################################################################################################################

######################################   FUCNTIONS   ######################################################################################
#Cost matrix
def get_cost_matrix():
    cost_matrix = [[100, 75, 50, 100] for row in range(12)]
    return cost_matrix

#Load reservations
def load_reservations():
    try:
        with open("reservations.txt", "r") as file:
            next(file)
            for line in file:
                fname, row, column, _ = line.strip().split(', ')
                row, column = int(row), int(column)
                seating_matrix[row][column] = "X"
    except FileNotFoundError:
        pass  # Handle file not found error
    except StopIteration:
        # Handle empty file or file with only header
        pass
    return seating_matrix

# Update seating chart
def update_seating_matrix(row, column):
    # Convert row and column to integers
    row = int(row)
    column = int(column)
    
    if 0 <= row < len(seating_matrix) and 0 <= column < len(seating_matrix[0]):
        if seating_matrix[row][column] == "O":
            seating_matrix[row][column] = "X"
            return True
    else:
        return False

# #Current seating chart
def get_seating_matrix():
    seating_matrix = [["O", "O", "O", "O"] for row in range(12)]
    try:
        with open("reservations.txt", "r") as file:
            next(file)  # Skip the header row
            for line in file:
                try:
                    fname, row, column, _ = line.strip().split(', ')
                    row, column = int(row), int(column)
                    seating_matrix[row][column] = "X"
                except ValueError:
                    # Skip the line if it doesn't have the expected format
                    print(
                        f"Skipping line with unexpected format: {line.strip()}")
    except FileNotFoundError:
        # Handle the case where the reservations.txt file doesn't exist yet
        pass
    return seating_matrix

# Save Reservation
def save_reservation(fname, row, column, confirmation):
    with open("reservations.txt", "a") as file:
        file.write(f'{fname}, {row}, {column}, {confirmation}\n')

#Get current sales
def get_current_sales():
    #getting the seating matrix and cost matrix
    sales = 0
    seats = get_seating_matrix()
    costs = get_cost_matrix()
    #looping through the seating matrix, 
    # if an X is found in a location, that same location will be found 
    # in the cost matrix and the price added to the sales variable
    for x in range(len(costs)):
        for y in range(len(costs[0])):
            if seats[x][y] == "X":
                sales += costs[x][y]
    #returning both the total sales and the seating chart
    return sales
########################################################################################################################################

#########################################   ROUTES   ######################################################################################
# Define routes for three pages
@app.route('/', methods = ('GET','POST'))
def index():
    #Drop down menu logic if the submit button is hit
    if request.method == "POST":
        choice = request.form["Menu"]
        if choice == "AdminLogin":
            return redirect('/admin')
        elif choice == "ReserveSeat":
            return redirect('/reservations')
        else:
            return render_template('index.html')
    #if method is GET then just render the index page
    if request.method =="GET":
        return render_template('index.html')

@app.route('/admin',methods = ('GET','POST'))
def admin():
    login = False
    error = None
    seats = get_seating_matrix()  # Load the seating matrix
    sales = get_current_sales()  # Calculate total sales

    if request.method == "POST":
        username = request.form["uname"]
        password = request.form["psw"]

        for admin in admins_dict:
            if admin['Username'] == username and admin['Password'] == password:
                login = True
                break
        if login:
            return render_template("admin.html", login=login, sales=sales, seats=seats)
        else:
            error = "Wrong username/password"

    return render_template("admin.html", login=login, error=error, sales=sales, seats=seats)
    
#Still working on this part
@app.route('/reservations',methods = ("GET","POST"))
def reservations():
    # Load the current state of the seating matrix
    seats = get_seating_matrix()

    if request.method == "POST":
        # Extract form data
        fname = request.form.get("firstname")
        lname = request.form.get("lastname")
        row = request.form.get("row")
        column = request.form.get("seat")

        # Validate form data
        if row and column and row != "choose" and column != "choose":
            # Update seating matrix and save the reservation if the seat is available
            if update_seating_matrix(row, column):
                # Generate a unique confirmation number (e.g., using uuid)
                confirmation = str(uuid.uuid4())
                save_reservation(fname, row, column, confirmation)
                print(
                    f"Saving reservation: {fname}, {row}, {column}, {confirmation}")
                # Reload the updated seating matrix
                seats = get_seating_matrix()
                flash(
                    f"Reservation successful! Your confirmation number is {confirmation}.")
            else:
                # Seat is already taken
                flash("Seat already taken, please select another seat.")
        else:
            # Form data is incomplete
            flash("Please fill out all fields in the form.")

    # Render the reservations page with the current state of the seating matrix
    return render_template("reservations.html", seats=seats)

##################################################################################################################################################
app.run(host="0.0.0.0")