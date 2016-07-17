'''
Modular Input Script

Copyright (C) 2012 Splunk, Inc.
All Rights Reserved

'''

import sys,logging,os,time,re,threading
import xml.dom.minidom
from datetime import datetime

SPLUNK_HOME = os.environ.get("SPLUNK_HOME")

SPLUNK_PORT = 8089
STANZA = None
SESSION_TOKEN = None

#dynamically load in any eggs in /etc/apps/cloudflare/bin
EGG_DIR = SPLUNK_HOME + "/etc/apps/cloudflare/bin/"

for filename in os.listdir(EGG_DIR):
    if filename.endswith(".egg"):
        sys.path.append(EGG_DIR + filename) 
       
import requests, json
from splunklib.client import connect
from splunklib.client import Service
           
#set up logging
logging.root
logging.root.setLevel(logging.ERROR)
formatter = logging.Formatter('%(levelname)s %(message)s')
#with zero args , should go to STD ERR
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logging.root.addHandler(handler)

SCHEME = """<scheme>
    <title>CloudFlare Log Share</title>
    <description>CloudFlare Log Share input</description>
    <use_external_validation>true</use_external_validation>
    <streaming_mode>simple</streaming_mode>
    <use_single_instance>false</use_single_instance>

    <endpoint>
        <args>    
            <arg name="name">
                <title>Name</title>
                <description>Name of this CloudFlare input</description>
            </arg>
            <arg name="zone_name">
                <title>Domain Name</title>
                <description>CloudFlare domain to download logs for.</description>
                <required_on_edit>false</required_on_edit>
                <required_on_create>true</required_on_create>
            </arg>
            <arg name="auth_email">
                <title>CloudFlare email</title>
                <description>CloudFlare email address</description>
                <required_on_edit>false</required_on_edit>
                <required_on_create>true</required_on_create>
            </arg>
            <arg name="auth_key">
                <title>API Key</title>
                <description>CloudFlare API key</description>
                <required_on_edit>false</required_on_edit>
                <required_on_create>true</required_on_create>
            </arg>
            <arg name="last_ray_id">
                <title>Last ray id</title>
                <description>The last ray id downloaded. Set to 0 to start over, otherwise handled internally.</description>
                <required_on_edit>false</required_on_edit>
                <required_on_create>false</required_on_create>
            </arg>
            <arg name="request_timeout">
                <title>Request Timeout</title>
                <description>Request Timeout in seconds</description>
                <required_on_edit>false</required_on_edit>
                <required_on_create>false</required_on_create>
            </arg>
            <arg name="backoff_time">
                <title>Backoff Time</title>
                <description>Time in seconds to wait for retry after error or timeout</description>
                <required_on_edit>false</required_on_edit>
                <required_on_create>false</required_on_create>
            </arg>
            <arg name="polling_interval">
                <title>Polling Interval</title>
                <description>Interval time in seconds to poll the endpoint</description>
                <required_on_edit>false</required_on_edit>
                <required_on_create>false</required_on_create>
            </arg>
        </args>
    </endpoint>
</scheme>
"""


class CloudFlareEventHandler:
    def __init__(self,**args):
        pass

    def __call__(self, response_object, raw_response_output, req_args, last_ray_id):
        req = json.loads(raw_response_output)
        last_rayid = 0

        if "rayId" not in req:
            return


        rayid = req['rayId']
        if rayid == last_ray_id:
            return

        print json.dumps(req)

        if not "params" in req_args:
	    req_args["params"] = {}

        req_args["params"]["start_id"] = rayid

def get_current_datetime_for_cron():
    current_dt = datetime.now()
    #dont need seconds/micros for cron
    current_dt = current_dt.replace(second=0, microsecond=0)
    return current_dt
            
def do_validate():
    config = get_validation_config() 
    
def do_run(config):
    server_uri = config.get("server_uri")
    global SPLUNK_PORT
    global STANZA
    global SESSION_TOKEN 
    global delimiter
    SPLUNK_PORT = server_uri[18:]
    STANZA = config.get("name")
    SESSION_TOKEN = config.get("session_key")
   
    zone_name = config.get("zone_name")
    auth_email = config.get("auth_email")
    auth_key = config.get("auth_key")
    last_ray_id = config.get("last_ray_id", 0)
 
    request_timeout = int(config.get("request_timeout", 30))
    
    backoff_time = int(config.get("backoff_time", 10))
    
    polling_interval = int(config.get("polling_interval", 60))
    
    cloudflare_handler = CloudFlareEventHandler()

    headers = {
        "x-auth-email": auth_email,
        "x-auth-key": auth_key,
    }

    zone_tag = None
    r = requests.get("https://api.cloudflare.com/client/v4/zones", params={'name': zone_name}, headers=headers).json()
    for result in r['result']:
        zone_tag = result['id']

    if not zone_tag:
        pass

    try: 
        req_args = {
            "verify": True,
            "stream": True,
            "timeout": float(request_timeout),
            "headers": headers
        }

        while True:
            if last_ray_id:
                req_args['params'] = { 'start_id': last_ray_id }
            else:
                req_args['params'] = { 'start': 0 }

            try:
                r = requests.get("https://api.cloudflare.com/client/v4/zones/%s/logs/requests" % zone_tag, **req_args)
            except requests.exceptions.Timeout,e:
                logging.error("HTTP Request Timeout error: %s" % str(e))
                time.sleep(float(backoff_time))
                continue
            except Exception as e:
                logging.error("Exception performing request: %s" % str(e))
                time.sleep(float(backoff_time))
                continue

            try:
                r.raise_for_status()
                for line in r.iter_lines():
                    if not line:
                        continue

                    cloudflare_handler(r, line, req_args, last_ray_id)
                    sys.stdout.flush()

                update_rayid(req_args, last_ray_id)
            except requests.exceptions.HTTPError,e:
                error_output = r.text
                error_http_code = r.status_code
                print json.dumps({'http_error_code': error_http_code, 'error_message': error_output})
                sys.stdout.flush()
                logging.error("HTTP Request error: %s" % str(e))
                time.sleep(float(backoff_time))
                continue
              
            time.sleep(float(polling_interval))
    except RuntimeError,e:
        logging.error("Looks like an error: %s" % str(e))
        sys.exit(2) 
         
