from slackclient import SlackClient
import requests
import json
from flask import Flask, request, Response
import random
from rq import Connection, Queue, Worker
from redis import Redis
import sys
from methods_delete_bot import return_files, response_to_invocation

file_list = list()
count = 0

# The security token is used to verify that the request comes from Slack
verif_token = 'WUIdVlRRxvlg5r6NFhj19i5e'
SLACK_TOKEN = 'xoxp-203970479943-203138037490-292397923959-4a45f022f9a9242002c12221985a9a90'

my_client = SlackClient(SLACK_TOKEN)

server = Flask(__name__)

def print_json(json_data):
    print(json.dumps(json_data,sort_keys=True, indent=4, separators=(',', ': ')))
	
# Here we are using a decorator (@server.route) to tell the server:
# where it will receive data: ('/test')
# the kind of http request it will receive: (methods=['GET'])
# what to do: run the local_test function that we are defining

@server.route ('/test', methods=['GET'])
def local_test():
  return Response("Status 200")

# button handler
@server.route ('/interactive_button', methods=['POST'])

def run_jobs():
  # Enqueueing jobs
  # redis_conn = Redis()
  # q1 = Queue('high', connection=redis_conn)
  # q2 = Queue('medium', connection=redis_conn)

  # # Delay execution of job
  # job1 = q1.enqueue(confirmado)
  # job2 = q2.enqueue(response_to_invocation)
  # print job1, job2
  response_to_invocation() 
  return Response(), 200 

@server.route ('/getallfiles', methods=['POST'])

def run_first_job():  
  # Enqueueing jobs
  # redis_conn = Redis()
  # q1 = Queue('high', connection=redis_conn)
  # q2 = Queue('medium', connection=redis_conn)

  # # Delay execution of job
  # job1 = q1.enqueue(confirmado)
  # job2 = q2.enqueue(return_files)

  # print job1, job2      
  return_files()
  return Response(), 200 

# if __name__== "__main__": is used in python to make sure that the code
# inside it is only ran when the module is executed and not when imported
# Not very useful here, but you will often see this as it is quite standard
if __name__== "__main__":
	# calling server's built in "run" function, which will actually launch
	# our server. Adding the debug parameter as this will expose more data
	# for debugging
	server.run(debug=True)