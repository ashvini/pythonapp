from common.utils import *
import json
import yaml #used for str to dict conversion
import random
import flowbodycreater

class Group:
    odlip = read_from_file('odl.ini','ip','odl_ip')
    def __init__(self,nodeip,groupid,grouptype,bucketlist,nodeip_id):
        self.nodeip = nodeip
        self.groupid = groupid
        self.grouptype = grouptype
        self.bucketlist = bucketlist
        self.nodeip_id = nodeip_id
    def pushgroup(self):
        '''
        This method is adding group into group table
        '''
        nodeid = None
        for key,value in self.nodeip_id.items():
            if key == self.nodeip:
                nodeid = value
                break
        groupname = "group"+self.groupid
        groupbody = flowbodycreater.create_groupbody(self.groupid,self.grouptype,groupname,self.bucketlist)
        url = "http://"+Group.odlip+":8181/restconf/config/opendaylight-inventory:nodes/node/"+nodeid+"/group/"+self.groupid
        resp = rest_call(url,'PUT',groupbody)
        if resp:
            print "Group has been pushed on node: %s"% (self.nodeip)
            print resp.status,resp.reason
        else:
            print "Failed in pushing group on node:%s"% (self.nodeip)
            print resp.status,resp.reason

