from deepgram import Deepgram
import asyncio
import aiohttp
import time
from flask import Flask,render_template,Response, request, jsonify
import os
import pymongo
from threading import Thread,Event

from utils.transcribe import task

app = Flask(__name__)

@app.route('/Transcription/transcription/<string:meetingid>',methods=["GET","POST"])
def transcription(meetingid):
    try:
        global r
        global session_exit_event
        DEEPGRAM_API_KEY = 'DEEPGRAM KEY'
        URL=request.json.get('meeting_link')
        speaker1_id=request.json.get('Speaker1Id')
        speaker2_id=request.json.get('Speaker2Id')
        
        thread=Thread(target=task,args=(meetingid,URL,speaker1_id,speaker2_id,DEEPGRAM_API_KEY),name=f"Transcription of speakers{[speaker1_id,speaker2_id]}")
        thread.start()   
        print("Here")    
        return 'successfull', 200
    except:
        return 'Unsuccessfull', 400

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=False, port=8027)   