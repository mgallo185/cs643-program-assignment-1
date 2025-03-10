# Programming Assignment 1: AWS Image Recognition Pipeline

This project is an introduction to developing an AWS Application. Here we made an image recognition system in AWS with 2 EC2 Instances with S3,SQS, and Rekognition. One EC2 Instance detects Cars from a set of Images from a S3 Bucket (EC2 A) . Another EC2 Instance detects text from that same set of images from the same S3 Bucket (EC2 B). EC2 A stores indees of the images with cars in them and sends them in an SQS Queue. EC2 B Retrieves the indexes of images and then will make a text file that features the indexes of images that contain cars and text and prints the actual text from these images. The figure below describes the system:

![fig1](https://github.com/user-attachments/assets/169563fd-f49c-4810-b3ad-c3393cffbdb1)

Your have to create 2 EC2 instances (EC2 A and B in the figure), with Amazon Linux AMI, that will work in parallel. Each instance will run a Java or any other programming language application. Instance A will read 10 images from an S3 bucket that we created (https://njit-cs-643.s3.us-east-1.amazonaws.com) and perform object detection in the images. When a car is detected using Rekognition, with confidence higher than 90%, the index of that image (e.g., 2.jpg) is stored in SQS. Instance B reads indexes of images from SQS as soon as these indexes become available in the queue, and performs text recognition on these images (i.e., downloads them from S3 one by one and uses Rekognition for text recognition). Note that the two instances work in parallel: for example, instance A is processing image 3, while instance B is processing image 1 that was recognized as a car by instance A. When instance A terminates its image processing, it adds index -1 to the queue to signal to instance B that no more indexes will come. When instance B finishes, it prints to a file, in its associated EBS, the indexes of the images that have both cars and text, and also prints the actual text in each image next to its index


This was programmed in python with the files
   - `car_detection.py` which recognizes cars from the Bucket using Rekognition and sends it to the SQS Queue and contains communication code to services
   - `text_detection.py`  which  retrieves the indexes of images fro SQS and recognizes text from the images

# Setting up EC2 Instances

## Set up on AWS Console
1. Login and go to AWS Academy Learner Lab and click on Start Lab
2. Wait for AWS to load (when the small circle turns green) and click on AWS to access AWS Console
3. On AWS Console search and click on the EC2 service in the All Services Menu
4. On the EC2 Dashboard click Launch Instance
5. Configure Instance Details
   - Name: Give a name to your instance
   - Amazon Machine Image (AMI): Choose Amazon Linux 2 (Free tier)
   - Instance Type: Choose t2.micro (free-tier)
   - Create New Key Pair give it a name and download the .pem file and save it in a safe place on your PC. (you will only need to do this once as you will use the same Key Pair for your other instance)
6. Configure Instance Security Group
   - Create a New Security Group and press the edit button
   - Give your security group a name
   - Allow the Necessary Ports SSH, HTTP, and HTTPS to the Source Type **MY IP**
   - You will only need to do this once, when making your 2nd instance, just use existing security group that you made
7. Use the Default 8GB of storage and click Launch Instance
8. Repeat the steps for the additional EC2 that you need.

## Connecting to your EC2 Instances
1. Navigate in your terminal or Git Bash to where you downloaded the .pem file
2. Connect using SSH:
  - `chmod 400 my-key-pair.pem  # Set correct permissions`
  - `ssh -i my-key-pair.pem ec2-user@your-ec2-public-ip`
  - Replace **your-ec2-public-ip** with the Public IPv4 Address of your EC2 Dashboard
  - Do this for both instances
3. Once connected into the machines, install tools:
    ```bash
    sudo yum update -y
    sudo yum install aws-cli -y
    sudo yum install python3-pip -y
    pip3 install boto3

## Configure AWS Credentials
1. Remove ~/.aws because whenever you will go back to your instance after stopping the Instances, data gets corrupted and you would need to start fresh
2. Configure your AWS with the credenitals in your AWS Acdemy Credentials
3. Edit the credentials file and copy and paste credentials from AWS CLI
4. Test it and you should be able to connect.
5. Do this in both instances
  ```bash
    rm -rf ~/.aws
    aws configure
    nano ~/.aws/credentials
    aws s3 ls s3://njit-cs-643
```
## Stopping Instances
1. To Stop the Instances, you can go to the Instance state for the specific instance and Press Stop Instances
2. End Lab in AWS Academy Learning Lab does stop and turn off the instances automatically.

## Create SQS Queue
1. Go to SQS and click Create queue
2. Set up a Standard queue and give it a name
3. Keep everything else the same and click create and this will give you your queue url


# Setting and Running Python Codes
1. Make a Directory to store codes and go to that Directory
2. Make your python virtual enviroment and activate it 
3. Make your Python File(s)
4.  Run your Python File
5. Access text file
```bash
mkdir Project1
cd Project1
python3 -m venv venv
source venv/bin/activate
nano car_detection.py # Make this only in your Car Detection EC2 Instance
nano text_detection.py # Make this only in your Text Detection EC2 Instance
python car_detection.py
python text_detection.py
cat detected_text_results.txt


