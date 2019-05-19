# This is a simple script to run scans using burp rest api and burp
# suite together.

import requests
import time
import datetime
import urllib


# Inputs to this script
# scope - Scope for burp scan. 

application_baseurl = "http://localhost:3100"
scope = application_baseurl
scanComplete = False
scanComplete50 = False
scanComplete75 = False
swagger_baseUrl = "http://localhost:8090"

'''
        curl -X GET "http://localhost:8090/burp/versions" -H  "accept: */*"
        Expected ResponseStatus: 200
        Response body example:
        {
          "burpVersion": "Burp Suite Professional.1.7.37",
          "extensionVersion": "2.0.1"
        }
'''
def healthCheckBurp():

    r = requests.get('http://localhost:8090/burp/versions',
                     headers={'accept': '*/*'})
    data = r.json()
    # print(r.status_code)
    if(r.status_code != 200):
        print("Something is wrong.. Healthcheck returned non 200 response.")
        print(str(r.status_code) + " " + str(data))
    else:
        print("healthcheckBurp: Using :" + str(data))
    pass

def add_burp_scope():
    '''
        # curl -X PUT "http://localhost:8090/burp/target/scope?
        # url=http%3A%2F%2Fcrackme.cenzic.com" -H  "accept: */*"
        Expected ResponseStatus: 200
        Response body example:
         content-length: 0
         date: Tue, 18 Dec 2018 18:51:36 GMT
         server: Jetty(9.2.14.v20151106)
    '''
    p = {"url": scope}
    u = urllib.parse.urlencode(p)
    r = requests.put('http://localhost:8090/burp/target/scope?' + u,
                     headers={'accept': '*/*'})

    if(r.status_code != 200):
        data = r.json()
        print("add_burp_scope: Something went wrong..")
        print("status:" + str(r.status_code) + "response:  " + str(data))
    else:
        print("add_burp_scope: Added in scope: " + scope)
    pass


def checkScanStatus():
    global scanComplete75
    r = requests.get('http://localhost:8090/burp/scanner/status',
                     headers={'accept': '*/*'})

    if r.status_code != 200:
        data = r.json()
        print("checkScanStatus: Issue with response " + str(data))
        return True
    else:
        data = r.json()
        print("scanPercentage: " + str(data["scanPercentage"]))
        if data["scanPercentage"] == 100:
            print("Scan Complete.. ")
            return True
        else:
            if scanComplete75 == False:
                if data["scanPercentage"] >= 75:
                    scanComplete75 = True
                    getResults()
            print("Will check back in 5 seconds.. ")
            return False


def getResults():
    global scanComplete
    p = {"urlPrefix": scope,
         "reportType": "HTML"}
    u = urllib.parse.urlencode(p)

    '''
        # curl -X GET "http://localhost:8090/burp/report?
                        reportType=HTML&urlPrefix=<url>" -H  "accept: */*"
    '''
    r = requests.get('http://localhost:8090/burp/report?' + u,
                     headers={'accept': '*/*'})

    if(r.status_code != 200):
        data = r.json()
        print("getResults: Something went wrong..")
        print("status:" + str(r.status_code) + "response:  " + str(data))
        return
    else:
        data = r.text
        filename = "BurpApplicationScanReport.html" 
        f = open(filename, "w")
        f.write(data)
        f.close()
        print("Scan Report saved as: " + filename)
    pass


def triggerQATests():
    # run QA automation tests
    pass


def scheduleScan():
    p = {"baseUrl": scope}
    u = urllib.parse.urlencode(p)

    # Schedule active scan
    r = requests.post('http://localhost:8090/burp/scanner/scans/active?' + u,
                      headers={'accept': '*/*'})

    if(r.status_code != 200):
        data = r.json()
        print("schedule_active_scan: Something went wrong..")
        print("status:" + str(r.status_code) + "response:  " + str(data))
        return
    else:
        print("schedule_active_scan: Active Scan scheduled for baseurl: " + scope)

    # Schedule passive scan
    r1 = requests.post('http://localhost:8090/burp/scanner/scans/passive?' + u,
                       headers={'accept': '*/*'})
    if(r1.status_code != 200):
        data1 = r1.json()
        print("schedule_passive_scan: Something went wrong..")
        print("status:" + str(r1.status_code) + "response:  " + str(data1))
        return
    else:
        print("schedule_passive_scan: Passive Scan scheduled for baseurl: " + scope)
    pass



healthCheckBurp()
#add_burp_scope()
#scheduleScan()

# wait until scan 100% finished
print("Waiting for scanning queue update")
time.sleep(30)
print("Will check the scan status in a minute")
time.sleep(30)


while scanComplete == False:
    if checkScanStatus():
        #print("Scan complete.")
        scanComplete = True
    else:
        time.sleep(5)


if(scanComplete == True):
    getResults()

