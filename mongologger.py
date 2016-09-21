#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import datetime as dt
import optparse, magic, gzip

def parse_args():
    """Parse  args"""
    usage = """uso: %prog [options] file
Carrega informações dos arquivos de log e insere no mongoDB.
Se o arquivo for comprimido com gzip, implica em --whole."""

    parser = optparse.OptionParser(usage)

    parser.add_option('-w','--whole',action="store_true",dest="filepart",default=False,
        help="Coleta todo o arquivo exceto a hora anterior.")

    options, args = parser.parse_args()

    if len(args) != 1:
        parser.error("Deve ser informado exatamente um arquivo.")

    arq = args[0]

    return options,arq

def getvalues(line):
    """Extract values as a dictionary fom logfiles."""
    chav = [ 'mes', 'dia', 'hora', 'endereco', 'metodo', 'url' ]
    if "web-proxy,account" in line:
        (mes, dia, hora, ippublico, _, _, endereco, metodo, url) = line.split()[0:9]
    elif "firewall,info" in line:
        (mes, dia, hora, ippublico, _, _, protocolo, _, _, _, _, macorg, _, _, _, operacao ) = line.split()[0:16]
        url = operacao.split(">")[1].split(":")[0]
        endereco = operacao.split(":")[0]
        metodo = protocolo
    else:
        print("Failed: {}".format(line))
        return None
    return {'mes': mes, 'dia': dia, 'hora': hora, 'ip_rt': ippublico, 'cliente': endereco, 'metodo': metodo, 'url': url}

if __name__ == "__main__": 
    options, arq = parse_args()

    dtlimit = dt.datetime.now()
    dtlog = dtlimit - dt.timedelta(hours=1)
    if 'gzip' in magic.detect_from_filename(arq).mime_type:
        with gzip.open(arq,'r') as logfile:
            lfile = logfile.readlines()
    else:
        with open(arq,'r') as logfile:
            lfile = logfile.readlines() if options.filepart == True else [line for line in logfile.readlines() if line.startswith(dtlog.strftime("%b %d %H:"))]
    lines = []
    for line in lfile:
        if "wigong.com.br/" in line:
            continue
        elif line.startswith(dtlimit.strftime("%b %d %H:")):
            break
        else:
            result = getvalues(line)
            if result is not None: 
                lines.append(result)

    print(lines)
    #from pymongo import MongoClient
    #client = MongoClient()
    #db = client.wigong_log

    #table = arq.split(".")[0]
    #result = db[table].insert_many(lines)
    #print(result)
