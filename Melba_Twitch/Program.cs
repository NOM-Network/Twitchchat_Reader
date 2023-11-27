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
        List<string> messages = new List<string>();
        List<string> Special_messages = new List<string>();
        int maxline_count = 7; //Changable

        bool read_sp = false;

        TwitchClient client;
        TwitchPubSub pubsub_client;
        public Bot()
        {
            ConnectionCredentials credentials = new ConnectionCredentials("", "");
            var clientOptions = new ClientOptions
            {
                MessagesAllowedInPeriod = 750,
                ThrottlingPeriod = TimeSpan.FromSeconds(30)
            };
            WebSocketClient customClient = new WebSocketClient(clientOptions);
            client = new TwitchClient(customClient);
            client.Initialize(credentials, "");

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

            pubsub_client.ListenToFollows("");
            pubsub_client.ListenToRaid("");

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
            pubsub_client.SendTopics("");
        }
        #endregion

        #region Subs
        //Im waiting for this function to get called.
        void pubsub_Follow(object sender, OnFollowArgs e)
        {
            string follow_msg = $"{e.Username} has followed. Thank the user melba \n \n";

            //Console.WriteLine($"{e.Username} has followed. Thank the user melba \n \n");

            Special_messages.Add(follow_msg);
        }

        void Client_MessageReciver(object sender, OnMessageReceivedArgs e)
        {
            //Console.Write($"{e.ChatMessage.Username}: {e.ChatMessage.Message} \n \n");
            Add_message($"{e.ChatMessage.Username}: {e.ChatMessage.Message}");
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

        async void Add_message(string text)
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

            read_chat();
        }

        //TODO: clean this code. because holy shit it's disgusting.
        async void read_chat()
        {

            if (read_sp)
            {
                if (Special_messages.Count <= 0) 
                {
                    read_sp = false;
                    sp_timer();
                    return;
                }

                using (ClientWebSocket client = new ClientWebSocket())
                {
                    Uri serviceUri = new Uri("URI");
                    var cTs = new CancellationTokenSource();
                    try
                    {
                        await client.ConnectAsync(serviceUri, cTs.Token);
                        string final_msg = Special_messages[0].ToString();
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

                Special_messages.RemoveAt(0);
                read_sp = false;

                //Create a cooldown.
                sp_timer();
            }
            else
            {
                Random random = new Random();
                int rand_msg = random.Next(0, messages.Count);

                //Console.WriteLine(messages[rand_msg]);
                using (ClientWebSocket client = new ClientWebSocket())
                {
                    Uri serviceUri = new Uri("URI");
                    var cTs = new CancellationTokenSource();
                    try
                    {
                        await client.ConnectAsync(serviceUri, cTs.Token);
                        string final_msg = messages[rand_msg].ToString();
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
                            break;
                        }
                    }
                    catch (WebSocketException e)
                    {
                        Console.WriteLine(e.Message);
                    }
                }

                messages.Remove(messages[rand_msg]);
            }
        }

        async void sp_timer()
        {
            await Task.Delay(5000);
            read_sp = true;
        }

    }

}