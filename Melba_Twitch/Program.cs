using System.Text;
using System.Net.WebSockets;
using TwitchLib.Client;
using TwitchLib.Client.Events;
using TwitchLib.Client.Models;
using TwitchLib.Communication.Clients;
using TwitchLib.Communication.Models;
using TwitchLib.PubSub;
using TwitchLib.PubSub.Events;

namespace Melba_Twitch
{
    internal class Program
    {
        static void Main(string[] args)
        {

            Bot bot = new Bot();
            Console.ReadKey();
        }
    }

    class Bot
    {

        const string channel_name = "";
        const string oauth_token = "";
        const string channel_id = "";
        
        List<string> messages = new List<string>();
        List<string> Special_messages = new List<string>();
        int maxline_count = 7; //Changable

        
        bool read_sp = false; //Read speical messages(follows, subs and bits).
        bool normal_messsage = false; //Just for checking and not spamming the backend.
        bool read_all_chat = false; //Allow Melba to read every message or not.

        TwitchClient client;
        TwitchPubSub pubsub_client;
        public Bot()
        {
            ConnectionCredentials credentials = new ConnectionCredentials(channel_name, oauth_token);
            var clientOptions = new ClientOptions
            {
                MessagesAllowedInPeriod = 750,
                ThrottlingPeriod = TimeSpan.FromSeconds(30)
            };
            WebSocketClient customClient = new WebSocketClient(clientOptions);
            client = new TwitchClient(customClient);
            client.Initialize(credentials, channel_name);

            pubsub_client = new TwitchPubSub();

            //Connections.
            pubsub_client.OnListenResponse += onListenResponse;
            pubsub_client.OnPubSubServiceConnected += onPubsubServiceConnected;
            client.OnJoinedChannel += Client_OnJoinedChannel;
            client.OnConnected += Client_OnConnected;

            //Senders
            client.OnMessageReceived += Client_MessageReciver;
            client.OnNewSubscriber += Client_OnNewSubscriber;
            client.OnRaidNotification += Client_Raided;
            pubsub_client.OnFollow += pubsub_Follow;

            pubsub_client.ListenToFollows(channel_id);
            pubsub_client.ListenToRaid(channel_id);

            pubsub_client.Connect();
            client.Connect();
        }

        #region Connections
        private void Client_OnConnected(object sender, OnConnectedArgs e)
        {
            Console.WriteLine($"Connected to channel");
        }

        private void Client_OnJoinedChannel(object sender, OnJoinedChannelArgs e)
        {
            Console.WriteLine("[MELBA HAS STARTED]");
        }

        private void onListenResponse(object sender, OnListenResponseArgs e)
        {
            if (!e.Successful)
                throw new Exception($"Failed to listen! Response: {e.Response}");
        }

        private void onPubsubServiceConnected(object sender, EventArgs e)
        {
            pubsub_client.SendTopics(oauth_token);
        }
        #endregion

        #region Subs
        //Im waiting for this function to get called.
        void pubsub_Follow(object sender, OnFollowArgs e)
        {
            string follow_msg = $"{e.Username} has followed. Thank the user melba \n \n";

            //Console.WriteLine($"{e.Username} has followed. Thank the user melba \n \n");

            Special_messages.Add(follow_msg);
            read_chat(Special_messages[0], 1000, 0);
        }

        void Client_MessageReciver(object sender, OnMessageReceivedArgs e)
        {

            //Console.Write($"{e.ChatMessage.Username}: {e.ChatMessage.Message} \n \n");
            if (read_all_chat)
            {
                string chatmesssage = $"{e.ChatMessage.Username}: {e.ChatMessage.Message}";
                read_chat(chatmesssage,1000,0);
            }
            else
            {
                Add_message($"{e.ChatMessage.Username}: {e.ChatMessage.Message}");
            }
        }

        void Client_Raided(object sender,OnRaidNotificationArgs e)
        {
            Console.Write($"We got raided by {e.Channel} \n \n");
        }

        private void Client_OnNewSubscriber(object sender, OnNewSubscriberArgs e)
        {
            //Send it using websockets
            Console.Write($"NEW SUB!!! {e.Subscriber.DisplayName} \n \n");
        }

        #endregion

        void Add_message(string text)
        {

            if (messages.Count < maxline_count)
            {
                //add the message
                messages.Add(text);
            }
            else
            {
                //Replace the first message
                messages.Remove(messages.First().ToString());
                messages.Add(text);
            }

            Random rand = new Random();
            int rand_msg = rand.Next(0,messages.Count);
            normal_messsage = true;

            read_chat(messages[rand_msg],1000,rand_msg);
        }

        async void read_chat(string final_msg, int delay,int randomnum)
        {

            using (ClientWebSocket client = new ClientWebSocket())
            {
                Uri serviceUri = new Uri("URI");
                var cTs = new CancellationTokenSource();
                try
                {
                    await client.ConnectAsync(serviceUri, cTs.Token);
                    while (client.State == WebSocketState.Open)
                    {
                        ArraySegment<byte> byteToSend = new ArraySegment<byte>(Encoding.UTF8.GetBytes(final_msg));
                        await client.SendAsync(byteToSend, WebSocketMessageType.Text, true, cTs.Token);
                        var responseBuffer = new byte[1024];
                        var offset = 0;
                        var packet = 1024;
                        while (true)
                        {
                            ArraySegment<byte> byteRecived = new ArraySegment<byte>(responseBuffer, offset, packet);
                            WebSocketReceiveResult responce = await client.ReceiveAsync(byteRecived, cTs.Token);
                            var responceMessage = Encoding.Unicode.GetString(responseBuffer, offset, responce.Count);
                            Console.WriteLine(responceMessage);
                            await client.CloseAsync(WebSocketCloseStatus.Empty, null, cTs.Token);
                            if (responce.EndOfMessage)
                                break;
                        }
                    }
                }
                catch (WebSocketException e)
                {
                    Console.WriteLine(e.Message);
                }

            }

            if (read_sp)
            {
                read_sp = false;
            }

            if (normal_messsage && !read_all_chat)
            {
                messages.Remove(messages[randomnum]);
                normal_messsage = true;
            }

            sp_timer(delay);
            
        }

        async void sp_timer(int time)
        {
            await Task.Delay(time);
            read_sp = true;
        }

    }

}