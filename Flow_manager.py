from common.utils import *
import json
import yaml #used for str to dict conversion
import random
import flowbodycreater

class Flow:
    FLOWID = 0
    odlip = read_from_file('odl.ini','ip','odl_ip') 
    def __init__(self,nodeip,outputnodeconnecter,destinationnodeip,protocol,tpmatch,set_tunnel64,nwproto,inport,table,outputgroup,priority,nodeip_id):
        self.nodeip = nodeip
        self.outputnodeconnecter = outputnodeconnecter
        self.destinationnodeip = destinationnodeip
        self.protocol = protocol
        self.tpmatch = tpmatch
        self.set_tunnel64 = set_tunnel64
        self.nwproto = nwproto
        self.inport = inport
        self.table = table
        self.outputgroup = outputgroup
        self.priority = priority
        self.nodeip_id = nodeip_id
    def pushflow(self):
        actionorder = []
        nodeid = None
        for key,value in self.nodeip_id.items():
            if key == self.nodeip:
                nodeid = value
                break
        #made changes in logic for writing tunnel action before outport
        if self.outputnodeconnecter!=None:
             if self.set_tunnel64!=None:
                 actionorder.append("1")
             actionorder.append("0")
        Flow.FLOWID=Flow.FLOWID + 1
        flowid = str(Flow.FLOWID)
        flowname = "flow"+flowid
        flowbody = flowbodycreater.create_flowbody(flowid,self.priority,self.table,flowname,actionorder,self.outputnodeconnecter,self.protocol,self.nwproto,self.tpmatch,self.set_tunnel64,self.destinationnodeip,self.inport,self.outputgroup)
        if self.table==None:
            self.table="0"

        url = "http://"+Flow.odlip+":8181/restconf/config/opendaylight-inventory:nodes/node/"+nodeid+"/table/"+self.table+"/flow/"+flowid
        resp = rest_call(url,'PUT',flowbody)
        if resp:
            print "FLow has been pushed on node: %s"% (self.nodeip)
            print resp.status,resp.reason
        else:
            print "Failed in pushing flow on node:%s"% (self.nodeip)
            print resp.status,resp.reason

