import sys 
import boto3
import time
import random
import os.path

import skimage
from skimage.viewer import ImageViewer

sigma = 5



sqs = boto3.resource('sqs')
s3 = boto3.client('s3')

queue = sqs.get_queue_by_name(QueueName='inbox')
Rqueue = sqs.create_queue(QueueName='outbox', Attributes={'DelaySeconds': '0'})
while True:
	if not queue.receive_messages(MessageAttributeNames=['All']):
		print('Aucun message à traiter.')
		time.sleep(1)

	for message in queue.receive_messages(MessageAttributeNames=['All']):
		if not message.body:
			print('Données non conformes.')
			message.delete()
			pass

		fileName = message.message_attributes.get('Key').get('StringValue')
		tmp = fileName.split('.')
		rnb = random.randrange(99999)
		nFileName = tmp[0] + '_' + str(rnb) + '.' + tmp[1]

		sigma = float(message.message_attributes.get('Sigma').get('StringValue'))


		# Processing
		s3.download_file('mybucket975846589', fileName, nFileName)
		image = skimage.io.imread(fname=nFileName)
		blurred = skimage.filters.gaussian(
		    image, sigma=(sigma, sigma), truncate=3.5, multichannel=True)

		skimage.io.imsave(nFileName, blurred)
		s3.upload_file(
		    nFileName, 'mybucket975846589', nFileName,
		    ExtraArgs={'Metadata': {'mykey': 'myvalue_mod'}}
		    )

		os.remove(nFileName)


		# Envoie de la réponse:
		rep = Rqueue.send_message(MessageBody='Réponse à' + str(message.message_id), MessageAttributes={
			'Key': {
			'StringValue': nFileName,
			'DataType': 'String'
			}
		})

		message.delete()






'''s3 = boto3.client('s3')
s3.download_file('mybucket975846589', 'cat.jpg', 'cat_mod.jpg')

image = skimage.io.imread(fname='cat_mod.jpg')

blurred = skimage.filters.gaussian(
    image, sigma=(sigma, sigma), truncate=3.5, multichannel=True)

skimage.io.imsave('cat_mod.jpg', blurred)


s3.upload_file(
    'cat_mod.jpg', 'mybucket975846589', 'cat_mod.jpg',
    ExtraArgs={'Metadata': {'mykey': 'myvalue_mod'}}
    )


viewer = ImageViewer(blurred)
viewer.show()'''