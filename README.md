# Audio De-noising 
A simple yet very powerful noise remover and reducer built in python.
The noise removed by using Wavelet Transform.

Can reduce noise from multiple format files and multi channels (mono, stereo)

The code is very robust, can process very large files without consuming 
huge amount og memory.
Tested with GB > files.

## Packages required
* pywt : Python wavelets library has various no of wavelet implementations.
* numpy
* soundfile : to read and write audio files.
* matplotlib
* tqdm : progress bar.

### Execution
1. Add the path of the audio file in the main.py file.
2. Run the main.py (python 3).
3. Call any of the functions.
4. Doc string explains what each part does.
