from slackclient import SlackClient
import requests
import json
from flask import Flask, request, Response
import random
from rq import Connection, Queue, Worker
from redis import Redis
import sys
import re


def print_json(json_data):
    print(json.dumps(json_data,sort_keys=True, indent=4, separators=(',', ': ')))

file_list = list()
index = 0
order = 1


verif_token = 'XXXXXXXXXXXXX'
SLACK_TOKEN = 'xoxp-XXXXXXXXXXXXXXXXXXXXXX'

my_client = SlackClient(SLACK_TOKEN)

server = Flask(__name__)

def return_files():
  global file_list, count, index, current_channel, order
  index = 0
  order = 1
  request_pload = request.form
  token_received = request_pload['token']
  user_id = request_pload['user_id'] 
  response_url = request_pload['response_url']
  current_channel = request_pload["channel_id"]
  
  # checking this for security purposes
  if token_received == verif_token:
    print "*** the tokens match ***"
    URL = "https://slack.com//api/chat.postMessage"
    headers = {'Content-Type' : 'application/json;charset=utf-8',
          'Authorization' : 'Bearer xoxp-XXXXXXXXXXXXXX0'    }
    get_files= my_client.api_call(
                       'files.list',
                       )
    inner_data = get_files["files"] 
    for g in inner_data:
      if g["user"] == user_id:
        if g not in file_list:
            file_list.append(g) 
    count = len(file_list)        
    text = file_list[int(index)]["permalink"]
    #print_json(file_list[int(index)])
    json_data = {
        "text": text,
        "channel" : current_channel,
        "attachments": [
            {
                "text": "Would you like to delete this file?",
                "fallback": "You are unable to delete this file",
                "callback_id": "wopr_game",
                "color": "#ED0024",
                "attachment_type": "default",
                "actions": [
                    {
                        "name": "Prev",
                        "text": "Prev",
                        "type": "button",
                        "value": "Prev"
                    },
                    {
                        "name": "Next",
                        "text": "Next",
                        "type": "button",
                        "value": "Next"
                    },
                    {
                        "name": "Yes",
                        "text": "Yes",
                        "style": "danger",
                        "type": "button",
                        "value": "Yes",
                        "confirm": {
                            "title": "Are you sure?",
                            "text": "Are you sure?",
                            "ok_text": "Yes",
                            "dismiss_text": "No"
                        }
                    }
                ]
            },
                {
            "text": "FILE NO. " + str(order),
            "fallback": "You are unable to choose a game",
            "callback_id": "wopr_game",
            "color": "#AAB777",
            "attachment_type": "default"
        },
        {
            "text": "YOU HAVE " + str(count) + " FILES",
            "fallback": "You are unable to choose a game",
            "callback_id": "wopr_game",
            "color": "#FFF777",
            "attachment_type": "default"
        }
        ]
    }
    print count
    payload = requests.post(url=URL, headers=headers, json=json_data)
    return Response(), 200
  else:
    print "*** tokens did not match ***"
    return Response('auth did not work'), 200    

