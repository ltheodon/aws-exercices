import sys 
import time
import boto3
import statistics

def Average(lst): 
	return sum(lst) / len(lst) 


sqs = boto3.resource('sqs')

logs = boto3.client('logs')

LOG_GROUP='group_lab3'
LOG_STREAM='stream_lab3'

try:
	logs.create_log_group(logGroupName=LOG_GROUP)
except logs.exceptions.ResourceAlreadyExistsException:
	pass
try:
	logs.create_log_stream(logGroupName=LOG_GROUP, logStreamName=LOG_STREAM)
except logs.exceptions.ResourceAlreadyExistsException:
	pass




queue = sqs.get_queue_by_name(QueueName='requestQueue')
while True:
	goNext = False
	if not queue.receive_messages(MessageAttributeNames=['All']):
		print('Aucun message à traiter.')
		time.sleep(1)
		goNext = True

	for message in queue.receive_messages(MessageAttributeNames=['All']):
		print(message.body)
		if not message.body.replace(',','').isdecimal():
			print('Données non conformes.')
			message.delete()
			sys.exit()
		L = message.body.split(',')
		Li = [int(s) for s in L if not s == '']
		lmin  = min(Li)
		lmax  = max(Li)
		lmean = statistics.mean(Li)
		lmed = statistics.median(Li)
		print('min:',lmin)
		print('max:',lmax)
		print('mean:',lmean)
		print('median:',lmed)


		# Envoie de la réponse:
		Rqueue = sqs.create_queue(QueueName='responseQueue', Attributes={'DelaySeconds': '5'})
		rep = Rqueue.send_message(MessageBody='Réponse à' + str(message.message_id), MessageAttributes={
			'min': {
			'StringValue': str(lmin),
			'DataType': 'Number'
			},
			'max': {
			'StringValue': str(lmax),
			'DataType': 'Number'
			},'mean': {
			'StringValue': str(lmean),
			'DataType': 'Number'
			},
			'median': {
			'StringValue': str(lmed),
			'DataType': 'Number'
			},
			'sendID': {
			'StringValue': str(message.message_id),
			'DataType': 'String'
			}
		})

		timestamp = int(round(time.time() * 1000))

		logrep = logs.describe_log_streams(logGroupName=LOG_GROUP)
		logrep['logStreams'][0]['uploadSequenceToken']
		logrep = logs.put_log_events(
			logGroupName=LOG_GROUP,
			logStreamName=LOG_STREAM,
			logEvents=[
				{
					'timestamp': timestamp,
					'message': time.strftime('%Y-%m-%d %H:%M:%S')+'\t from:' + str(message.message_id) + ' -- to:'
					+ rep['MessageId'] + ' -- msg:' + message.body + '-- min:' + str(lmin) + '-- max:' + str(lmax)
					 + '-- mean:' + str(lmean) + '-- median:' + str(lmed)
				}
			],
			sequenceToken=logrep['logStreams'][0]['uploadSequenceToken']
		)


		message.delete()