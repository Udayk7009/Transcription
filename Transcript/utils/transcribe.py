from deepgram import Deepgram
import asyncio
import aiohttp
import numpy as np
import datetime

def task(meetingid,URL,speaker1_id,speaker2_id,DEEPGRAM_API_KEY):
    try:
        # print("Here")
        async def transcribe():

            # Initializes the Deepgram SDK
            deepgram = Deepgram(DEEPGRAM_API_KEY)
            STREAM_KEY=f"Transcription:{meetingid}"
            # Create a websocket connection to Deepgram
            try:
                deepgramLive = await deepgram.transcription.live(
                    { "punctuate": True, "model": "meeting", "language": "en-IN", "tier": "enhanced","diarize": True,"utterances": True }
                )
            except Exception as e:
                print(f'Could not open socket: {e}')
                return

            # Listen for the connection to close
            deepgramLive.registerHandler(deepgramLive.event.CLOSE, lambda _: check_connection())

            def check_connection():
                pass
            # Listen for any transcripts received from Deepgram and write them to the console
            deepgramLive.registerHandler(deepgramLive.event.TRANSCRIPT_RECEIVED, lambda x: capture_json(x))
            print("Here")
            
            def capture_json(x:dict):
                try:
                    words_li=x['channel']['alternatives'][0]['words']
                    CURRENT_TIME_STAMP=datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
                    speaker1_text=""
                    speaker2_text=""
                    unknown_text=""
                    for i in words_li:
                        if i['speaker']==0:
                            speaker1_text+=i['punctuated_word']+" "
                        elif i['speaker']==1:
                            speaker2_text+=i['punctuated_word']+" "
                        else:
                            unknown_text+=i['punctuated_word']+" "                                           
                    string=f'[{CURRENT_TIME_STAMP}]$Speaker[{speaker1_id}]:{speaker1_text}$Speaker[{speaker2_id}]:{speaker2_text}$Speaker[Unknown]:{unknown_text}'
                    e={0:string}
                    if len(speaker1_text)==0 and len(speaker2_text)==0 and len(unknown_text)==0:
                        pass
                    else:
                        #r.xadd(STREAM_KEY,e)    
                        print(e)
                except:
                    pass    
            # Listen for the connection to open and send streaming audio from the URL to Deepgram
            async with aiohttp.ClientSession() as session:
                async with session.get(URL) as audio:
                    while True:
                        data = await audio.content.readany()
                        deepgramLive.send(data)

                        # If no data is being sent from the live stream, then break out of the loop.
                        if not data:
                            break
                        #if session_exit_event.is_set():
                            #break

            # Indicate that we've finished sending data by sending the customary zero-byte message to the Deepgram streaming endpoint, and wait until we get back the final summary metadata object
            await deepgramLive.finish()
    except Exception as e:
        raise e

    asyncio.run(transcribe()) 
