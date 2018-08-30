# vacabot

What is Vacabot?
It’s a web chatbot for our vacation, so employee can request time off, and make it easy to see their time off :-)

Dialogflow Steps:
-----------------
Steps to upload the agent:
- Create a new account in dialogflow.com
- Create a new agent
- From agent' setting, go to Import and Export, then upload the zip file
- Go to https://console.cloud.google.com/
- Select your project from the menu
- Copy and paste the project id to DIALOGFLOW_PROJECT_ID variable in .env file
- From API services in the main menu, select credentials, then create credentials and choose service account key 

Dependencies:
-------------
- We use Python v3.6
- pip3.6 install -r requirements.txt


![chatbot](https://user-images.githubusercontent.com/37369603/44788355-1aef3e00-ab9a-11e8-958f-a7dcc49086bf.png)
