import credentials
import imaplib
import email
from email.header import decode_header
import os
from PIL import Image, UnidentifiedImageError
#TODO get this working with antivirus at some point just need to configure clam. maybe rebuild the environment?
#import pyclamd

# Account credentials
username = credentials.username
password = credentials.password

# Connect to the server
mail = imaplib.IMAP4_SSL("outlook.office365.com")

# Login to your account
mail.login(username, password)

# Select the mailbox you want to use
mail.select("inbox")

# Search for unread emails
status, messages = mail.search(None, "UNSEEN")

# Convert messages to a list of email IDs
email_ids = messages[0].split()

# Create a temporary directory to save attachments
temp_dir = "temp_attachments"
os.makedirs(temp_dir, exist_ok=True)

# Initialize ClamAV client
#cd = pyclamd.ClamdAgnostic()

# Iterate through the email IDs
for email_id in email_ids:
    # Fetch the email by ID
    status, msg_data = mail.fetch(email_id, "(RFC822)")

    # Get the email content
    msg = email.message_from_bytes(msg_data[0][1])

    # Decode the email subject
    subject, encoding = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
        # If it's a bytes type, decode to str
        subject = subject.decode(encoding if encoding else "utf-8")

    # Initialize the email body variable
    body = ""

    # If the email message is multipart
    if msg.is_multipart():
        # Iterate over each part
        for part in msg.walk():
            # Extract content type of the email part
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            try:
                # Get the email body
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    body = part.get_payload(decode=True).decode()
                elif content_type == "text/html" and "attachment" not in content_disposition:
                    html_body = part.get_payload(decode=True).decode()
                    # Optionally, you can use an HTML to text converter here
                elif "attachment" in content_disposition:
                    # Check if the part is an image
                    if content_type.startswith("image/"):
                        # Download the image
                        filename = part.get_filename()
                        if filename:
                            filepath = os.path.join(temp_dir, filename)
                            with open(filepath, "wb") as f:
                                f.write(part.get_payload(decode=True))

                            # Check if the file is a valid image
                            try:
                                image = Image.open(filepath)
                                image.verify()  # Verify that it is, in fact, an image
                            except UnidentifiedImageError:
                                print(f"File {filename} is not a valid image.")
                                continue

                            # Scan the image with ClamAV
                            # scan_result = cd.scan_file(filepath)
                            # if scan_result:
                            #     print(f"Warning: {filename} is flagged by ClamAV: {scan_result}")
                            #     os.remove(filepath)
                            #     continue

                            # Display the image
                            image = Image.open(filepath)
                            image.show()

                            # Optionally, delete the image after displaying
                            os.remove(filepath)
            except Exception as e:
                print(f"Error decoding email part: {e}")
    else:
        # If the email message is not multipart
        body = msg.get_payload(decode=True).decode()

    print("Subject:", subject)
    print("Body:", body)
    print("="*50)  # Separator between emails


# Logout and close the connection
mail.logout()
