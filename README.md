# Audio De-noising 
A simple yet very powerful noise remover and reducer built in python.
The noise removed by using Wavelet Transform.

Wavelets has been very powerful tool to decompose the audio signal into parts and apply thresholds to eliminate
unwanted signal like noise. The thresholding method is the most important in the process of Audio De nosing.

The thresholding used is VisuShrink method or the universal threshold introduce by Donoho


## Execution
- Install the dependencies
    ```$ pip3 install -r requirements.txt```
- Use the denoise.py file
    ```python
    from denoise import AudioDeNoise 
    
    audioDenoiser = AudioDeNoise(inputFile="input.wav")
    audioDenoiser.deNoise(outputFile="input_denoised.wav")
    audioDenoiser.generateNoiseProfile(noiseFile="input_noise_profile.wav")
    ```

