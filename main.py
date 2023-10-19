from twitchio.ext import commands, pubsub
import asyncio

user_oauth_token = "oauth:hiwnardtvp6dj4pcjplyids2ue6b7p"

class Bot(commands.Bot):
    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        super().__init__(token=user_oauth_token, prefix="", initial_channels=["riotgames"])

    async def event_ready(self):
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')
    
    #Add Proirity system for each message
    
    #this function prints the chat bot messages.
    async def event_message(self,Message):
        print(f"{Message.author.display_name}: {Message.content}")
        
    #This functions prints bits and their messages
    async def event_pubsub_bits(self,event: pubsub.PubSubBitsMessage):
        print(f"{event.user.name}: {event.message.content}")
    
    #This function checks if the redeem is a highlight one then prints it.
    async def event_pubsub_channel_points(self,event: pubsub.PubSubChannelPointsMessage):
        print(event.reward.prompt)
        if str(event.reward.title).lower == "highlight my message":
            print(f"{event.user.name}: {event.reward.prompt}")
    
    #this function prints out if a user has subbed.
    async def event_usernotice_subscription(self, metadata):
        print(f"{metadata.user.display_name} has subscribed")
    

bot = Bot()
bot.run()