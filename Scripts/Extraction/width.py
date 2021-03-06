# Extract the width of the signal based on the raw squiggle time series
# Requires access to spectrogram images

import numpy as np
from PIL import Image
from scipy.ndimage import filters
import sys
import os

# 0 = black, 255 = white
def parseData(filename, paths):
    f = open(filename)
    for line in f:
        if "2014" in line: #ID
            continue

        breakpt = line.find(":")

        ts = line[:breakpt]
        paths.append([int(num) for num in ts.strip().split()])
    f.close()
    paths = np.array(paths)

def main():
    t = 5 #bandwidth

    # Build path matrix: each row is the path
    paths = []
    parseData("./DATA/squiggle_ts.txt", paths)
    count = 0

    width_vector = np.zeros(833)
    for fn in os.listdir("./SquiggleExamples/"):
        print(fn)
        #print(count)

        if "2014" not in fn:
            continue #pass this hidden file

        filename = "SquiggleExamples/" + fn
        img = Image.open(filename)

        # Convert to grayscale if necessary
        # img = img.convert("L")

        col,row =  img.size

        intensities = np.zeros((row, col))
        pixels = img.load()

        # print(row, col)
        for i in range(row):
            for j in range(col):
                #print(i, j)
                intensity =  pixels[j,i]
                intensities[i,j] = intensity

        # Find width/thickness for each row
        path = paths[count]
        widths = np.zeros(129)

        for row_index in range(129):

            targetpt = path[row_index]
            threshold = intensities[row_index,targetpt]//2

            upper = targetpt+5
            lower = targetpt-5

            #print(targetpt)
            #print(threshold)
            # upwards
            for neighbor_index in range(min(targetpt+1,767),min(targetpt+6,767)):
                #print(neighbor_index)

                if (intensities[row_index,neighbor_index] < threshold): #find first index under threshold, stop there
                    upper = neighbor_index
                    break

            # downwards
            for neighbor_index in reversed(range(max(0,targetpt-5),targetpt)):
                #print(neighbor_index)

                if (intensities[row_index,neighbor_index] < threshold): #find first index under threshold, stop there
                    lower = neighbor_index
                    break

            width = upper - lower + 1
            widths[row_index] = width
            #print(upper, lower)

        #width_vector[count] = np.median(widths)

        widths = np.sort(widths)
        iqr_average = np.mean( widths[round(0.25*len(widths)) : round(0.75*len(widths)) ])
        width_vector[count] = iqr_average
        count += 1

    print(width_vector)

    outputFile = open("width_squiggle.txt",'w')
    for width in width_vector:
        outputFile.write("{0}\n".format(width))

if __name__ == "__main__":
    main()