def response_to_invocation():
    global index, current_channel, count, order
    URL = "https://slack.com//api/chat.update"
    headers = {'Content-Type' : 'application/json;charset=utf-8',
          'Authorization' : 'Bearer xoxp-XXXXXXXXXXXXXXXXXXX'    }
    init_data = request.data 
    data = request.form.to_dict()
    inner_data = data["payload"] 
    inner_data = json.loads(inner_data)
    ts = inner_data['message_ts']
    #print_json(inner_data)
    text = file_list[int(index)]["permalink"]
    
    # to go forward one in the file list
    if inner_data["actions"][0]["value"] == 'Next':

        order = (order + 1) % int(count)
        index = (index + 1) % int(count)
        if order == 0:
            file_num = count
        else: file_num = order
        text = file_list[int(index)]["permalink"]
        #print_json(file_list[int(order)-1])
        print "order is " +  str(order)
        print "index is " + str(index)
        json_data = {
        "text": text,
        "ts" : ts,
        "channel" : current_channel,
        "attachments": [
            {
                "text": "Would you like to delete this file?",
                "fallback": "You are unable to delete this file",
                "callback_id": "wopr_game",
                "color": "#ED0024",
                "attachment_type": "default",
                "actions": [
                    {
                        "name": "Prev",
                        "text": "Prev",
                        "type": "button",
                        "value": "Prev"
                    },
                    {
                        "name": "Next",
                        "text": "Next",
                        "type": "button",
                        "value": "Next"
                    },
                    {
                        "name": "Yes",
                        "text": "Yes",
                        "style": "danger",
                        "type": "button",
                        "value": "Yes",
                        "confirm": {
                            "title": "Are you sure?",
                            "text": "Are you sure?",
                            "ok_text": "Yes",
                            "dismiss_text": "No"
                        }
                    }
                ]
            },
                {
            "text": "FILE NO. " + str(file_num),
            "fallback": "You are unable to choose a game",
            "callback_id": "wopr_game",
            "color": "#AAB777",
            "attachment_type": "default"
        },
        {
            "text": "YOU HAVE " + str(count) + " FILES",
            "fallback": "You are unable to choose a game",
            "callback_id": "wopr_game",
            "color": "#FFF777",
            "attachment_type": "default"
        }
        ]
    }
        payload = requests.post(url=URL, headers=headers, json=json_data)

    ##### CHECK IF THERE"S A WAY TO OPEN FILE IN SIDEBAR WITHIN API METHODS ######    

    ###Maybe files.info

    # to go back one in the file list
    elif inner_data["actions"][0]["value"] == 'Prev':
        print "yeehah"
        order = (order - 1) % int(count)
        index = (index - 1) % int(count)
        if order == 0:
            file_num = count
        else: file_num = order
        text = file_list[int(index)]["permalink"]
        #print_json(file_list[int(order)-1])
        #print "order is " +  str(order)
        #print "index is " + str(index)
        json_data = {
        "text": text,
        "ts" : ts,
        "channel" : current_channel,
        "attachments": [
            {
                "text": "Would you like to delete this file?",
                "fallback": "You are unable to delete this file",
                "callback_id": "wopr_game",
                "color": "#ED0024",
                "attachment_type": "default",
                "actions": [
                    {
                        "name": "Prev",
                        "text": "Prev",
                        "type": "button",
                        "value": "Prev"
                    },
                    {
                        "name": "Next",
                        "text": "Next",
                        "type": "button",
                        "value": "Next"
                    },
                    {
                        "name": "Yes",
                        "text": "Yes",
                        "style": "danger",
                        "type": "button",
                        "value": "Yes",
                        "confirm": {
                            "title": "Are you sure?",
                            "text": "Are you sure?",
                            "ok_text": "Yes",
                            "dismiss_text": "No"
                        }
                    }
                ]
            },
                {
            "text": "FILE NO. " + str(file_num),
            "fallback": "You are unable to choose a game",
            "callback_id": "wopr_game",
            "color": "#AAB777",
            "attachment_type": "default"
        },
        {
            "text": "YOU HAVE " + str(count) + " FILES",
            "fallback": "You are unable to choose a game",
            "callback_id": "wopr_game",
            "color": "#FFF777",
            "attachment_type": "default"
        }
        ]
    }
        payload = requests.post(url=URL, headers=headers, json=json_data)

    # to delete the file 
    elif inner_data["actions"][0]["value"] == 'Yes':
        file = inner_data["original_message"]["text"]
        file = re.findall('/(F.+)/', file)
        file = file[0]
        file = str(file)
        for x in file_list:
            if file == x["id"]:
                #print_json(x["permalink"])
                file_list.remove(x)

        URL_delete = 'https://www.slack.com/api/files.delete'
        headers = {'Content-Type' : 'application/json;charset=utf-8',
               'Authorization' : 'Bearer xoxp-XXXXXXXXXXXX'
    }
        json_data_delete = {
                     "file" : file   
        }
        print "order is " +  str(order)
        print "index is " + str(index)

        text = file_list[int(index)]["permalink"]
        count = len(file_list)
        print "Count is " + str(count)
        json_data = {
        "text": text,
        "ts" : ts,
        "channel" : current_channel,
        "attachments": [
            {
                "text": "Would you like to delete this file?",
                "fallback": "You are unable to delete this file",
                "callback_id": "wopr_game",
                "color": "#ED0024",
                "attachment_type": "default",
                "actions": [
                    {
                        "name": "Prev",
                        "text": "Prev",
                        "type": "button",
                        "value": "Prev"
                    },
                    {
                        "name": "Next",
                        "text": "Next",
                        "type": "button",
                        "value": "Next"
                    },
                    {
                        "name": "Yes",
                        "text": "Yes",
                        "style": "danger",
                        "type": "button",
                        "value": "Yes",
                        "confirm": {
                            "title": "Are you sure?",
                            "text": "Are you sure?",
                            "ok_text": "Yes",
                            "dismiss_text": "No"
                        }
                    }
                ]
            },
                  {
            "text": "*FILE TERMINATED!!!*",
            "fallback": "You are unable to choose a game",
            "callback_id": "wopr_game",
            "color": "#FFFFFF",
            "attachment_type": "default"
        },
                {
            "text": "FILE NO. " + str(order),
            "fallback": "You are unable to choose a game",
            "callback_id": "wopr_game",
            "color": "#AAB777",
            "attachment_type": "default"
        },
        {
            "text": "YOU HAVE " + str(count) + " FILES",
            "fallback": "You are unable to choose a game",
            "callback_id": "wopr_game",
            "color": "#FFF777",
            "attachment_type": "default"
        }
        ]
    }
        deleteFile = requests.post(url=URL_delete, headers=headers, json=json_data_delete)  
        payload = requests.post(url=URL, headers=headers, json=json_data)
        print "order is " +  str(order)
        print "index is " + str(index)
        print "count is " + str(count)
        URL2 = 'https://www.slack.com/api/chat.postEphemeral'
        json_data2 = {
                    'text' : 'FILE DELETION AFFIRMATIVE',
                    'channel' : current_channel,
                    'as_user' : 'true'


        }
        #payload2 = requests.post(url=URL2, headers=headers, json=json_data2)
    else: print inner_data["actions"][0]["value"] 

        ##### send ephemeral message that file has been deleted ######

