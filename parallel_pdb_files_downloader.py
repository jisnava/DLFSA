#Code for downloading pdb files of proteins. 
#The names of proteins must be stored in a file named 'mylist'. Sample protein names are stored in file homosapiens_pdbid

from threading import Thread
import queue
import requests
import gzip
import os
import sys

concurrent = 100
dir_name = os.getcwd()
os.makedirs(os.path.dirname(dir_name+'/PDB/'), exist_ok=True)
dir_name += "/PDB/"

def doWork():
    while True:
        url = q.get()
        Download_PDB(url)
        q.task_done()

def Download_PDB(url):
    try:
        pdb = gzip.decompress(requests.get(url).content)
        with open(dir_name + url[-11:-7] + '.pdb','wb') as myfle:
            myfle.write(pdb)

    except (requests.exceptions.RequestException, OSError):
        with open('errors','a+') as myfle:
            myfle.write(url)

q = queue.Queue(concurrent * 2)
for i in range(concurrent):
    t = Thread(target=doWork)
    t.daemon = True
    t.start()
try:
    for url in open('mylist'):
        q.put('https://files.rcsb.org/download/'+url.strip()+'.pdb.gz')
    q.join()
except KeyboardInterrupt:
    sys.exit(1)
