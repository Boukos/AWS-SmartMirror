import botocore
import boto.s3
from twilio.rest import TwilioRestClient
from twilio.exceptions import TwilioException

#s3_client = boto3.client('s3')
#s3_resource = boto3.resource('s3')
phonebucket = "arivanosersourcebucket"
account_sid = "AC9cdea9c1ccce7cb74bcf5083dfaab500"
auth_token = "62fb9f1943517116fd1044009a19a12f"
client = TwilioRestClient(account_sid, auth_token)
def lambda_handler(event, context):
	for record in event['Records']:
		conn = boto.s3.connect_to_region('us-east-1')
		bucket = conn.get_bucket(phonebucket)
		key = record['s3']['object']['key']
		target = bucket.lookup(image1key)
		target.set_acl('public-read')
		print "pic is public :)"
		#gary = "0r5stVi.png"

		try:
			client.messages.create(from_="+16692363653", to="+14089604952", body="REEEEEESH!", media_url="https://s3.amazonaws.com/arivanosersourcebucket/image.png")
			#	print "mms message sent!"
		except TwilioException as e:
			raise MotionAlertError("Error sending MMS with Twilio: ""{0}".format(e))

