import boto3
import sys
'''
this section is for credentials
sess = boto3.Session(
    aws_access_key_id = credentials['AccessKeyId'],
    aws_secret_access_key = credentials['SecretAccessKey'],
    aws_session_token = credentials['SessionToken'],
)
'''
assert sys.stdout.encoding == "UTF-8", "Wrong stdout encoding. set PYTHONIOENCODING=utf8 and restart"
if len(sys.argv) < 2:
    sys.exit('Usage: %s You to have to provide vpcid' % sys.argv[0])
else:
    vpcid = sys.argv[1]
    print (vpcid)

region = "us-east-1"
session = boto3.session.Session(region_name=region)
ec2 = session.resource('ec2')
ec2_non_complaint = []
permissible_tags_with_space = ['Data Classification', 'Environment',  'Application Name', 'Resource Owner', 'XYZ Mail Alias', 'Data Taxonomy']
# permissible_tags_without_space = ['DataClassification', 'Environment', 'ApplicationName', 'ResourceOwner', 'XYZMailAlias', 'DataTaxonomy']
permissible_tags_without_space = ['DataClassification', 'Environment', 'ResourceOwner', 'XYZMailAlias', 'DataTaxonomy','AutomatedShutdown']
permissible_tags = permissible_tags_without_space+permissible_tags_with_space

def list_instances_by_vpc_id(vpcid):
    # When passed a tag key, tag value this will return a list of InstanceIds that were found.
    instancelist = []
    ec2client = boto3.client('ec2')
    response = ec2client.describe_instances(Filters=[{'Name': 'vpc-id','Values': [vpcid]}])
    instancelist = []
    for reservation in (response["Reservations"]):
        for instance in reservation["Instances"]:
            instancelist.append(instance["InstanceId"])
    return instancelist

def list_subnets_by_vpc_id(vpcid):
    subnetlist = []
    ec2client = boto3.client('ec2')
    response = ec2client.describe_subnets(Filters=[{'Name': 'vpc-id','Values': [vpcid]}])
    response = (response)['Subnets']
    for x in response:
        subnetlist.append((x)['SubnetId'])
    return subnetlist

def list_route_tables_by_vpc_id(vpcid):
    routeTableList = []
    ec2client = boto3.client('ec2')
    response = ec2client.describe_route_tables(Filters=[{'Name': 'vpc-id','Values': [vpcid]}])
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

instancelist = list_instances_by_vpc_id(vpcid)
subnetlist = list_subnets_by_vpc_id(vpcid)
routeTableList = list_route_tables_by_vpc_id(vpcid)

# print (instancelist)
fetchResourcesEc2Instances(instancelist)
fetchResourcesEc2Subnets(subnetlist)
fetchResourcesEc2RouteTables(routeTableList)
for a in ec2_non_complaint:
    print (a[0] + " has missing tags for " + ",".join(a[1]) )
