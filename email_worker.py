import mailbox
from email.header import decode_header
from email import message_from_string

# Function to decode MIME headers
def decode_email_header(header):
    decoded = decode_header(header)
    decoded_str = ''
    for part, encoding in decoded:
        if encoding:
            decoded_str += part.decode(encoding)
        else:
            decoded_str += str(part, 'utf-8') if isinstance(part, bytes) else part
    return decoded_str

# Function to extract the body of the email
def extract_email_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                return part.get_payload(decode=True).decode('utf-8')
    else:
        return msg.get_payload()

# Open the .mbox file
mbox = mailbox.mbox('email_data/Непрочитанные.mbox')

# Iterate through all messages in the .mbox file
for message in mbox:
    subject = decode_email_header(message['subject'])
    sender = decode_email_header(message['from'])
    date = decode_email_header(message['date'])
    
    print(f"Subject: {subject}, Sender: {sender}, Date: {date}")

    # Extract and print the email body
    msg = message_from_string(str(message))
    body = extract_email_body(msg)
    print("Body:", body[:100])  # Displaying only first 100 characters for demonstration
    print('-' * 50)  # Add a separator for readability
