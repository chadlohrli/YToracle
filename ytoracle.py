#!/usr/bin/python

# Usage example:
# python ytoracle --videoId='<youtube video id>' --key='<youtube api key>'

import httplib2
import os
import sys
import json
import base58
import argparse

def postTransaction(address,commentId,username):
       
    #create transaction
    tx = json.dumps({
    'from':[
        {
            'type':'communityGrowth',
            'amount':10*oneSirajcoin,
            'id':username,
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
            'address':'sirajaddress',
            'amount':oneSirajcoin
        }
    ]
    })
    
    # TODO : sign transaction
    
    #post transaction
    h = httplib2.Http()
    url = "http://localhost:3000/txs"
    headers = {'content-type':'application/x-www-form-urlencoded'}
    resp, content = h.request(url, method="POST", body=tx, headers=headers)
    
    print(resp)
                    

def processComments(comments):
    
    addressLength = 33
    
    #find address based on length of words in comments
    comment = comments["snippet"]["topLevelComment"]["snippet"]["textOriginal"]
    words = comment.split(" ")
    for word in words:
        #check for possible key
        if(len(word) == addressLength):
            try:
                #base58 check for valid address
                word = 'b'+word
                base58.b58decode_check(word)
                address = word
                break
            except ValueError:
                print("Invalid key")


    #comment Id
    commentId = comments["id"]
    
    #username
    username = comments["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"]
    username = 'youtube:' + username

    postTransaction(address,commentId,username)
    

def requestComments(videoId, key, pageToken):
    
    http = httplib2.Http()
    baseurl = 'https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&maxResults=100'
    
    #check for pageToken
    if(pageToken != ""):
        pageToken = '&pageToken='+ pageToken
        
    url = baseurl + '&videoId=' + videoId + '&key=' + key + pageToken
    
    #GET request
    response, content = http.request(url, 'GET')
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
    parser.add_argument('--videoId',help="Required; ID for video for which the comment will be inserted.")
    parser.add_argument('--key',help="Youtube API key")
    args = parser.parse_args()
    
    videoId = args.videoid
    key = args.key
   
    #getComments("bqsfkGbBU6k","AIzaSyAKVl2B0vDob_FC34z11TQcg3lGjxYYe70")
    getComments(videoId,key)
    
if __name__ == '__main__':
    main()
    
    