import boto3
import csv
import configparser

# Function to read AWS credentials from file
def get_aws_credentials(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    return config['default']['aws_access_key_id'], config['default']['aws_secret_access_key']

# Function to list all public IPs in a region for a given account
def list_public_ips(ec2_client, csv_writer):
    # List all Elastic IPs
    eips = ec2_client.describe_addresses().get('Addresses', [])
    for eip in eips:
        csv_writer.writerow([eip.get('PublicIp'), 'Elastic IP', eip.get('InstanceId', 'Unassociated')])

    # List all EC2 instances and their public IPs
    instances = ec2_client.describe_instances().get('Reservations', [])
    for reservation in instances:
        for instance in reservation['Instances']:
            public_ip = instance.get('PublicIpAddress')
            if public_ip:
                csv_writer.writerow([public_ip, 'EC2 Instance', instance['InstanceId']])

# Function to list all public IPs in all AWS regions
def list_all_public_ips_in_all_regions(credentials_file_path, csv_file_path):
    aws_access_key_id, aws_secret_access_key = get_aws_credentials(credentials_file_path)
    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

    ec2_client = session.client('ec2')

    # Get all available AWS regions
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]

    for region in regions:
        ec2_client = session.client('ec2', region_name=region)
        with open(f"{csv_file_path}_{region}.csv", 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Public IP', 'Type', 'Associated Resource'])
            list_public_ips(ec2_client, writer)

# Specify the AWS credentials file path and the CSV file base name
credentials_file_path = '/home/ejev/.aws/credentials'  # Updated to use 'ejev' user
csv_file_path = 'public-ips-list'  # Base name for output CSV files
list_all_public_ips_in_all_regions(credentials_file_path, csv_file_path)
