"""
This class has two main functions

    - De-noising the file (pywt does it)
    - Creating a Noise Profile (parses the signal and creates a profile very memory heavy)
"""

import numpy as np
import pywt
import soundfile
from tqdm import tqdm

from lib.noiseProfiler import NoiseProfiler


def mad(arr):
    """ Median Absolute Deviation: a "Robust" version of standard deviation.
        Indices variability of the sample.
        https://en.wikipedia.org/wiki/Median_absolute_deviation 
    """
    arr = np.ma.array(arr).compressed()
    med = np.median(arr)
    return np.median(np.abs(arr - med))


class AudioDeNoise:
    """
    Class to de-noise the audio signal. The audio file is read in chunks and processed,
    cleaned and appended to the output file..

    It can de-noise multiple channels, any sized file, formats supported by soundfile

    Wavelets used ::
        Daubechies 4 : db4
        Level : decided by pyWavelets

    Attributes
    ----------
    __inputFile : str
        name of the input audio file

    Examples
    --------
    To de noise an audio file

    >>> audioDenoiser = AudioDeNoise("input.wav")
    >>> audioDenoiser.deNoise("input_denoised.wav")

    To generate the noise profile

    >>> audioDenoiser = AudioDeNoise("input.wav")
    >>> audioDenoiser.generateNoiseProfile("input_noise_profile.wav")
    """

    def __init__(self, inputFile):
        self.__inputFile = inputFile
        self.__noiseProfile = None

    def deNoise(self, outputFile):
        """
        De-noising function that reads the audio signal in chunks and processes
        and writes to the output file efficiently.

        VISU Shrink is used to generate the noise threshold

        Parameters
        ----------
        outputFile : str
            de-noised file name

        """
        info = soundfile.info(self.__inputFile)  # getting info of the audio
        rate = info.samplerate

        with soundfile.SoundFile(outputFile, "w", samplerate=rate, channels=info.channels) as of:
            for block in tqdm(soundfile.blocks(self.__inputFile, int(rate * info.duration * 0.10))):
                coefficients = pywt.wavedec(block, 'db4', mode='per')

                #  getting variance of the input signal
                sigma = mad(coefficients[- 1])

                # VISU Shrink thresholding by applying the universal threshold proposed by Donoho and Johnstone
                thresh = sigma * np.sqrt(2 * np.log(len(block)))

                # thresholding using the noise threshold generated
                coefficients[1:] = (pywt.threshold(i, value=thresh, mode='soft') for i in coefficients[1:])

                # getting the clean signal as in original form and writing to the file
                clean = pywt.waverec(coefficients, 'db4', mode='per')
                of.write(clean)

    def generateNoiseProfile(self, noiseFile):
        """
        Parses the input signal and generate the noise profile using wavelet helper
        Look into lib modules to see how the parsing is done

        NOTE: Heavy on the memory, suitable for small files.

        Parameters
        ----------
        noiseFile : str
            name for the noise signal extracted
        """
        data, rate = soundfile.read(noiseFile)
        self.__noiseProfile = NoiseProfiler(noiseFile)
        noiseSignal = self.__noiseProfile.getNoiseDataPredicted()

        soundfile.write(noiseFile, noiseSignal, rate)

    def __del__(self):
        """
        clean up
        """
        del self.__noiseProfile
