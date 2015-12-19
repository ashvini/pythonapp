import ConfigParser
from ConfigParser import SafeConfigParser
import httplib2
import json
import yaml #used for str to dict conversion
import random
import flowbodycreater
#import ast {for str to dict converion not supported after python 2.6v}
import time
import sys

###function for reading values from ini file ######
def read_from_file(file_path,section,param):
    parser = SafeConfigParser(allow_no_value=True)
    parser.read(file_path)
    value = parser.get(section, param)
    return value


def rest_call(url,method,requestBody=None):
    ''' Rest call '''
    odl_username = read_from_file('odl.ini','user','odl_username')
    odl_password = read_from_file('odl.ini','pass','odl_password')
    h = httplib2.Http(".cache")
    h.add_credentials(odl_username,odl_password)

    print "METHOD: ",method," ","URL: "," ",url
    try:
        if requestBody==None:
            resp, content = h.request( uri = url,method = method)
        else:
            resp, content = h.request( uri = url,method = method,headers={'Content-Type' : 'application/json'},  body=json.dumps(requestBody))
    except Exception , err :
        print "error"
    if resp.status in [200,201,203,204]:
        print "Rest call successfully"
        if method=="GET":
            content = json.loads(content)
            return resp,content
        return resp
    else:
        print "error"
        #elog.error(response.text)
        return resp


