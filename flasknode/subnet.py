#from flasknode import config
import socket

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

def init_swarm():
   my_ip = get_ip()
   if 'nodes' in config.sections():
      for node_name in config['nodes']:
         ip = config['nodes'][node_name]
         if ip != my_ip:
            print ("node %s -> %s" % (node_name, ip))
