import argparse
import cv2
import numpy
import math
import sys
import os
import fnmatch

def line_deg_angle(x1, y1, x2, y2):
    delta_y = y2-y1
    delta_x = x2-x1
    return math.atan2(delta_y, delta_x)*180/math.pi

## >>> line_deg_angle(1, 1, 5, 5)
##45.0
##>>> line_deg_angle(0, 5, 5, 0)
##-45.0
def draw_lines_in_image(image, lines, color, line_thickness):
    try:
        for ln in lines:
            x1, y1, x2, y2 = ln[0]
            cv2.line(image, (x1, y1), (x2, y2), color, line_thickness)
    except Exception as e:
        print str(e)

def draw_ht_lines_in_image(image, lines, color, line_thickness):
    try:
        for ln in lines:
            x1, y1, x2, y2 = ln[0]
            cv2.line(image, (x1, y1), (x2, y2), color, line_thickness)
    except Exception as e:
        print str(e)

def display_lines_and_angles(lines):
    try:
        for ln in lines:
            x1, y1, x2, y2 = ln[0]
            print (x1, y1, x2, y2), line_deg_angle(x1, y1, x2, y2)
    except Exception as e:
        print str(e)

def display_ht_lines_and_angles(lines):
    try:
        for ln in lines:
            x1, y1, x2, y2 = ln[0]
            print (x1, y1, x2, y2), line_deg_angle(x1, y1, x2, y2)
    except Exception as e:
        print str(e)

def is_angle_in_range(a, ang_lower, ang_upper):
    return a in range(ang_lower, ang_upper)

def is_left_lane_line(x1, y1, x2, y2, ang_lower=-60, ang_upper=-30):
    return is_angle_in_range(line_deg_angle(x1, y1, x2, y2), ang_lower, ang_upper)

def is_right_lane_line(x1, y1, x2, y2, ang_lower=25, ang_upper=60):
    return is_angle_in_range(line_deg_angle(x1, y1, x2, y2), ang_lower, ang_upper)

def display_ht_lanes_in_image(image_path, rho_accuracy, theta_accuracy, num_votes, min_len, max_gap):
    image = cv2.imread(image_path) ## read the image
    gray  = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) ## grayscale
    edges = cv2.Canny(gray, 50, 150, apertureSize=3) ## detect edges
    lines = cv2.HoughLinesP(edges, rho_accuracy, theta_accuracy, num_votes, min_len, max_gap) ## detect hough lines
    print 'Detected lines and angles:'
    display_ht_lines_and_angles(lines)
    draw_ht_lines_in_image(image, lines, (255, 0, 0), 2)
    cv2.imshow('Gray',  gray)
    cv2.imshow('Edges', edges)
    cv2.imshow('Lines in Image', image)
    cv2.waitKey(0)

def filter_left_lane_lines(lines, ang_lower=-60, ang_upper=-20):
    if lines is None:
        return []
    ll_lines = []
    for line in lines:
        x1,y1,x2,y2 = line[0]
        if is_left_lane_line(x1,y1,x2,y2, ang_lower, ang_upper):
            ll_lines.append(line)
    return ll_lines
    # return [line for line in lines if is_left_lane_line(line[0][0], line[0][1], line[0][2], line[0][3], ang_lower, ang_upper)]

def filter_right_lane_lines(lines, ang_lower=20, ang_upper=60):
    if lines is None:
        return []
    rl_lines = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if is_right_lane_line(x1, y1, x2, y2, ang_lower, ang_upper):
            rl_lines.append(line)
    return rl_lines
    # return [line for line in lines if is_right_lane_line(line[0][0], line[0][1], line[0][2], line[0][3], ang_lower, ang_upper)]

