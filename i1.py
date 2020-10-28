import sys 
import boto3

# GUI
import PySimpleGUI as sg
import os.path

# First the window layout in 2 columns

file_list_column = [
	[
		sg.Text("Image Folder"),
		sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
		sg.FolderBrowse(),
	],
	[
		sg.Listbox(
			values=[], enable_events=True, size=(40, 20), key="-FILE LIST-"
		)
	],
]

# For now will only show the name of the file that was chosen
image_viewer_column = [
	[sg.Text("Choose an image from list on left:")],
	[sg.Text(size=(40, 1), key="-TOUT-")],
	[sg.Image(key="-IMAGE-")],
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

window = sg.Window("Sélectionner une image (png ou GIF)", layout).Finalize()

window.FindElement('send').Update(disabled=True)

# Run the Event Loop
filename = ''
while True:
	event, values = window.read()
	if event == "Exit" or event == sg.WIN_CLOSED or event == "send":
		break
	# Folder name was filled in, make a list of files in the folder
	if event == "-FOLDER-":
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
		window["-FILE LIST-"].update(fnames)
	elif event == "-FILE LIST-":  # A file was chosen from the listbox
		try:
			filename = os.path.join(
				values["-FOLDER-"], values["-FILE LIST-"][0]
			)
			window["-TOUT-"].update(filename)
			window["-IMAGE-"].update(filename=filename)
			window.FindElement('send').Update(disabled=False)

		except:
			pass

window.close()

if not filename:
	layout = [[sg.Text("Aucun fichier sélectionné.")], [sg.Button("OK")]]

	window = sg.Window("Alerte", layout)

	while True:
		event, values = window.read()
		if event == "OK" or event == sg.WIN_CLOSED:
			break

	window.close()
	exit()




h,t = os.path.split(filename)


import skimage
from skimage.viewer import ImageViewer

image = skimage.io.imread(fname=filename)

layout = [[sg.Text("Image en cours d'envoi...")]]


s3 = boto3.client('s3')

r = True
window = sg.Window("Alerte", layout, margins=(100, 50)).Finalize()
while r:
	r = s3.upload_file(
		filename, 'mybucket975846589', t,
		ExtraArgs={'Metadata': {'mykey': 'myvalue'}}
		)
window.close()

#viewer = ImageViewer(image)
#viewer.show()
layout = [[sg.Text("Image envoyée....")], [sg.Button("OK")]]

window = sg.Window("Alerte", layout)

while True:
	event, values = window.read()
	if event == "OK" or event == sg.WIN_CLOSED:
		break

window.close()