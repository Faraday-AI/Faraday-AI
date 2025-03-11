from twilio.rest import Client
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get Twilio credentials from environment
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
from_number = os.getenv('TWILIO_FROM_NUMBER')

def test_twilio_connection():
    try:
        # Initialize Twilio client
        client = Client(account_sid, auth_token)
        
        # Send a test message to the provided number
        message = client.messages.create(
            body="Test message from Faraday AI",
            from_=from_number,
            to="+17329770185"  # US country code (+1) added
        )
        
        print(f"Message sent successfully! SID: {message.sid}")
        return True
        
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        return False

if __name__ == "__main__":
    test_twilio_connection() 