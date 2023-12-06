from flask import Flask, render_template,request, render_template, url_for,flash, redirect, abort
import pandas as pd
import numpy as np
import sys
import os
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

#Current seating chart
def get_seating_matrix():
    #parsing the reservations.txt to a dict
    seats = pd.read_csv('reservations.txt')
    seats_dict = seats.to_dict("records")
    #loop through seats_dict and change every seat indicated into an "X"
    for x in range(len(seats_dict)):
       seating_matrix[seats_dict[x]["Row"]][seats_dict[x]["Column"]] = "X"
    #return the seating matrix of X's and O's 
    return seating_matrix

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
    return sales,seats
########################################################################################################################################








#########################################   ROUTES   ######################################################################################
# Define routes for three pages
@app.route('/', methods = ('GET','POST'))
def index():
    #Drop down menu logic if the submit button is hit
    if request.method == "POST":
        choice = request.form["Menu"]
        if choice == "AdminLogin":
            return render_template('admin.html')
        elif choice == "ReserveSeat":
            return render_template('reservations.html',seats=get_seating_matrix())
        else:
            return render_template('index.html')
    #if method is GET then just render the index page
    if request.method =="GET":
        return render_template('index.html')



@app.route('/admin',methods = ('GET','POST'))
def admin():
    #login variable that will indicate if the login attempt was successful
    login = False

    #if the submit button is clicked (POST method), save the username and password
    if request.method =="POST":

        username = request.form["uname"]
        password = request.form["psw"]
        #if the username and password is found in admins_dict, login =True and the current seating and sales are retrieved
        for x in range(len(admins_dict)):
            if admins_dict[x]['Username'] == username and str(admins_dict[x]['Password']) == password:
                login = True
                sales, seats = get_current_sales() 
        #admin.html is rendered, with login, sales and seats       
        return render_template("admin.html",login=login,sales=sales,seats=seats)
    #if the request method is GET, we do not need the sales and seats variables
    if request.method == "GET":
        return render_template("admin.html",login=login)


#Still working on this part
@app.route('/reservations',methods = ("GET","POST"))
def reservations():
    if request.method == "GET":
        seats = get_seating_matrix()   
        return render_template("reservations.html",seats=seats)

##################################################################################################################################################





app.run(host="0.0.0.0")
