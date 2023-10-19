import twitchio
from twitchio.ext import commands, pubsub, eventsub
import asyncio


user_oauth_token = "oauth:hiwnardtvp6dj4pcjplyids2ue6b7p"
client_secret = "b0tjse2f34u6wezzhxco7z2ozo8d1o"
user_channel_id = "khaleddev_"

esbot = commands.Bot.from_client_credentials(client_id=user_channel_id,client_secret=client_secret)

esclient = eventsub.EventSubClient(esbot,webhook_secret="",callback_route="")

class Bot(commands.Bot):
    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        super().__init__(token=user_oauth_token, prefix="", initial_channels=["khaleddev_"])
        self.pubsub = pubsub.PubSubPool(self)       
    
    async def __ainit__(self) -> None:

        self.loop.create_task(esclient.listen(port=1433))

        try:
            await esclient.subscribe_channel_follows_v2(broadcaster=user_channel_id,moderator=user_channel_id)
        except twitchio.HTTPException:
            pass
    
    async def event_ready(self):
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')
    
    #Add Proirity system for each message
    
    #this function prints the chat bot messages.
    async def event_message(self,Message):
        print(f"{Message.author.display_name}: {Message.content}")
        pass
        
    #This functions prints bits and their messages
    async def event_pubsub_bits(self,event: pubsub.PubSubBitsMessage):
        print(f"{event.user.name}: {event.message.content}")
    
    #This function checks if the redeem is a highlight one then prints it.
    async def event_pubsub_channel_points(self,event: pubsub.PubSubChannelPointsMessage):
        print(event.reward.prompt)
        if str(event.reward.title).lower == "highlight my message":
            print(f"{event.user.name}: {event.reward.prompt}")

bot = Bot()
bot.loop.run_until_complete(bot.__ainit__())

@esbot.event()
async def event_eventsub_notification_followV2(payload: eventsub.ChannelFollowData) -> None:
    print('Received event!')
    channel = bot.get_channel(user_channel_id)
    await channel.send(f'{payload.user.name} followed woohoo!')



bot.run()