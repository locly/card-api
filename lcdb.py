from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer
from pprint import pprint
import urlparse
import os
import base64
import json
import time
import sys

PORT_NUMBER = 8000

class bridgeHandler(BaseHTTPRequestHandler):
    
    #Handler for the GET requests
    def do_GET(self):
        urlInfo = urlparse.urlparse(self.path)

        if os.path.basename(urlInfo.path) == 'log.js':
            # Pull out the query
            query = urlparse.parse_qs(urlInfo.query)
            callbackList = query.get('cb', ['cb'])
            callback = callbackList[0] if len(callbackList) >= 1 else 'cb'
            dataList = query.get('data', [])
            data = dataList[0] if len(dataList) >= 1 else []
            data = json.loads(base64.b64decode(data))

            # Print the logs
            for log in data:
                self.printLog(log)

            # Respond
            self.send_response(200)
            self.send_header('Content-type', 'application/javascript')
            self.end_headers()
            self.wfile.write(callback + '()')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write('404 not found')
        return
    def log_message(self, format, *args):
        return

    def printLog(self, log):
        level = log.get('level', 'log').upper()
        timeStr = time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(log.get('time', 1000) / 1000))
        messages = log.get('messages', [])

        col = ''
        if level == 'ERROR':
            col = '\033[91m'
        elif level == 'WARN':
            col = '\033[93m'
        else:
            col = '\033[92m'

        sys.stdout.write(col)
        sys.stdout.write('[' + level + ' ' + timeStr + ']\033[0m ')
        for message in messages:
            pprint(message)




try:
    server = HTTPServer(('', PORT_NUMBER), bridgeHandler)
    print 'Started Locly Card Debug Bridge (LCDB) on port ', PORT_NUMBER
    server.serve_forever()
except KeyboardInterrupt:
    print '^C received, shutting down the web server'
    server.socket.close()