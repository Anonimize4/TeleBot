import asyncio
import os
import json
from KrisBot import (
    start,
    handle_text,
    handle_email,
    handle_phone,
    add_social_media,
    scrape_tiktok,
    scrape_instagram,
    scrape_facebook,
    help_command,
    USER_DATA_FILE,
    load_user_data,
    save_user_data,
)

class MockMessage:
    def __init__(self, text=""):
        self.text = text
    async def reply_text(self, txt):
        print("BOT reply_text:", txt)
    async def reply_html(self, txt):
        print("BOT reply_html:", txt)

class MockUser:
    def __init__(self, user_id, name="TestUser"):
        self.id = user_id
        self._name = name
    def mention_html(self):
        return f"<a href=\"tg://user?id={self.id}\">{self._name}</a>"

class MockUpdate:
    def __init__(self, user_id, text=""):
        self.effective_user = MockUser(user_id)
        self.message = MockMessage(text)

class MockContext:
    pass

async def run_comprehensive_tests():
    print("=== Comprehensive Testing of KrisBot Functionality ===\n")

    # Test 1: Single User Full Flow
    print("--- Test 1: Single User Full Flow ---")
    user_id = 12345
    ctx = MockContext()

    print("1.1 Sending /start")

    import asyncio
    from KrisBot import (
        start,
        handle_text,
        add_social_media,
        scrape_tiktok,
        scrape_instagram,
        scrape_facebook,
    )


    class MockMessage:
        def __init__(self, text=""):
            self.text = text

        async def reply_text(self, txt):
            print("BOT reply_text:", txt)

        async def reply_html(self, txt):
            print("BOT reply_html:", txt)


    class MockUser:
        def __init__(self, user_id, name="TestUser"):
            self.id = user_id
            self._name = name

        def mention_html(self):
            return f"<a href=\"tg://user?id={self.id}\">{self._name}</a>"


    class MockUpdate:
        def __init__(self, user_id, text=""):
            self.effective_user = MockUser(user_id)
            self.message = MockMessage(text)


    class MockContext:
        pass


    async def run_sequence():
        user_id = 12345
        ctx = MockContext()

        print("--- Sending /start ---")
        upd = MockUpdate(user_id)
        await start(upd, ctx)

        print("--- Sending email text ---")
        upd = MockUpdate(user_id, text="user@example.com")
        await handle_text(upd, ctx)

        print("--- Sending phone text ---")
        upd = MockUpdate(user_id, text="+11234567890")
        await handle_text(upd, ctx)

        print("--- Sending /tiktok command ---")
        upd = MockUpdate(user_id, text="/tiktok")
        await scrape_tiktok(upd, ctx)

        print("--- Adding new platform via /add then name ---")
        upd = MockUpdate(user_id, text="/add")
        await add_social_media(upd, ctx)
        upd = MockUpdate(user_id, text="LinkedIn")
        await handle_text(upd, ctx)

        print("--- List of other commands behavior ---")
        await scrape_instagram(upd, ctx)
        await scrape_facebook(upd, ctx)


    if __name__ == '__main__':
        asyncio.run(run_sequence())
        await add_social_media(upd, ctx)
        upd = MockUpdate(user_id, text="LinkedIn")
        await handle_text(upd, ctx)

        print("--- List of other commands behavior ---")
        await scrape_instagram(upd, ctx)
        await scrape_facebook(upd, ctx)


    if __name__ == '__main__':
        asyncio.run(run_sequence())
