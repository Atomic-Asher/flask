from flask import Flask, request
from PIL import Image
from pyzbar.pyzbar import decode
import requests
import urllib.parse

app = Flask(__name__)
external_base_url = "https://exciting-worm-64.deno.dev/check/"

@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    # Get the incoming WhatsApp message
    incoming_message = request.json
    
    if 'Body' in incoming_message and incoming_message['Body'].lower() == 'send qr':
        # Send a message to the user requesting the QR code image
        response = {
            "body": "Please send the QR code image.",
            "to": incoming_message["From"]
        }
        return response, 200
    elif 'NumMedia' in incoming_message and incoming_message['NumMedia'] == '1':
        # An image was received
        image_url = incoming_message['MediaUrl0']
        image_response = requests.get(image_url)
        qr_code_image = Image.open(BytesIO(image_response.content))
        decoded_objects = decode(qr_code_image)

        if decoded_objects:
            extracted_url = decoded_objects[0].data.decode('utf-8')
            encoded_url = urllib.parse.quote(extracted_url, safe='')
            external_endpoint = external_base_url + encoded_url
            response_text = f"Extracted link: {extracted_url}\nResponse from external endpoint: {external_endpoint}"
        else:
            response_text = "No QR code found or it couldn't be decoded."

        # Send the response back to the user
        response = {
            "body": response_text,
            "to": incoming_message["From"]
        }
        return response, 200
    else:
        # Handle other message types or commands
        response = {
            "body": "Invalid command. Send 'send qr' to scan a QR code.",
            "to": incoming_message["From"]
        }
        return response, 200

if __name__ == '__main__':
    app.run(debug=True)