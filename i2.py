import sys 
import boto3

import skimage
from skimage.viewer import ImageViewer

sigma = 5

s3 = boto3.client('s3')
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
viewer.show()