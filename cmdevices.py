#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script for querying Cisco RisPort Serviceability API for device registration status.
Api descripbed at https://developer.cisco.com/site/sxml/documents/api-reference/risport/

CLI Args:
    "-c", "--cucm" CUCM node IP
    "-u", "--user" AXL username
    "-p", "--password" AXL user password
    "-m", "--models" models (int values separated by space - consult models.txt for mappings to names)
    (i.e -m 626 682 will monitor SX10 and SX20 statuses)
"""

import argparse

import requests

requests.packages.urllib3.disable_warnings()

# this is a template for SelectCmDevice request body
select_cm_device_req = """
<SOAP-ENV:Envelope xmlns:ns3="http://www.w3.org/2001/XMLSchema"
xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"
xmlns:ns0="http://schemas.xmlsoap.org/soap/encoding/"
xmlns:ns1="http://schemas.cisco.com/ast/soap/"
xmlns:ns2="http://schemas.xmlsoap.org/soap/envelope/"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
<SOAP-ENV:Header/>
<ns2:Body>
<ns1:SelectCmDevice>
<CmSelectionCriteria xsi:type="ns1:CmSelectionCriteria">
<ns1:MaxReturnedDevices xsi:type="xsd:unsignedInt">10000</ns1:MaxReturnedDevices>
<ns1:Class xsi:type="ns3:string">SIP Trunk</ns1:Class>
<ns1:SelectBy xsi:type="ns3:string">Name</ns1:SelectBy>
</CmSelectionCriteria></ns1:SelectCmDevice>
</ns2:Body>
</SOAP-ENV:Envelope>"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cucm", help="CUCM node IP", required=True)
    parser.add_argument("-u", "--user", help="AXL username", required=True)
    parser.add_argument("-p", "--password",
                        help="AXL user password", required=True)
    args = parser.parse_args()
    headers = {
        'SOAPAction': '"http://schemas.cisco.com/ast/soap/action/#RisPort#SelectCmDevice"'}
    try:
        response = requests.post('https://{}:8443/realtimeservice/services/RisPort'.format(args.cucm),data=select_cm_device_req,auth=requests.auth.HTTPBasicAuth(args.user, args.password),headers=headers,verify=False,timeout=5)
        print(response)
        print(response.text)
    except (SystemExit, KeyboardInterrupt):
        print "Exiting"
