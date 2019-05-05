# chat/consumers.py
from .models import Messages
from channels.generic.websocket import AsyncWebsocketConsumer
import json


class ChatConsumer(AsyncWebsocketConsumer):


	def New_Message(self, text_data_json):
		message = text_data_json['message']
		From = text_data_json['from']
		To = text_data_json['to']
		m = Messages.CreateNewMessage(From, To, message)
		return self.channel_layer.group_send(
			self.room_group_name,
			{
				'status': m.status,
				'command': 'New_Message',
				'type': 'chat_message',
				'message': message,
				'From': From,
				'To': To,
				'id': m.id,
				'datetime' : str(m.datetime),
			}
		)
		

	def messages_to_json(self, messages):
		r = []
		for o in messages:
			r.append(self.message_to_json(o))
		return r

	def message_to_json(self, message):
		return {
			'From' : message.sendingUser.username,
			'To': message.receivingUser.username,
			'message': message.message,
			'datetime': str(message.datetime),
			'status': message.status,
			'id': message.id,
		}


	def fetch_n_messages(self, text_data_json, n = 20):
		m = Messages.Get_Last_N_Messages(text_data_json['From'], text_data_json['To'] , n)
		m_json = self.messages_to_json(m)
		# print('1')
		return self.channel_layer.group_send(
			self.room_group_name,
			{
				'command':'messages', 'messages': m_json, 'requestuser': text_data_json['requestuser'],
				'type': 'chat_message',
			}
		)
		
	def receiveMessage(self, text_data_json):
		# print('receiveMessage')
		id = text_data_json['id']
		status = text_data_json['status']
		if status == "Pending_View":
			m = Messages.objects.filter(id = id)[0]
			if m is not None and m.status == "Pending_View":
				m.status = "Seen"
				m.save()
		return self.channel_layer.group_send(
			self.room_group_name,
			{
				'command': 'blank',
				'type': 'blank',
			}
		)

	
	def blank(self, event):
		return self.send(text_data=json.dumps({
			'command': event['command'],
		}))
		
	

	commands = {
			'fetch_n_messages': fetch_n_messages,
			'New_Message': New_Message,
			'receiveMessage': receiveMessage,
		}



		
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
		await self.commands[text_data_json['command']](self, text_data_json)

		

    # Receive message from room group
	async def chat_message(self, event):
		if event['command'] == 'New_Message':
			From = event['From']
			To = event['To']
			message = event['message']
			id = event['id']
			datetime = event['datetime']
			status = event['status']
			# Send message to WebSocket
			await self.send(text_data=json.dumps({
				'message': message,
				'From': From,
				'To': To,
				'id': id,
				'command': 'New_Message',
				'datetime': datetime,
				'status': status,
			}))
			
		elif event['command'] == 'messages':
			command = event['command']
			messages = event['messages']
			requestuser = event['requestuser']
			await self.send(text_data=json.dumps({
				'command': command,
				'messages': messages,
				'requestuser': requestuser,
			}))



