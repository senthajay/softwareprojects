from PIL import Image
import os

# set the directory containing the images
directory = 'C:/Users/SENTHA.JAY/Desktop/newhomes_choices_extras_mangmt/static/images/products_pics'
# set the target size
target_size = (365, 365)

# loop through each file in the directory
for filename in os.listdir(directory):
    if filename.endswith('.jpg') or filename.endswith('.png'):
        # open the image
        image = Image.open(os.path.join(directory, filename))

        # resize the image
        resized_image = image.resize(target_size)

        # delete the original file
        os.remove(os.path.join(directory, filename))

        # save the resized image with the original filename
        resized_image.save(os.path.join(directory, filename))

