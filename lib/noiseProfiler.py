"""
Class to create a noise profile from an audio input
"""
import numpy
import matplotlib.pyplot as plt
import math
from lib import windowBundle, waveletHelper
from lib.linkedList import LinkedList


class NoiseProfiler:
    """Basic denoiser wrapper for keeping store of the settings"""

    def __init__(self, x, timeWindow=0.1, sampleRate=44100, percentileLevel=95, wlevels=4, dbName='db8'):
        self.x = x
        self.timeWindow = timeWindow
        self.windowSamples = int(timeWindow * sampleRate)
        self.wlevels = wlevels
        self.dbName = dbName

        self.windows = list()
        self.sortedWindows = list()

        self.noiseWindows = None
        self.noiseLinked = LinkedList()
        self.signalWindows = None
        self.signalLinked = LinkedList()

        self.percentileLevel = percentileLevel
        self.noiseData = None
        self.noiseWavelets = list()
        self.threshold = None

        self.extractWindows()
        print("Noise profiler finished")

    def cleanUp(self):
        self.windows = None
        self.sortedWindows = None
        self.noiseData = None
        self.noiseLinked = None
        self.signalLinked = None
        self.signalWindows = None
        self.noiseWavelets = None

    def drawOriginalVsNoiseAndSingal(self):
        self.threshold = self.extractRMSthresholdFromWindows(
            self.percentileLevel)
        self.extractSignalAndNoiseWindows(self.threshold)

        noiseData = self.getDataOrZeroFromPartialWindows(
            self.windows, self.noiseWindows)
        signalData = self.getDataOrZeroFromPartialWindows(
            self.windows, self.signalWindows)

        rmsEnvelope = self.getWindowsRMSasEnvelope()

        plt.figure(1)
        plt.subplot(211)
        plt.plot(self.x)
        plt.subplot(211)
        plt.plot(rmsEnvelope)
        plt.plot(-1 * rmsEnvelope)
        plt.subplot(212)
        plt.plot(signalData)
        plt.plot(noiseData)
        plt.show()

    # Generally in each iteration we return the current window plus what's missing from the past
    # except if we are at the last noise window: then we have to care for the
    # missing future windows
    def __getPredictedDataBetweenNoiseWindows(self, currentWindow, prevWindow, nextWindow):
        result = []
        if prevWindow is None:
            # it's the first noise window, so return this (replicated enough
            # times)
            numberToFill = currentWindow.id + 1
            for i in range(numberToFill):
                result.extend(currentWindow.data)
        elif nextWindow is None:
            # if we're missing some windows from the end, pad/duplicate
            nWindows = len(self.windows)
            numberToFill = nWindows - currentWindow.id
            for i in range(numberToFill):
                result.extend(currentWindow.data)
        else:
            # we are between two noise windows
            numberToFill = currentWindow.id - prevWindow.id
            # TODO make some
            for i in range(numberToFill):
                result.extend(currentWindow.data)

        return result

    def __getPredictedDataBetweenNoiseNodes(self, currNode, prevNode, nextNode):
        result = []
        if prevNode is None:
            # it's the first noise window, so return this
            currentWindow = currNode.data
            numberToFill = currentWindow.id + 1
        return result

    def __getWindowIndexInList(self, needle, haystack):
        pos = 0
        for candidate in haystack:
            if candidate == needle:
                return pos
            pos += 1

        return -1

    def __getUpToNConsecutiveWindows(self, lastWindow, windowList, n):
        result = []
        result.append
        windowIndex = self.__getWindowIndexInList(lastWindow, windowList)

    # def __circularPadWindow(self, window, windowList, times):

    def getNoiseOrZero(self):
        self.threshold = self.extractRMSthresholdFromWindows(
            self.percentileLevel)
        self.extractSignalAndNoiseWindows(self.threshold)

        noiseData = []
        for noiseNode in self.noiseLinked.getAsList():
            window = noiseNode.data
            if window is None:
                noiseData.extend(numpy.zeros(self.windowSamples))
            else:
                noiseData.extend(window.data)

        return noiseData

    def __getNodesWindowData(self, nodes):
        data = []
        for node in nodes:
            window = node.data
            data.extend(window.data)

        return data

    def __getNodeCircularPrediction(self, node, n):
        prevNode = node.getPrevWithValidData()
        nextNode = node.getNextWithValidData()
        if prevNode is None:
            # work with current->future period of silence
            return self.__getFutureCircularNodes(nextNode, n)
        # working with the previous period of silence
        return self.__getPastCircularNodes(prevNode, n)

    def __getFutureCircularNodes(self, initialNode, n):
        ret = []
        count = 0
        current = initialNode
        while True:
            ret.append(current)
            count += 1
            if count == n:
                return ret

            if current.next and current.next.data:
                current = current.next
            else:
                current = initialNode

    def __getPastCircularNodes(self, initialNode, n):
        ret = []
        count = 0
        current = initialNode
        while True:
            ret.append(current)
            count += 1
            if count == n:
                return ret

            if current.prev and current.prev.data:
                current = current.prev
            else:
                current = initialNode

    def getNoiseDataPredicted(self):
        self.threshold = self.extractRMSthresholdFromWindows(
            self.percentileLevel)
        self.extractSignalAndNoiseWindows(self.threshold)

        noiseDataPredicted = []

        consecutiveEmptyNodes = 0
        lastValidNode = None
        for node in self.noiseLinked.getAsList():
            if node.data is None:
                consecutiveEmptyNodes += 1
            else:
                lastValidNode = node

                if consecutiveEmptyNodes != 0:
                    predictedNodes = self.__getNodeCircularPrediction(
                        node, consecutiveEmptyNodes)
                    noiseDataPredicted.extend(self.__getNodesWindowData(predictedNodes))
                    consecutiveEmptyNodes = 0

                window = node.data
                noiseDataPredicted.extend(window.data)

        # in case we had empty data on the end
        if consecutiveEmptyNodes != 0:
            predictedNodes = self.__getNodeCircularPrediction(
                lastValidNode, consecutiveEmptyNodes)
            noiseDataPredicted.extend(self.__getNodesWindowData(predictedNodes))

        self.cleanUp()
        return noiseDataPredicted

    def __getPreviousNoiseWindowFromLinkedList(self, node):
        prevNode = node.getPrevWithValidData()
        if prevNode is not None:
            return prevNode.data
        return None

    def __getNextNoiseWindowFromLinkedList(self, node):
        nextNode = node.getNextWithValidData()
        if nextNode is not None:
            return nextNode.data
        return None

    def extractRMSthresholdFromWindows(self, percentileLevel):
        if self.threshold is not None:
            return self.threshold

        sortedWindows = sorted(
            self.windows, key=lambda x: x.getRMS(), reverse=True)
        # now the are arranged with the max DESC
        nWindows = len(sortedWindows)
        thresholdIndex = math.floor(percentileLevel / 100 * nWindows)
        self.threshold = sortedWindows[thresholdIndex].getRMS()

        return self.threshold

    def getWindowsRMSasEnvelope(self):
        envelope = numpy.array([])
        """
        :type self.windows: list[windowBundle]
        """
        for window in self.windows:
            windowEnvelope = window.getRMS() * numpy.ones(len(window.data))
            envelope = numpy.concatenate([envelope, windowEnvelope])

        return envelope

    def extractWindows(self):
        xLength = len(self.x)
        nWindows = math.ceil(xLength / self.windowSamples)
        lastWindowPaddingSamples = xLength - nWindows * self.windowSamples
        for i in range(0, nWindows):
            windowBeginning = i * self.windowSamples
            windowEnd = windowBeginning + self.windowSamples
            windowData = self.x[windowBeginning:windowEnd]
            # checking wether we need to pad the last band
            if (i == nWindows - 1 and windowEnd - windowBeginning < self.windowSamples):
                paddingLength = windowEnd - windowBeginning - self.windowSamples
                paddingArray = numpy.zeros(paddingLength)
                windowData = numpy.concatenate(windowData, paddingArray)
            window = windowBundle.WindowBundle(windowData, i)
            self.windows.append(window)

    def extractSignalAndNoiseWindows(self, rmsThreshold):
        if self.noiseWindows is not None and self.signalWindows is not None:
            return

        self.noiseWindows = list()
        self.signalWindows = list()
        for window in self.windows:
            # giving a +5% grace on the rms threshold comparison
            if window.getRMS() < (rmsThreshold + 0.05 * rmsThreshold):
                self.noiseWindows.append(window)
                self.noiseLinked.append(window)
                self.signalLinked.append(None)
            else:
                self.signalWindows.append(window)
                self.signalLinked.append(window)
                self.noiseLinked.append(None)

    def getDataOrZeroFromPartialWindows(self, allWindows, partialWindows):
        data = []
        idx = 0
        for window in allWindows:
            if idx < len(partialWindows) and window == partialWindows[idx]:
                data.extend(window.data)
                idx += 1
            else:
                data.extend(numpy.zeros(self.windowSamples))

        return data

    def extractWavelets(self):
        for window in self.windows:
            window.extractWaveletPacket(self.dbName, self.wlevels)

    def plotWavelets(self):
        wtBandsLength = 0
        for window in self.windows:
            windowWaveletData = list()

            windowDataLength = 0
            data = window.getData()
            wt = window.extractWaveletPacket(self.dbName, self.wlevels)
            leafNodes = [node.path for node in wt.get_level(
                self.wlevels, 'freq')]

            for node in leafNodes:
                bandData = wt[node].data
                windowWaveletData.extend(bandData)
                wtBandsLength += len(bandData)
                windowDataLength += len(bandData)

            print("window # " + str(window.id) +
                  " of " + str(len(self.windows)))
            plt.figure(window.id)
            plt.subplot(211)
            plt.plot(window.data)
            plt.subplot(212)
            plt.plot(waveletHelper.waveletLeafData(window.waveletPacket))
            plt.show()
