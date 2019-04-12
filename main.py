# -*- coding: utf-8 -*-

import requests
import json
import time
import os, csv, pandas as pd
from multiprocessing import Pool
import asyncio
import aiofiles
import aiohttp
import concurrent.futures
import threading, urllib3, time
import codecs

# import settings
from settings import *

# for printing Simplified Chinese in Git Bash
import sys
sys.stdout.reconfigure(encoding='utf-8')

chosenResponses = []

def main():
    #createMappingCsv
    #pool = Pool(os.cpu_count())
    content = pd.DataFrame(pd.read_csv("mapping.csv", encoding='utf-8'))
    if content is not None:
        processRows = []
        for rowData in content.values:
            curId = rowData[0]
            isParent = rowData[2]
            dbcode = rowData[3]
            if isParent == False and dbcode == 'hgyd':
                processRows.append(rowData)

        print(len(processRows))
        # threads = [threading.Thread(target=getDetailedResposne, args=(chosenRow,)) for chosenRow in processRows]
        # for thread in threads:
        #     thread.start()
        # for thread in threads:
        #     thread.join()
        # for chosenRow in processRows:
        #      print(count)
        #      chosenResponses.append(getDetailedResposne(chosenRow))
        #      count = count + 1
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            asyncio.gather(
                *(getDetailedResposne(chosenRow) for chosenRow in processRows)
            )
        )
        with open('result.csv', 'w', newline='', encoding='utf-8-sig') as csvFile:
            # fieldnames = ['date', 'dateName','wdname', 'cname', 'value', 'hasdata', 'memo', 'tag', 'unit']
            fieldnames = ['date', 'value', 'wdcode']
            writer = csv.DictWriter(csvFile, fieldnames=fieldnames)
            writer.writeheader()
            for responseJson in chosenResponses:
                returndata = responseJson['returndata']
                datanodes = returndata['datanodes']
                for node in datanodes:
                    data = node['data']
                    wds = node['wds']
                    if data['hasdata']:
                        writer.writerow({
                            'date': wds[1]['valuecode'],
                            'value': data['data'],
                            'wdcode': wds[0]['valuecode'],
                        })



async def getDetailedResposne(chosenRow, retryCount = 1, url=""):
    nationalDataUrl = 'http://data.stats.gov.cn/easyquery.htm'
    convertPayload = ""
    if (len(url) != 0):
        nationalDataUrl = url
    if (retryCount <= 1):
        currentTimeMilisecs = int(round(time.time()))
        detailedPayload = {
            'm': 'QueryData',
            'dbcode': chosenRow[3],
            'rowcode': 'zb',
            'colcode': 'sj',
            'wds': [],
            'dfwds': [
                {
                    'wdcode':'zb',
                    'valuecode': chosenRow[0],
                },
                {
                    'wdcode': 'sj',
                    'valuecode': '1978-2019',
                }

            ],
            'k1': currentTimeMilisecs
        }
        convertPayload = {key:str(value).replace("'",'"') for key,value in detailedPayload.items()}
    custTimeout = aiohttp.ClientTimeout(total=5*60, connect=60, sock_connect=60, sock_read=60)
    async with aiohttp.ClientSession(timeout = custTimeout) as session:
        async with session.get(nationalDataUrl, params=convertPayload, timeout=custTimeout) as resp:
            try:
                # data = await resp.json(content_type=None)
                # chosenResponses.append(data)
                print(resp.status)
            except Exception as e:
                print("RetryCount: " + str(retryCount))
                time.sleep(2*retryCount)
                retryCount = retryCount + 1
                if retryCount <= 10:
                    await getDetailedResposne(chosenRow, retryCount, resp.url)


def createMappingCsv():
    currentTimeMilisecs = int(round(time.time()))
    tempDictF = open(tempDictPath, 'r', encoding='utf-8-sig')
    tempDict = json.load(tempDictF)
    tempDictF.close()

    with open(mappingCsvPath, 'w', newline='', encoding='utf-8-sig') as csvFile:
        fieldnames = ['id', 'name', 'isParent', 'dbcode', 'pid', '分类']
        writer = csv.DictWriter(csvFile, fieldnames=fieldnames)
        writer.writeheader()
        for key, value in tempDict.items():
            payload = {
                'id': 'zb',
                'dbcode': key,
                'wdcode': 'zb',
                'm': 'getTree',
                'k1': currentTimeMilisecs,
            }
            r = requests.get(nationalDataUrl, params=payload)
            responses = json.loads(r.text)
            print("request returned")
            print(responses)
            print('='*20)
            queue = []
            queue.append(responses)
            while(len(queue) != 0):
                curResponses = queue.pop()
                for response in curResponses:
                    print(response['name'])
                    writer.writerow({
                        'id': response['id'],
                        'name': response['name'],
                        'isParent': response['isParent'],
                        'dbcode': response['dbcode'],
                        'pid': response['pid'],
                        '分类': value
                    })
                    if(response['isParent']):
                        payload['id'] = response['id']
                        parentResponse = requests.get(nationalDataUrl, params=payload)
                        queue.append(json.loads(parentResponse.text))


    # detailedPayload = {
    #     'm': 'QueryData',
    #     'dbcode': 'hgyd',
    #     'rowcode': 'zb',
    #     'colcode': 'sj',
    #     'wds': [],
    #     'dfwds': [
    #         {
    #             'wdcode':'zb',
    #             'valuecode': 'A0201',
    #         },
    #         {
    #             'wdcode': 'sj',
    #             'valuecode': '1978-2019',
    #         }

    #     ],
    #     'k1': currentTimeMilisecs
    # }

    # convertPayload = convertParams(detailedPayload)
    # dr = requests.get(nationalDataUrl, params=convertPayload)

if __name__ == '__main__':
    main()

def convertParams(payload):
    return {key:str(value).replace("'",'"') for key,value in payload.items()}

# def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())
# def json2obj(data): return json.loads(data, object_hook=_json_object_hook)

class MappingPayload:
    def __init__(self, payloadId, dbcode, wdcode):
        self.id = payloadId
        self.dbcode = dbcode
        self.wdcode = wdcode
        self.m = 'getTree'
        self.k1 = int(round(time.time()))

class DetailedPayload:
    def __init__(self, dbcode, rowcode, colcode, dfwds, m = 'QueryData', wds = []):
        self.m = m
        self.dbcode = dbcode
        self.rowcode = rowcode
        self.colcode = colcode
        self.wds = wds
        self.dfwds = dfwds
        self.k1 = int(round(time.time()))



class ResponseDimension:
    def __init__(self, dbcode, responseId, isParent, name, pid, wdcode):
        self.dbcode = dbcode
        self.id = responseId
        self.isParent = isParent
        self.name = name
        self.pid = pid
        self.wdcode = wdcode



# class Payload:
#     def __init__(self, *args, **kwargs):
#         return super().__init__(*args, **kwargs)
