import httplib2
import json
import yaml #used for str to dict conversion
import random
import flowbodycreater
#import ast {for str to dict converion not supported after python 2.6v}
import time
import sys
from common.utils import *
from Flow_manager import Flow
from Group_manager import Group
from Tunnel_manager import Tunnel
odlip = read_from_file('odl.ini','ip','odl_ip')
nodeip_id ={}

def get_nodeip_id_dict():
    '''
    This method get inventory details and return nodeip nodeid dictonary 
    '''
    url = "http://"+odlip+":8181/restconf/operational/opendaylight-inventory:nodes/"
    resp,content = rest_call(url,'GET')
    #nodeip_id ={}
    for i in content:
	for j in content[i]:
	    for k in content[i][j]:
		nodeid = k["id"]
		nodeip = k["flow-node-inventory:ip-address"]
		nodeip_id[nodeip] = nodeid
    print nodeip_id
    return nodeip_id
		

def fileread(lnconfig_file):
    '''
    This method will read tunnel.txt and perform tunnel creation for each input line
    '''
    lines = [line.rstrip('\n').split(',') for line in open(lnconfig_file)]
    print lines
    nodekeyportlist = []
    #import pdb;pdb.set_trace()
    for tunnelinfo in lines:
        print tunnelinfo
        nodeip=None
        tunneltype=None    
        key=None
        destinationnodeip = None
        protocol = None
        tpmatch = None
	set_tunnel64 = None
        nwproto = None
	inport = None	
	outport = None
	portid= None
	priority = None
	tunnelname = None
	table = None
	groupid = None
	grouptype = None
	outputgroup = None
	bucketlist = []
        bucketlist_file = []
        for pairs in tunnelinfo:
            pairlist = pairs.split(':')
            if pairlist[0]=='nodeIp':
                nodeip = pairlist[1]
            elif pairlist[0]=='type':
                tunneltype = pairlist[1]
            elif pairlist[0]=='key':
                key = pairlist[1]
	    elif  pairlist[0]=='node_destinationIp':
                destinationnodeip = pairlist[1]
       	    elif  pairlist[0]=='protocol':
                protocol = pairlist[1]
	    elif  pairlist[0]=='tp_src' or pairlist[0]=='tp_dst':
                tpmatch = pairlist
	    elif  pairlist[0]=='set_tunnel64':
                set_tunnel64 = pairlist[1]
	    elif  pairlist[0]=='nw_proto':
                nwproto = pairlist[1]
            elif  pairlist[0]=='inport':
                inport = pairlist[1]
            elif  pairlist[0]=='output':
                outport= pairlist[1]
            elif  pairlist[0]=='priority':
                priority= pairlist[1]
            elif  pairlist[0]=='table':
                table = pairlist[1]
            elif  pairlist[0]=='groupId':
                groupid = pairlist[1]
	    elif  pairlist[0]=='groupType':
                grouptype = pairlist[1]
	    elif  pairlist[0]=='outputGroup':
                outputgroup = pairlist[1]
            elif  pairlist[0]=='bucket':
                bucketlist_file.append(pairlist[1])
        #import pdb; pdb.set_trace()
        if tunneltype=='lntun':
            tunnelname='cpt'+key
        elif tunneltype=='service':
            tunnelname='ipsec'
        #connect_ovsdb(nodeip)
        if tunneltype!=None:
            tunnel = Tunnel(nodeip,tunnelname)
            tunnel.connect_ovsdb()
            import pdb;pdb.set_trace()
            portid = tunnel.get_OFPortID()
            if portid == None:
                #tunnel.connect_ovsdb(nodeip)
                tunnel.create_port()
                interfaceid= tunnel.get_interfaceUUID()
                tunnel.configure_port(interfaceid,tunnelinfo,tunneltype)
    	        print " I am sleeping for 5 sec..",time.sleep(5)
                portid =  tunnel.get_OFPortID()
           	nodekeyportlist.append(nodeip+":"+key+":"+str(portid)+":"+tunnelname)
                if protocol!=None:
                    flow = Flow(nodeip,portid,destinationnodeip,protocol,tpmatch,set_tunnel64,nwproto,inport,table,outputgroup,priority,nodeip_id)
             	    flow.pushflow()
	    else:
		print "%s PORT already exists with PORT ID: %s"%(tunnelname,portid)
		nodekeyportlist.append(nodeip+":"+key+":"+str(portid)+":"+tunnelname)
                if protocol!=None:
           	    flow = Flow(nodeip,portid,destinationnodeip,protocol,tpmatch,set_tunnel64,nwproto,inport,table,outputgroup,priority,nodeip_id)
                    flow.pushflow()

        elif groupid!=None:
            bucketlist = []
            #import pdb;pdb.set_trace()
            
            for bucket in bucketlist_file:
                tunnel = Tunnel(nodeip,"cpt"+bucket)
                portid = tunnel.get_OFPortID()
                if portid !=None:
                    bucketlist.append(portid)
            group = Group(nodeip,groupid,grouptype,bucketlist,nodeip_id) 
	    group.pushgroup()
        elif outputgroup!= None:
            flow = Flow(nodeip,portid,destinationnodeip,protocol,tpmatch,set_tunnel64,nwproto,inport,table,outputgroup,priority,nodeip_id)
            flow.pushflow()
	else:
	    if outport!=None:
	        flow = Flow(nodeip,outport,destinationnodeip,protocol,tpmatch,set_tunnel64,nwproto,inport,table,outputgroup,priority,nodeip_id)
                flow.pushflow()
	    else:
		port = None
		for nodekeyport in nodekeyportlist:
		    nodekeyportarray = nodekeyport.split(':')
		    if nodekeyportarray[0] == nodeip:
			if nodekeyportarray[1] == key:
			    portid = nodekeyportarray[2]
			    flow = Flow(nodeip,portid,destinationnodeip,protocol,tpmatch,set_tunnel64,nwproto,inport,table,outputgroup,priority,nodeip_id)
                            flow.pushflow()
	
if __name__ == "__main__":
    #import pdb; pdb.set_trace()
    lnconfig_file = sys.argv[1]
    nodeip_id = get_nodeip_id_dict()
    print lnconfig_file
    fileread(lnconfig_file)


