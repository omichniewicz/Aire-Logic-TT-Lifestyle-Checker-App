from flask import Flask, render_template, redirect, url_for
from flask import request
from datetime import date, timedelta
import requests
import json

app = Flask(__name__)

personal_data_dict = {}

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
    else:
        return api_validator(nhsnumber)
        
def api_validator(nhsnumber):
    api_key = 'INSERT SUBSCRIPTION KEY HERE'
   
    url = f'https://al-tech-test-apim.azure-api.net/tech-test/t2/patients/{nhsnumber}'
    headers = {'Ocp-Apim-Subscription-Key': '{key}'.format(key=api_key)}

    response = requests.get(url, headers=headers)
    personal_data_api = json.loads(response.content)
    if response.status_code == 404 or nhsnumber == 123456789:
        return render_template("error.html", text="Invalid NHS number")
    elif response.status_code == 200:
        user_name = (personal_data_api["name"]).split(',')
        user_surname_check = user_name[0] 
        if personal_data_dict["name"].casefold() != user_surname_check.casefold() or personal_data_dict["born"] != personal_data_api["born"]:
            return render_template("error.html", text="Your details could not be found")
        elif int(personal_data_dict["age"]) < 16:
            return render_template("error.html", text="You are not eligble for this service")
        else:
            return redirect(url_for("ask_questions"))

@app.route("/questions", methods = ['GET','POST'])
def ask_questions():
    question_one = request.form.get("question_one")
    question_two =  request.form.get("question_two")   
    question_three =  request.form.get("question_three")
    if request.method == 'POST':
        return score_generator(question_one, question_two, question_three)
    else:
        return render_template('questions.html')

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

@app.route("/result")
def result():
    score = personal_data_dict["score"]
    if score <= 3:
        text = "Thank you for answering our questions, we don't need to see you at this time. Keep up the good work!"
        return render_template('result.html', text=text)
    elif score > 3:
        text = "We think there are some simple things you could do to improve you quality of life, please phone to book an appointment."
        return render_template('result.html', text=text) 
    
@app.errorhandler(500)
def error_handler():
    return render_template("key_error.html")

@app.errorhandler(404)
def error_handler():
    return render_template("key_error.html")

if __name__ == "__main__":
    app.run(debug=True)



