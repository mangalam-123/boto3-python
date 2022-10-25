import io

import boto3

import json

from botocore.exceptions import ClientError


AWS_REGION = "us-east-2"

vpc_client = boto3.client("ec2", region_name=AWS_REGION)


def describe_ec2():


    instance_id = ""

    try:
        response = vpc_client.describe_instances()
        instance_id = response["Reservations"][1]["Instances"][0]["InstanceId"]
        print(instance_id)

    except Exception as e:
        print(e)
    else:
        return instance_id

def start_ec2(instance_id):

    try:
        response = vpc_client.start_instances(InstanceIds=[instance_id])
    except Exception as e:
        print(e)
    else:
        return "Started successfully"

def stop_ec2(instance_id):

    try:
        response = vpc_client.stop_instances(InstanceIds=[instance_id])
    except Exception as e:
        print(e)
    else:
        return "Stopping ec2 instance"

def create_keypair():
    key_pair= "python_key"
    private_key = ""
    try:
        response = vpc_client.create_key_pair(KeyName=key_pair)
        private_key = response["KeyMaterial"]

    except Exception as e:
        if str(e).__contains__("already exists"):
            response = vpc_client.describe_key_pairs()
            return 0

    else:
        return private_key


if __name__ == '__main__':

    # instance_id = describe_ec2()
    # start_ec2(instance_id)
    # stop_ec2(instance_id)
    # data = create_keypair()
    # with io.open("python.pem", "w", encoding="utf-8") as file:
    #     file.write(str(data))
    #     file.close()



