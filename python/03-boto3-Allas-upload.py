"""
2025-11-19 Maria Yli-Heikkilä

To set up boto3-connection to Allas, you need to create a S3 access token or use the existing token 
for the project. Instructions:
https://docs.csc.fi/data/Allas/using_allas/python_boto3/

Note: to be safe not to mess up your old boto3 credentials, forward the token to a tmp file first:
sed -E 's/^(access|secret)/aws_\1/g' ~/.config/rclone/rclone.conf > ~/.boto3_credentials2

and then copy-paste your token to ~/.boto3_credentials (or point your s3_credentials below to boto3_credentials2).


RUN:
python boto3-Allas-upload.py -i /scratch/project_2000371/FBSadjusted/results/ \
-b FoodBalanceSheets

"""


import pandas as pd
import argparse
import textwrap
import os
import datetime
import boto3
import glob

s3_credentials = '~/.boto3_credentials3'
s3_profile = 's3allas-project_2000371'
s3_profile = 'default'

os.environ['AWS_SHARED_CREDENTIALS_FILE'] = s3_credentials
os.environ["AWS_REQUEST_CHECKSUM_CALCULATION"] = "when_required"
os.environ["AWS_RESPONSE_CHECKSUM_VALIDATION"] = "when_required"

s3_session = boto3.Session(profile_name=s3_profile)
s3_resource = s3_session.resource('s3', endpoint_url='https://a3s.fi')

today = datetime.datetime.now().strftime('%Y-%b')

# HERE STARTS MAIN:

def main(args):
    try:
        if not args.inputpath:
            raise Exception('Missing input filepath argument. Try --help .')

        print(f'\nboto3-Allas-upload.py')
        print(f'\nResults in: {args.inputpath}')
        print(f'\nFiles saved in s3 bucket: {args.bucketname}')

        s3_resource = boto3.resource('s3', endpoint_url='https://a3s.fi')
        my_bucketname = args.bucketname
        
        fp = args.inputpath

        print(f'\nRead all results in csv files and upload to Allas...')

        fps = glob.iglob(args.inputpath + '*.csv')
        for filename in fps:
            print(filename)

            # boto3:               
            boto3file = today + '-' + os.path.basename(filename)
            print(f'Saving all data into Allas {boto3file}')
            s3_resource.Object(my_bucketname, boto3file).upload_file(filename, ExtraArgs={'ACL':'public-read'})

            
            # If you want to see the list of Allas files:
            print(f'My files in Allas {my_bucketname}:')
            
            my_bucket = s3_resource.Bucket(my_bucketname)
            
            for my_bucket_object in my_bucket.objects.all():
                print(my_bucket_object.key)

            print(f'\nDone.')

    except Exception as e:
        print('\n\nUnable to read input or upload files to Allas. Check prerequisites and see exception output below.')
        parser.print_help()
        raise e


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=textwrap.dedent(__doc__))

    parser.add_argument('-i', '--inputpath',
                        help='Path to the directory where the files are.',
                        type=str)
    parser.add_argument('-b', '--bucketname',
                        help='Give a name of an existing bucket in S3.',
                        type=str)

    args = parser.parse_args()
    main(args)
