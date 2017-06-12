#!/usr/bin/env python

import urllib
import json
import os
import psycopg2

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

_connect_str = "dbname='customer' user='eena' port='5432'"+\
    "host='chatbotdbinstance.c6gisnki06mz.us-east-2.rds.amazonaws.com' " + \
                  "password='eenaeena'"

@app.route('/customers', methods=['GET'])
def customers():
    try:
        conn = psycopg2.connect(_connect_str)
        cursor = conn.cursor()
        cursor.execute("""select * from call_customer""")
        rows = cursor.fetchall()
        r = make_response(rows)
    except Exception as e:
        r = make_response("Error connecting to database")
        print("Uh oh, can't connect. Invalid dbname, user or password?")
        print(e)
    finally:
    if conn is not None:
        conn.close()
        
    r.headers['Content-Type'] = 'application/json'
    return r

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = makeWebhookResult(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeWebhookResult(req):
    if req.get("result").get("action") == "postpaid.details":
        result = req.get("result")
        parameters = result.get("parameters")
        plan_chosen = parameters.get("PostpaidPlan")
        
        cost = {'MaxisOne plan 188':188, 'MaxisOne plan 158':158, 'MaxisOne plan 128':128, 'MaxisOne plan 98':98}
        data = {'MaxisOne plan 188':50, 'MaxisOne plan 158':40, 'MaxisOne plan 128':30, 'MaxisOne plan 98':20}
        shareline = {'MaxisOne plan 188':4, 'MaxisOne plan 158':3, 'MaxisOne plan 128':1, 'MaxisOne plan 98':1}
        
        speech = "This plan is only RM" + str(cost[plan_chosen]) + "/month. " + \
        "It comes with " + str(data[plan_chosen]) + "GB data and " + \
        "Unlimited calls & SMS to all network." + \
        "You can also get up to " + str(shareline[plan_chosen]) + " MaxisONE Share Line at RM 48/mth per line. " + \
        "Would you like to subscribe to this plan?"
        
        print("Response")
        print(speech)
        
        return {
            "speech": speech,
            "displayText": speech,
            #"data": {},
            "contextOut": [{"name":"purchasing","lifespan":5,"parameters":{"PostpaidPlan":plan_chosen}}],
            "source": "apiai-maxisstore-postpaiddetails"
        }
        
        
    if req.get("result").get("action") == "call-customer-info":
        result = req.get("result")
        parameters = result.get("parameters")
        customer_name = parameters.get("customer-name")
        customer_nric = parameters.get("customer-nric")
        customer_mobile = parameters.get("customer-mobile")
        customer_email = parameters.get("customer-email")
        plan_chosen = parameters.get("customer-plan")

        speech = "You've entered details as follows.. "
        speech2 = "Name\t: " + customer_name
        speech3 = "Id No\t: " + customer_nric 
        speech4 = "Mobile No\t: " + customer_mobile
        speech5 = "Email\t: " + customer_email
        speech6 = "Plan\t: " + plan_chosen
        speech7 = "Would you like to submit?" 

        print("Response:")
        print(speech)

        return {
            "speech": speech,
            #"displayText": speech,
            "messages": [
                {"type":0, "speech":speech},
                {"type":0, "speech":speech2},
                {"type":0,"speech":speech3},
                {"type":0,"speech":speech4},
                {"type":0,"speech":speech5},
                {"type":0,"speech":speech6},
                {"type":0,"speech":speech7}
            ],
            #"data": {},
            "contextOut": [{"name":"purchasing-call-submission","lifespan":5,
                            "parameters":parameters}],
            "source": "apiai-maxisstore-postpaiddetails"
        }
    
    if req.get("result").get("action") == "call-customer":
        result = req.get("result")
        parameters = result.get("parameters")
        
        #insert to postgres far, at aws
        _insert_customer_to_postgres(parameters)
        
        speech = "We will contact you shortly."
        return {
            "speech": speech,
            "displayText": speech,
            #"data": {},
            "contextOut": [{"name":"purchasing","lifespan":0},{"name":"purchasing-call-submission","lifespan":0}],
            "source": "apiai-maxisstore-postpaiddetails"
        }
        
    return {}

def _insert_customer_to_postgres(parameters):
    customer_name = parameters.get("customer-name")
    customer_nric = parameters.get("customer-nric")
    customer_mobile = parameters.get("customer-mobile")
    customer_email = parameters.get("customer-email")
    plan_chosen = parameters.get("customer-plan")
    sql = """INSERT INTO call_customer values ('{}','{}','{}','{}','{}')""".format(customer_name, customer_mobile, customer_email, plan_chosen, customer_nric)

    try:
        conn = psycopg2.connect(_connect_str)
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        cursor.close()
    except Exception as e:
        print("Uh oh, can't connect. Invalid dbname, user or password?")
        print(e)
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=True, port=port, host='0.0.0.0')


