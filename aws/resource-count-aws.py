"""Gathers data for Prisma Cloud sizing in AWS"""

# Questions / TODOs
# - Do we need to get list of ELBv1?
# - Org support
# - Multi-account support via credentials file

import datetime
import argparse

import botocore
import boto3

starttime = datetime.datetime.now()
print('Start time: %s' % starttime)

parser = argparse.ArgumentParser()
parser.add_argument('--nocsv', action='store_true')
args = parser.parse_args()

accountid = boto3.client('sts').get_caller_identity().get('Account')

ec2_total = 0
ec2_account_total = 0
rds_total = 0
rds_account_total = 0
natgw_total = 0
natgw_account_total = 0
redshift_total = 0
redshift_account_total = 0
elb_total = 0
elb_account_total = 0

f = None
if not args.nocsv:
    outputfile = 'sizing.csv'
    f = open(outputfile, 'w')
    print('Account ID, Service, Count', file=f)

# Count EC2
ec2client = boto3.client('ec2')
regions = ec2client.describe_regions()
regions = {'Regions': [{'RegionName': 'us-west-2'}]}

for region in regions['Regions']:
    ec2 = boto3.resource('ec2', region_name=region['RegionName'])
    # aws ec2 describe-instances --max-items 99999 --region="${1}" --filters "Name=instance-state-name,Values=running"
    for instance in ec2.instances.filter(Filters=[{'Name':'instance-state-name', 'Values':['running']}]):
        ec2_account_total += 1
if not args.nocsv:
    print('%s, EC2, %d' % (accountid, ec2_account_total), file=f)
ec2_total += ec2_account_total
ec2_account_total = 0

# Count RDS
rdsregions = boto3.Session().get_available_regions('rds')
for region in rdsregions:
    rds = boto3.client('rds', region_name=region)
    try:
        instances = rds.describe_db_instances()
    except botocore.exceptions.ClientError as error:
        print(error.response['Error'])
        continue

    # aws rds describe-db-instances --max-items 99999
    for instance in instances['DBInstances']:
        rds_account_total += 1
if not args.nocsv:
    print('%s, RDS, %d' % (accountid, rds_account_total), file=f)
rds_total += rds_account_total
rds_account_total = 0

# Count NAT Gateways
# aws ec2 describe-nat-gateways --max-items 99999

for region in regions['Regions']:
    ec2 = boto3.resource('ec2', region_name=region['RegionName'])
    natgws = ec2client.describe_nat_gateways()
    for instance in natgws['NatGateways']:
        natgw_account_total += 1
if not args.nocsv:
    print('%s, NATGW, %d' % (accountid, natgw_account_total), file=f)
natgw_total += natgw_account_total
natgw_account_total = 0

# Count Redshift
#aws redshift describe-clusters --max-items 99999
for region in regions['Regions']:
    redshift = boto3.client('redshift', region_name=region['RegionName'])
    clusters = redshift.describe_clusters()
    for cluster in clusters['Clusters']:
        redshift_account_total += 1
if not args.nocsv:
    print('%s, Redshift, %d' % (accountid, redshift_account_total), file=f)
redshift_total += redshift_account_total
redshift_account_total = 0

# Count ELBs
# aws elb describe-load-balancers --max-items 99999
for region in regions['Regions']:
    elb = boto3.client('elbv2', region_name=region['RegionName'])
    lbs = elb.describe_load_balancers()
    for lb in lbs['LoadBalancers']:
        elb_account_total += 1
if not args.nocsv:
    print('%s, ELB, %d' % (accountid, elb_account_total), file=f)
elb_total += elb_account_total
elb_account_total = 0

account_total = ec2_total + rds_total + redshift_total + natgw_total + elb_total

if not args.nocsv:
    print('', file=f)
    print('%s, TOTAL, %d' % (accountid, account_total), file=f)

if not args.nocsv:
    f.close()

endtime = datetime.datetime.now()
print('End time: %s' % endtime)
print('Total runtime: %s' % (endtime - starttime))
