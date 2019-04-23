#!/usr/bin/env python3
import time
import subprocess
import re
import json
import os
import requests
from multiprocessing import Process, Manager


class Vigilante():
    def __init__(self):
        self.dir = os.path.dirname(os.path.abspath(__file__))
        self.filename = os.path.join(self.dir, 'vigilante.json')
        self.read_keys()
        self.local_ip = self.get_local_ip()
        self.manager = Manager()
        if os.path.exists(self.filename):
            self.read()
        else:
            self.ips = []
            self.macs = []
            self.save()

    def get_mac_address(self, ip):
        try:
            proc = subprocess.Popen(['arp', '-n', ip], stdout=subprocess.PIPE)
            out, err = proc.communicate()
            ans = re.search(r'([0-9A-F]{2}[:-]){5}([0-9A-F]{2})', out.decode(), re.I).group()
        except:
            ans = 'Unknown'
        return ans

    def get_local_ip(self):
        proc = subprocess.Popen(['hostname', '-I'], stdout=subprocess.PIPE)
        out, err = proc.communicate()
        return out.decode().split(' ')[0]

    def read_keys(self):
        filename = os.path.join(self.dir, 'keys.json')
        f = open(filename, 'r')
        content = f.read()
        f.close()
        data = json.loads(content)
        self.token = data['token']
        self.channel_id = data['channel_id']

    def send_warning(self, ip, mac):
        message = "New device with IP {0} and MAC {1}".format(ip, mac)
        url = 'https://api.telegram.org/bot{0}/sendMessage'.format(self.token)
        data = {'chat_id': self.channel_id, 'text': message}
        r = requests.post(url, data)

    def read(self):
        f = open(self.filename, 'r')
        content = f.read()
        f.close()
        data = json.loads(content)
        self.macs = data['macs']
        self.ips = data['ips']

    def save(self):
        f = open(self.filename, 'w')
        data = {'macs': self.macs, 'ips': self.ips}
        f.write(json.dumps(data))

    def exists(self, item):
        if item.find(':') > -1:
            return mac in self.macs
        else:
            return ip in self.ips

    def add(self, item):
        if item.find(':') > -1:
            self.macs.append(item)
        else:
            self.ips.append(item)

    def check_host(self, ip):
        ret_code = subprocess.call(['ping', '-c1', '-W20', ip],
                                   stdout=subprocess.PIPE)
        if ret_code == 0:
            self.data[ip] = self.get_mac_address(ip)

    def vigila(self):
        self.data = self.manager.dict()
        jobs = []
        range_ip = '.'.join(self.local_ip.split('.')[:-1])
        for i in range(1, 255):
            ip = '{0}.{1}'.format(range_ip, i)
            if self.local_ip != ip:
                job = Process(target=self.check_host, args=(ip,))
                jobs.append(job)
                job.start()
        for job in jobs:
            job.join()
        for ip in self.data.keys():
            if self.data[ip] == 'Unknown':
                if ip not in self.ips:
                    self.ips.append(ip)
                    self.send_warning(ip, self.data[ip])
            elif self.data[ip] not in self.macs:
                self.macs.append(self.data[ip])
                self.send_warning(ip, self.data[ip])


if __name__ == '__main__':
    start = time.time()
    vigilante = Vigilante()
    vigilante.vigila()
    vigilante.save()
    print('Total time: {0}'.format(time.time() - start))
