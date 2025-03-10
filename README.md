# Programming Assignment 1


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


