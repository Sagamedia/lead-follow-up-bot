import os
import requests
from typing import Dict, Any
import openai

class LeadFollowUpBot:
    def __init__(self, 
                 openai_api_key: str, 
                 zapier_webhook_sms: str,
                 zapier_webhook_email: str):
        """
        Initialize the Lead Follow-Up Bot with Zapier webhooks
        """
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        self.zapier_sms_webhook = zapier_webhook_sms
        self.zapier_email_webhook = zapier_webhook_email

    def generate_personalized_message(self, lead_info: Dict[str, Any]) -> str:
        """
        Generate a personalized follow-up message using AI
        """
        prompt = f"""Generate a professional, personalized initial contact message 
        for a potential client with the following details:
        Name: {lead_info.get('name', 'Potential Client')}
        Business Type: {lead_info.get('business_type', 'Not Specified')}
        Source: {lead_info.get('source', 'Unknown')}
        
        The message should:
        - Be warm and engaging
        - Suggest scheduling a consultation
        - Reflect the lead's specific context
        """
        
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional sales assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content

    def send_sms_via_zapier(self, phone_number: str, message: str):
        """
        Send SMS using Zapier webhook
        """
        try:
            response = requests.post(self.zapier_sms_webhook, json={
                'phone_number': phone_number,
                'message': message
            })
            response.raise_for_status()
            print(f"SMS sent successfully to {phone_number}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to send SMS: {e}")

    def send_email_via_zapier(self, email: str, message: str):
        """
        Send email using Zapier webhook
        """
        try:
            response = requests.post(self.zapier_email_webhook, json={
                'to_email': email,
                'subject': 'Quick Follow-Up: Schedule Your Consultation',
                'body': message
            })
            response.raise_for_status()
            print(f"Email sent successfully to {email}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to send email: {e}")

    def send_follow_up(self, lead_info: Dict[str, Any]):
        """
        Send follow-up communication via Zapier
        """
        # Generate personalized message
        message_text = self.generate_personalized_message(lead_info)
        
        # Send SMS if phone number exists
        if lead_info.get('phone'):
            self.send_sms_via_zapier(lead_info['phone'], message_text)
        
        # Send email if email exists
        if lead_info.get('email'):
            self.send_email_via_zapier(lead_info['email'], message_text)

def main():
    # Initialize bot with Zapier webhooks and OpenAI API key
    bot = LeadFollowUpBot(
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        zapier_webhook_sms=os.getenv('ZAPIER_SMS_WEBHOOK'),
        zapier_webhook_email=os.getenv('ZAPIER_EMAIL_WEBHOOK')
    )
    
    # Example lead information
    lead = {
        'name': 'John Doe',
        'phone': '+15551234567',
        'email': 'john.doe@example.com',
        'business_type': 'Software Consulting',
        'source': 'Website Contact Form'
    }
    
    # Send follow-up
    bot.send_follow_up(lead)

if __name__ == "__main__":
    main()
