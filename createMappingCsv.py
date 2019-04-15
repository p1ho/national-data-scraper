# -*- coding: utf-8 -*-

import os
import time
from settings import tempDictPath, mappingCsvPath, nationalDataUrl
import json
import csv
import requests
import asyncio
import aiohttp

# for printing Simplified Chinese in Git Bash
import sys
sys.stdout.reconfigure(encoding='utf-8')

async def main():
    if os.path.isfile('./resource/mapping.csv'):
        refetch = ''
        while refetch != 'y' and refetch != 'n':
            refetch = input("mapping.csv exists, refetch? (y/n) ").lower()
        await createMappingCsv() if refetch == 'y' else quit()
    else:
        print("mapping.csv not found, refetching...")
        await createMappingCsv()

async def createMappingCsv():
    currentTimeMilisecs = int(round(time.time()))
    tempDictF = open(tempDictPath, 'r', encoding='utf-8-sig')
    tempDict = json.load(tempDictF)
    tempDictF.close()

    with open(mappingCsvPath, 'w', newline='', encoding='utf-8-sig') as csvFile:
        fieldnames = ['id', 'name', 'isParent', 'dbcode', 'pid', '分类']
        writer = csv.DictWriter(csvFile, fieldnames=fieldnames)
        writer.writeheader()

        dbcodes = list(tempDict.keys())

        loop = asyncio.get_event_loop()

        resultStore = {}
        async with aiohttp.ClientSession() as session:

            # first batch fetch and store into resultStore, stored by key, so even
            # if tasks are completed out of order, the result will be the consistent
            
            tasks = [asyncio.create_task(fetchDim(nationalDataUrl, dbcode, session))
                    for dbcode in dbcodes]

            results = await asyncio.gather(*tasks)

            for result in results:
                result_dbcode = list(result.keys())[0]
                resultStore[result_dbcode] = result[result_dbcode]

            # print(json.dumps(resultStore, indent=4))

            # enter into recursive search if returned dimension is a parent



            # second batch fetch and add to each resultstore
            # for dbcode in dbcodes:
            #     for entry in resultStore[dbcode]:
            #         if entry['isParent']:
            #             params['dbcode'] =
            #
            #
            #
            #
            #     writer.writerow({
            #         'id': entry['id'],
            #         'name': entry['name'],
            #         'isParent': entry['isParent'],
            #         'dbcode': entry['dbcode'],
            #         'pid': entry['pid'],
            #         '分类': tempDict[dbcode]
            #     })

        # for key, value in tempDict.items():
        #
        #     params = {
        #         'id': 'zb',
        #         'dbcode': key,
        #         'wdcode': 'zb',
        #         'm': 'getTree',
        #     }
        #     r = requests.get(nationalDataUrl, params=params)
        #     responses = json.loads(r.text)
        #     queue = []
        #     queue.append(responses)
        #     while(len(queue) != 0):
        #         curResponses = queue.pop()
        #         for response in curResponses:
        #             print(response['name'])
        #             writer.writerow({
        #                 'id': response['id'],
        #                 'name': response['name'],
        #                 'isParent': response['isParent'],
        #                 'dbcode': response['dbcode'],
        #                 'pid': response['pid'],
        #                 '分类': value
        #             })
        #             if(response['isParent']):
        #                 payload['id'] = response['id']
        #                 parentResponse = requests.get(nationalDataUrl, params=payload)
        #                 queue.append(json.loads(parentResponse.text))

async def fetchDim(url, dbcode, session):
    params = {
        'id': 'zb',
        'dbcode': dbcode,
        'wdcode': 'zb',
        'm': 'getTree',
    }
    resp = await session.get(url, params=params)
    while resp.status != 200:
        print("fetching {} failed, retrying...".format(dbcode))
        resp = await session.get(url, params=params)
    text = await resp.text()
    print(text)
    return {dbcode: json.loads(text)}

if __name__ == '__main__':
    t1 = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(createMappingCsv())
    t2 = time.time()
    print(str(t2-t1) + ' sec elapsed')


# commented code from before (could be useful later)
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
