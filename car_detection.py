import boto3
from botocore.exceptions import ClientError

# Set the bucket and queue URLs
BUCKET_NAME = "njit-cs-643"
SQS_QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/205912991141/CarDetectionQueue"
IMAGES=10

def get_images_from_s3(s3):
    """Retrieve image list from S3 bucket"""
    """ using EAFP to try directly getting images from the s3 bucket"""
    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, MaxKeys=IMAGES)
        
        # if no objects in bucket print a statement and return empty list
        if 'Contents' not in response:
            print(f"No objects found in bucket {BUCKET_NAME}")
            return []
        # get image file names filter for different types of formats
        images = [obj['Key'] for obj in response['Contents'] 
                 if obj['Key'].lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        #print statement that we found the number of images in bucket
        print(f"Found {len(images)} images in S3 bucket")
        return images
    
    # catch error if getting images didnt work
    except Exception as e:
        print(f"Error retrieving images from S3: {str(e)}")
        return []

def detect_car_in_image(rekognition_client, image_name):
    """Detect if car is present in image with confidence above threshold"""
    try:
        response = rekognition_client.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': BUCKET_NAME,
                    'Name': image_name
                }
            },
            MaxLabels=10,
            MinConfidence=90 #confidence needs to be 90% as were requirements
        )
        
        # Check if a car is detected, this is done for each image
        for label in response['Labels']:
            if (label['Name'].lower() in ['car', 'automobile', 'vehicle'] and 
                label['Confidence'] >= 90): #using 90% coverage or above
                
                confidence = label['Confidence']
                print(f"Car detected in {image_name} with confidence: {confidence:.2f}%")
                return True, confidence
                
        return False, 0.0
    #Except statement if rekognition fails
    except Exception as e:
        print(f"Error detecting car in {image_name}: {str(e)}")
        return False, 0.0

def send_message_to_sqs(sqs_client, message):
    """Send message to SQS queue with the Queue URL we defined"""
    try:
        response = sqs_client.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=message
        )
        message_id = response['MessageId']
        print(f"Message sent to SQS: {message} (ID: {message_id})")
        return True
    
    except Exception as e:
        print(f"Error sending message to SQS: {str(e)}")
        return False

def main():
    """Main function to coordinate the car detection workflow"""
    try:
        # Initialize AWS clients
        s3 = boto3.client('s3')
        sqs = boto3.client('sqs')
        rekognition = boto3.client('rekognition')
        
        # Get images from S3 
        images = get_images_from_s3(s3)
        if not images:
            print("No images to process. Exiting.")
            return
        
        # Process each image for car detection
        cars_detected = 0
        for image_name in images:
            print(f"Processing image: {image_name}")
            
            # Detect car in image
            car_detected, confidence = detect_car_in_image(rekognition, image_name)
            
            # If car detected add it to the counter and send image name to SQS
            if car_detected:
                send_message_to_sqs(sqs, image_name)
                cars_detected += 1
        
        # Send termination signal sends -1 index when we are done with all of the image processing
        print(f"Finished processing. Detected cars in {cars_detected} images.")
        print("Sending termination signal to SQS")
        send_message_to_sqs(sqs, "-1")
        
        print("Exiting. Done with sending messages")
        
    except Exception as e:
        print(f"Unexpected error in main process: {str(e)}")

#run main
if __name__ == "__main__":
    print("Starting car detection application (EC2 Instance A)")
    main()
