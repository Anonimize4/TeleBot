import asyncio
import os
from KrisBot import search_username, user_data, save_user_data

class MockMessage:
    def __init__(self, text=""):
        self.text = text
    async def reply_text(self, txt):
        print("BOT reply_text:", txt)

class MockUser:
    def __init__(self, user_id, name="LocalTest"):
        self.id = user_id
        self.first_name = name
    def mention_html(self):
        return f"<a href=\"tg://user?id={self.id}\">{self.first_name}</a>"

class MockUpdate:
    def __init__(self, user_id):
        self.effective_user = MockUser(user_id)
        self.message = MockMessage()

class MockContext:
    def __init__(self, args):
        self.args = args

async def run_test():
    # Tune probe settings to keep runtime small
    os.environ.setdefault('PROBE_MAX_LEN', '1')
    os.environ.setdefault('PROBE_CONCURRENCY', '3')
    os.environ.setdefault('PROBE_CANDIDATE_LIMIT', '50')

    upd = MockUpdate(99999)
    ctx = MockContext(['@test*'])
    await search_username(upd, ctx)

if __name__ == '__main__':
    asyncio.run(run_test())