## most common value for rho_accuracy is 1
## most common value for theta_accuracy is numpy.pi/180.
## typo with display_line_angles is fixed.
def plot_ht_lanes_in_image(image_path, rho_accuracy, theta_accuracy, num_votes, min_len, max_gap):
    image = cv2.imread(image_path) ## read the image
    gray  = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) ## grayscale
    edges = cv2.Canny(gray, 50, 150, apertureSize=3) ## detect edges
    lines = cv2.HoughLinesP(edges, rho_accuracy, theta_accuracy, num_votes, min_len, max_gap) ## detect hough lines
    display_lines_and_angles(lines)
    cv2.imshow('Gray',  gray)
    cv2.imshow('Edges', edges)
    ll_lines = filter_left_lane_lines(lines)
    rl_lines = filter_right_lane_lines(lines)
    draw_lines_in_image(image, ll_lines, (255, 0, 0), 2)
    draw_lines_in_image(image, rl_lines, (0, 0, 255), 2)
    print 'detected', len(ll_lines), 'left lanes'
    print 'detected', len(rl_lines), 'right lanes'
    cv2.imshow('Lanes in Image', image)
    cv2.waitKey(0)

def detect_ht_lanes_in_image(image_path, rho_accuracy, theta_accuracy, num_votes, min_len, max_gap):
    image = cv2.imread(image_path) ## read the image
    gray  = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) ## grayscale
    edges = cv2.Canny(gray, 50, 150, apertureSize=3) ## detect edges
    lines = cv2.HoughLinesP(edges, rho_accuracy, theta_accuracy, num_votes, min_len, max_gap) ## detect hough lines
    ll_lines = filter_left_lane_lines(lines)
    rl_lines = filter_right_lane_lines(lines)
    draw_lines_in_image(image, ll_lines, (255, 0, 0), 2)
    draw_lines_in_image(image, rl_lines, (0, 0, 255), 2)
    if(len(ll_lines)!=0 or len(rl_lines)!=0):
        cv2.imwrite(image_path[:-4] + '_lanes' + image_path[-4:], image)
    return (len(ll_lines), len(rl_lines))

def find_ll_rl_lanes_in_images_in_dir(imgdir, filepat, rho_acc, th_acc, num_votes, min_len, max_gap):
    files = generate_file_names(filepat, imgdir)
    for f in files:
        yield (f, detect_ht_lanes_in_image(f, rho_acc, th_acc, num_votes, min_len, max_gap))

def generate_file_names(fnpat, rootdir):
  for path, dirlist, filelist in os.walk(rootdir):
    for file_name in fnmatch.filter(filelist, fnpat):
        yield os.path.join(path, file_name)


def unit_test_01(x1, y1, x2, y2):
    print line_deg_angle(x1, y1, x2, y2)

def unit_test_02(image_path, num_votes, min_len, max_gap):
    display_ht_lanes_in_image(image_path, 1, numpy.pi/180, num_votes, min_len, max_gap)

def unit_test_03(image_path, rho_accuracy, theta_accuracy, num_votes, min_len, max_gap):
    ll, rl = detect_ht_lanes_in_image(image_path, rho_accuracy, theta_accuracy, num_votes, min_len, max_gap)
    print 'number of left lanes:', ll
    print 'number of right lanes:', rl

def unit_test_04(imgdir, filepat, rho_acc, th_acc, num_votes, min_len, max_gap):
    for fp, ll_rl in find_ll_rl_lanes_in_images_in_dir(imgdir, filepat, 1, numpy.pi/180,
                                         num_votes, min_len, max_gap):
       print fp, ll_rl[0], ll_rl[1]
    
## This is the new __main__
if __name__ == '__main__':
    #unit_test_01(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
    filename = "road_images/16_07_02_08_24_59_orig.png"
    num_votes = 25
    min_len = 200
    max_gap = 5
    # print "---plot_ht_lanes_in_image:", filename, " ---"
    # plot_ht_lanes_in_image(filename, 1, numpy.pi/180, num_votes, min_len, max_gap)
    # print "---unit_test_02---"
    # unit_test_02(filename, num_votes, min_len, max_gap)
    # print "---unit_test_03---"
    # unit_test_03(filename, 1, numpy.pi/180, num_votes, min_len, max_gap)
    print "---unit_test_04---"
    # unit_test_04("road_images", "*_orig.png", 1, numpy.pi/180, num_votes, min_len, max_gap)
    # 50 150 10
    unit_test_04(sys.argv[1], sys.argv[2], 1, numpy.pi/180, int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))
    pass




