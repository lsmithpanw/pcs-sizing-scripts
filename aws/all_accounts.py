"""Run sizing script for each AWS account in ~/.aws/credentials"""

import configparser
import os
from subprocess import call

credentialsfile = os.path.expanduser('~/.aws/credentials')
profileenvvar = 'AWS_PROFILE'

print('Reading AWS credentials from %s' % credentialsfile)
credentials = configparser.ConfigParser()
credentials.read(credentialsfile)

for i in credentials.sections():
    if 'aws_access_key_id' in credentials[i] and 'aws_secret_access_key' in credentials[i]:
        print()
        print('Running sizing script for credentials labelled %s' % i)
        os.environ[profileenvvar] = i
        call('./resource-count-aws.sh')
    else:
        print()
        print('Skipping empty section %s' % i)
