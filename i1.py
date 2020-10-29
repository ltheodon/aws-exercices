import sys 
import boto3

#Image
import skimage
from skimage.viewer import ImageViewer

# GUI
import PySimpleGUI as sg
import os.path

def alerte(s):
	layout = [[sg.Text(s)], [sg.Button("OK")]]

	window = sg.Window("Alerte", layout)

	while True:
		event, values = window.read()
		if event == "OK" or event == sg.WIN_CLOSED:
			break

	window.close()
	exit()



s3 = boto3.client('s3')
sqs = boto3.resource('sqs')
Rqueue = sqs.get_queue_by_name(QueueName='outbox')



try:
	file_list = os.listdir(os.getcwd())
except:
	file_list = []
fnames = [
	f
	for f in file_list
	if os.path.isfile(os.path.join(os.getcwd(), f))
	and f.lower().endswith((".png", ".gif"))
]


# First the window layout in 2 columns
file_list_column = [
	[
		sg.Text("Dossier:"),
		sg.In(size=(25, 1), enable_events=True, key="-FOLDER-", default_text=os.getcwd()),
		sg.FolderBrowse(),
	],
	[
		sg.Listbox(
			values=fnames, enable_events=True, size=(40, 20), key="-FILE LIST-"
		)
	],
]

# For now will only show the name of the file that was chosen
image_viewer_column = [
	[sg.Text("Choisir une image à flouter dans la liste à gauche:")],
	[sg.Text(size=(40, 1), key="-TOUT-")],
	[sg.Image(key="-IMAGE-")],
	[sg.Text("Valeur de sigma:"),
		sg.Slider(
			(0.1, 10),
			5,
			0.001,
			orientation="h",
			size=(40, 15),
			key="-SIGMA SLIDER-",
		),
	],
	[sg.Button("Envoyer", key="send")]
]

# ----- Full layout -----
layout = [
	[
		sg.Column(file_list_column),
		sg.VSeperator(),
		sg.Column(image_viewer_column),
	]
]

main = sg.Window("Sélectionner une image (png ou GIF)", layout).Finalize()

main.FindElement('send').Update(disabled=True)

# Run the Event Loop
filename = ''
sigma = None
newFile = False
while True:
	for message in Rqueue.receive_messages(MessageAttributeNames=['All']):
		if not message.body:
			message.delete()
			pass
		rFileName = message.message_attributes.get('Key').get('StringValue')
		print('Téléchargement de ' + rFileName)
		s3.download_file('mybucket975846589', rFileName, rFileName)
		newFile = True
		message.delete()


	event, values = main.read()
	sigma  = values["-SIGMA SLIDER-"]
	if event == "Exit" or event == sg.WIN_CLOSED:
		exit()
	if event == "send":
		
		if not filename:
			alerte("Aucun fichier sélectionné.")

		if not sigma:
			alerte("Valeur de sigma introuvable.")

		h,t = os.path.split(filename)
		image = skimage.io.imread(fname=filename)
		layout = [[sg.Text("Image en cours d'envoi...")]]


		r = True
		window = sg.Window("Alerte", layout, margins=(100, 50)).Finalize()
		while r:
			r = s3.upload_file(
				filename, 'mybucket975846589', t,
				ExtraArgs={'Metadata': {'mykey': 'myvalue'}}
				)

			queue = sqs.create_queue(QueueName='inbox', Attributes={'DelaySeconds': '0'})
			response = queue.send_message(MessageBody="Sending picture to process: "+ t, MessageAttributes={
						'Key': {
							'StringValue': t,
							'DataType': 'String'
							},
						'Sigma': {
							'StringValue': str(sigma),
							'DataType': 'String'
							}
						})	
			r = False
		window.close()

		layout = [[sg.Text("Image envoyée....")], [sg.Button("OK")]]
		window = sg.Window("Alerte", layout)

		while True:
			event, values = window.read()
			if event == "OK" or event == sg.WIN_CLOSED:
				break
		window.close()


	# Folder name was filled in, make a list of files in the folder
	if event == "-FOLDER-" or newFile:
		newFile = False
		folder = values["-FOLDER-"]
		try:
			# Get list of files in folder
			file_list = os.listdir(folder)
		except:
			file_list = []

		fnames = [
			f
			for f in file_list
			if os.path.isfile(os.path.join(folder, f))
			and f.lower().endswith((".png", ".gif"))
		]
		main["-FILE LIST-"].update(fnames)
	elif event == "-FILE LIST-":  # A file was chosen from the listbox
		try:
			filename = os.path.join(
				values["-FOLDER-"], values["-FILE LIST-"][0]
			)
			main["-TOUT-"].update(filename)
			main["-IMAGE-"].update(filename=filename)
			main.FindElement('send').Update(disabled=False)

		except:
			pass

#main.close()

