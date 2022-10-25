
import boto3

from botocore.exceptions import ClientError

import json

AWS_REGION = "us-east-2"

vpc_resource = boto3.client("ec2", region_name=AWS_REGION)

vpc_client = boto3.client("ec2", region_name=AWS_REGION)

rds_client = boto3.client("rds", region_name=AWS_REGION)



with open('userdata_base64.txt', 'r') as fp:
    USERDATA_B64 = fp.read()

def create_vpc():

    try:

        response = vpc_resource.create_vpc(CidrBlock="10.0.0.0/16",
                                           InstanceTenancy="default",
                                           TagSpecifications=[{
                                               'ResourceType': 'vpc',
                                               'Tags': [{
                                                   'Key': 'Name',
                                                   'Value': 'Demo-vpc'
                                               }]
                                           }])
    except Exception as e:
        print(e)
    else:
        return "vpc created successfully"


def describe_vpc():

    vpc_id = ""
    try:
        response = vpc_client.describe_vpcs()
        for vpc in response["Vpcs"]:
            if vpc["Tags"][0]["Value"].__contains__("Demo-vpc"):
                vpc_id = vpc["VpcId"]
                break;
    except Exception as e:
        print(e)
    else:
        return vpc_id


def modify_vpc_attributes(vpc_id):

    try:
        response = vpc_client.modify_vpc_attribute(EnableDnsHostnames={'Value': True},
                                                   VpcId=vpc_id)
    except Exception as e:
        print(e)
    else:
        return "Succesfully modified vpc"


def create_igw(vpc_id):

    try:
        response = vpc_resource.create_internet_gateway(TagSpecifications=[{
            'ResourceType': 'internet-gateway',
            'Tags':[{
                'Key': 'Name',
                'Value': 'Demo-igw'
            }]
        }])
    except Exception as e:
        print(e)
    else:
         return "successfully created igw"


def describe_igw():

    gateway_id = ""
    try:
        response = vpc_client.describe_internet_gateways()
        for igw in response["InternetGateways"]:
            if igw["Tags"][0]["Value"].__contains__("Demo-igw"):
                gateway_id = igw["InternetGatewayId"]
                break;
    except Exception as e:
        print(e)
    else:
        return gateway_id


def attach_igw(igw_id, vpc_id):

    try:
        response = vpc_client.attach_internet_gateway(VpcId=vpc_id, InternetGatewayId=igw_id)
    except Exception as e:
        print(e)
    else:
        return "successfully attached igw"


def create_subnets(subnet_ids,vpc_id,az):
    subnet_name = ["public-subnet-1", "private-subnet-1", "private-subnet-2"]
    i = 0
    try:
        for subnet in subnet_ids:
            response = vpc_resource.create_subnet(TagSpecifications=[{
                'ResourceType': 'subnet',
                'Tags': [{
                    'Key': 'Name',
                    'Value': subnet_name[i]
                }]
            }],
            VpcId=vpc_id,
            CidrBlock=subnet,
            AvailabilityZone=az[i])
            i = i + 1
    except Exception as e:
        print(e)
    else:
        return "successfully created subnets"

def describe_subnets(vpc_id):

    subnet_ids = []

    try:
        response = vpc_client.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
        for subnet in response["Subnets"]:
            if subnet["Tags"][0]["Value"].__contains__("public") or subnet["Tags"][0]["Value"].__contains__("private"):
                subnet_ids.append(subnet["SubnetId"])

    except Exception as e:
        print(e)
    else:
        return subnet_ids


def modify_subnet_attribute(subnet_ids):

    try:
        response = vpc_client.modify_subnet_attribute(MapPublicIpOnLaunch={'Value': True},
                                                       SubnetId=subnet_ids[0])
    except Exception as e:
        print(e)
    return "Successfully modified subnet"

def create_route_table(vpc_id):

    try:
        response = vpc_resource.create_route_table(TagSpecifications=[{
            'ResourceType': 'route-table',
            'Tags':[{
                'Key': 'Name',
                'Value': 'Demo-pub-rt'
            }]
        }], VpcId=vpc_id)
    except Exception as e:
        print(e)
    else:
        return "Successfully created route-table"

def describe_rt(vpc_id):

    rt_id = ""
    try:
        response = vpc_client.describe_route_tables()
        print(response)
        for rt in response["RouteTables"]:
            if rt["Tags"][0]["Value"].__contains__("Demo-pub-rt"):
                rt_id = rt["RouteTableId"]
                break;
    except Exception as e:
        print(e)
    else:
        return rt_id

def create_route(vpc_id, igw_id, rt_id):

    try:
        response = vpc_client.create_route(DestinationCidrBlock="0.0.0.0/0",
                                           GatewayId=igw_id,
                                           RouteTableId=rt_id)
    except Exception as e:
        print(e)
    else:
        return "Successfully Create route"

