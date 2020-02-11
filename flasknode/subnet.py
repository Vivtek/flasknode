import socket
import threading
import time

# The following is from this answer: https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def init_swarm(app):
   if 'nodes' in app.fnconfig.sections():
      print ("nodes defined in config")
      for node_name in app.fnconfig['nodes']:
         ip = app.fnconfig['nodes'][node_name]
         if ip != app.my_ip:
            print ("  node %s -> %s" % (node_name, ip))
            
def subnet_maint_thread(app):
   time.sleep(3)
   print ("in subnet_maint_thread, our IP is %s" % app.my_ip)
   init_swarm(app)
            
def start_subnet_maintenance(app):
   x = threading.Thread(target=subnet_maint_thread, args=(app,), daemon=True)
   x.start()
