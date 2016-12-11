import datetime
import boto
import boto3
import botocore
import os
import sys
import time
import numpy as np
import uuid
import imutils
import cv2
from twilio.rest import TwilioRestClient
from twilio.exceptions import TwilioException
from PIL import Image
from boto.s3.key import Key

s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')
bucket = "arivanoserbucket"
targetbucket = "arivanoseroutputbucket"
#phonebucket = "arivanosersourcebucket"
minarea = 500

AWS_ACCESS_KEY_ID = 'AKIAI2U6AJEUPDZIJMZQ'
AWS_SECRET_ACCESS_KEY = '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'

twilio_account_sid = "AC9cdea9c1ccce7cb74bcf5083dfaab500"
twilio_auth_token = "62fb9f1943517116fd1044009a19a12f"
twilio_client = TwilioRestClient(twilio_account_sid, twilio_auth_token)

conn = boto.connect_s3(AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY)
outputbucket = conn.get_bucket(targetbucket)
outputphonebucket = conn.get_bucket(phonebucket)

def detect_motion(photo1, photo2):
    photo_1 = cv2.imread(photo1)
    photo_2 = cv2.imread(photo2)
    motiondetected=False
    #frame1 = imutils.resize(photo_1, width=500)
    print "success frame1"
    #frame2 = imutils.resize(photo_2, width=500)
    print "success frame2"
    gray1 = cv2.cvtColor(photo_1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(photo_2, cv2.COLOR_BGR2GRAY)

    frameDelta = cv2.absdiff(gray1,gray2)
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

    thresh = cv2.dilate(thresh, None, iterations=2)
    (image, cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for c in cnts:
        if cv2.contourArea(c) < minarea:
            continue

        motiondetected=True

    if motiondetected:
        return True

    return False

def lambda_handler(event, context):
    for record in event['Records']:
        image1key = record['s3']['object']['key']
        download_path = '/tmp/{}{}'.format(uuid.uuid4(), image1key)
        download_path2 = '/tmp/{}{}'.format(uuid.uuid4(), 'tempphoto.jpg')
        #upload_path = '/tmp/resized-{}'.format(image1key) #later you want this to be timestamp
        try:
            s3_resource.Object('arivanoseroutputbucket', image1key).load()
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                s3_client.download_file(bucket, image1key, download_path)
                k = Key(outputbucket)
                k.key = image1key
                #k.set_metadata('Content-Type', 'image/png')
                k.set_contents_from_filename(download_path)
                #s3_client.upload_file(download_path, targetbucket, image1key)
                print "First picture, uploading to 2nd bucket"
            else:
                raise
        else:
            s3_client.download_file(bucket, image1key, download_path)
            print "not first pic; downloaded pic"
            s3_client.download_file(targetbucket, image1key, download_path2)
            print "downloaded most recent pic, beginning motion detection"
            if detect_motion(download_path, download_path2):
                print "Motion Detected"
                conn = boto.s3.connect_to_region('us-east-1')
                twilio_bucket = conn.get_bucket(bucket)
                phone_target = twilio_bucket.lookup(image1key)
                phone_target.set_acl('public-read')
                print "pic is public :)"
                try:
                    twilio_client.messages.create(from_="+16692363653", to="+14089604952", body="REEEEEESH!", media_url="https://s3.amazonaws.com/arivanosersourcebucket/{}".format(image1key))
                    print "message sent yo"
                except TwilioException as e:
                    raise MotionAlertError("Error sending MMS with Twilio: ""{0}".format(e))
                #k1 = Key(outputphonebucket)
                #k1.key = image1key
                #k1.set_metadata('Content-Type', 'image/png')
                #k1.set_contents_from_filename(download_path)
                #download_path = imagify(download_path)

                #s3_client.upload_file(download_path, phonebucket, image1key)
            else:
                print "No Motion Detected"
            k2 = Key(outputbucket)
            k2.key = image1key
            #k2.set_metadata('Content-Type', 'image/png')
            k2.set_contents_from_filename(download_path)
            #s3_client.upload_file(download_path, targetbucket, image1key)
            print "uploaded most recent pic to bucket"
        #s3_client.download_file(bucket, image1key, download_path)
        #s3_client.upload_file(download_path, targetbucket, image1key)
        s3_client.delete_object(Bucket=bucket,Key=image1key)

    return "It works!"