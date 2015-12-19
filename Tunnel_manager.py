from common.utils import *
import json
import yaml #used for str to dict conversion
import random

class Tunnel:
    odlip = read_from_file('odl.ini','ip','odl_ip')
    def __init__(self,nodeip,portname):
	self.nodeip = nodeip
        self.portname = portname
    def connect_ovsdb(self):
        '''
        This method builds an OVSDB Channel from ODL to the CPE/CE on the listener port 6640
        '''
        #print 'i am running ovsdb()******************'
        url = "http://"+Tunnel.odlip+":8080/controller/nb/v2/connectionmanager/node/"+self.nodeip+"/address/"+self.nodeip+"/port/6640"
        resp = rest_call(url,'PUT')
        #print resp
        if resp:
            print "Connected with OVSDB server of Node: %s"%(self.nodeip)
        else:
            print "Failed in connecting to the Node: %s" % (self.nodeip)

    def create_port(self):
        '''
        This method creates a Tunnel port of type either 'ipsec' or 'lntun' on the CPE/CE
        '''
        #print 'i am creating tunnel\\\\\\\\\\\\\\\"'
        url = "http://"+Tunnel.odlip+":8080/controller/nb/v2/networkconfig/bridgedomain/port/OVS/"+self.nodeip +"/br0/"+self.portname
        resp = rest_call(url,'POST',{})
        #print resp
        if resp:
            print " Port %s is created on Node: %s" % (self.portname,self.nodeip)
        else:
            print "Failed in port creation on Node: %s"%(self.nodeip)

    def get_interfaceUUID(self):
        '''
        This method will retrive interfaceuuid for the created port and used for configuring the created ports on CPE/CE
        '''
        #print 'i am getting interfaceuuid...:::::'
        url = "http://"+Tunnel.odlip+":8080/ovsdb/nb/v2/node/OVS/"+self.nodeip +"/tables/interface/rows"
        resp,content = rest_call(url,'GET')
        #print resp
        #print content
        interfaceUUID = {}
        for i in content:
            for j in content[i]:
                for y in content[i][j]:
                    #print res[i][j][y]
                    if(y == "_uuid"):
                        tuuid = content[i][j][y][1]
                    if(y == "name"):
                        tport = content[i][j][y]
                        #print y," : ",content[i][j][y]
                print 'READING PORT: %s'%(tport)
                interfaceUUID[tport] = tuuid
        print self.portname," : ",interfaceUUID[self.portname]
        return interfaceUUID[self.portname]

    def get_OFPortID(self):
        '''
        This method will retrieve the OF PortID of the ports created on the CPE/CE
        '''
        url = "http://"+Tunnel.odlip+":8080/ovsdb/nb/v2/node/OVS/"+self.nodeip +"/tables/interface/rows"
        resp,content = rest_call(url,'GET')
        #print resp
        #print content
        OFportID = {}
        try:
            for i in content:
                for j in content[i]:
                    for y in content[i][j]:
                        if(y == "ofport"):
                            tportid = content[i][j][y][1]
                        if(y == "name"):
                            tport = content[i][j][y]
                    print 'READING PORT: %s'%(tport)
                    OFportID[tport] = tportid
            print self.portname," : ",OFportID[self.portname][0]
            return OFportID[self.portname][0]
        except KeyError, e:
                    print "port not present(key error)"
                    return None
        except Exception, e:
                    print "port not present(exception)"
                    return None

    def configure_port(self,interfaceuuid,portinfolist,porttype):
        '''
            This method will configure the with the interfaceuuid retreived
        '''
        #print 'i am configuring tunnel..'
        url = "http://"+Tunnel.odlip+":8080/ovsdb/nb/v2/node/OVS/"+self.nodeip +"/tables/interface/rows/"+interfaceuuid
        option = []
        for pairs in portinfolist:
            pairlist = pairs.split(':')
            if pairlist[0]=='key':
                option.append(pairlist)
            elif pairlist[0]=='type':
                option.append(pairlist)
            if porttype == 'lntun':
                if pairlist[0]=='remote_ip':
                    option.append(pairlist)
                elif pairlist[0]=='tx_port':
                    option.append(pairlist)
                elif pairlist[0]=='hs_on':
                    option.append(pairlist)
        options = ["map",option]
        requestBody = {"row":{"Interface":{"type":porttype,"options" : options}}}
        resp = rest_call(url,'PUT',requestBody)
        #print resp
        if resp:
            print "Port is created with specified options on Node: %s" % (self.nodeip)
        else:
            print "Failed in creating port with options specified on Node: %s"%(self.nodeip)
            print resp.status


    
