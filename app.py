from flask import Flask, render_template, request, url_for,flash, redirect, abort
import pandas as pd
import random
import uuid
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
    # Re-initialize seating_matrix each time this function is called
    seating_matrix = [["O", "O", "O", "O"] for _ in range(12)]

    try:
        with open('reservations.txt', 'r') as file:
            next(file)  # Skip the header line
            for line in file:
                # print("Parsing line:", line.strip()) # Debugging
                parts = line.strip().split(',')
                if len(parts) >= 5:
                    # Extract row and column assuming they are the third and fourth items
                    row, column = parts[2].strip(), parts[3].strip()
                    seating_matrix[int(row)][int(column)] = "X"
    except FileNotFoundError:
        print("reservations.txt file not found. Creating a new one.")
        open('reservations.txt', 'w').close()
    except StopIteration:  # Handle empty file with only header
        pass
    except ValueError:
        # Handle lines that cannot be parsed
        print("Error parsing a line in reservations.txt")
        pass

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
    return sales

def generate_custom_uuid():
    # Generate UUID and convert it to string
    raw_uuid = str(uuid.uuid4())
    formatted_uuid = raw_uuid.replace('-', ':')
    mixed_case_uuid = ''.join(random.choice((str.upper, str.lower))(c) for c in formatted_uuid)

    return mixed_case_uuid
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
    if request.method =="POST":
        username = request.form["uname"]
        password = request.form["psw"]
        if username != None and password != None:
            for x in range(len(admins_dict)):
                if admins_dict[x]['Username'] == username and str(admins_dict[x]['Password']) == password:
                    login = True
                    break
                else:
                    continue
            if login == True:
                sales = get_current_sales()
                seats = get_seating_matrix()   
                return render_template("admin.html",login=login,sales=sales,seats=seats)
            else:
                error = "Wrong username/password"
                return render_template("admin.html",login=login,error=error)
    if request.method == "GET":
        return render_template("admin.html",login=login)


#Still working on this part
@app.route('/reservations', methods=("GET", "POST"))
def reservations():
    if request.method == "GET":
        seats = get_seating_matrix()
        return render_template("reservations.html", seats=seats)

    if request.method == "POST":
        # print("Received Form Data:", request.form)
        
        fname = request.form.get("firstname")
        lname = request.form.get("lastname")
        row = request.form.get("row")
        seat = request.form.get("seat")

        # Validate form input
        if not all([fname, lname, row, seat]) or row == "choose" or seat == "choose":
            seats = get_seating_matrix()  # Refresh the seating matrix
            return render_template("reservations.html", seats=seats, confirmation="Blank Form Error")

        row, seat = int(row), int(seat)
        current_seats = get_seating_matrix()  # Get current state of seats

        # Check if seat is available
        if current_seats[row][seat] == "O":
            confirmation = generate_custom_uuid()    

            # Write reservation to file
            try:
                with open("reservations.txt", "a") as file:
                    file.write(f"{fname}, {lname}, {row}, {seat}, {confirmation}\n")
            except IOError:
                return render_template("reservations.html", seats=current_seats, confirmation="Error in saving reservation.")

            seats = get_seating_matrix()  # Refresh the seating matrix after updating the file
            return render_template("reservations.html", seats=seats, name=fname, confirmation=confirmation)

        else:
            return render_template("reservations.html", seats=current_seats, confirmation="Seat Taken Error")



##################################################################################################################################################





app.run(host="0.0.0.0")
