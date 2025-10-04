import os

try:
    from twilio.rest import Client
except ImportError:
    Client = None


class SMSNotifier:
    def __init__(self):
        # Correctly read environment variables by NAME
        self.sid = os.getenv("AC85a586e193735e8bb20b4771bc3dee3e")
        self.auth = os.getenv("d80f11820f7cb297f543ed669cdc04ef")
        self.from_number = os.getenv("+97466187079")

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
