from flask import Flask, render_template, redirect, url_for, session
from flask import request
from datetime import date, timedelta
import requests
import json
import os
from dotenv import load_dotenv

app = Flask(__name__)

def session_key_generator():
    key = os.urandom(12).hex()
    return key

app.secret_key = session_key_generator()

# PART ONE - collect and validate the data

# Index function is responsible for fetching data from the user. 
# Date validation is implemented in this function so the flow is interupted before it hits datetime function.
# try/except block prevents alpha characters from being processed
@app.route("/", methods = ['GET','POST'])
def index():
    if request.method == 'POST':
        session['nhsnumber'] = request.form.get("nhsnumber")
        session['name'] = request.form.get("name")
        session['day'] = request.form.get("day")
        session['month'] = request.form.get("month")
        session['year'] = request.form.get("year")   
        try:
            if int(session['month']) in [2] and int(session['day']) in range(1,29):
                return get_personal_data(session['nhsnumber'], session['name'], session['day'], session['month'], session['year'])
            elif int(session['month']) in [2] and int(session['day']) in range(1,30) and ((int(session['year']) % 4 == 0 and int(session['year']) % 100 != 0) or int(session['year']) % 400 == 0):
                return get_personal_data(session['nhsnumber'], session['name'], session['day'], session['month'], session['year'])
            elif int(session['month']) in [4,6,9,11] and int(session['day']) in range(1,31):
                return get_personal_data(session['nhsnumber'], session['name'], session['day'], session['month'], session['year'])
            elif int(session['month']) in [1,3,5,7,8,10,12] and int(session['day']) in range(1,32):
                return get_personal_data()
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
def get_personal_data():
    day = int(session['day'])
    month = int(session['month'])
    year = int(session['year'])
    user_dob = date(year,month,day)
    user_age = (date.today() - user_dob) // timedelta(days=365.2425)
    session['born'] = f'{"{:02d}".format(day)}-{"{:02d}".format(month)}-{year}'
    session['age'] = user_age
    if len(session['nhsnumber']) != 9:
        return render_template("error.html", text="Incorrect NHS Number")
    elif int(session['age']) < 16:
        return render_template("error.html", text="You are not eligble for this service")
    else:
        return api_validator()

# api_validator function uses nhsnumber to access API.
# once matched it splits name into first name and surname since only surname is required by app
# further processing checks if surname and dob are matching API        
def api_validator():
    nhsnumber = session['nhsnumber']
    load_dotenv()
    api_key = os.getenv('API_SUBSCRIPTION_KEY')
   
    url = f'https://al-tech-test-apim.azure-api.net/tech-test/t2/patients/{nhsnumber}'
    headers = {'Ocp-Apim-Subscription-Key': '{key}'.format(key=api_key)}

    response = requests.get(url, headers=headers)
    personal_data_api = json.loads(response.content)
    if response.status_code == 404 or nhsnumber == 123456789:
        return render_template("error.html", text="Your details could not be found")
    elif response.status_code == 200:
        user_name = (personal_data_api["name"]).split(',')
        user_surname_check = user_name[0] 
        if session["name"].casefold() != user_surname_check.casefold() or session["born"] != personal_data_api["born"]:
            return render_template("error.html", text="Your details could not be found")
        else:
            return redirect(url_for("ask_questions"))
    else: 
        return render_template("key_error.html")

# PART TWO - collect lifestyle answers and generate score

# ask_questions gatheres lifestyle answers from user. 
# Only yes/no answer is accepted due to Python's limitation to read from radio or dropdown type inputs.
@app.route("/questions", methods = ['GET','POST'])
def ask_questions():
    session['question_one'] = request.form.get("question_one")
    session['question_two'] =  request.form.get("question_two")   
    session['question_three'] =  request.form.get("question_three")
    if request.method == 'POST':
        return score_generator()
    else:
        return render_template('questions.html')

# Score_generator follows a simple counter logic and only works if the answer is in range. 
# There is an additional key_error handler here. I have noticed multiple times that if there is too much going back and forth
# data gets lost and programme is unable to continue. 
def score_generator():
    try:
        age = int(session["age"])
        answer_range = ["yes", "no"]    
        if session['question_one'].casefold() in answer_range and session['question_two'].casefold() in answer_range and session['question_three'].casefold() in answer_range:
            score = 0
            if age >= 16 and age <= 21:
                if session['question_one'] == "yes":
                    score += 1
                if session['question_two'] == "yes":
                    score += 2
                if session['question_three'] == "no":
                    score += 1
                session["score"] = score
            elif age >= 22 and age <= 40:
                if session['question_one'] == "yes":
                    score += 2
                if session['question_two'] == "yes":
                    score += 2
                if session['question_three'] == "no":
                    score += 3
                session["score"] = score
            elif age >= 41 and age <= 64:
                if session['question_one'] == "yes":
                    score += 3
                if session['question_two'] == "yes":
                    score += 2
                if session['question_three'] == "no":
                    score += 2
                session["score"] = score
            elif age >= 65:
                if session['question_one'] == "yes":
                    score += 3
                if session['question_two'] == "yes":
                    score += 3
                if session['question_three'] == "no":
                    score += 1
                session["score"] = score
        else:
            return render_template("error.html", text="Answer has to be Yes/No")    
    except KeyError:
        return render_template("key_error.html") 
    return redirect(url_for("result"))


# PART THREE - generate result based on final score

@app.route("/result")
def result():
    score = session["score"]
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



