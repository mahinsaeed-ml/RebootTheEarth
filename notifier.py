import os

try:
    from twilio.rest import Client
except ImportError:
    Client = None

class SMSNotifier:
    def __init__(self):
        self.sid = os.getenv("AC85a586e193735e8bb20b4771bc3dee3e")
        self.auth = os.getenv("3a434ad41b1963c6b2f9dc86200157e2")
        self.from_number = os.getenv("66187079")

        # Only enable Twilio if creds exist
        if self.sid and self.auth and self.from_number and Client:
            self.enabled = True
            self.client = Client(self.sid, self.auth)
        else:
            self.enabled = False
            self.client = None

    def send_sms(self, to_number: str, message: str) -> str:
        if not self.enabled:
            print(f"[MOCK SMS] to {to_number}: {message}")
            return "mock-sid"
        msg = self.client.messages.create(
            body=message,
            from_=self.from_number,
            to=to_number
        )
        return msg.sid
