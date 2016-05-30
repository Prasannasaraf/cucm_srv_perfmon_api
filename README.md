# cucm_srv_perfmon_api
This script written in python queries CUCM (Cisco Unified Communicaion Manager) Serviceability API for a registration status of phones and other devices controled by it.
More at https://developer.cisco.com/site/sxml/discover/overview/perfmon/

For script to work:

1) Run SOAP services and add an AXL user as described here https://developer.cisco.com/site/sxml/learn/getting-started/risport/index.gsp#service-activation

2) Clone Install requirements

`git clone https://github.com/smirnov-am/cucm_srv_perfmon_api`

`pip install -r requirements`

3) Run script with credentials from p.1

`chmod +x cmdevices.py`

`./cmdevices.py -c 192.168.0.1 -u axl_admin -p *****`

