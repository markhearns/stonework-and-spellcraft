import json,tempfile,threading,unittest,urllib.request,urllib.error,uuid
from server import create_server
class ArmouryHTTPTests(unittest.TestCase):
 def test_readonly_quote_revision_retry_and_asset_routes(self):
  with tempfile.TemporaryDirectory() as d:
   server=create_server('127.0.0.1',0,d);thread=threading.Thread(target=lambda:server.serve_forever(poll_interval=.02),daemon=True);thread.start()
   def call(path,data=None):
    req=urllib.request.Request('http://127.0.0.1:'+str(server.server_port)+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=5) as response:return json.load(response)
   try:
    s=call('/api/state');q=call('/api/equipment/quote',{'action':{'type':'gear-review'}});self.assertEqual(q['revision'],s['revision']);self.assertEqual(call('/api/state'),s)
    request={'requestId':uuid.uuid4().hex,'expectedRevision':s['revision'],'action':q['action']};after=call('/api/action',request);self.assertEqual(call('/api/action',request),after)
    request['requestId']=uuid.uuid4().hex
    with self.assertRaises(urllib.error.HTTPError) as err:call('/api/action',request)
    self.assertEqual(err.exception.code,409)
    for asset in ('/assets/equipment/equipment-steel-sword.webp','/assets/equipment/signature-founder.webp','/assets/expeditions/north-watch-road.webp','/assets/ui/arms-of-our-own.webp'):
     with urllib.request.urlopen('http://127.0.0.1:'+str(server.server_port)+asset) as response:self.assertEqual(response.status,200);self.assertIn('image/',response.headers['Content-Type']);self.assertTrue(response.read())
   finally:server.shutdown();thread.join(5);server.server_close()
