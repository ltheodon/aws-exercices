import sys 
import boto3

import skimage
from skimage.viewer import ImageViewer

image = skimage.io.imread(fname='cat.jpg')


s3 = boto3.client('s3')

s3.upload_file(
    'cat.jpg', 'mybucket975846589', 'cat.jpg',
    ExtraArgs={'Metadata': {'mykey': 'myvalue'}}
	)


viewer = ImageViewer(image)
viewer.show()
