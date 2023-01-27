# -*- coding: utf-8 -*-
import mido
import ctypes

# Ключ - номер клавиши MIDI
# Значение - Скан-код клавиши клавиатуры ПК
assignedInputs = {
    54: 0x11,  # W
    53: 0x1F,  # S
    50: 0x1E,  # A
    57: 0x20,  # D
    48: 0x39  # Space
}

# Код управления клавиатурой взят по ссылке
# https://stackoverflow.com/a/23468236/12953156
SendInput = ctypes.windll.user32.SendInput
PUL = ctypes.POINTER(ctypes.c_ulong)


class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]


class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]


class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]


def PressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def ReleaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


activeKeys = []
with mido.open_input() as midiDevice:
    for msg in midiDevice:
        try:
            if msg.type == 'note_on' and assignedInputs[msg.note] not in activeKeys:
                activeKeys.append(assignedInputs[msg.note])
                PressKey(assignedInputs[msg.note])
            elif msg.type == 'note_off' and assignedInputs[msg.note] in activeKeys:
                activeKeys.remove(assignedInputs[msg.note])
                ReleaseKey(assignedInputs[msg.note])
        except KeyError:
            pass
