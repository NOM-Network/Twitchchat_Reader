import twitchio
from twitchio.ext import commands, eventsub
import asyncio

user_oauth_token = ""
client_secret = ""
user_channel_id = "khaleddev_"


class Bot(commands.Bot):
    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        super().__init__(token=user_oauth_token, prefix="", initial_channels=["khaleddev_"])
        self.esclient = eventsub.EventSubWSClient(self)
       
    async def event_ready(self):
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    #this function prints the chat bot messages.
    async def event_message(self,Message):
        print(f"{Message.author.display_name}: {Message.content}")
    
        
    async def event_eventsub_notification_channel_reward_redeem(self, payload: eventsub.CustomRewardRedemptionAddUpdateData) -> None:
        print('Received event!')
        print(payload.data.id)   

    async def event_eventsub_notification_followV2(self, payload: eventsub.ChannelFollowData) -> None:
        print('Received event!')
        print(f'{payload.data.user.name} followed woohoo!')

    async def event_eventsub_channel_bans(self,payload: eventsub.ChannelBanData) -> None:
        print('Recived Event')
        print(f'{payload.data.user.name} got banned')
    
    async def sub(self):
        await self.esclient.subscribe_channel_points_redeemed(broadcaster=user_channel_id, token=user_oauth_token)
        await self.esclient.subscribe_channel_follows_v2(broadcaster=user_channel_id, moderator=user_channel_id, token=user_oauth_token)
        await self.esclient.subscribe_channel_bans(broadcaster=user_channel_id,token=user_oauth_token)
        
bot = Bot()
bot.loop.create_task(bot.sub())
bot.run()