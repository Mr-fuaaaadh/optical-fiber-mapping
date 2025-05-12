import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from office.models import Office
from opticalfiber_app.models import Staff
from .serializers import OfficeSerializer

class MapDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("map_updates", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("map_updates", self.channel_name)

    async def receive(self, text_data):
        try:
            payload = json.loads(text_data)
            user_id = payload.get("user_id")

            if not user_id:
                await self.send(text_data=json.dumps({"error": "user_id is required"}))
                return

            staff = await self.get_staff(user_id)
            if not staff:
                await self.send(text_data=json.dumps({"error": "Staff not found"}))
                return

            company = staff.company
            offices = await self.get_offices(company)

            serializer = OfficeSerializer(offices, many=True)
            await self.send(text_data=json.dumps(serializer.data))

        except Exception as e:
            await self.send(text_data=json.dumps({"error": f"Exception: {str(e)}"}))

    @database_sync_to_async
    def get_staff(self, user_id):
        try:
            return Staff.objects.select_related('company').get(pk=user_id)
        except Staff.DoesNotExist:
            return None

    @database_sync_to_async
    def get_offices(self, company):
        return Office.objects.filter(company=company)
