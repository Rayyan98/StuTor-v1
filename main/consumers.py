# chat/consumers.py
# from .models import Messages
from multiprocessing import Process
from channels.generic.websocket import AsyncWebsocketConsumer
import json

def AddMessage(From , To , message):
#	Messages.objects.create(sendingUser = From, receivingUser = To, message = message)
	pass

class ChatConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		self.room_name = self.scope['url_route']['kwargs']['room_name']
		self.room_group_name = 'chat_%s' % self.room_name
		# Join room group
		await self.channel_layer.group_add(
			self.room_group_name,
			self.channel_name
		)

		await self.accept()

	async def disconnect(self, close_code):
		# Leave room group
		await self.channel_layer.group_discard(
			self.room_group_name,
			self.channel_name
		)
		

    # Receive message from WebSocket
	async def receive(self, text_data):
		text_data_json = json.loads(text_data)
		message = text_data_json['message']
		From = text_data_json['from']
		To = text_data_json['to']
		writeToDb = Process(target= AddMessage, args = (From, To, message))
		writeToDb.start()

		# Send message to room group
		await self.channel_layer.group_send(
			self.room_group_name,
			{
				'type': 'chat_message',
				'message': message,
				'From': From,
			}
		)
		
		

    # Receive message from room group
	async def chat_message(self, event):
		message = event['message']
		From = event['From']
		# Send message to WebSocket
		await self.send(text_data=json.dumps({
			'message': From + ": \t" + message
		}))

