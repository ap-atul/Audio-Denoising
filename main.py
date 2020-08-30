import numpy as np
import pywt
import soundfile
from tqdm import tqdm
from lib.noiseProfiler import NoiseProfiler

inputFile = "example/example.wav"
outputFile = "example/example_denoised.wav"


def mad(arr):
    """ Median Absolute Deviation: a "Robust" version of standard deviation.
        Indices variabililty of the sample.
        https://en.wikipedia.org/wiki/Median_absolute_deviation 
    """
    arr = np.ma.array(arr).compressed()
    med = np.median(arr)
    return np.median(np.abs(arr - med))


def doAll():
    """
    read the file once and de-noised it once
    Useful with small files but for big files,
    you might run out of memory, use below function
    fot big files.
    :return: write the de-noised file
    """
    data, rate = soundfile.read(inputFile)
    print(len(data))
    coefficients = pywt.wavedec(data, 'db4', mode='per')
    sigma = mad(coefficients[- 1])

    thresh = sigma * np.sqrt(2 * np.log(len(data)))
    coefficients[1:] = (pywt.threshold(i, value=thresh, mode='soft') for i in coefficients[1:])

    clean = pywt.waverec(coefficients, 'db4', mode='per')
    soundfile.write(outputFile, clean, rate)


def doStep():
    """
    reads the file in bits of 10% at one time, and saves
    the chunks in array. Write at the end when all chunks
    are processed.
    Useful for big audio files.
    As the size of chunk is reduced the processing will take longer
    :return:
    """
    info = soundfile.info(inputFile)  # getting info of the audio
    rate = info.samplerate
    cleanSignal = np.array([])
    for block in tqdm(soundfile.blocks(inputFile, int((rate * info.duration) * 0.10))):
        if len(block.shape) > 1:
            block = block.T[0]
        coefficients = pywt.wavedec(block, 'db4', mode='per')
        sigma = mad(coefficients[- 1])

        thresh = sigma * np.sqrt(2 * np.log(len(block)))
        coefficients[1:] = (pywt.threshold(i, value=thresh, mode='soft') for i in coefficients[1:])

        cleanSignal = np.concatenate([cleanSignal, pywt.waverec(coefficients, 'db4', mode='per')])

    soundfile.write(outputFile, np.array(cleanSignal, dtype=float), rate)


def genNoiseProfile():
    """
    takes an audio file and generates a noise profile for the audio
    file, so the output of this function would be noise audio file
    you can use the noise profile to mask the original audio
    CAUTION :: it is very memory hungry code
    :return: write a audio file
    """
    data, rate = soundfile.read(inputFile)
    noiseProfile = NoiseProfiler(inputFile)
    noiseSignal = noiseProfile.getNoiseDataPredicted()

    soundfile.write("noise.wav", noiseSignal, rate)


# call function
doStep()
# doAll()
