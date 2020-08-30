import pywt
import matplotlib.pyplot as plt


def waveletLeafData(waveletPacket: pywt.WaveletPacket):
    leafData = list()
    leafNodes = [node.path for node in waveletPacket.get_level(
        waveletPacket.maxlevel, 'freq')]

    for node in leafNodes:
        bandData = waveletPacket[node].data
        leafData.extend(bandData)

    return leafData


def morphWaveletPacket(originalPacket: pywt.WaveletPacket, targetPacket=None, steps=1):
    if targetPacket == None:
        return originalPacket

    result = []
    morphed = pywt.WaveletPacket(
        data=None, wavelet='db8', mode='symmetric')
    leafNodes = [node.path for node in originalPacket.get_level(
        originalPacket.maxlevel, 'freq')]

    for node in leafNodes:
        originalData = originalPacket[node].data
        targetData = targetPacket[node].data
        dataDiff = originalData - targetData


def audioFromWavelets(wavelets: list()):
    audio = []
    for wavelet in wavelets:
        audio.extend(wavelet.reconstruct())

    return audio


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
