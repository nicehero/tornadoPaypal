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
paypal.Buttons({
    createOrder: function(data, actions) {
      // Set up the transaction
      return actions.order.create({
        purchase_units: [{
          amount: {
		    currency_code: "USD",
            value: "%s"
          }
        }]
      });
    },
    onApprove: function(data, actions) {
      return actions.order.capture().then(function(details) {
		var d = {data,'ext':"%s"}
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
clientID = "AQG0BHDHJiNOW_cLOHCiJ3gV_ogy1ggjsHuXT9jykaEVsuX54G31v1sOjHDw4RU-bhRV74aORtZHmNdZ"
secure = "EBx3OTa9q6GrrGWzrbDysvSpOQjGIhdNWjHJLVQ4ffLjjN7biyNNKlW4mRQ50RlaKDfHbVCbLDlJWs9k"
testAccount = "sb-tqb8n1333149@personal.example.com"
testPassword = "Ix\"r1.?j"
class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.write(html % (clientID,"1.0","userID_productID_"))

class PaypalPayOk(tornado.web.RequestHandler):
	def post(self):
		url = "https://api.sandbox.paypal.com/v2/checkout/orders/"
		#url = "https://api.paypal.com/v2/checkout/orders/"
		j = json.loads(self.request.body.decode('utf-8'))
		ua_header = {"Content-Type" : "application/json"}
		ua_header["Authorization"] = "Basic " + base64.b64encode(clientID + ":" + secure)
		request = urllib2.Request(url + j["data"]["orderID"], headers = ua_header)
		response = urllib2.urlopen(request)
		html = response.read()
		print html
		j2 = json.loads(html)
		if j2["status"] == "COMPLETED":
			pass
		self.write("OK")
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

