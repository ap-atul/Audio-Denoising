"""
A class to keep:
1) the window's raw data
2) the window's max(abs(data))

To be utilized to later extract the level that was surpassed the x% of the time
"""

import math

import numpy
import pywt


class WindowBundle:
    def __init__(self, data: numpy, id):
        self.id = id
        self.data = data
        self.rms = None
        self.waveletPacket = None
        self.noiseWindow = None
        self.denoisedData = []

        self.dbName = None
        self.wlevels = None

    def extractWaveletPacket(self, dbName, wlevels):
        if self.waveletPacket is not None:
            return self.waveletPacket

        self.dbName = dbName
        self.wlevels = wlevels
        self.waveletPacket = pywt.WaveletPacket(
            self.data, dbName, 'symmetric', wlevels)

        return self.waveletPacket

    def getWaveletLeafData(self):
        windowWaveletData = list()
        leafNodes = [node.path for node in self.waveletPacket.get_level(
            self.wlevels, 'freq')]

        for node in leafNodes:
            bandData = self.waveletPacket[node].data
            windowWaveletData.extend(bandData)

        return windowWaveletData

    def setDenoisedData(self, denoisedData):
        self.denoisedData = denoisedData

    def getDenoisedData(self):
        return self.denoisedData

    def setNoiseWindow(self, window):
        self.noiseWindow = window

    def isBelowThreshold(self, threshold):
        if self.getRMS() < threshold:
            return True

        return False

    def getData(self):
        return self.data

    def getRMS(self):
        if self.rms is not None:
            return self.rms

        squaredSum = numpy.sum(numpy.power(self.data, 2))
        self.rms = math.sqrt(squaredSum / len(self.data))

        return self.rms

    # gets the Mean Absolute
    def getMA(self):
        _sum = numpy.sum(numpy.abs(self.data))
        ma = _sum / len(self.data)

        return ma

    def getRMSasArray(self):
        return self.getRMS() * numpy.ones(len(self.data))

    @staticmethod
    def joinDenoisedData(windows: list):
        result = []
        for window in windows:
            result.extend(window.denoisedData)

        return result

    @staticmethod
    def joinData(windows: list):
        result = []
        for window in windows:
            result.extend(window.data)

        return result

    @staticmethod
    def joinNoiseData(windows: list):
        result = []
        for window in windows:
            result.extend(window.noiseWindow.data)

        return result
