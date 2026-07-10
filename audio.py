import pygame
import numpy as np
from scale import note_to_frequency
import wave
recording = False

record_buffer = []

# 初始化声音

pygame.mixer.init(
    frequency=44100,
    size=-16,
    channels=2
)


def speed_to_frequency(speed):

    # 限制范围

    speed = max(
        0,
        min(speed,100)
    )


    # 速度映射频率

    frequency = (
        200 +
        speed * 6
    )

    return frequency



def create_sound(
        frequency,
        duration=0.1,
        instrument="sine",
        volume=0.9
):

    sample_rate = 44100


    t = np.linspace(
        0,
        duration,
        int(sample_rate * duration),
        False
    )


    # 正弦波
    wave = generate_wave(
        frequency,
        duration,
        instrument
    )

    wave = apply_envelope(
        wave
    )# 简单混响

    delay = int(len(wave)*0.25)

    echo = np.zeros_like(wave)

    echo[delay:] = wave[:-delay] * 0.25

    wave = wave + echo




    # 转16位

    audio = (
        wave * 32767*volume
    ).astype(np.int16)


    # 单声道复制成左右声道

    audio = np.column_stack(
        (
            audio,
            audio
        )
    )


    sound = pygame.sndarray.make_sound(
        audio
    )


    return sound


def create_sound_from_wave(
        wave,
        volume=0.5
):

    audio = (
        wave * 32767 * volume
    ).astype(np.int16)


    audio = np.column_stack(
        (
            audio,
            audio
        )
    )


    sound = pygame.sndarray.make_sound(
        audio
    )


    return sound


def play_speed_sound(speed):

    frequency = speed_to_frequency(speed)

    sound = create_sound(
        frequency,
        0.5
    )

    sound.play()

speed=50
def play_note(note,instrument="sine",volume=0.5):
    frequency = note_to_frequency(note)

    sound = create_sound(
        frequency,
        0.15,
        instrument,
        volume
    )

    if recording:
        wave = generate_wave(
            frequency,
            0.15,
            instrument
        )

        wave = apply_envelope(
            wave
        )

        record_buffer.append(
            wave * volume
        )
    sound.play()


def play_chord(
        notes,
        instrument="pad",
        volume=0.3
):

    duration = 0.8

    waves = []


    for note in notes:

        frequency = note_to_frequency(note)


        wave = generate_wave(
            frequency,
            duration,
            instrument
        )


        wave = apply_envelope(
            wave
        )


        waves.append(wave)



    # 波形叠加

    chord_wave = sum(waves)


    # 防止爆音

    chord_wave = np.clip(
        chord_wave,
        -1,
        1
    )

    sound = create_sound_from_wave(
        chord_wave,
        volume
    )

    if recording:
        record_buffer.append(chord_wave * volume)

    sound.play()


def generate_wave(
        frequency,
        duration,
        instrument="sine"
):

    sample_rate = 44100

    t = np.linspace(
        0,
        duration,
        int(sample_rate*duration),
        False
    )

    if instrument == "piano":

        wave = (
                1.0 * np.sin(
            2 * np.pi * frequency * t
        )
                +
                0.5 * np.sin(
            2 * np.pi * frequency * 2 * t
        )
                +
                0.25 * np.sin(
            2 * np.pi * frequency * 3 * t
        )
                +
                0.1 * np.sin(
            2 * np.pi * frequency * 5 * t
        )
        )


    elif instrument=="pad":

        wave = (
            np.sin(
                2*np.pi*frequency*t
            )
            +
            0.15*np.sin(
                2*np.pi*frequency*2*t
            )
        )


    elif instrument=="bell":

        wave = (
            np.sin(
                2*np.pi*frequency*t
            )
            +
            0.3*np.sin(
                2*np.pi*frequency*4*t
            )
        )


    else:

        wave = np.sin(
            2*np.pi*frequency*t
        )


    return wave

def apply_envelope(wave):

    length = len(wave)

    envelope = np.ones(length)


    attack = int(length * 0.05)
    release = int(length * 0.3)


    # 淡入
    envelope[:attack] = np.linspace(
        0,
        1,
        attack
    )


    # 淡出
    envelope[-release:] = np.linspace(
        1,
        0,
        release
    )


    return wave * envelope


def save_record(filename="music.wav"):

    global record_buffer

    if len(record_buffer) == 0:
        return


    data = np.concatenate(
        record_buffer
    )

    # 加速 1.25 倍

    speed = 1.25

    new_length = int(
        len(data) / speed
    )

    data = np.interp(
        np.linspace(
            0,
            len(data),
            new_length
        ),
        np.arange(len(data)),
        data
    )




    data = np.clip(
        data,
        -1,
        1
    )


    data = (
        data * 32767
    ).astype(np.int16)


    with wave.open(
        filename,
        "wb"
    ) as f:

        f.setnchannels(1)

        f.setsampwidth(2)

        f.setframerate(44100)

        f.writeframes(
            data.tobytes()
        )


    print(
        "保存声音:",
        filename
    )