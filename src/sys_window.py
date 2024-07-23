from typing import List, Optional, Union
import wmctrl
import Xlib.display
import Xlib.X
from enum import Enum

"""
Mejora en un futuro: mejorar window para que no cree variables individuales sino que
utilice la data del array copiado. De esta manera nada puede fallar y todo va mucho
más rápido
"""

class IdFormat(Enum):
    INT = 1
    HEX = 2
    HEX8 = 4


class IdConverter(Enum):
    @staticmethod
    def convert(
        values: List[Union[str, int]],
        *,
        input: IdFormat,
        output: IdFormat,
    ):
        int_values = IdConverter._convert_to_int(values, input)

        # format to output 
        result = []
        if output == IdFormat.HEX:
            result.extend(IdConverter._convert_to_hex(int_values))
        elif output == IdFormat.HEX8:
            result.extend(IdConverter._convert_to_hex10(int_values))
        else:
            result = int_values
        
        return result

    @staticmethod
    def _convert_to_int(values: List[Union[int, str]], input: IdFormat):
        result = []
        for value in values:
            if isinstance(value, int):
                result.append(value)
            elif input == IdFormat.INT:
                result.append(int(value))
            else:
                result.append(int(value, 16))
        return result

    @staticmethod
    def _convert_to_hex(values: List[int]) -> List[str]:
        result = []
        for value in values:
            result.append(hex(value))
        return result

    @staticmethod
    def _convert_to_hex10(values: List[int]) -> List[str]:
        result = []
        for value in values:
            result.append(f'0x{value:08x}')
        return result


def get_active(format: IdFormat):
    active_id = disp.get_input_focus().focus.id
    return IdConverter.convert([active_id],input=IdFormat.INT, output=format)[0]


disp = Xlib.display.Display()
root = disp.screen().root


class WMWindow:
    def __init__(self, *, wmctrl_data: wmctrl.Window):
        self._data = wmctrl_data 

    def get_id(self, format: Union[IdFormat, None] = None):
        if format is not None:
            return IdConverter.convert([self.get_id()], input=IdFormat.HEX8, output=format)[0]

        return self._data.id
    
    def get_desktop(self):
        return self._data.desktop

    def get_x(self):
        return self._data.x

    def get_y(self):
        return self._data.y

    def get_w(self):
        return self._data.w

    def get_h(self):
        return self._data.h

    def get_name(self):
        return self._data.wm_name

    def get_class(self):
        return self._data.wm_class

    def get_active(self):
        return self.get_id(format=IdFormat.HEX8) == get_active(format=IdFormat.HEX8) 

    # def get_host(self):
    #     return self.host
    #
    # def get_wm_window_role(self):
    #     return self._wm_window_role
    #
    # def get_wm_state(self):
    #     return self._wm_state

    def __str__(self):
        msg = ""
        msg += f"id={self.get_id()}"
        msg += f", desktop={self.get_desktop()}"
        msg += f", x={self.get_x()}"
        msg += f", y={self.get_y()}"
        msg += f", w={self.get_w()}"
        msg += f", h={self.get_h()}"
        msg += f", wm_name={self.get_name()}"
        msg += f", wm_class={self.get_class()}"
        msg += f", active={self.get_active()}"
        # msg += f", host={self.host}"
        # msg += f", _wm_window_role={self._wm_window_role}"
        # msg += f", _wm_state={self._wm_state}"
        return msg


class WindowManager:
    def __init__(self):
        self.windows = {}
        self._updating = False

    def update(self) -> None:
        try:
            # print(f"Invocamos a update WindowManager")
            if self._updating:
                print("Update already in progress. Abandoning new update call.")
                return
        
            self._updating = True
            # Intentar obtener la lista de ventanas
            found_windows = wmctrl.Window.list()
            
            self.windows.clear()  # Limpiar el diccionario actual de ventanas
            for wmctrl_data in found_windows:
                self.windows[wmctrl_data.id] = WMWindow(wmctrl_data=wmctrl_data)

            # print(f"actualizado con {found_windows}")

        except Exception as e:
            # Capturar y manejar cualquier excepción que pueda ocurrir
            print(f"Error updating windows: {e}")
        finally:
            self._updating = False

    def find(self, tid: Optional[str] = None, tname: Optional[str] = None, tclass: Optional[str] = None) -> List[str]:
        result = []
        
        for window in self.windows.values():
            window_id = window.get_id()
            window_name = window.get_name()
            window_class = window.get_class()

            if tid is not None and window_id != tid:
                continue
            if tname is not None and window_name != tname:
                continue
            if tclass is not None and window_class != tclass:
                continue 
            result.append(window_id)

        return result

    def __getitem__(self, window_id):
        if window_id not in self.windows:
            raise KeyError(f"Window ID {window_id} not found.")
        return self.windows[window_id]

    def get_active(self, format: IdFormat = IdFormat.HEX8):
        # Assuming `get_active` is a function that gets the active window ID
        return get_active(format)

    def __str__(self):
        msg = "[ WindowManager ]\n"

        # Active Window
        msg += "active_window: "
        active_window = self.get_active()
        if active_window:
            msg += f"{active_window}\n"
        else:
            msg += "None\n"

        # Window Data
        for window_data in self.windows.values():
            msg += f"[{window_data.__str__()}]\n"

        return msg

    def __contains__(self, window_id):
        return window_id in self.windows


if __name__ == "__main__":
    wm = WindowManager()
    wm.update()
    print(wm)
