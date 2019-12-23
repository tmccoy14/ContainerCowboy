#!/bin/bash
. configs/aws.conf

# Create AWS Config and Credentials files
mkdir -p ~/.aws
echo $'[profile studio]\nregion = us-east-1' >> ~/.aws/config
echo $'[profile studio]\naws_access_key_id = '$aws_access_key_id'' >> ~/.aws/credentials
echo $'aws_secret_access_key = '$aws_secret_access_key'' >> ~/.aws/credentials

# Create Gauth Config file
mkdir -p ~/.config
echo 'AWS: '$aws_token'' >> ~/.config/gauth.csv

# Get CLI AWS Tool
wget https://github.com/outlawlabs/awsctl/releases/download/v0.4.0/awsctl_0.4.0_linux_amd64
chmod +x awsctl_0.4.0_linux_amd64
mv awsctl_0.4.0_linux_amd64 ~/

# Get CLI Authenticator Tool
go get github.com/pcarrier/gauth
cd ~/go/bin && ./gauth > gauth.csv
current=$(tail -n+2 gauth.csv | cut --delimiter=, -f3-5)
token=$(echo $current | cut -c12-17)

# Create MFA enabled AWS Profile
cd && ./awsctl_0.4.0_linux_amd64 auth -p studio -d 129000 -t $token
sleep 3
export AWS_PROFILE=studio_mfa