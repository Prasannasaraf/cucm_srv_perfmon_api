from lxml import etree
from requests import Session
from requests.auth import HTTPBasicAuth

from zeep import Client, Settings, Plugin
from zeep.transports import Transport
from zeep.cache import SqliteCache
from zeep.plugins import HistoryPlugin
from zeep.exceptions import Fault

# These are sample values for DevNet sandbox
# replace them with values for your own CUCM, if needed

WSDL_URL = 'AXLAPI.wsdl'
CUCM_URL = 'https://localhost:200/axl/'
USERNAME = 'administrator'
PASSWD = 'ciscopsdt'
phoneName = ''

history = HistoryPlugin()

# This class lets you view the incoming and outgoing http headers and XML
class MyLoggingPlugin(Plugin):

    def ingress(self, envelope, http_headers, operation):
        print(etree.tostring(envelope, pretty_print=True))
        return envelope, http_headers

    def egress(self, envelope, http_headers, operation, binding_options):
        print(etree.tostring(envelope, pretty_print=True))
        return envelope, http_headers

session = Session()

session.verify = False
session.auth = HTTPBasicAuth(USERNAME, PASSWD)

transport = Transport(session=session, timeout=10, cache=SqliteCache())

# strict=False is not always necessary, but it allows zeep to parse imperfect XML
settings = Settings(strict=False, xml_huge_tree=True)

client = Client(WSDL_URL, settings=settings, transport=transport, plugins=[MyLoggingPlugin(),history])

service = client.create_service("{http://www.cisco.com/AXLAPIService/}AXLAPIBinding", CUCM_URL)

try:
  phone_resp = service.getPhone(name = phoneName)
except Fault as err:
  print("Zeep error: {0}".format(err))
else:
  print("\ngetPhone response:\n")
  print(phone_resp,"\n")
  print(history.last_sent)
  print(history.last_received)

