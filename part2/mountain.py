#!/usr/bin/python
#
# Mountain ridge finder
# Based on skeleton code by D. Crandall, Oct 2016
#

'''
For each programming problem, please include a detailed comments section at the top of your code that describes: 
(1) a description of how you formulated the problem, including precisely defining the abstractions (e.g. HMM formulation); 
(2) a brief description of how your program works; 
(3) a discussion of any problems, assumptions, simplifications, and/or design decisions you made; and 
(4) answers to any questions asked below in the assignment.
'''

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
    #print filtered_y.shape
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
    
def draw_state(obs_prob, prev = -1, next = -1):
    #draw random state given transition probabilities from previous and next states in sample and emission probabilities

    if prev == -1:
        p = [ 1.0/(abs(next-i)+1) * obs_prob[i] for i in range(len(obs_prob)) ] #p(s_t | (s_(t+1), obs_t)
    elif next == -1:
        p = [ 1.0/(abs(prev-i)+1) * obs_prob[i] for i in range(len(obs_prob)) ] #p(s_t | (s_(t-1), obs_t)
    else:
        p = [ 1.0/(abs(prev-i)+1) * 1.0/(abs(next-i)+1) * obs_prob[i] for i in range(len(obs_prob)) ] #p(s_t | (s_(t-1), s_(t+1), obs_t)
    #print "prev, next, prob", prev, next, p/sum(p)
    return random.choice(range(len(p)), 1, replace = True, p = array(p/sum(p))) #normalize probabilities and pick one at random

def mcmc(e, iterations = 10000):
    m, n = map(int, e.shape)
    #normalize emission probabilities
    e /= e.sum(axis=0)
    #generate initial sample as baseline ridge (simple bayes)
    sample = edge_strength.argmax(axis = 0)
    #sample = random.choice(m, n, replace = True)
    #gibbs sampling
    for iter in range(iterations):
      sample[0] = draw_state(e[:,0], next = sample[1])
      for i in range(1, n-1):
        sample[i] = draw_state(e[:,i], prev = sample[i-1], next = sample[i+1])
      sample[n-1] = draw_state(e[:,n-1], prev = sample[n-2])
      if iter % 100 == 0: print iter
    return sample
          
  
# main program
#
(input_filename, output_filename, gt_row, gt_col) = sys.argv[1:]

# load in image 
input_image = Image.open(input_filename)

# compute edge strength mask
edge_strength = edge_strength(input_image)
imsave('edges.jpg', edge_strength)


baseline_ridge = [ edge_strength.shape[0]/2 ] * edge_strength.shape[1]
simple_bayes_ridge = edge_strength.argmax(axis = 0)
#mcmc_ridge = mcmc( array([[.9,.1,.1,.1],[.1,.9,.9,.1],[.1,.1,.1,.9]]) ) #test on small array
mcmc_ridge = mcmc(edge_strength, iterations = 100)
print mcmc_ridge


# output answer
#imsave(output_filename, draw_edge(input_image, simple_bayes_ridge, (255, 0, 0), 5))
imsave(output_filename, draw_edge(input_image, mcmc_ridge, (255, 0, 0), 5))

