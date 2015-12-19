import json
def create_flowbody(flowid,priority,tableid,flowname,actionorder,outputnodeconnector,ipprotocol,netproto,tpmatch,set_tunnel64action,destinationnodeip,inport,outputgroup):
    flowbody ={}
    flowbodyjson = {}
    instructions = {}
    match ={}	
   
    flowbodyjson["id"] = flowid
    if priority!=None:
	flowbodyjson["priority"] = priority
    else:
	flowbodyjson["priority"] = "100"
    flowbodyjson["flow-name"] = flowname
    flowbodyjson["hard-timeout"] = "0"
    flowbodyjson["idle-timeout"] = "0"
    if tableid!= None:
	 flowbodyjson["table_id"] = tableid
    else:
	flowbodyjson["table_id"] = "0"


    instruction = {}
    instruction["order"]="0"
    listaction = []
    if outputnodeconnector !=None:
	action = {}
        action["order"] = actionorder[0]
	action["output-action"] = {"output-node-connector":outputnodeconnector}
        listaction.append(action)
    if set_tunnel64action !=None:
	action = {}
        action["order"] = actionorder[1]
        action["set-field"] = {"tunnel":{"tunnel-id":set_tunnel64action}}
        listaction.append(action)
    if outputgroup !=None:
	action = {}
        action["order"] = "0"
        action["group-action"] = {"group-id":outputgroup}
	listaction.append(action)
    instruction["apply-actions"] = {"action":listaction}
    instructions["instruction"] = instruction
    flowbodyjson["instructions"] = instructions
    
    matchjson = {}
    if destinationnodeip!=None:
        if '/' in destinationnodeip :
            matchjson["ipv4-destination"] = destinationnodeip
	else:
	    matchjson["ipv4-destination"] = destinationnodeip+"/32"
        #matchjson["ethernet-match"] = {"ethernet-type": { "type": "2048" }
    if inport!=None:
         matchjson["in-port"] = inport
    if ipprotocol!=None:
	matchjson["ethernet-match"] = {"ethernet-type": { "type": "2048" }}
	if netproto !=None:
	    matchjson["ip-match"] = {"ip-protocol":netproto}
	if ipprotocol=="udp":
	    matchjson["ip-match"] = {"ip-protocol":"17"}
	elif ipprotocol=="icmp":
	     matchjson["ip-match"] = {"ip-protocol":"1"}
	elif ipprotocol=="tcp":
             matchjson["ip-match"] = {"ip-protocol":"6"}
        #made changes in logic for chacking tpmatch is not equal to null
        if tpmatch!= None:
            if ipprotocol=="udp":
                if tpmatch[0]=="tp_src":
                    matchjson["udp-source-port"] = tpmatch[1]
                elif tpmatch[0]=="tp_dst":
                    matchjson["udp-destination-port"] = tpmatch[1]
            elif ipprotocol=="tcp":
                if tpmatch[0]=="tp_src":
                    matchjson["tcp-source-port"] = tpmatch[1]
                elif tpmatch[0]=="tp_dst":
                    matchjson["udp-source-port"] = tpmatch[1]
    flowbodyjson["match"] = matchjson
    flowbody["flow"] = flowbodyjson
    return flowbody
	
def create_groupbody(groupid,grouptype,groupname,bucketlist):
	groupbody = {}
	groupbodyjson = {}
	bucketsjson = {}
	groupbodyjson["group-id"] = groupid
	groupbodyjson["group-type"] = "group-"+grouptype
	groupbodyjson["group-name"] = groupname
        buckets = []
	for i in range(len(bucketlist)):
		bucketjson = {}
		actionjson = {}
		actionjson["order"] = "0"
		actionjson["output-action"] = {"output-node-connector":bucketlist[i]}
		bucketjson["action"] = actionjson
		bucketjson["bucket-id"] = str(i)
		bucketjson["weight"] = "1"
		bucketjson["watch_group"] = "4294967295"
		bucketjson["watch_port"] = "4294967295"
		buckets.append(bucketjson)
	bucketsjson["bucket"] = buckets
	groupbodyjson["buckets"] = bucketsjson
        groupbody["group"] = groupbodyjson
        return groupbody
	
		
		
		
		


