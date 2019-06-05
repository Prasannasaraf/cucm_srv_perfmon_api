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
import xml.etree.ElementTree as ET
from collections import defaultdict
from time import sleep
from datetime import datetime
from xml.sax.saxutils import escape
from copy import deepcopy
import re
from itertools import izip_longest

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
<StateInfo xsi:type="ns3:string">{}</StateInfo>
<CmSelectionCriteria xsi:type="ns1:CmSelectionCriteria">
<ns1:MaxReturnedDevices xsi:type="xsd:unsignedInt">10000</ns1:MaxReturnedDevices>
<ns1:Class xsi:type="ns3:string">Phone</ns1:Class>
<ns1:Model xsi:type="ns3:unsignedInt">{}</ns1:Model>
<ns1:SelectBy xsi:type="ns3:string">Name</ns1:SelectBy>
</CmSelectionCriteria></ns1:SelectCmDevice>
</ns2:Body>
</SOAP-ENV:Envelope>"""


def compare_outputs(a, b):
    """Compare previous and current result of a SelectCmDevice query from CUCM
    Now it doesn't support StateInfo and used to compare consequtive queries
    :param a: previous query
    :param b: current query
    :return: list of strings describing changes
    """
    a_keys = set(a.keys())
    b_keys = set(b.keys())
    keys_added = b_keys - a_keys
    keys_deleted = a_keys - b_keys
    _common = a_keys & b_keys
    common_eq = set(k for k in _common if sorted(a[k]) == sorted(b[k]))
    common_neq = _common - common_eq
    added = ['{}  added'.format(x) for x, y in b.items() if x in keys_added]
    deleted = ['{} deleted'.format(x)
               for x, y in a.items() if x in keys_deleted]
    changed = []
    for i in common_neq:
        for pair in izip_longest(sorted(a[i]), sorted(b[i]), fillvalue=dict((k, 'NA') for k in ('Status', 'IP'))):
            for key in ('Status', 'IP'):
                if pair[0][key] != pair[1][key]:
                    changed.append('{} changed {} to {} on node {}'.format(
                        i, key, pair[1][key], pair[1]['node']))
    return added + deleted + changed


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cucm", help="CUCM node IP", required=True)
    parser.add_argument("-u", "--user", help="AXL username", required=True)
    parser.add_argument("-p", "--password",
                        help="AXL user password", required=True)
    parser.add_argument("-m", "--models", help="models", default='682 626')
    args = parser.parse_args()
    headers = {
        'SOAPAction': '"http://schemas.cisco.com/ast/soap/action/#RisPort#SelectCmDevice"'}
    state_info = ''
    temp = defaultdict(list)
    models = {}
    models_re = re.compile('(\d+) (.+)')
    with open('models.txt', 'r') as f:
        for model in f:
            models[models_re.split(model)[1]] = models_re.split(model)[2]
    models_required = args.models.split()
    try:
        all_devices = defaultdict(list)
        for model in models_required:
            response = requests.post('https://{}:8443/realtimeservice/services/RisPort'.format(args.cucm),
                                     data=select_cm_device_req.format(
                                         state_info, model),
                                     auth=requests.auth.HTTPBasicAuth(
                                         args.user, args.password),
                                     headers=headers,
                                     verify=False,
                                     timeout=5)

            xml = ET.fromstring(response.text)
            for node in xml.iter('item'):
                if 'ns1:CmNode' in node.attrib.values():
                    node_name = node.find('Name').text
                    for j in node.find('CmDevices').findall('item'):
                        all_devices[j.find('Name').text].append({'IP': j.find('IpAddress').text,
                                                                 'node': node_name,
                                                                 'Model': models[j.find('Model').text],
                                                                 'Description': j.find('Description').text,
                                                                 'Status': j.find('Status').text})

            # SelectCmdevices supports Stateinfo string to be sent with subsequent requests. Try this!!
            # for j in xml.iter('StateInfo'):
            #    state_info = escape(j.text)
            sleep(1)
        for s in compare_outputs(temp, all_devices):
            print '{} : {}'.format(datetime.now(), s)
        temp = deepcopy(all_devices)
        sleep(15)
    except (SystemExit, KeyboardInterrupt):
        print "Exiting"
