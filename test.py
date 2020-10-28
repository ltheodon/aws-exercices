import sys 
import boto3






L = input("Entrer les entiers séparés par des virgules: ") 
if not L.replace(',','').isdecimal():
	print('Données non conformes.')
	sys.exit()


sqs = boto3.resource('sqs')

queue = sqs.create_queue(QueueName='requestQueue', Attributes={'DelaySeconds': '5'})

response = queue.send_message(MessageBody=L, MessageAttributes={
	'Key': {
		'StringValue': '001',
		'DataType': 'String'
	}
})

#print(queue.url)
#print(queue.attributes.get('DelaySeconds'))
#print(response['MessageId'])

print('Message envoyé.')