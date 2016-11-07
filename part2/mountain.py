#!/usr/bin/python
#
# Mountain ridge finder
# Based on skeleton code by D. Crandall, Oct 2016
#

'''
For each programming problem, please include a detailed comments section at the top of your code that describes: 
(1) a description of how you formulated the problem, including precisely defining the abstractions (e.g. HMM formulation); 
  Emission probabilities: normalized edge_strength matrix
  part 1: for each column, choose the pixel with the highest edge_strength. this is equivalent to argmax_i P(s_i(t) | obs ) 
  which is proportional to argmax_i P(obs | s_i(t)), since the probability of a state (e.g., row pixel) is assumed uniform.
  
  part 2: Using an HMM, we model the probability for each state given all other states and all observations
  p(s_t | s1, s2, ..., s_(t-1), s_(t+1), ..., sT | o1, o2, ..., oT) as proportional to 
  p(s_t | s_(t-1))*p(s_(t+1) | s_t)*p(ot | s_t).
  The transition probabilities are drawn from a normal distribution with much higher probabilities at neigboring row states:
  p(s_t | s_(t-1) = Normal( abs(s_t - s_(t-1)), Mu = 0, Sd = 2), abs(s_t - s_(t-1) > 2, 0.5 otherwise.
  
  For the Gibbs sampling, we start with an initial state "guess", and then resample s1, s2, ..., sT in that order.
  A good initial guess limits the number of iterations to 2000 or many fewer.
  
  The initial guess chooses a pixel for s1 randomly in the upper third of the image. Then, s_t = argmax_{i} p(s_t(i) | s_(t-1)) * p(obs_t|s_t(i))
  Here, the transition probability is a normal with sd = 5 if the difference between pixels is less than 50, otherwise 0.
  
  part 3: we start our initial guess at the given pixel, and compute the rest of the sample to the left and right from it.
  we set the emission probability of that pixel to 1 and all others to 0.

(2) a brief description of how your program works; 
  ***to run part 2: set pixel = (-1, -1)***
  We add to what we described in (1): we compute 20 initial guesses and their loglikelihood, and choose the best one.
  
(3) a discussion of any problems, assumptions, simplifications, and/or design decisions you made; and 
  It was difficult to choose the parameters for the transition probability. The program feels quite slow because for every
  state sample, a probability vector of length |colums| has to be initialized. 
  
  We take the average of the last 100 samples, but this still does not make our solution look perfectly smooth like the
  one in the assignment pdf.
  
  If the initial guess is bad, the line will be "stuck" in a bad place and no number of iterations will fix it.

(4) answers to any questions asked below in the assignment.
  N/A
'''

from PIL import Image
from numpy import *
from scipy.stats import norm
from scipy.ndimage import filters
from scipy.misc import imsave
import sys
import os
#import matplotlib.pyplot as plt
import copy

# calculate "Edge strength map" of an image
#
def compute_edge_strength(input_image):
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
#     for (x in range(215)):
#       image.putpixel( 
#       e[:,pixel[1]] = 0.
#       e[pixel[0],pixel[1]] = 1.
#     image.putpixel(107,208
    return image
    
def draw_state(obs_prob, prev = -1, next = -1):
    #draw random state given transition probabilities from previous and next states in sample and emission probabilities
    if prev == -1:
        p = [ (normal_dist[abs(next-i)] if abs(next-i)>2 else 0.5) * obs_prob[i] for i in range(len(obs_prob)) ] #p(s_t | (s_(t+1), obs_t)
    elif next == -1:
        p = [ (normal_dist[abs(prev-i)] if abs(prev-i)>2 else 0.5) * obs_prob[i] for i in range(len(obs_prob)) ] #p(s_t | (s_(t-1), obs_t)
    else:
        p = [ (normal_dist[abs(prev-i)] if abs(prev-i)>2 else 0.5) * (normal_dist[abs(next-i)] if abs(next-i)>2 else 0.5) * obs_prob[i] for i in range(len(obs_prob)) ] #p(s_t | (s_(t-1), s_(t+1), obs_t)
    return random.choice(range(len(p)), 1, replace = True, p = array(p/sum(p))) #normalize probabilities and pick one at random

def draw_initial_state(obs_prob, prev, normal_dist_initial):
    lp = [ normal_dist_initial[abs(prev-i)] + 1.5*log(1e-5+obs_prob[i]) for i in range(len(obs_prob)) ] #p(s_t | (s_(t-1), obs_t)
    choice = int(argmax(lp))
    return choice, lp[choice]

