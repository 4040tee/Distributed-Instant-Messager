
from concurrent import futures
import grpc
import chatRPC_pb2
import chatRPC_pb2_grpc
import json
import os
import socket
import sys
import threading
import mysql.connector as db
from datetime import datetime
from confluent_kafka import Consumer, Producer

consumer_conf = {
	'bootstrap.servers': 'broker:9092',
	'group.id': os.getenv("HOSTNAME")
}

producer_conf = {
    'bootstrap.servers': 'broker:9092',
    'client.id': socket.gethostname(),
}

class ChatAppManager(chatRPC_pb2_grpc.ChatServiceServicer):

    def __init__(self):
        self.chats = []
        self.consumer = Consumer(consumer_conf)
        self.producer = Producer(producer_conf)
        self.missed = 0
        consume_loop = threading.Thread(target=self.consumer_loop)
        consume_loop.start()
    
    def consumer_loop(self):
        self.consumer.subscribe(['messages'])
        while True:
            msg = self.consumer.poll(timeout=1.0)
            try:
                message = json.loads(msg.value())
            except:
                continue
            self.message_receiver(message["sender"], message["message"], message["date"], message["receiver_id"], message["channel"] is not 'no-channel', message["channel"])

    def message_receiver(self, message_sender, message_text, message_date, message_receiver_id, message_from_channel=False, message_channel_name=None):
        if message_from_channel:
            self.chats.append(chatRPC_pb2.MessageResponse(sender=message_sender, text=message_text, date=message_date, receiver_id=message_receiver_id, channel_name=message_channel_name))
        else:
            self.chats.append(chatRPC_pb2.MessageResponse(sender=message_sender, text=message_text, date=message_date, receiver_id=message_receiver_id))

    def get_db(self):
        # Open connection to DB and return cursor
        conn = db.connect(host='chat-app-db', port=3306, user='chat-app', password=os.environ.get('MYSQL_PASSWORD'), database='ChatApp')
        cur = conn.cursor(buffered=True)
        return conn, cur
    
    def get_missed_messages(self, user_id, cur, conn):
        # Upon login, retrieve missed messages
        data = {
            'id': user_id
        }
        query = 'SELECT message, from_user, sender_name, datetime, channel_name FROM Missed WHERE user_id=%(id)s;'
        cur.execute(query, data)
        results = cur.fetchall()
        self.missed = len(results)
        for (text, from_user, sender, date, channel_name) in results:
            if from_user == 0:
                self.message_receiver(message_sender=sender, message_text=text, message_date=date.strftime('%m/%d/%Y'), message_receiver_id=user_id, message_from_channel=True, message_channel_name=channel_name)
            else:
                self.message_receiver(message_sender=sender, message_text=text, message_date=date.strftime('%m/%d/%Y'), message_receiver_id=user_id)
        query = 'DELETE FROM Missed WHERE user_id=%(id)s;'
        cur.execute(query, data)

    def get_user(self, conn, cur, token):
        # Check if access token is valid
        data = {
            'token': token
        }
        query = 'SELECT user_id FROM Online WHERE access_token=%(token)s;'
        cur.execute(query, data)

        # If invalid token then return None and exit
        if cur.rowcount == 0:
            return None

        # If valid token then return User object
        row = cur.fetchone()
        data = {
            'id': row[0]
        }
        query = 'SELECT id, username FROM User WHERE id=%(id)s;'
        cur.execute(query, data)
        return cur.fetchone()

    def is_blocked(self, conn, cur, user_id, recipient_id):
        data = {
            'user_id': user_id,
            'block_id': recipient_id
        }
        query = 'SELECT * FROM Block WHERE user_id=%(user_id)s AND block_id=%(block_id)s;'
        cur.execute(query, data)

        if cur.rowcount == 0:
            data = {
                'user_id': recipient_id,
                'block_id': user_id
            }
            query = 'SELECT * FROM Block WHERE user_id=%(user_id)s AND block_id=%(block_id)s;'
            cur.execute(query, data)

        return cur.rowcount > 0
    
    def block_helper(self, request, block):
        response_message = ''
        conn, cur = self.get_db()
        # Check if logged in
        user = self.get_user(conn, cur, request.access_token)
        if user == None:
            response_message = 'Unauthenticated.'
            status = False
            cur.close()
            conn.close()
            return chatRPC_pb2.Response(text=response_message, status=status)

        # Get user ID if exists
        data = {
            'username': request.blocked_user
        }
        query = 'SELECT id FROM User WHERE username=%(username)s;'
        cur.execute(query, data)
        if cur.rowcount == 0:
            response_message = 'User does not exist.'
            cur.close()
            conn.close()
            status = True
            return chatRPC_pb2.Response(text=response_message, status=status)
        
        # Block/Unblock user
        data = {
            'user_id': user[0],
            'block_id': cur.fetchone()[0]
        }
        if block:
            query = 'INSERT INTO Block (user_id, block_id) VALUES (%(user_id)s, %(block_id)s);'
            response_message = 'User blocked.'
        else:
            query = 'DELETE FROM Block WHERE user_id=%(user_id)s AND block_id=%(block_id)s;'
            response_message = 'User unblocked.'
        cur.execute(query, data)
        conn.commit()

        cur.close()
        conn.close()
        status = True
        return chatRPC_pb2.Response(text=response_message, status=status)
    
    def watch_helper(self, request, watch):
        response_message = ''
        conn, cur = self.get_db()
        # Check if logged in
        user = self.get_user(conn, cur, request.access_token)
        if user == None:
            response_message = 'Unauthenticated.'
            status = False
            cur.close()
            conn.close()
            return chatRPC_pb2.Response(text=response_message, status=status)
        
        # Get Channel ID if exists
        data = {
            'channel': request.channel_name
        }
        query = 'SELECT id FROM Channel WHERE channel_name=%(channel)s;'
        cur.execute(query, data)

        if cur.rowcount == 0:
            response_message = 'Channel does not exist.'
            cur.close()
            conn.close()
            status = True
            return chatRPC_pb2.Response(text=response_message, status=status)
        
        # Watch/Unwatch channel
        data = {
            'user_id': user[0],
            'channel_id': cur.fetchone()[0],
        }
        if watch:
            query = 'INSERT INTO Watching (user_id, channel_id) VALUES (%(user_id)s, %(channel_id)s);'
            response_message = 'Watching channel.'
        else:
            query = 'DELETE FROM Watching WHERE user_id=%(user_id)s AND channel_id=%(channel_id)s;'
            response_message = 'Unwatching channel.'
        cur.execute(query, data)
        conn.commit()

        cur.close()
        conn.close()
        status = True
        return chatRPC_pb2.Response(text=response_message, status=status)

    def MessageStream(self, request_iterator, ctx):
        conn, cur = self.get_db()
        user = self.get_user(conn, cur, request_iterator.access_token)
        last_index = len(self.chats)-1
        while True:
            while len(self.chats) > last_index+1:
                last_index += 1
                if self.chats[last_index].receiver_id == user[0]:
                    message = self.chats[last_index]
                    yield message

    def RegisterUser(self, request, ctx):
        print('registering')
        conn, cur = self.get_db()

        data = {
            'username': request.username,
            'password': request.password
        }
        query = 'INSERT INTO User (username, password) VALUES (%(username)s, %(password)s);'

        # Create User, if user exists then fail
        try:
            cur.execute(query, data)
            conn.commit()
        except:
            response_message = 'User already exists.'
            status = False
            cur.close()
            conn.close()
            return chatRPC_pb2.Response(text=response_message, status=status)
        
        response_message = 'Account successfully registered.'
        status = True
        cur.close()
        conn.close()

        return chatRPC_pb2.Response(text=response_message, status=status)

    def Login(self, request, ctx):
        conn, cur = self.get_db()

        # Confirm user exists
        data = {
            'username': request.username,
            'password': request.password
        }
        query = 'SELECT id FROM User WHERE username=%(username)s AND password=%(password)s;'
        cur.execute(query, data)
        
        if cur.rowcount == 0:
            response_message = 'Incorrect login info.'
            status = False
            cur.close()
            conn.close()
            return chatRPC_pb2.Response(text=response_message, status=status)

        # Check if user has access token (did not log out)
        data = {
            'id': cur.fetchone()[0]
        }
        query = 'SELECT user_id, access_token FROM Online WHERE user_id=%(id)s;'
        cur.execute(query, data)

        # If access token exists then return it
        if cur.rowcount > 0:
            response_message = cur.fetchone()[1]
            status = True
            self.get_missed_messages(data['id'], cur, conn)
            cur.close()
            conn.close()
            return chatRPC_pb2.Response(text=response_message, status=status)
        
        # If new login, create token and return to user
        data['token'] = str(hash(request.username + request.password) % (10 ** 20))
        query = 'INSERT INTO Online (user_id, access_token) VALUES(%(id)s, %(token)s);'
        cur.execute(query, data)
        conn.commit()

        access_token = data['token']
        status = True
        self.get_missed_messages(data['id'], cur, conn) # Get missed messages
        cur.close()
        conn.close()
        return chatRPC_pb2.Response(text=access_token, status=status)
    
    def Logout(self, request, ctx):
        conn, cur = self.get_db()

        # Remove user from Online sessions
        data = {
            'token': request.access_token
        }
        query = 'DELETE FROM Online WHERE access_token=%(token)s;'
        cur.execute(query, data)
        conn.commit()

        response_message = 'User logged out.'
        status = True
        cur.close()
        conn.close()
        return chatRPC_pb2.Response(text=response_message, status=status)

    def DirectMessage(self, request, ctx):
        conn, cur = self.get_db()
        # Check if logged in
        user = self.get_user(conn, cur, request.access_token)
        if user == None:
            response_message = 'Unauthenticated.'
            status = False
            cur.close()
            conn.close()
            return chatRPC_pb2.Response(text=response_message, status=status)

        # Get recipient user ID if exists
        data = {
            'recipient': request.recipient
        }
        query = 'SELECT id FROM User WHERE username=%(recipient)s;'
        cur.execute(query, data)

        if cur.rowcount == 0:
            response_message = 'Recipient does not exist.'
            status = False
            cur.close()
            conn.close()
            return chatRPC_pb2.Response(text=response_message, status=status)
        
        recipient_id = cur.fetchone()[0]
        if self.is_blocked(conn, cur, user[0], recipient_id):
            response_message = 'User is blocked.'
            status = False
            cur.close()
            conn.close()
            return chatRPC_pb2.Response(text=response_message, status=status)
        data = {
            'id': recipient_id
        }
        query = 'SELECT user_id FROM Online WHERE user_id=%(id)s;'
        cur.execute(query, data)

        # If user is offline then save message to send later, else send it
        if cur.rowcount == 0:
            data = {
                'id': recipient_id,
                'message': request.message,
                'from_user': user[0],
                'sender': user[1],
                'datetime': datetime.now().date()
            }
            query = 'INSERT INTO Missed (user_id, message, from_user, sender_name, datetime) VALUES (%(id)s, %(message)s, %(from_user)s, %(sender)s, %(datetime)s);'
            cur.execute(query, data)
            conn.commit()
            response_message = 'User offline, message stored.'
        else:
            response_message = 'User online, message sent.'
            self.producer.produce('messages', value=json.dumps({
                'sender': user[1],
                'message': request.message,
                'receiver_id': recipient_id,
                'date': str(int(datetime.now().timestamp())),
                'channel': 'no-channel'
            }))
            self.producer.flush()
        
        cur.close()
        conn.close()
        status = True
        return chatRPC_pb2.Response(text=response_message, status=status)    
    
    def ChannelPost(self, request, ctx):
        conn, cur = self.get_db()
        # Check if logged in
        user = self.get_user(conn, cur, request.access_token)
        if user == None:
            response_message = 'Unauthenticated.'
            status = False
            cur.close()
            conn.close()
            return chatRPC_pb2.Response(text=response_message, status=status)
        
        # If channel exists then get channel ID
        data = {
            'channel': request.channel_name
        }
        query = 'SELECT id FROM Channel WHERE channel_name=%(channel)s;'
        cur.execute(query, data)

        if cur.rowcount == 0:
            response_message = 'Channel ' + request.channel_name + ' does not exist.'
            cur.close()
            conn.close()
            status = True
            return chatRPC_pb2.Response(text=response_message, status=status)
        
        # Get list of users in channel
        data = {
            'id': cur.fetchone()[0]
        }
        query = 'SELECT user_id FROM Watching WHERE channel_id=%(id)s;'
        cur.execute(query, data)
        
        recipient_list = cur.fetchall()
        online_list = []

        # Get list of online users
        for recipient in recipient_list:
            data = {
                'id': recipient[0]
            }
            query = 'SELECT * FROM Online WHERE user_id=%(id)s;'
            cur.execute(query, data)

            if cur.rowcount > 0:
                online_list.append(recipient)

        # Get list of offline users
        offline_list = list(set(recipient_list) - set(online_list))

        # Send messages to online users
        for recipient in online_list:
            if self.is_blocked(conn, cur, user[0], recipient[0]):
                continue
            self.producer.produce('messages', value=json.dumps({
                'sender': user[1],
                'message': request.message,
                'receiver_id': recipient[0],
                'date': str(int(datetime.now().timestamp())),
                'channel': request.channel_name
            }))
        self.producer.flush()
        
        # Store messages for offline users
        for recipient in offline_list:
            if self.is_blocked(conn, cur, user[0], recipient[0]):
                continue
            data = {
                'id': recipient[0],
                'message': request.message,
                'from_user': 0,
                'sender': user[1],
                'datetime': datetime.now().date(),
                'channel_name': request.channel_name
            }
            query = 'INSERT INTO Missed (user_id, message, from_user, sender_name, datetime, channel_name) VALUES (%(id)s, %(message)s, %(from_user)s, %(sender)s, %(datetime)s, %(channel_name)s);'
            cur.execute(query, data)
            conn.commit()
        
        response_message = 'Message sent to channel.'
        cur.close()
        conn.close()
        status = True
        return chatRPC_pb2.Response(text=response_message, status=status)

    def Block(self, request, ctx):
        return self.block_helper(request, True)

    def Unblock(self, request, ctx):
        return self.block_helper(request, False)

    def Watch(self, request, ctx):
        return self.watch_helper(request, True)

    def Unwatch(self, request, ctx):
        return self.watch_helper(request, False)

def server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chatRPC_pb2_grpc.add_ChatServiceServicer_to_server(ChatAppManager(), server)
    server.add_insecure_port('[::]:3001')
    server.start()
    server.wait_for_termination()

server()