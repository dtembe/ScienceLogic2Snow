from silo_common.database import local_db
from datetime import datetime
from collections import namedtuple
from silo_utils import silo_api, APIError
import requests, json
from requests.auth import HTTPBasicAuth

'''
This script is to be run as an automation snippet inside of ScienceLogic EM7
it is used as a part of a run book automation to post an event from SL to ServiceNow 
Event Management. 
Inspiration from SL users slack channels & existing EM7 automations - slam-ug.slack.com
email - dtembe@yahoo.com
Date of script creation - 2019/01/13

Recommendations - 

'''

#EM7 results is a holder for a response from this snippet.
#not necessary if we are using a  logger (?) but this is something to implement in the future.

EM7_RESULT={}
EM7_RESULT['log']=[]
EM7_RESULT['outsnow']= []
outsnow=True

#Vars Used to Post Data to ServiceNow -
snowemurl = "https://<serviceNowInstance.service-now.com/api/now/table/em_event"
snowemuser = "SnowEmApiUser"
snowempassword = "SnowEmPassword"

# Logger var declared for logging snow events action

logger = em7_snippets.logger(filename='/tmp/sl2snow.log')
logger.debug('Start setting severity')

logger.debug("Starting sl2snow - %s" % EM7_VALUES['%N'])
logger.debug("Event Vales  - %s" % EM7_VALUES)
try:
    # for last_result in EM7_LAST_RESULT_LIST:
    #     if 'outsnow' in last_result.result.keys():
    #         outsnow=True
    #below is the JSON array to post to ServiceNow em_event table
    o_source = "ScienceLogic-API"
    o_node = EM7_VALUES['%X']
    o_metric_name = EM7_VALUES['%Y']
    o_type = EM7_VALUES['%x']
    o_resource = EM7_VALUES['%O']
    o_severity = '3'
    o_description = EM7_VALUES['%M']
    o_event_class = EM7_VALUES['%7']
    o_additional_info = EM7_VALUES
    # print ("-" * 50)
    # print (o_source, o_node, o_metric_name, o_type, o_resource, o_severity, o_description, o_event_class, o_additional_info)
    # print ("-" * 50)
    #data is the JSON array containing a single event values.
    data = {"source": o_source, "node": o_node, "metric_name": o_metric_name, "type": o_type,
            "resource": o_resource, "severity": o_severity, "event_class": o_event_class, "description": o_description,
            "additional_info": o_additional_info}
    data = json.dumps(data)
    #print data values to log file.
    logger.debug(data)

    try:
        #std code from RBA snippets for email post or other actions. Keeping w/o changes.
        api_instance = silo_api(EM7_ACTION_CRED)
        if not api_instance:
            raise APIError
            logger.debug(APIError)
        try:
            api_res = api_instance.get('api/device/{}'.format(EM7_VALUES['%x']))
            api_res = api_instance.get( (api_res.json())['organization'] )
            #mailbcc= (api_res.json())['email']
        except Exception as e:
            logger.debug((5, 'Error "{}" while processing last_result_list'.format(e)))
            pass

        if 'windowsservice'in last_result.result.keys():
            servicename=last_result.result['windowsservice']['name']
            servicestatus=last_result.result['windowsservice']['status']
    except Exception as e:
    #EM7_RESULT['log'].append((5,'Error "{}" while processing last_result_list'.format(e)))
        logger.debug((5,'Error "{}" while processing last_result_list'.format(e)))
        pass
#POST to JSON using BASIC Auth and requests.
    url = snowemurl
    auth = HTTPBasicAuth(snowemuser, snowempassword)
    head = {'Content-type': 'application/json',
            'Accept': 'application/json'}
    payld = data
    ret = requests.post(url, auth=auth, data=payld, headers=head)
    # sys.stdout.write(ret.text)
    ret.close()
#Capture return code and log to logger the output.
    if ret.status_code != 200:
        logger.debug("HTTP status code from API request: %s" % (ret.status_code,))
    else:
        logger.debug("Message Posted to ServiceNOW successfully. request: %s" % (ret.status_code,))
#closing the 1st try block with necessary expect.
except APIError as e:
    EM7_RESULT = e
    
