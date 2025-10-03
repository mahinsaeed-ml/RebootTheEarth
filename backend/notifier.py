import os

try:
    from twilio.rest import Client
except ImportError:
    Client = None

class SMSNotifier:
    def __init__(self):
        self.sid = os.getenv("")
        self.auth = os.getenv("")
        self.from_number = os.getenv("")

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
