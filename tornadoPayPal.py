#encoding=utf8
import tornado.ioloop
import tornado.web
import tornado.escape
import tornado.options
import tornado.websocket
import tornado.autoreload
import tornado.httpclient
from tornado.httputil import url_concat
import urllib2
import base64
import os
import hashlib
import time
import json
import md5
import struct

import time
import MySQLdb
import datetime
 
html = """
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="X-UA-Compatible" content="IE=edge" />
</head>
<body>
<script id ="purchase" src="https://www.paypal.com/sdk/js?client-id=%s"></script>
<script>
var amount_ = "%s";
var custom_id_ = "%s";
paypal.Buttons({
    createOrder: function(data, actions) {
      // Set up the transaction
      return actions.order.create({
        purchase_units: [{
           amount: {
		    currency_code: "USD",
            value: amount_
          },
		  custom_id:custom_id_
        }]
      });
    },
    onApprove: function(data, actions) {
      return actions.order.capture().then(function(details) {
		var d = {data,'ext':custom_id_}
		document.write("<h1>Thank you for purchase.Please save your order.</h1>"
		+ "<h2>" + JSON.stringify(d) + "</h2>"
		+ "<input id='btnClose' type='button' value='close' onClick='custom_close()' />")
        return fetch('/PaypalPayOk', {
          method: 'post',
          headers: {
            'content-type': 'application/json'
          },
          body: JSON.stringify(d)
        });
      });
    }
	}).render('body');
	function custom_close()
	{
		if (confirm("ok?"))
		{
			window.opener=null;
			window.open('','_self');
			window.close();
		}
	}
	</script>
</body>
"""
clientID = "AUBZswxAZYPGXSN-JS43rnDWbE-R3NAnaMjoPVOS9zozbF3uJ82R0-nj_8kMCyHEcPwvSD5Fc6w_pnnZ"
secure = "EAbuW3yTQlVAVPVS19_wvPKKe_k0TU4_RT62uiTSccblCGAivK6v_HhlNUklLMBZZFD4_PIr0puwzIBX"

url1 = "https://api.sandbox.paypal.com/v1/payments/payment/"
url = "https://api.sandbox.paypal.com/v2/checkout/orders/"
url2 = "https://api.sandbox.paypal.com/v2/payments/captures/"

#url1 = "https://api.paypal.com/v1/payments/payment/"
#url = "https://api.paypal.com/v2/checkout/orders/"
#url2 = "https://api.paypal.com/v2/payments/captures/"

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.set_cookie('SameSite','Strict')
		self.set_header(name="Access-Control-Allow-Origin", value="*")
		self.set_header(name="Access-Control-Allow-Credentials", value="true")
		self.write(html % (clientID,"1.0","userID_productID_"))

#on "event_type": "PAYMENT.CAPTURE.COMPLETED"
class PaypalPayWebhook(tornado.web.RequestHandler):
	def post(self):
		logging.info("webhook postData:")
		postData = self.request.body.decode('utf-8')
		logging.info(postData)
		j = json.loads(postData)
		if j["event_type"] != "PAYMENT.CAPTURE.COMPLETED":
			self.write("success")
			return
		try:
			if j["resource"]["status"] != "COMPLETED":
				self.write("success")
				return
			ua_header = {"Content-Type" : "application/json"}
			ua_header["Authorization"] = "Basic " + base64.b64encode(clientID + ":" + secure)
			request = urllib2.Request(url2 + j["resource"]["id"], headers = ua_header)
			response = urllib2.urlopen(request)
			ret = response.read()
			print ret
			j2 = json.loads(ret)
			if j2["status"] == "COMPLETED":
				orderID = "paypal_" + j["resource"]["id"]
				ext = j["resource"]["custom_id"]
				logging.info("orderID:")
				logging.info(orderID)
				#TODO recharge
			self.write("success")
		except Exception as e:
			logging.info("except")
			logging.info(e.args)
			logging.info(str(e))
			logging.info(repr(e))
			self.write("success")
			return
		
class PaypalPayOk(tornado.web.RequestHandler):
	def post(self):
		j = json.loads(self.request.body.decode('utf-8'))
		ua_header = {"Content-Type" : "application/json"}
		ua_header["Authorization"] = "Basic " + base64.b64encode(clientID + ":" + secure)
		
		request = urllib2.Request(url1 + j["data"]["orderID"], headers = ua_header)
		try:
			response = urllib2.urlopen(request)
			ret = response.read()
			print ret
			j1 = json.loads(ret)
			j["data"]["orderID"] = j1["cart"]
		except:
			pass
		
		request = urllib2.Request(url + j["data"]["orderID"], headers = ua_header)
		response = urllib2.urlopen(request)
		ret = response.read()
		print ret
		j2 = json.loads(ret)
		if j2["status"] == "COMPLETED":
			try:
				j["data"]["orderID"] = j["data"]["orderID"] + "_" + j2["purchase_units"][0]["payments"]["captures"][0]["id"]
				logging.info("paypal_" + j["data"]["orderID"])
			except:
				pass
			#do recharge
			pass
		self.write("success")
"""
settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    "login_url": "/login",
    "xsrf_cookies": True,
}
application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/RechargeRank", RechargeRankHandler),
	(r"/(apple-touch-icon\.html)", tornado.web.StaticFileHandler, dict(path=settings['static_path'])),
], **settings)
"""
class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
			(r"/", MainHandler),
			(r"/PaypalPayOk", PaypalPayOk),
			(r"/PaypalPayWebhook", PaypalPayWebhook),
		]
		settings = dict(
			cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
			template_path=os.path.join(os.path.dirname(__file__), "templates"),
			static_path=os.path.join(os.path.dirname(__file__), "static"),
			static_url_prefix = "/static/",
			xsrf_cookies=False,
		)
		tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == "__main__":
	tornado.options.parse_command_line()
	app = Application()
	app.listen(8800)
	loop = tornado.ioloop.IOLoop.instance()
	#tornado.autoreload.watch(r'static\temp.js')
	tornado.autoreload.start(loop)
	loop.start()
	#application.listen(config.WEB_PORT)
	#tornado.ioloop.IOLoop.instance().start()


