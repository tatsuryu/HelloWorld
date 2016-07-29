#!/usr/bin/env python
# -*- coding: utf-8 -*-
import paramiko, scp
import os.path
import sys

home = os.path.expanduser("~")

def createSSHClient(server, porta=22,user='admin', senha=None, keyfile=home + '/.ssh/id_dsa',tempo=10):
  client = paramiko.SSHClient()
  client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  try:
    if senha:
      client.connect(server, port=porta, username=user, password=senha, timeout=tempo)
    elif keyfile:
      client.connect(server, port=porta, username=user, key_filename=keyfile, timeout=tempo)
  except Exception, e:
    print e
    return None
  return client

def progress(filename, size, sent):
  sys.stdout.write("\rCopying {:30} [ {:10} ] {:>2}% ".format(filename,'#'*int((sent*100)/size/10),int((sent*100)/size)))
  sys.stdout.flush()
  if size == sent: print

def scpFile(client,srcfile,dstfile):
  scpHandler = scp.SCPClient(client.get_transport(), progress=progress)
  try:
    if os.path.exists(srcfile):
      scpHandler.put(srcfile,dstfile,recursive=True)
    elif os.path.exists(dstfile):
      scpHandler.get(srcfile,dstfile,recursive=True)
  except Exception, e:
    print e
    return None
  return True

def add_SSHKey(host,senha='password',tempo=5, keyfile=home + '/.ssh/id_dsa.pub'):
  client = createSSHClient(host,senha=senha,tempo=tempo)
  if client:
    print "Copying key file..."
    scpFile(client,keyfile,'/chave')
    print "Adjusting ssh-key..."
    #Mikrotik?
    stdin, stdout, stderr = client.exec_command('/user ssh-keys import public-key-file=chave user=admin')
    output = stdout.readlines()
    print(''.join(output))
    return client
  else:
    return None
    
if __name__ == "__main__":
  ssh = createSSHClient("127.0.0.1", user="user", senha="password")
  if ssh:
    #res = scpFile(ssh,"teste.tst","/tmp/teste.tst")
    res = scpFile(ssh,"upload","/tmp/teste")
