
import piper
import inspect

print("Attributes of piper:")
print(dir(piper))

if hasattr(piper, 'PiperVoice'):
    print("\nAttributes of piper.PiperVoice:")
    print(dir(piper.PiperVoice))
    print("\nHelp on piper.PiperVoice:")
    # print(help(piper.PiperVoice)) 
