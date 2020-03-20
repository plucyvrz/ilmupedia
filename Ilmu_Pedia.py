import os
import sys
import random
import socket
import select
import datetime
import threading


hostname = "www.google.com" 
response = os.system("ping -c 3 -w3 " + hostname) 
#and then check the response... 
if response == 0:
  print hostname, '-----up-----\n\n' 
else: 
  print hostname, '-----down-----\n\n'

lock = threading.RLock(); os.system('cls' if os.name == 'nt' else 'clear')

def real_path(file_name):
    return os.path.dirname(os.path.abspath(__file__)) + file_name

def filter_array(array):
    for i in range(len(array)):
        array[i] = array[i].strip()
        if array[i].startswith('#'):
            array[i] = ''

    return [x for x in array if x]

def colors(value):
    patterns = {
        'R1' : '\033[31;1m', 'R2' : '\033[31;2m',
        'G1' : '\033[32;1m', 'Y1' : '\033[33;1m',
        'P1' : '\033[35;1m', 'CC' : '\033[0m',
    }   

    for code in patterns:
        value = value.replace('[{}]'.format(code), patterns[code])

    return value

def log(value, status='\xf0\x9d\x95\x83\xf0\x9d\x95\xa0\xf0\x9d\x95\x94\xf0\x9d\x95\x92\xf0\x9d\x95\x9d\xe2\x84\x8d\xf0\x9d\x95\xa0\xf0\x9d\x95\xa4\xf0\x9d\x95\xa5', color='[CC]'):
    value = colors('{color}''[CC]''[{time}] [R1]{color}{status} [Y1]{color}{value}[R1]'.format(
        time=datetime.datetime.now().strftime('%H:%M:%S'),
        value=value,
        color=color,
        status=status
    ))
    with lock: print(value)

def log_replace(value, status='[R1]\xe2\x84\x99\xf0\x9d\x95\x96\xf0\x9d\x95\xa3\xf0\x9d\x95\x99\xf0\x9d\x95\x92\xf0\x9d\x95\xa5\xf0\x9d\x95\x9a\xf0\x9d\x95\x92\xf0\x9d\x95\x9f\x21     ', color='[Y1]'):
    value = colors('{}{} ({})        [CC]\r'.format(color, status, value))
    with lock:
        sys.stdout.write(value)
        sys.stdout.flush()

class inject(object):
    def __init__(self, inject_host, inject_port):
        super(inject, self).__init__()

        self.inject_host = str(inject_host)
        self.inject_port = int(inject_port)

    def log(self, value, color='[G1]'):
        log(value, color=color)

    def start(self):
        try:
            socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_server.bind((self.inject_host, self.inject_port))
            socket_server.listen(1)
            frontend_domains = open(real_path('/config.txt')).readlines()
            frontend_domains = filter_array(frontend_domains)
            if len(frontend_domains) == 0:
                self.log('Frontend Domains not found. Please check config.txt', color='[Y1]')
                return
            self.log('{} PORT {}'.format(self.inject_host, self.inject_port))
            while True:
                socket_client, _ = socket_server.accept()
                socket_client.recv(65535)
                domain_fronting(socket_client, frontend_domains).start()
        except Exception as exception:
            self.log('{} PORT {}'.format(self.inject_host, self.inject_port), color='[R1]')

class domain_fronting(threading.Thread):
    def __init__(self, socket_client, frontend_domains):
        super(domain_fronting, self).__init__()

        self.frontend_domains = frontend_domains
        self.socket_tunnel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_client = socket_client
        self.buffer_size = 1028
        self.daemon = True

    def log(self, value, status='\xe1\x8f\x92\xe1\x8f\x8b\xe1\x8f\x97\xe1\x8e\xb4\xe1\x8e\xa5\xe1\x8f\x81\xe1\x8e\xb6\x20\xe1\x8f\x95\xe1\x8f\x8b\xe1\x8f\x92\xe1\x8f\x89\xe1\x8f\x8b\xe1\x8f\x92\x2e\x2e\x2e...', color='[Y1]'):     
    	  log(value, status=status, color=color)
        
    def handler(self, socket_tunnel, socket_client, buffer_size):
        sockets = [socket_tunnel, socket_client]
        timeout = 0
        while True:
            timeout += 1
            socket_io, _, errors = select.select(sockets, [], sockets, 3)
            if errors: break
            if socket_io:
                for sock in socket_io:
                    try:
                        data = sock.recv(buffer_size)
                        if not data: break
                        # SENT -> RECEIVED
                        elif sock is socket_client:
                            socket_tunnel.sendall(data)
                        elif sock is socket_tunnel:
                            socket_client.sendall(data)
                        timeout = 30
                    except: break
            if timeout == 60: break

    def run(self):
        try:
            self.proxy_host_port = random.choice(self.frontend_domains).split('https://ruangguru.com:80')
            self.proxy_host = self.proxy_host_port[0]
            self.proxy_port = self.proxy_host_port[1] if len(self.proxy_host_port) >= 2 and self.proxy_host_port[1] else '8080'
            self.log('[R1]  \xe1\x8f\x82\xe1\x8f\x97\xe1\x8d\x88\xe1\x8f\xa6\xe1\x8f\x8b\xe1\x8e\xb4...!  '.format(self.proxy_host, self.proxy_port))
            self.socket_tunnel.connect((str(self.proxy_host), int(self.proxy_port)))
            self.socket_client.sendall(b'HTTP/1.1 200 OK\r\n\r\n')
            self.handler(self.socket_tunnel, self.socket_client, self.buffer_size)
            self.socket_client.close()
            self.socket_tunnel.close()
            self.log('[G1]\xe1\x8f\x95\xe1\x8f\xac\xe1\x8d\x88\xe1\x8d\x88\xe1\x8f\x8b\xe1\x8f\x95\xe1\x8f\x95\x2e\x2e\x2e\xf0\x9f\x91\x8d   ','[R1]'.format(self.proxy_host, self.proxy_port), color='[CC]')
        except OSError:
            self.log('Connection Error', color='[CC]')
        except TimeoutError:
            self.log('{} Not Responding'.format(self.proxy_host), color='[R1]')
            


def main():
    print(colors('\n'.join([
	'Putra Alvians Wuzz Here!!\nInjection Started\n\n'
    ])))   
    inject('127.0.0.1','8989').start()
  
if __name__ == '__main__':
    main()