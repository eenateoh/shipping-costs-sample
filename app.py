#!/usr/bin/env python

import urllib
import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


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
            "contextOut": ["purchasing"],
            "source": "apiai-maxisstore-postpaiddetails"
        }
        
        
    if req.get("result").get("action") == "shipping.cost":
        result = req.get("result")
        parameters = result.get("parameters")
        zone = parameters.get("shipping-zone")

        cost = {'Europe':100, 'North America':200, 'South America':300, 'Asia':400, 'Africa':500}

        speech = "The cost of shipping to " + zone + " is " + str(cost[zone]) + " euros."

        print("Response:")
        print(speech)

        return {
            "speech": speech,
            "displayText": speech,
            #"data": {},
            # "contextOut": [],
            "source": "apiai-onlinestore-shipping"
        }
    
    return {}


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=True, port=port, host='0.0.0.0')

