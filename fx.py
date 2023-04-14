from pedalboard import Compressor, Gain, Pedalboard, Chorus, Distortion, Reverb, PitchShift, Delay, Mix, Limiter
from pedalboard.io import AudioFile
import numpy as np
import openai
import re
import os

ranger = iter(range(1, 31))

openai.api_key = os.environ.get('KEY_PT')

#########
## Audio I/O ##
#########

def set_input(f_name = '/content/drive/MyDrive/Pedalboard Experiment/Dry Guitar.wav'):
  """
  Takes in an audio file as a file-path string, returns an AudioFile object.
  Use this method to select and sample the input file for processing.

    Parameters:
        f_name (str): Valid file path pointing to the "dry" audio.

    Returns:
        audio: AudioFile object that can be processed and exported via pedalboard.io
  """
  with AudioFile(f_name) as f:
    audio = f.read(f.frames)
  return audio
  
def write_output(input_audio, f_name, p_board, samplerate = 44100):
  """
  Takes in an AudioFile object, a valid path name, a Pedalboard object and
  (optionally) a desired sample rate. Applies the Pedalboard effects to
  the audio and exports it to the specified path name.

    Parameters:
        input_audio (AudioFile): Object representing dry audio for processing.
        f_name (str): File path specifying the output destination for processed or "wet" audio.
        p_board (Pedalboard): Object representing effects chain to be applied.
        samplerate (float): Sampling rate to be used for the export.

    Returns:
        effected (AudioFile): Object containing processed or "wet" audio.
  """
  effected = p_board(input_audio, samplerate)
  with AudioFile(f_name, 'w', samplerate, effected.shape[0]) as f:
    f.write(effected)
  return effected

#########
## Placeholder Genre Presets ##
#########

# Creating an empty pedalboard object that will ultimately contain all of our "effects".
board = Pedalboard()

# Designing pedalboards for specific genre requests that can later be concatenated for a "composite" sound.
def jazz(x):
  return Mix([
    Chorus(rate_hz = 8, mix = x / 100, depth = 0.2),
  ])

def prog(x):
  return Mix([
    Compressor(threshold_db = 10, ratio = 1, attack_ms = 15),
    Chorus(rate_hz = 20),
    Gain(gain_db = x/10),
    ])

def indie(x):
  return Mix([
    Chorus(rate_hz = 30, mix = 1, depth = 0.6 * (x/100)), Gain(gain_db = 40 * (x/100))
    ])

octaver = Mix([PitchShift(semitones = -12), Distortion(drive_db = 8), Compressor(threshold_db = 15)])

def metal(x):
  return Mix([
    Compressor(threshold_db = 5, ratio = 1.2),
    Gain(gain_db = 8),
    Distortion(drive_db = 15)
  ])

def reverb(x):
  return Reverb(room_size = 0.2, damping = 0.6, wet_level = min(1, x/100 + 0.3), dry_level = 0.7)

pedals = {
  "Jazz": jazz, 
  "Prog": prog,
  "Indie": indie,
  "Metal": metal,
  "Reverb": reverb
}


"""
Enter desired properties below.
Available sounds: 0: Jazz, 1: 60s Gain, 2: Both
"""
"""
def modify_board(p_board, option):
    option = int(option)
    if option == 0:
        p_board.append(Mix([jazz, Reverb()]))
    elif option == 1:
        p_board = (Mix([Compressor(threshold_db = -50, ratio = 25), prog]))
    else:
        p_board = Pedalboard([
            Compressor(threshold_db = -50, ratio = 25), 
            Mix([jazz, prog]), 
            Reverb()])
    return p_board
"""

#########
## OOP Implementation of Generated Pedal ##
#########

system_prompt = "Take in a 5 word prompt from the user and return a comma-separated list of its percentage closeness to 5 musical genres: Jazz, Metal, Prog, Indie, Reverb. Answers must add up to 100%."
class BoardGenerator:
  def __init__(self, input_text):
    self.input_text = input_text
    self.board = Pedalboard()
    self.weights = self.get_weights()
    self.board = self.make_board()

  def get_weights(self):
    user_token = self.input_text
    completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_token}
      ],
      max_tokens = 40
    )
    response = completion.choices[0].message["content"]
    self.gpt_response = response
    print("user token: " + str(user_token) + " || gpt response: " + str(response))
    percentage_pattern = re.compile(r"\d+%")
    percentage_values = percentage_pattern.findall(response)
    percentages = [int(value[:-1]) for value in percentage_values]
    return percentages

  def make_board(self):
    for i in range(5):
      if self.weights[i] > 10:
        self.board.append(list(pedals.values())[i](self.weights[i]))
    return self.board
