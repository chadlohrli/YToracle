#!/usr/bin/python

# Usage example:
# python ytoracle --videoId='<youtube video id>' --key='<youtube api key>'

import httplib2
import os
import sys
import json
import base58
import argparse

def postTransaction(address,commentId,user):

    oneSirajcoin = 1e8

    #create transaction
    tx = json.dumps({
    'from':[
        {
            'type':'communityGrowth',
            'amount':12.5*oneSirajcoin,
            'id':user,
            'data:':commentId
        }
    ],

    'to': [
        {
            'address':address,
             'amount':10*oneSirajcoin
        },
        {
            'address':'treasury',
            'amount':1.5*oneSirajcoin
        },
        {
            'address':'siraj',
            'amount':oneSirajcoin
        }
    ]
    })

    #post transaction to signer
    h = httplib2.Http()
    url = "http://localhost:3001/"
    headers = {'content-type':'application/json'}
    resp, content = h.request(url, method="POST", body=tx, headers=headers)

    print(resp)

def processComments(comments):

    addressLength = 33

    #find address based on length of words in comments
    comment = comments["snippet"]["topLevelComment"]["snippet"]["textOriginal"]
    words = comment.split(" ")

    address = ""
    for word in words:
        #check for possible key
        if(len(word) == addressLength):
            try:
                #base58 check for valid address
                base58.b58decode_check(word)
                address = word
                break
            except ValueError:
                print("Invalid key")

    if(address == ""):
        return


    #comment Id
    commentId = comments["id"]

    #author id
    author = comments["snippet"]["topLevelComment"]["snippet"]["authorChannelId"]["value"]
    author = 'youtube:' + author

    postTransaction(address,commentId,author)


def requestComments(videoId, key, pageToken):

    http = httplib2.Http()
    baseurl = 'https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&maxResults=100'

    #check for pageToken
    if(pageToken != ""):
        pageToken = '&pageToken='+ pageToken

    url = baseurl + '&videoId=' + videoId + '&key=' + key + pageToken

    #GET request
    response, content = http.request(url, 'GET')

    #check response
    if(response["status"] != "200"):
        print("Invalid key or videoId")
        sys.exit(0)

    data = json.loads(content)

    #check for morePages
    nextPageToken = ""
    if "nextPageToken" not in data:
        print("no more pages")
    else:
        nextPageToken = data["nextPageToken"]
        print(nextPageToken)

    #return JSON and nextpage is available
    return data,nextPageToken


def getComments(videoId, key):

    nextPageToken = ""

    #cycle through all pages in comments grabbing 100 comments
    while(True):

        data, nextPageToken = requestComments(videoId,key,nextPageToken)

        comments = data["items"]
        print(len(comments))

        for i in xrange(len(comments)):
            #comment = comments[i]["snippet"]["topLevelComment"]["snippet"]["textOriginal"]
            processComments(comments[i])
        if(nextPageToken == ""):
            break

def main():

    parser = argparse.ArgumentParser(description='Youtube Oracle')
    parser.add_argument('--videoId',required=True,help="Required; ID for video for which the comment will be inserted.")
    parser.add_argument('--key',required=True,help="Youtube API key")
    args = parser.parse_args()

    videoId = args.videoId
    apiKey = args.key

    getComments(videoId,apiKey)


if __name__ == '__main__':
    main()
