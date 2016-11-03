#!/usr/bin/python
#
# Mountain ridge finder
# Based on skeleton code by D. Crandall, Oct 2016
#

from PIL import Image
from numpy import *
from scipy.ndimage import filters
from scipy.misc import imsave
import sys

# calculate "Edge strength map" of an image
#
def edge_strength(input_image):
    grayscale = array(input_image.convert('L'))
    filtered_y = zeros(grayscale.shape)
    filters.sobel(grayscale,0,filtered_y)
    print filtered_y.shape
    return filtered_y**2

# draw a "line" on an image (actually just plot the given y-coordinates
#  for each x-coordinate)
# - image is the image to draw on
# - y_coordinates is a list, containing the y-coordinates and length equal to the x dimension size
#   of the image
# - color is a (red, green, blue) color triple (e.g. (255, 0, 0) would be pure red
# - thickness is thickness of line in pixels
#
def draw_edge(image, y_coordinates, color, thickness):
    for (x, y) in enumerate(y_coordinates):
        for t in range( max(y-thickness/2, 0), min(y+thickness/2, image.size[1]-1 ) ):
            image.putpixel((x, t), color)
    return image
    
def draw_state(e, prev):
    #draw random state for a column given transition probabilities from previous state in sample and emission probabilities
    p = [ 1.0/(abs(prev-i)+1) * e[i] for i in range(len(e)) ]
    choice = random.choice(range(len(e)), 10, replace = True, p = array(p/sum(p)))
    return choice[0]


def mcmc(e):
    m, n = map(int, e.shape)
    #normalize emission probabilities
    e /= e.sum(axis=0)
    #initial probabilities: equal to emission probabilities for first column, tiny for the rest
    probs = 0.0001*ones((m,n)) 
    
    sample = zeros(n) #observation sample
    for _ in range(10):
        sample[0] = random.choice(range(len(e)), 1, replace = True, p = list(e[:,0]))
        for i in range(1, n):
          sample[i] = draw_state(e[:,i], prev = sample[i-1])
          print sample  
          
  
# main program
#
(input_filename, output_filename, gt_row, gt_col) = sys.argv[1:]

# load in image 
input_image = Image.open(input_filename)

# compute edge strength mask
edge_strength = edge_strength(input_image)
imsave('edges.jpg', edge_strength)


simple_bayes_ridge = edge_strength.argmax(axis = 0)
baseline_ridge = [ edge_strength.shape[0]/2 ] * edge_strength.shape[1]
mcmc_ridge = mcmc( array([[.1,.5,.7,.8],[.9,.5,.3,.2]]) )


# output answer
imsave(output_filename, draw_edge(input_image, simple_bayes_ridge, (255, 0, 0), 5))
