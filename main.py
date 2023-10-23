from twitchio.ext.commands import Bot
from twitchio.ext import pubsub
import random
import time
import datetime
import signal
from asyncio import *

def cllm(str):
    return 'example llm output'

class Melba(Bot):
    DEBUG = True
    KILL = False

    MAX_GAB = 3
    MAX_CHATS = 7
    MELBA_CHANNEL = 'test_dev_69'
    pen = list()
    gab = list()
    chats = list()
    ideas = list()
    marks = list()
    echos = list()
    voices = list()
    speaking = False
    thinking = False
    
    def __init__(self):
        print('[ melba initialize ]')
        super().__init__( \
            token = "", \
            prefix = '-',
            initial_channels = [Melba.MELBA_CHANNEL] \
        )
        self.melba_pubsub = pubsub.PubSubPool(self)

    def should_not_echo():
        return Melba.speaking or Melba.thinking
    
    #Read the chat and get a responce.
    async def read():
        while True:
            if len(Melba.chats) >= 8:
                sleep_max = max(.7, min((len(Melba.chats) - 8), 7))
                await sleep(random.uniform(.4, sleep_max) + (len(Melba.chats)/7))
            else:
                await sleep(.2)
            if Melba.should_not_echo():
                pass
            if len(Melba.chats):
                response, chats = Melba.get_response()
                print('got response:', response)
                Melba.add_echo(chats, response)
    
    #not 100% sure of this function. while waiting for response print echo? then answer?
    async def echo():
        while True:
            print('echo?')
            await sleep(0.2 + (0.2 * min((len(Melba.chats) + len(Melba.echos)), 20)))
            if Melba.should_not_echo():
                pass
            if len(Melba.echos):
                print('do echo')
                e = Melba.echos[0]
                print(e)
                Melba.say_response(e['chats'], e['response'])
                Melba.echos.pop(0)
    
    #Checks if the point redeem is highlight my message
    async def event_pubsub_channel_points(self,event: pubsub.PubSubChannelPointsMessage):
        print("Received channel point redeem checking if highlight message")
        if event.id.tolower() == "highlight my message":
            Melba.chats.append({'name': event.user.name, 'massage' : event.topic})
            print("Sent massage to melba.")
    
    #Prints that melba is online.
    def print_online():
        print('[ melba is online! ]')
    
    
    #TwitchIO function just means when melba is ready
    async def event_ready(self):
        Melba.task_read = create_task(Melba.read())
        Melba.task_echo = create_task(Melba.echo())
        topics = [pubsub.channel_points("")[00000000]]
        await self.melba_pubsub.subscribe_topics(topics=topics)
        await self.start()
        Melba.print_online()
    
    #Adds the current message sent to list and prints the ENTIRE LIST?
    def add_chat(name, message):
        print('add_chat')
        Melba.chats.append({ 'name': name, 'message': message })
        print(Melba.chats)
    
    # Sends to melba that a user has subbed or followed
    def Thank_sub_follow(name,message):
        print(f'sending sub or follow message to melba {name}')
        Melba.chats.append({'name': name,'message': message})
        print(Melba.chats)
    
    def Thank_Cheer(name,message):
        print(f'Send to melba the cheer amount and message')
        Melba.chats.append({'name': name, 'message': message})
        print(Melba.chats)
    
    #add echo just to wait until a response
    def add_echo(chats, response):
        print('add_echo')
        Melba.echos.append({
            'chats': chats, 'response': response,
        })
    
    #TwitchIO function just means get the current chat. with sorting if it's a follow/sub or bit donation
    async def event_message(self, message):
        print('event_message')
        m = message.content
        
        if message.author.name == "streamelements":
            if "following" in m or "subscribed" in m:
                Melba.Thank_sub_follow(m.split(' ',1),m)
                return
                
            if "cheered" in m: 
                m_c = m.split()
                msg_list = []
                i = 5
                for i in range(5,len(m_c)):
                    msg_list.append(m_c[i])
                bit_msg = ' '.join(msg_list)
                Melba.Thank_Cheer(m.split(' ',1),bit_msg)
                return
        
        if len(Melba.chats) > Melba.MAX_CHATS:
            return
        
        if message.author.name != "streamelements":
            Melba.add_chat(message.author.name, m)
    
    #moves the chat and melbas respone to the gab list which I think means answered questions?
    def add_gab(role, content):
        print('add_gab')
        Melba.gab.append({ 'role': role, 'content': content })
    
    #sends the message to the llm and gets a response?
    def do_gab(chat_message):
        print('do_gab')
        Melba.add_gab('chat', chat_message)
        response = cllm(Melba.gab)
        Melba.add_gab('melba', response)
        return response
    
    #prints the chat.
    def print_chat(name, message):
        print(f'{name}: {message}')
    
    #prints melbas responce?
    def print_melba(response):
        print(f'melba: {response}')
    
    #closes the file again? why?
    def write_clear():
        time.sleep(1.5)
        Melba.speaking = False
        open('chatter.txt', 'w').close()
        open('output.txt', 'w').close()
    
    #this is function checks if there is a file? and writes to it
    def write_a(file, text):
        with open(file, 'a', encoding = 'utf-8') as out:
            out.write(text)
            out.close()

    #thiss function also writes the text? why?
    def write_w(file, text):
        with open(file, 'w', encoding = 'utf-8') as out:
            out.write(text)
            out.close()

    #writes the output
    def write_output(text):
        Melba.write_a('output.txt', text)
    
    #removes the chat that she answered
    def forget():
        print('forget')
        if len(Melba.gab) > Melba.MAX_GAB:
            Melba.gab.pop(1)
            Melba.gab.pop(2)
    
    #deletes her memory :despair:
    def pop_memory():
        print('pop_memory')
        Melba.chats.clear()
    
    #writes the logs of melbas response
    def write_log(chats, response):
        print('write_log')
        date = str(datetime.date.today())
        hour = str(datetime.datetime.now().hour).zfill(2)
        log_file = f'log/{date}_{hour}.txt'
        log = f'{chats}\nmelba: {response}\n\n'
        Melba.write_a(log_file, log)

    #I have no clue what this does but I think it works? let's melba think?
    def devise():
        print('devise')
        chats = ''
        if len(Melba.chats):
            action = 'chat'
            for i, chat in enumerate(Melba.chats):
                name = chat['name']
                message = chat['message']
                chats = f'{chats}{name}: {message}\n'
                if i >= Melba.MAX_CHATS:
                    break
        try:
            response = Melba.do_gab(chats)
        except Exception as e:
            if Melba.DEBUG:
                print(e)
        # response = melba_translate(response)
        return response, chats
    
    #get responce from the llm????????
    def get_response():
        print('get_response')
        Melba.thinking = True
        response, chats = Melba.devise()
        Melba.pop_memory()
        Melba.thinking = False
        return response, chats
    
    #Say the responce
    def say_response(messages, response):
        print('say_response')
        for chat in messages.split('\n'):
            if len(chat) < 2:
                break
            if ':' in chat:
                name = chat.split(':')[0]
                message = chat.replace(f'{name}: ', '')
                # message = melba_filter(message)
                Melba.print_chat(name, message)
        Melba.print_melba(response)
        Melba.write_log(messages, response)
        # get and play voice file
        # Melba.get_voice(response)
        Melba.say(response)
        Melba.forget()

    #Requires the tts.
    def say(response):
        print('say')
        Melba.speaking = True
        # voice = Melba.voices[0]
        # play voice file and write contents to screen here (OBS)
        Melba.write_clear()
        Melba.voices.pop(0)

#makes melba POG
def make_melba():
    try:
        melba = Melba()
        create_task(melba.run())
    except Exception as e:
        if Melba.DEBUG:
            print(e)

#something like a update loop
if __name__ == '__main__':
    if not Melba.DEBUG:
        signal.signal(signal.SIGINT, Melba.KILL)
    make_melba()
