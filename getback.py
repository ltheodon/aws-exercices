import sys 
import time
import boto3
import statistics

def Average(lst): 
    return sum(lst) / len(lst) 


sqs = boto3.resource('sqs')

queue = sqs.get_queue_by_name(QueueName='test')

'''while len(queue.receive_messages(MessageAttributeNames=['Key'])) < 1:
	print('Aucun message à traiter.')
	time.sleep(1)
	queue = sqs.get_queue_by_name(QueueName='test')'''

for message in queue.receive_messages(MessageAttributeNames=['Key']):
    if not message.body.replace(',','').isdecimal():
    	print('Données non conformes.')
    	sys.exit()
    L = message.body.split(',')
    Li = [int(s) for s in L if not s == '']
    print('min:',min(Li))
    print('max:',max(Li))
    print('mean:',statistics.mean(Li))
    print('median:',statistics.median(Li))

    message.delete()