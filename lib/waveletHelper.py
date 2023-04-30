import pywt
import matplotlib.pyplot as plt

'''
WaveletPacket object is a tree data structure, which evaluates to a set of Node objects. 
WaveletPacket is just a special subclass of the Node class (which in turn inherits from the BaseNode).
Tree nodes can be accessed using the obj[x] (Node.__getitem__()) operator. 
Each tree node has a set of attributes: data, path, node_name, parent, level, maxlevel and mode.
'''
'''
Wavelet Packet nodes are arranged in a tree. Each node in a WP tree is uniquely identified and addressed by a path string.
In the 1D WaveletPacket case nodes were accessed using 'a' (approximation) and 'd' (details) path names (each node has two 1D children).
 WaveletPacket.get_level() also performs automatic decomposition until it reaches the specified level.
 Tree - https://www.researchgate.net/figure/Wavelet-Packet-Decomposition-Tree_fig1_331045743
'''

def waveletLeafData(waveletPacket: pywt.WaveletPacket):
    leafData = list()
    leafNodes = [node.path for node in waveletPacket.get_level(
        waveletPacket.maxlevel, 'freq')]

    for node in leafNodes:
        bandData = waveletPacket[node].data
        leafData.extend(bandData)

    return leafData

'''
plt.figure(): This creates a new figure for the plot.
subplotIdx = 1: This initializes the subplot index to 1.
leafNodes = [node.path for node in wavelets[0].get_level(wavelets[0].maxlevel, 'natural', False)]: This gets a list of leaf node paths for the first pywt.WaveletPacket object in the list wavelets. The get_level method is used to get all the leaf nodes at the maximum level of decomposition, and the path attribute of each node is extracted.
for wavelet in wavelets:: This iterates over each pywt.WaveletPacket object in the input list wavelets.
plt.subplot(len(wavelets), 1, subplotIdx): This creates a new subplot for the current pywt.WaveletPacket object in the list. The first argument specifies the total number of rows in the plot (which is the length of the wavelets list), the second argument specifies the number of columns (which is 1 in this case), and the third argument specifies the index of the current subplot.
for node in leafNodes:: This iterates over each leaf node path in leafNodes.
bandData = wavelet[node].data: This gets the data for the current leaf node in the current pywt.WaveletPacket object.
bandLength = len(bandData): This gets the length of the data for the current leaf node.
rangeArr = range(bandIdx * bandLength, (bandIdx + 1) * bandLength): This creates a range of indices for the x-axis of the plot, where bandIdx is the index of the current leaf node.
plt.plot(rangeArr, bandData): This plots the data for the current leaf node using the indices from rangeArr as the x-axis and the data from bandData as the y-axis.
bandIdx += 1: This increments the index of the current leaf node.
subplotIdx += 1: This increments the subplot index for the current pywt.WaveletPacket object.
'''

def plotWavelets(wavelets: list):
    plt.figure()
    subplotIdx = 1
    leafNodes = [node.path for node in wavelets[0].get_level(
        wavelets[0].maxlevel, 'natural', False)]

    for wavelet in wavelets:
        plt.subplot(len(wavelets), 1, subplotIdx)
        bandIdx = 0
        for node in leafNodes:
            bandData = wavelet[node].data
            bandLength = len(bandData)
            rangeArr = range(bandIdx * bandLength, (bandIdx + 1) * bandLength)
            plt.plot(rangeArr, bandData)
            bandIdx += 1
        subplotIdx += 1
    plt.show()
