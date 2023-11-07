from twitchio.ext.commands import Bot
from asyncio import *
import websockets
import time
import random



#create the melba class
class melba(Bot):
    
    MAX_NUM_MSG = 7
    MELBA_TOKEN = ""
    INITIAL_CHANNEL = ""
    MSG_OUTPUT_NAME = "twitchout.txt"
    WEBSOCKET_URI = "localhost"
    
    #Initilization of the bot/connection to the websocket uri and twitch servers
    def __init__(self):
        print("Starting melba")
        super().__init__(token=melba.MELBA_TOKEN, \
                         prefix="", \
                         initial_channels=[melba.INITIAL_CHANNEL]
                        )
        #websockets.connect(melba.WEBSOCKET_URI)
    
    #Connected to both the websocket and twitch server
    async def event_ready(self):
        with open(melba.MSG_OUTPUT_NAME, 'w',encoding= 'utf-8') as r:
            r.close()
        print("[Melba has started!]")
    
    #function sends every twitch message
    async def event_message(self, message) -> None:
        #Get the message
        user_msg = f"{message.author.name}: {message.content} \n"
        
        line_count = 0
        
        #if there are less lines than the max_message delete the first message(oldest) then add the new one
        with open(melba.MSG_OUTPUT_NAME,'r',encoding='utf-8') as r:
            line_count = r.readlines()
        
        if len(line_count) >= melba.MAX_NUM_MSG:
            line_count.pop(0)
            
            new_msg = user_msg
            
            line_count.append(new_msg)
            
            with open(melba.MSG_OUTPUT_NAME,'w',encoding = 'utf-8') as f:
                f.writelines(line_count)
        else:
            with open(melba.MSG_OUTPUT_NAME,'a',encoding = 'utf-8') as f:
                f.write(user_msg)
        #Then check the twitchout.txt and how many lines it is
        
        if len(line_count) == melba.MAX_NUM_MSG:
            melba.choose_random_msg()
        
        
        
    #Will read a random message from the {melba.MSG_OUTPUT_NAME} and send it to the LLM using the websockets
    def choose_random_msg():
        #save the message as a string
        
        #open the twitchout.txt and choose one random message that are in the file
        with open(melba.MSG_OUTPUT_NAME,'r',encoding='utf-8') as r:
            lines = r.readlines()
            random_line = random.randrange(0,len(lines))
            msg = lines[random_line]    
            
        lines.pop(random_line)
        
        lines.append("")
        
        with open(melba.MSG_OUTPUT_NAME,'w',encoding='utf-8') as w:
            w.writelines(lines)
        
        print(msg)   
        
        #TODO: OPEN THE WEBHOOKS ONCE I GET THE BACKEND ON MY PC
        #send the string to websocket
        #websockets.serve(msg)
    
    

bot = melba()
create_task(bot.run())