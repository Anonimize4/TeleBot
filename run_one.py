import asyncio
from KrisBot import start

class MockMessage:
    async def reply_html(self, t):
        print('REPLY_HTML:', t)

class MockUser:
    def __init__(self):
        self.id = 999
        self.first_name = 'Test'
    def mention_html(self):
        return '<a>Test</a>'

class MockUpdate:
    def __init__(self):
        self.effective_user = MockUser()
        self.message = MockMessage()

async def main():
    upd = MockUpdate()
    await start(upd, None)

asyncio.run(main())
