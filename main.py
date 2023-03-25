from flask import Flask, render_template, redirect, url_for
from flask import request
from datetime import date, timedelta
import requests
import json

app = Flask(__name__)

# Global dictionary to store values during programme run
personal_data_dict = {}

# PART ONE - collect and validate the data

# Index function is responsible for fetching data from the user. 
# Date validation is implemented in this function so the flow is interupted before it hits datetime function.
# try/except block prevents alpha characters from being processed
@app.route("/", methods = ['GET','POST'])
def index():
    nhsnumber = request.form.get("nhsnumber")
    name = request.form.get("name")
    day = request.form.get("day")
    month = request.form.get("month")
    year = request.form.get("year")
    if request.method == 'POST':
        try:
            if int(month) in [2] and int(day) in range(1,29):
                return get_personal_data(nhsnumber, name, day, month, year)
            elif int(month) in [2] and int(day) in range(1,30) and ((int(year) % 4 == 0 and int(year) % 100 != 0) or int(year) % 400 == 0):
                return get_personal_data(nhsnumber, name, day, month, year)
            elif int(month) in [4,6,9,11] and int(day) in range(1,31):
                return get_personal_data(nhsnumber, name, day, month, year)
            elif int(month) in [1,3,5,7,8,10,12] and int(day) in range(1,32):
                return get_personal_data(nhsnumber, name, day, month, year)
            else:
                return render_template("error.html", text="Please check date entered")
        except ValueError:
            return render_template("error.html", text="Unexpected characters in date")
    return (render_template('index.html'))

# get_personal_data function processes data from user input.
# date is transformed to match API format and age is calculated
# Programme stops here if user is too young
# There's additional validation for NHSnumber being too short/too long. This is not compliant with the actual standard
# It has been implemented to avoid unnecessary API calls
# All data is stored in personal_data_dict 
def get_personal_data(nhsnumber, name, day, month, year):
    personal_data_dict["nhsnumber"] = nhsnumber
    personal_data_dict["name"] = name
    day = int(day)
    month = int(month)
    year = int(year)
    user_dob = date(year,month,day)
    user_age = (date.today() - user_dob) // timedelta(days=365.2425)
    personal_data_dict["born"] = f'{"{:02d}".format(day)}-{"{:02d}".format(month)}-{year}'
    personal_data_dict["age"] = user_age
    if len(nhsnumber) != 9:
        return render_template("error.html", text="Incorrect NHS Number")
    elif int(personal_data_dict["age"]) < 16:
        return render_template("error.html", text="You are not eligble for this service")
    else:
        return api_validator(nhsnumber)

# api_validator function uses nhsnumber to access API.
# once matched it splits name into first name and surname since only surname is required by app
# further processing checks if surname and dob are matching API        
def api_validator(nhsnumber):
    api_key = 'INSERT SUBSCRIPTION KEY HERE'
    # SUBSCRIPTION KEY IS NECESSARY TO ACCESS API
   
    url = f'https://al-tech-test-apim.azure-api.net/tech-test/t2/patients/{nhsnumber}'
    headers = {'Ocp-Apim-Subscription-Key': '{key}'.format(key=api_key)}

    response = requests.get(url, headers=headers)
    personal_data_api = json.loads(response.content)
    if response.status_code == 404 or nhsnumber == 123456789:
        return render_template("error.html", text="Your details could not be found")
    elif response.status_code == 200:
        user_name = (personal_data_api["name"]).split(',')
        user_surname_check = user_name[0] 
        if personal_data_dict["name"].casefold() != user_surname_check.casefold() or personal_data_dict["born"] != personal_data_api["born"]:
            return render_template("error.html", text="Your details could not be found")
        else:
            return redirect(url_for("ask_questions"))

# PART TWO - collect lifestyle answers and generate score

# ask_questions gatheres lifestyle answers from user. 
# Only yes/no answer is accepted due to Python's limitation to read from radio or dropdown type inputs.
@app.route("/questions", methods = ['GET','POST'])
def ask_questions():
    question_one = request.form.get("question_one")
    question_two =  request.form.get("question_two")   
    question_three =  request.form.get("question_three")
    if request.method == 'POST':
        return score_generator(question_one, question_two, question_three)
    else:
        return render_template('questions.html')

# Score_generator follows a simple counter logic and only works if the answer is in range. 
# There is an additional key_error handler here. I have noticed multiple times that if there is too much going back and forth
# global dictionary gets emptied and programme is unable to continue. 
def score_generator(question_one, question_two, question_three):
    try:
        age = int(personal_data_dict["age"])
        answer_range = ["yes", "no"]    
        if question_one.casefold() in answer_range and question_two.casefold() in answer_range and question_three.casefold() in answer_range:
            score = 0
            if age >= 16 and age <= 21:
                if question_one == "yes":
                    score += 1
                if question_two == "yes":
                    score += 2
                if question_three == "no":
                    score += 1
                personal_data_dict["score"] = score
            elif age >= 22 and age <= 40:
                if question_one == "yes":
                    score += 2
                if question_two == "yes":
                    score += 2
                if question_three == "no":
                    score += 3
                personal_data_dict["score"] = score
            elif age >= 41 and age <= 64:
                if question_one == "yes":
                    score += 3
                if question_two == "yes":
                    score += 2
                if question_three == "no":
                    score += 2
                personal_data_dict["score"] = score
            elif age >= 65:
                if question_one == "yes":
                    score += 3
                if question_two == "yes":
                    score += 3
                if question_three == "no":
                    score += 1
                personal_data_dict["score"] = score
        else:
            return render_template("error.html", text="Answer has to be Yes/No")    
    except KeyError:
        return render_template("key_error.html") 
    return redirect(url_for("result"))


# PART THREE - generate result based on final score

@app.route("/result")
def result():
    score = personal_data_dict["score"]
    if score <= 3:
        text = "Thank you for answering our questions, we don't need to see you at this time. Keep up the good work!"
        return render_template('result.html', text=text)
    else:
        text = "We think there are some simple things you could do to improve your quality of life, please phone to book an appointment."
        return render_template('result.html', text=text) 
    
    
# COMMON WEB ERROR HANDLING
@app.errorhandler(500)
def error_handler():
    return render_template("key_error.html")

@app.errorhandler(404)
def error_handler():
    return render_template("key_error.html")

if __name__ == "__main__":
    app.run(debug=True)