def initial_guess(e, pixel = (-1, -1)):
    m, n = map(int, e.shape)
    normal_dist_initial = log([ 1e-5 + norm.pdf(i, 0, 5) if i < 50 else 1e-8 for i in range(m) ]) #transition probability
    best_sample, best_logp = [], -1e10 #try 20 initial guesses, keep the one with the highest loglikelihood
    sample = zeros(n)
    if pixel == (-1, -1):
        for _ in range(20):
            sample[0] = random.choice(range(int(m*0.35))) #mountains only show in upper area
            logp = log(1e-5+e[int(sample[0]),0])
            for i in range(1, n): #generate sample column by column
                sample[i], lp = draw_initial_state(e[:,i], int(sample[i-1]), normal_dist_initial)
                logp += lp
            if logp > best_logp: #replace if better loglikelihood
                best_logp = logp
                best_sample = copy.deepcopy(sample)
    else:
        for _ in range(20):
            sample[pixel[1]] = pixel[0] #set given pixel to chosen value
            logp = 0
            for i in range(pixel[1]+1, n): #choose other sample pixels to the right
                sample[i], lp = draw_initial_state(e[:,i], int(sample[i-1]), normal_dist_initial)
                logp += lp
            for i in range(pixel[1]-1, -1, -1): #choose other sample pixels to the left
                sample[i], lp = draw_initial_state(e[:,i], int(sample[i+1]), normal_dist_initial)
                logp += lp
            if logp > best_logp:
                best_logp = logp
                best_sample = copy.deepcopy(sample)
    #plot initial guess:
#     plt.axis([0,512, 0,384])
#     ax = plt.gca()
#     ax.set_autoscale_on(False)
#     plt.plot(subtract(m,best_sample))
#     plt.show()
    return best_sample
    

def mcmc(e, iterations = 1000, pixel = (-1, -1)):
    m, n = map(int, e.shape)
    #normalize emission probabilities
    e /= e.sum(axis=0)
    if pixel != (-1, -1):
      e[:,pixel[1]] = 1e-10
      e[pixel] = 1.
    #generate initial guess for the solution:
    sample = initial_guess(e, pixel)
    #gibbs sampling
    sample_average = zeros(n)
    for iter in range(iterations):
      sample[0] = draw_state(e[:,0], next = int(sample[1]))
      for i in range(1, n-1):
        sample[i] = draw_state(e[:,i], prev = int(sample[i-1]), next = int(sample[i+1]))
      sample[n-1] = draw_state(e[:,n-1], prev = int(sample[n-2]))
      if iter % 250 == 0: print "iteration", iter
      if iterations - iter <= 10: 
        sample_average = add(sample, sample_average)
    return map(int, divide(sample_average, 10))
          
  
# main program
#
'''
img_directory = "test_images/"
for file in os.listdir(img_directory):
    if not file.endswith(".jpg") or file != "mountain.jpg": continue
    print file
    input_filename = os.path.join(img_directory, file)
    output_filename = "part3_" + file
    gt_row = gt_col = -1

    # load in image 
    input_image = Image.open(input_filename)

    # compute edge strength mask
    edge_strength = compute_edge_strength(input_image)
    imsave('edges.jpg', edge_strength)

    if file == "mountain.jpg":
        pixel = (34,284)
    elif file == "mountain2.jpg":
        pixel = (114,131)
    elif file == "mountain3.jpg":
        pixel = (110,116)
    elif file == "mountain4.jpg":
        pixel = (119,184)
    elif file == "mountain5.jpg":
        pixel = (128,200)
    elif file == "mountain6.jpg":
        pixel = (133,139)
    elif file == "mountain7.jpg":
        pixel = (34,85)
    elif file == "mountain8.jpg":
        pixel = (97,73)
    elif file == "mountain9.jpg":
        pixel = (137,374)

    baseline_ridge = [ edge_strength.shape[0]/2 ] * edge_strength.shape[1]
    simple_bayes_ridge = edge_strength.argmax(axis = 0)
    normal_dist = [ 1e-07 + norm.pdf(i, 0, 2) for i in range(edge_strength.shape[1]) ]

    mcmc_ridge = mcmc(edge_strength, iterations = 2000, pixel = pixel)

    # output answer
    imsave(output_filename, draw_edge(input_image, mcmc_ridge, (0, 255, 0), 5))
'''

#'''
#old code that runs only on one file
(input_filename, output_filename, gt_row, gt_col) = sys.argv[1:]

# load in image 
input_image = Image.open(input_filename)

if (gt_row, gt_col) != (-1, -1):
    if input_filename.endswith("mountain.jpg"):
        pixel = (107,208)
    elif input_filename.endswith("mountain2.jpg"):
        pixel = (114,131)
    elif input_filename.endswith("mountain3.jpg"):
        pixel = (110,116)
    elif input_filename.endswith("mountain4.jpg"):
        pixel = (119,184)
    elif input_filename.endswith("mountain5.jpg"):
        pixel = (128,200)
    elif input_filename.endswith("mountain6.jpg"):
        pixel = (133,139)
    elif input_filename.endswith("mountain7.jpg"):
        pixel = (34,85)
    elif input_filename.endswith("mountain8.jpg"):
        pixel = (97,73)
    elif input_filename.endswith("mountain9.jpg"):
        pixel = (137,374)

# compute edge strength mask
edge_strength = compute_edge_strength(input_image)
imsave('edges.jpg', edge_strength)


baseline_ridge = [ edge_strength.shape[0]/2 ] * edge_strength.shape[1]
simple_bayes_ridge = edge_strength.argmax(axis = 0)
normal_dist = [ 1e-07 + norm.pdf(i, 0, 2) for i in range(edge_strength.shape[1]) ]
mcmc_ridge = mcmc(edge_strength, iterations = 20, pixel = pixel)

# output answer
#imsave(output_filename, draw_edge(input_image, simple_bayes_ridge, (255, 0, 0), 5))
imsave(output_filename, draw_edge(input_image, mcmc_ridge, (0, 255, 0), 5))
#'''
