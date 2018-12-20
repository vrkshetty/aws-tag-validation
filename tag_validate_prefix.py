import boto3
import sys
import argparse
'''
this section is for credentials
sess = boto3.Session(
    aws_access_key_id = credentials['AccessKeyId'],
    aws_secret_access_key = credentials['SecretAccessKey'],
    aws_session_token = credentials['SessionToken'],
)

#ArgumentParser

assert sys.stdout.encoding == "UTF-8", "Wrong stdout encoding. set PYTHONIOENCODING=utf8 and restart"
if len(sys.argv) < 2:
    sys.exit('Usage: %s You to have to provide prifix' % sys.argv[0])
else:
    prifix = sys.argv[1]
    print (prifix)
'''
filter = [{'Name': 'tag:Name','Values': ['vrkshetty*']}]
region = "us-east-1"
session = boto3.session.Session(region_name=region)
ec2 = session.resource('ec2')
ec2_non_complaint = []
permissible_tags_with_space = ['Data Classification', 'Environment',  'Application Name', 'Resource Owner', 'XYZ Mail Alias', 'Data Taxonomy']
# permissible_tags_without_space = ['DataClassification', 'Environment', 'ApplicationName', 'ResourceOwner', 'XYZMailAlias', 'DataTaxonomy']
# permissible_tags_without_space = ['DataClassification', 'Environment', 'ResourceOwner', 'XYZMailAlias', 'DataTaxonomy','AutomatedShutdown']

permissible_tags_without_space = ['DataClassification', 'Environment', 'ResourceOwner', 'XYZMailAlias', 'DataTaxonomy','ProductFamilyName']
# permissible_tags_without_space = []
permissible_tags = permissible_tags_without_space+permissible_tags_with_space
def list_instances():
    # When passed a tag key, tag value this will return a list of InstanceIds that were found.
    instancelist = []
    ec2client = boto3.client('ec2')
    response = ec2client.describe_instances(Filters=filter)
    instancelist = []
    for reservation in (response["Reservations"]):
        for instance in reservation["Instances"]:
            instancelist.append(instance["InstanceId"])
    return instancelist

def list_vpc():
    vpclist = []
    ec2client = boto3.client('ec2')
    response = ec2client.describe_vpcs(Filters=filter)
    response = (response)['Vpcs']
    for x in response:
        vpclist.append((x)['VpcId'])
    return vpclist

def list_subnets():
    subnetlist = []
    ec2client = boto3.client('ec2')
    response = ec2client.describe_subnets(Filters=filter)
    response = (response)['Subnets']
    for x in response:
        subnetlist.append((x)['SubnetId'])
    return subnetlist

def list_route_tables():
    routeTableList = []
    ec2client = boto3.client('ec2')
    response = ec2client.describe_route_tables(Filters=filter)
    response = (response)['RouteTables']
    for x in response:
        routeTableList.append((x)['RouteTableId'])
    return routeTableList

def fetchResourcesEc2Instances(ec2_list):
    for id in ec2_list:
        instance = ec2.Instance(id)
        locals()['list_'.format(id)] = [id]
        if instance.tags == None:
          locals()['list_'.format(id)].append(permissible_tags_without_space)
          ec2_non_complaint.append(locals()['list_'.format(id)])
        else:
            evaluvate_tags(instance.tags,id)

def fetchResourcesEc2Subnets(ec2_list):
    for id in ec2_list:
        instance = ec2.Subnet(id)
        locals()['list_'.format(id)] = [id]
        if instance.tags == None:
          locals()['list_'.format(id)].append(permissible_tags_without_space)
          ec2_non_complaint.append(locals()['list_'.format(id)])
        else:
            evaluvate_tags(instance.tags,id)
def fetchResourcesEc2RouteTables(ec2_list):
    for id in ec2_list:
        instance = ec2.RouteTable(id)
        locals()['list_'.format(id)] = [id]
        if instance.tags == None:
          locals()['list_'.format(id)].append(permissible_tags_without_space)
          ec2_non_complaint.append(locals()['list_'.format(id)])
        else:
            evaluvate_tags(instance.tags,id)
def fetchResourcesEc2Vpc(ec2_list):
    for id in ec2_list:
        instance = ec2.Vpc(id)
        locals()['list_'.format(id)] = [id]
        if instance.tags == None:
          locals()['list_'.format(id)].append(permissible_tags_without_space)
          ec2_non_complaint.append(locals()['list_'.format(id)])
        else:
            evaluvate_tags(instance.tags,id)
def evaluvate_tags(resourceTags,instanceID):
    lst= []
    for list in resourceTags:
        lst.append(list['Key'])
    diff_list = [item for item in permissible_tags_without_space if item not in lst]
    # print("instance id: "+ instanceID +" not found tags " )
    locals()['list_'.format(instanceID)] = [instanceID]
    # print(locals()['list_'.format(instanceID)])
    if diff_list == []:
        print (instanceID + " is tag Complaint")
    else:
        locals()['list_'.format(instanceID)].append(diff_list)
        ec2_non_complaint.append(locals()['list_'.format(instanceID)])

    # print(diff_list)

# execution for EC2 instances
instancelist = list_instances()
fetchResourcesEc2Instances(instancelist)

# execution for EC2 subnets
subnetlist = list_subnets()
fetchResourcesEc2Subnets(subnetlist)

# execution for EC2 RouteTables
routeTableList = list_route_tables()
fetchResourcesEc2RouteTables(routeTableList)

# execution for EC2 VPC
vpclist = list_vpc()
fetchResourcesEc2Vpc(vpclist)
# print (instancelist)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Utility to fetch S3 and EC2 Resources for AWS Account")
	parser.add_argument("-p", "--profile", help="AWS profile name", default="default")
	parser.add_argument("-r", "--region", help="AWS Region", default="us-east-1")
	parser.add_argument("-o", "--output", help="Output File Name without extension", default="ResourceTaggingTemplate")

	args = parser.parse_args()
	filename = args.output
	profile = args.profile
	region = args.region
if len(ec2_non_complaint) == 0:
    print("All Resournces are Tag Complaint")
else:
    for a in ec2_non_complaint:
        print (a[0] + " has missing tags for " + ",".join(a[1]) )