def associate_subnet(rt_id, subnet_ids):

    try:
        response = vpc_client.associate_route_table(RouteTableId=rt_id, SubnetId=subnet_ids[0])
    except Exception as e:
        print(e)
    else:
        return "Successfully associated subnet"


def create_sg(vpc_id):
    sg_name = "ec2-demo-securitygrp"
    sg_id = ""
    try:
        response = vpc_client.create_security_group(GroupName=sg_name,
                                                    Description="The sg for my ec2",
                                                    VpcId=vpc_id)
        sg_id = response["GroupId"]
        sg_config = vpc_client.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[{
                'IpProtocol': 'tcp',
                'ToPort': 22,
                'FromPort': 22,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                },
                {
                    'IpProtocol': 'tcp',
                    'ToPort': 80,
                    'FromPort': 80,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                }]
        )
    except Exception as e:
        if str(e).__contains__("already exists"):
            response = vpc_client.describe_security_groups(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]},
                                                                    {'Name': 'group-name', 'Values': [sg_name]}])
            sg_id = response["SecurityGroups"][0]["GroupId"]
            return sg_id

    else:
        return sg_id

def create_ec2(sg_id,subnet_ids):

    try:
        response = vpc_client.run_instances(ImageId="ami-0f924dc71d44d23e2",
                                            InstanceType="t2.micro",
                                            MaxCount=1,
                                            MinCount=1,
                                            KeyName="Terraform-key",
                                            SecurityGroupIds=[sg_id],
                                            SubnetId=subnet_ids[0],
                                            UserData=USERDATA_B64,
                                            TagSpecifications=[{
                                            'ResourceType': 'instance',
                                            'Tags': [{
                                                'Key': 'Name',
                                                'Value': 'Demo-ec2'
                                            }]
        }]
                                    )
    except Exception as e:
        print(e)
    else:
        return "Successfully created ec2"

def create_db_subnet_grp(subnet_ids):

    try:
        response = rds_client.create_db_subnet_group(
            DBSubnetGroupDescription="My-db-prvt-subnets",
            DBSubnetGroupName="rds-db-grp",
            SubnetIds=[
                subnet_ids[1],
                subnet_ids[2]
            ]

        )
    except Exception as e:
        print(e)
    else:
        return "Seccessfully created db-sub-grp"

def db_sg(vpc_id):

    sg_name="db-sg"
    sg_id= ""

    try:
        response = vpc_client.create_security_group(GroupName=sg_name,
                                                    VpcId=vpc_id,
                                                    Description="This is the sg for my db")
        sg_id = response["GroupId"]

        sg_config = vpc_client.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[{
                'IpProtocol': 'tcp',
                'ToPort': 3306,
                'FromPort': 3306,
                'IpRanges':[{'CidrIp': '0.0.0.0/0'}]
            }]
        )
    except Exception as e:
        if str(e).__contains__("already exists"):
            response = vpc_client.describe_security_groups(Filters=[{'Name':'vpc-id', 'Values':[vpc_id]},
                                                                    {'Name': 'group-name', 'Values': [sg_name]}])
        sg_id = response["SecurityGroups"][0]["GroupId"]
        return sg_id
    else:
        return sg_id


def create_db(db_sg_id):

    try:
        response = rds_client.create_db_instance(
            AllocatedStorage=20,
            DBInstanceClass="db.t2.micro",
            DBInstanceIdentifier="my-db-instance",
            Engine="MySQL",
            EngineVersion="8.0.28",
            VpcSecurityGroupIds=[db_sg_id],
            MasterUsername="admin",
            MasterUserPassword="Admin123",
            DBSubnetGroupName="rds-db-grp",
            MultiAZ=False,
            PubliclyAccessible=False

        )
    except Exception as e:
        print(e)
    else:
        return "Successfully created db "


if __name__ == '__main__':
    subnet_ids = ["10.0.0.0/27", "10.0.0.32/27", "10.0.0.64/27"]
    az = ["us-east-2a", "us-east-2b", "us-east-2c"]
    # create_vpc()
    vpc_id = describe_vpc()
    # modify_vpc_attributes(vpc_id)
    # create_igw(vpc_id)
    igw_id = describe_igw()
    # attach_igw(igw_id, vpc_id)
    # create_subnets(subnet_ids,vpc_id,az)
    subnet_ids = describe_subnets(vpc_id)
    # create_route_table(vpc_id)
    rt_id = describe_rt(vpc_id)
    print(rt_id)
    # modify_subnet_attribute(subnet_ids)
    # create_route(vpc_id, igw_id, rt_id)
    # associate_subnet(rt_id, subnet_ids)
    sg_id = create_sg(vpc_id)
    create_ec2(sg_id,subnet_ids)
    # create_db_subnet_grp(subnet_ids)
    db_sg_id = db_sg(vpc_id)
    # create_db(db_sg_id)









