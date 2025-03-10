import boto3
import time
import os
from botocore.exceptions import ClientError

#defining bucket name, queue url, waiting time, and the output file
BUCKET_NAME = "njit-cs-643"
SQS_QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/205912991141/CarDetectionQueue"
OUTPUT_FILE = "/home/ec2-user/Project1/detected_text_results.txt"
POLLING_WAIT_TIME = 20


def receive_messages_from_sqs(sqs_client):
    """Receive messages from SQS queue """
    #gets up to 10 messages with a polling wait time
    try:
        response = sqs_client.receive_message(
            QueueUrl=SQS_QUEUE_URL,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=POLLING_WAIT_TIME
        )
        #if no messages are recieved, return empty list
        if 'Messages' not in response:
            return []
        
        return response['Messages']
    
    except Exception as e:
        print(f"Error receiving messages from SQS: {str(e)}")
        return []

def delete_message_from_sqs(sqs_client, receipt_handle):
    """Delete a message from SQS queue"""
    try:
        sqs_client.delete_message(
            QueueUrl=SQS_QUEUE_URL,
            ReceiptHandle=receipt_handle
        )
        return True
    
    except Exception as e:
        print(f"Error deleting message from SQS: {str(e)}")
        return False

def detect_text_in_image(rekognition_client, image_name):
    """Detect text in image using Rekognition"""
    try:
        response = rekognition_client.detect_text(
            Image={
                'S3Object': {
                    'Bucket': BUCKET_NAME,
                    'Name': image_name
                }
            }
        )
        
        # Extract detected line of text
        detected_texts = []
        for text in response['TextDetections']:
            if text['Type'] == 'LINE':  
                detected_texts.append({
                    'text': text['DetectedText'],
                    'confidence': text['Confidence']
                })
        
        return detected_texts
    
    except Exception as e:
        print(f"Error detecting text in {image_name}: {str(e)}")
        return []

def write_results_to_file(results, output_path):
    """Write detection results to output file"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        #write to the file
        with open(output_path, 'w') as file:
            file.write("Images with both cars and text:\n\n")
            
            #if theres nothing, write to the file no images were found with the conditions
            if not results:
                file.write("No images found with both cars and text.\n")
                return
            
            for image_name, texts in results.items():
                # Write the image index/name
                file.write(f"{image_name}: ")
                
                # Write the text detected in the image
                text_list = [f'"{item["text"]}"' for item in texts]
                file.write(", ".join(text_list))
                file.write("\n")
                
        print(f"Results successfully written to {output_path}")
        return True
    
    except Exception as e:
        print(f"Error writing results to file: {str(e)}")
        return False

def main():
    """Main function for text recognition workflow"""
    try:
        print("Initializing text recognition process (EC2 Instance B)")
        
        # Initialize AWS clients
        s3 = boto3.client('s3')
        sqs = boto3.client('sqs')
        rekognition = boto3.client('rekognition')
        # Dictionary to store results
        results = {}
        total_processed = 0
        
        # Continue processing until termination signal
        processing = True
        while processing:
            print("Polling SQS queue for messages...")
            
            # Receive messages from SQS queue
            messages = receive_messages_from_sqs(sqs)
            
            if not messages:
                print("No messages received, continuing to poll...")
                continue
            
            print(f"Received {len(messages)} messages from queue")
            
            for message in messages:
                # Get the image name from the message
                image_name = message['Body']
                receipt_handle = message['ReceiptHandle']
                
                # Delete the message from the queue
                delete_message_from_sqs(sqs, receipt_handle)
                
                # Check for termination signal
                if image_name == "-1":
                    print("Received termination signal (-1), finishing processing")
                    processing = False
                    break
                
                print(f"Processing image for text recognition: {image_name}")
                total_processed += 1
                
                # Process the image for text recognition
                detected_texts = detect_text_in_image(rekognition, image_name)
                
                if detected_texts:
                    text_count = len(detected_texts)
                    print(f"Detected {text_count} text items in image {image_name}")
                    results[image_name] = detected_texts
                else:
                    print(f"No text detected in image {image_name}")
        
        # Write final results to output file
        print(f"Processing complete. Analyzed {total_processed} images with {len(results)} containing text.")
        write_results_to_file(results, OUTPUT_FILE)
        
    except Exception as e:
        print(f"Unexpected error in main process: {str(e)}")

if __name__ == "__main__":
    main()