def update_rayid(req_args, ray_id):
    if 'start_id' not in req_args['params'] or req_args['params']['start_id'] == ray_id:
        return

    try:
        service = Service(host='localhost', port=SPLUNK_PORT, token=SESSION_TOKEN)
        item = service.inputs.__getitem__(STANZA[13:])
        item.update(last_ray_id=req_args['params']['start_id'])
    except RuntimeError,e:
        logging.error("Looks like an error updating the modular input parameter last_ray_id: %s" % (rest_name,str(e),))   
        
def usage():
    print "usage: %s [--scheme|--validate-arguments]"
    logging.error("Incorrect Program Usage")
    sys.exit(2)

def do_scheme():
    print SCHEME

#read XML configuration passed from splunkd, need to refactor to support single instance mode
def get_input_config():
    config = {}

    try:
        # read everything from stdin
        config_str = sys.stdin.read()

        # parse the config XML
        doc = xml.dom.minidom.parseString(config_str)
        root = doc.documentElement
        
        session_key_node = root.getElementsByTagName("session_key")[0]
        if session_key_node and session_key_node.firstChild and session_key_node.firstChild.nodeType == session_key_node.firstChild.TEXT_NODE:
            data = session_key_node.firstChild.data
            config["session_key"] = data 
            
        server_uri_node = root.getElementsByTagName("server_uri")[0]
        if server_uri_node and server_uri_node.firstChild and server_uri_node.firstChild.nodeType == server_uri_node.firstChild.TEXT_NODE:
            data = server_uri_node.firstChild.data
            config["server_uri"] = data   
            
        conf_node = root.getElementsByTagName("configuration")[0]
        if conf_node:
            logging.debug("XML: found configuration")
            stanza = conf_node.getElementsByTagName("stanza")[0]
            if stanza:
                stanza_name = stanza.getAttribute("name")
                if stanza_name:
                    logging.debug("XML: found stanza " + stanza_name)
                    config["name"] = stanza_name

                    params = stanza.getElementsByTagName("param")
                    for param in params:
                        param_name = param.getAttribute("name")
                        logging.debug("XML: found param '%s'" % param_name)
                        if param_name and param.firstChild and \
                           param.firstChild.nodeType == param.firstChild.TEXT_NODE:
                            data = param.firstChild.data
                            config[param_name] = data
                            logging.debug("XML: '%s' -> '%s'" % (param_name, data))

        checkpnt_node = root.getElementsByTagName("checkpoint_dir")[0]
        if checkpnt_node and checkpnt_node.firstChild and \
           checkpnt_node.firstChild.nodeType == checkpnt_node.firstChild.TEXT_NODE:
            config["checkpoint_dir"] = checkpnt_node.firstChild.data

        if not config:
            raise Exception, "Invalid configuration received from Splunk."

        
    except Exception, e:
        raise Exception, "Error getting Splunk configuration via STDIN: %s" % str(e)

    return config

#read XML configuration passed from splunkd, need to refactor to support single instance mode
def get_validation_config():
    val_data = {}

    # read everything from stdin
    val_str = sys.stdin.read()

    # parse the validation XML
    doc = xml.dom.minidom.parseString(val_str)
    root = doc.documentElement

    logging.debug("XML: found items")
    item_node = root.getElementsByTagName("item")[0]
    if item_node:
        logging.debug("XML: found item")

        name = item_node.getAttribute("name")
        val_data["stanza"] = name

        params_node = item_node.getElementsByTagName("param")
        for param in params_node:
            name = param.getAttribute("name")
            logging.debug("Found param %s" % name)
            if name and param.firstChild and \
               param.firstChild.nodeType == param.firstChild.TEXT_NODE:
                val_data[name] = param.firstChild.data

    return val_data

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == "--scheme":           
            do_scheme()
        elif sys.argv[1] == "--validate-arguments":
            do_validate()
        else:
            usage()
    else:
        config = get_input_config()
        do_run(config)
        
    sys.exit(0)
