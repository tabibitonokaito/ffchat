from pynput import keyboard
from typing import Callable
import time


class SystemKeyboard:
    def __init__(self):

        self.pressed_keys = set()
        self._on_key_press: Callable 
        self._on_key_release: Callable

        # Inicializar el listener
        self.listener = keyboard.Listener(
            on_press=self._on_press, # type: ignore
            on_release=self._on_release # type: ignore
        )

    def send_keystroke(self, keys):
        controller = keyboard.Controller()  # Crear una instancia de Controller
        for key in keys:
            if isinstance(key, str):
                controller.press(keyboard.KeyCode.from_char(key))
            else:
                controller.press(key)

        time.sleep(0.1)
        
        for key in reversed(keys):
            if isinstance(key, str):
                controller.release(keyboard.KeyCode.from_char(key))
            else:
                controller.release(key)

    def _on_press(self, key: keyboard.Key):
        self.pressed_keys.add(key)
        self._on_key_press(key)  # Delegar el manejo del evento a la función proporcionada

    def _on_release(self, key: keyboard.Key):
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)
        self._on_key_release(key)  # Delegar el manejo del evento a la función proporcionada
    def assign_functions(self, on_key_press: Callable[[keyboard.Key], None], 
                         on_key_release: Callable[[keyboard.Key], None]):
        self._on_key_press = on_key_press
        self._on_key_release = on_key_release

    def run(self):
        self.listener.start()

    def stop(self):
        self.listener.stop()

