from flasknode import app

@app.route('/')
def index():
   return app.send_static_file('index.html')
   
@app.route('/favicon.ico')
def favicon():
   return app.send_static_file('favicon.ico')
   
@app.route('/js/<path:path>')
def return_js(path):
   return app.send_static_file('js/%s' % path)
   
@app.route('/css/<path:path>')
def return_css(path):
   return app.send_static_file('css/%s' % path)
   
@app.route('/img/<path:path>')
def return_img(path):
   return app.send_static_file('img/%s' % path)
   

