
<br />
<div align="center">
  
  <h1 align="center" style="font-size: 10px;">Lifestyle Checker App</h1>

  </a>

  <h3 align="center">Olga Michniewicz</h3>

  <p align="center">
    Simple Web Application to assess your health based on your lifestyle choices.
    <br />
    <br />
    <a href="https://lifestyle-checker-app.nw.r.appspot.com/" target="_blank"><b>Launch App</b></a>
  
  </p>
</div>



<br>
<br>

## Project Background

<br>
A local health authority wants to provide lifestyle choice information to its registered patients. This information will be displayed to relevant patients based on their current lifestyle choices. To do this the local authority would like to build a simple web application that patients can use.
<br>

## Workflow

<br>
App works in three steps:
<br>
<br>
1. Ask the user to enter their NHS Number and details, the system will then call an API to identify the patient.
<br><br>
Part one of the project is based on three functions. First is responsible for display and collecting data from the user. 
Additionally it validates date input before moving to another step. Step two is normalising given data before further processing. It transforms date input to match API format and generates age value. If patient is below 16 years old programme stops at this point as they are not eligible for this service. NHS number length is set at 9 (which is not the actual format but has been set) to avoid unnecessary API calls. Third function calls API and validates NHS number first. If found it checks name and DOB. If there is a match it will let user continue to part two otherwise it will throw an error.
<br><br>
2. The application will ask the user a number of simple questions about their current lifestyle choices, the answers to these along with their age will be used to generate a risk score. 
<br><br>
Part two consists of two functions. First is responsible for display and collecting data from the user. Second validates user input and generates score. The only acceptable answers are "yes" and "no". Any other input will result in error. With valid input it will calculate final score based on "age" value stored in session and answers passed from ask_question function. Final score will be stored in the session dictionary as well.
<br><br>
3. Based on their score user will be shown applicable result.
<br><br>
In third part a single function will get "score" value from the global dictionary. If "score" value is lower than or equal 3 it will display positive result. Otherwise the result will be negative. 


## Building process
<br>
I started by creating CLI Python app to cover input/output related requirements of the project. Based on my research I decided to use Flask and Google Cloud to transform my script into Web Application. I had to apply Flask logic to my code and initiate app engine in Google cloud. While logic was still flawed I was able to deploy simple version of my app. I had a lot of issues implementing correct routing. I have never worked with Flask before this task and it took me some time to understand how to create proper conections between the functions. In the meantime I started using very basic HTML templates with render_template function and this actually really helped me. Ultimately I was able to create the routing I wanted and the app was performing as expected. I repurposed some of my old Web Design projects to create user friendly interface. I also used HTML functionality to avoid some input mistakes. 
<br>
<br>
Last task was testing and error handling. I tried to cover all possible scenarios. There is one case not covered in the log: 404 and 500 errors are covered the same way as Key Error as I find the message suitable for either scenario. 
<br>You can find the documentation here:
<br><br>
<a href="https://docs.google.com/spreadsheets/d/1X3Q0gJnxrXzVPL-RR7yzc0Kyv0dxKXczAfBF_z0nGnM/edit?usp=sharing" target="_blank"><b>Testing Log</b></a>
<br>
<br>

## Important features
<br>
- each session gets its inidivual key
- API Subscription Key is stored in .env file
- CSS allows readability on all types of devices

## Further developments

<br>
Part Three
<br>
Implementing additional functionality so the scoring system can be altered without redeploying the code. 
<br>
My idea for this implemenation is to create API to store score values. Each record will contain "min_age", "max_age" and "scores" keys. "Scores" key will contain "question_one", "question_two" and "question_three" values. 
Values from each API will be called in score_generator function.
Admin path will be added. Accessible only via URL, not from the user interface. Login will be required. 
Admin should be able to choose between updating age groups and scores.
Age groups will have to be updated all at once. Input validation function will be implemented to avoid gaps.
For score section user can be given option to choose specific age group.
<br>

## Setup
<br>

1. Clone repo
2. Add .env file containing Api Subscription Key ```API_SUBSCRIPTION_KEY='{INSERT TOKEN HERE}'```
3. Create project in <a href='https://console.cloud.google.com/'>Google Cloud</a>
4. Initialise app engine
5. Download <a href='https://cloud.google.com/sdk/?_ga=2.86659729.-809347455.1679625444&_gac=1.215527653.1679837133.Cj0KCQjw2v-gBhC1ARIsAOQdKY1GnplYqaD31ap2GmFrIc-xOpbGja4cd170rNHZNU79BeNFS5vRl_8aAgFOEALw_wcB'>Google Cloud SDK</a>
6. In terminal move to app directory, type ```gcloud init``` and follow instructions
7. Deploy app with ```gcloud app deploy```

## Credits
Olga Michniewicz
<br>
<a href="mailto:michniewicz.olga@gmail.com" target="_blank">michniewicz.olga@gmail.com</a>
<br>
<a href="https://github.com/omichniewicz" target="_blank">GitHUB</a>


