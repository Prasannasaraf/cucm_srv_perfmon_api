import sys
import ssl
import urllib2
from suds.xsd.doctor import Import
from suds.xsd.doctor import ImportDoctor
from suds.client import Client
from suds.transport.https import HttpAuthenticated
from email.mime.text import MIMEText
from subprocess import Popen, PIPE

# Defining some variable
CMServer 	= '192.168.0.1' #IP of CUCM publisher
port 	= '8443'
user 		= 'srv_api_user' # Do not forget to create this user and add him to appropriate groups
passwd 		= '**********';
wsdl = 'https://'+ CMServer + ':' + port +'/realtimeservice/services/RisPort?wsdl'
location = 'https://' + CMServer + ':' + port + '/realtimeservice/services/RisPort'

# Here are the models of cmdevices registration status we are querying. For the full list of model ids see models.txt
models=['626', '682', '431']

# Repairing xml schema
tns = 'http://schemas.cisco.com/ast/soap/'
imp = Import('http://schemas.xmlsoap.org/soap/encoding/', 'http://schemas.xmlsoap.org/soap/encoding/')
imp.filter.add(tns)

# As soon as we are using https for access to CUCM we need an appropriate ssl context. 
# Following code works with ssl module from python 2.7.9.
ssl_def_context = ssl.create_default_context()
ssl_def_context.check_hostname = False
ssl_def_context.verify_mode = ssl.CERT_NONE

# Main action starts here
layout=[]
for model in models:
    t0 = HttpAuthenticated(username=user, password=passwd)
    t0.handler=urllib2.HTTPBasicAuthHandler(t0.pm)
    t1=urllib2.HTTPSHandler(context=ssl_def_context)
    t.urlopener = urllib2.build_opener(t0.handler,t1)
    client=Client(wsdl,location=location, plugins=[ImportDoctor(imp)], transport=t)
    result = client.service.SelectCmDevice('',{'SelectBy':'Name', 'Class':'Phone', 'Model':model})
    for node in result['SelectCmDeviceResult']['CmNodes']:
        for device in node['CmDevices']:
            layout.append({ 'Name':str(device['Name']),
                            'Description': unicode(device['Description']),
                            'IP': str(device['IpAddress']),
                            'Status':str(device['Status']),
                            'Model':str(device['Model']),
                            'Registrar':str(node['Name'])
                                   })


# Strangely enough but CUCM (10.5.2 in my case) shows device status as Unregistered if it's unregistered from one node but registered on another
# Following code will search for such split status and reduce layout 								   
layout_reduce=[]
for i in range(len(layout)):
    for j in range(i+1,len(layout)):
        if (layout[i]['Name']==layout[j]['Name']) and (layout[i]['Status']!=layout[j]['Status']) and (layout[i]['Status']=='Registered'  and layout[j]['Status']=='UnRegistered'):
            layout[j]['Status']='split'
        if (layout[i]['Name']==layout[j]['Name']) and (layout[i]['Status']!=layout[j]['Status']) and (layout[i]['Status']=='UnRegistered'  and layout[j]['Status']=='Registered'):
            layout[i]['Status']='split'
for i in layout:
    if i['Status']!='split':
        layout_reduce.append(i)


# Here we are going to print device status
for i in layout_reduce:
    print "Status of %s (%s) with IP %s is %s  at server %s" %(i['Name'],i['Description'],i['IP'],i['Status'],i['Registrar'])

