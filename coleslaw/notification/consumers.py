from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from system_manage.models import Shop

import json

class OrderConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        try:
            self.shop_id = self.scope['url_route']['kwargs']['shop_id']
            self.group_name = f"shop_order_{self.shop_id}"

            if not await self.check_shop_exists(self.shop_id): # 가맹점체크
                raise ValueError('가맹점이 존재하지 않습니다.')

            # send 등 과 같은 동기적인 함수를 비동기적으로 사용하기 위해서는 async_to_sync 로 감싸줘야함
            # 현재 채널을 그룹에 추가합니다. 
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()
        except ValueError as e: # 값 오류가 있을 경우 연결을 종료합니다.
            await self.close()

    async def disconnect(self, close_code):
        try:  
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
        except Exception as e: # 일반 예외를 처리합니다 (예: 오류 기록).         
            pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type' : 'chat_message',
                'message': message,
            }
        )

    # Receive message from group
    async def chat_message(self, event):
        message = event['message']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
        }))
    
    @database_sync_to_async
    def check_shop_exists(self, shop_id):
        # 주어진 ID로 채팅방이 존재하는지 확인합니다.
        return Shop.objects.filter(id=shop_id).exists()