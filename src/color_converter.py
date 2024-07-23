from typing import Union, Tuple, Optional
from enum import Enum

class OutputColor(Enum):
    RGB = 'rgb'
    RGBA = 'rgba'
    HEX6 = 'hex6'
    HEX8 = 'hex8'

class ColorConverter:
    Num = Union[int, float]

    @staticmethod
    def _determine_format(values: Tuple[Num, ...]) -> str:
        format_chars = ""        
        for value in values:
            if isinstance(value, int):
                format_chars += "I"
            elif isinstance(value, float):
                format_chars += "F"
            else:
                raise ValueError("Unsupported value type")
        return format_chars 

    @staticmethod
    def _hex_to_rgb(hex_color: str, format: Optional[str] = None) -> Tuple[Num, Num, Num]:
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]

        if len(hex_color) not in {3, 6}:
            raise ValueError("El color hexadecimal debe tener 3 o 6 caracteres.")

        if len(hex_color) == 3:
            hex_color = ''.join([c * 2 for c in hex_color])

        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        if format is None:
            format = ColorConverter._determine_format((r, g, b))

        return ColorConverter._format_rgb((r, g, b), format)

    @staticmethod
    def _hex_to_rgba(hex_color: str, format: Optional[str] = None) -> Tuple[Num, Num, Num, Num]:
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]

        if len(hex_color) not in {3, 4, 6, 8}:
            raise ValueError("El color hexadecimal debe tener {3, 4, 6, 8} caracteres.")

        # Full alpha if not specified
        if len(hex_color) == 3:
            hex_color += "F"
        elif len(hex_color) == 6:
            hex_color += "FF"

        # Ensures an 8 characters hex number 
        if len(hex_color) == 4:
            hex_color = ''.join([c * 2 for c in hex_color])

        # Convert and store the characters
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        a = int(hex_color[6:8], 16)

        if format is None:
            format = ColorConverter._determine_format((r, g, b))

        return ColorConverter._format_rgba((r, g, b, a), format)

    @staticmethod
    def _rgb_to_hex6(rgb: Tuple[Num, Num, Num]) -> str:
        return "#{:02X}{:02X}{:02X}".format(
            ColorConverter.float_to_int(rgb[0]) if isinstance(rgb[0], float) else rgb[0],
            ColorConverter.float_to_int(rgb[1]) if isinstance(rgb[1], float) else rgb[1],
            ColorConverter.float_to_int(rgb[2]) if isinstance(rgb[2], float) else rgb[2]
        )

    @staticmethod
    def _rgba_to_hex8(rgba: Union[Tuple[Num, Num, Num, Num], Tuple[Num, Num, Num]]) -> str:

        if len(rgba) == 3:
            rgba = (*rgba, 255)  # Adds an alpha value of 255

        return "#{:02X}{:02X}{:02X}{:02X}".format(
            ColorConverter.float_to_int(rgba[0]) if isinstance(rgba[0], float) else rgba[0],
            ColorConverter.float_to_int(rgba[1]) if isinstance(rgba[1], float) else rgba[1],
            ColorConverter.float_to_int(rgba[2]) if isinstance(rgba[2], float) else rgba[2],
            ColorConverter.float_to_int(rgba[3]) if isinstance(rgba[3], float) else rgba[3]
        )

    @staticmethod
    def int_to_float(value: int) -> float:
        if not (0 <= value <= 255):
            raise ValueError("El valor debe estar entre 0 y 255.")
        return value / 255.0

    @staticmethod
    def float_to_int(value: float) -> int:
        if not (0.0 <= value <= 1.0):
            raise ValueError("El valor debe estar entre 0.0 y 1.0.")
        return round(value * 255)
 
    @staticmethod
    def _format_rgb(rgb: Tuple[Num, Num, Num], format: Optional[str]) -> Tuple[Num, Num, Num]:
        if format is None:
            format = ColorConverter._determine_format(rgb)

        if any(char not in {"I", "F"} for char in format):
            raise ValueError("The format can only be composed of 'I' or 'F'")

        def get_type(conversion_char):
            return int if conversion_char == 'I' else float

        def convert_value(value, target_type):
            if isinstance(value, target_type):
                return value
            return ColorConverter.float_to_int(value) if target_type == int else ColorConverter.int_to_float(value)

        format_length = len(format)
        if format_length == 1:
            r_type = g_type = b_type = get_type(format[0])
        elif format_length == 3:
            r_type = get_type(format[0])
            g_type = get_type(format[1])
            b_type = get_type(format[2])
        else:
            raise ValueError("Format string length must be 1 or 3")

        converted_values = (
            convert_value(rgb[0], r_type),
            convert_value(rgb[1], g_type),
            convert_value(rgb[2], b_type)
        )

        return converted_values
   
    @staticmethod
    def _format_rgba(rgba: Union[Tuple[Num, Num, Num, Num], Tuple[Num, Num, Num]], format: Optional[str]) -> Tuple[Num, Num, Num, Num]:
        if len(rgba) == 3:
            rgba = (*rgba, 255)  # Adds an alpha value of 255

        if format is None:
            format = ColorConverter._determine_format(rgba)

        if any(char not in {"I", "F"} for char in format):
            raise ValueError("The format can only be composed of 'I' or 'F'")

        def get_type(conversion_char):
            return int if conversion_char == 'I' else float

        def convert_value(value, target_type):
            if isinstance(value, target_type):
                return value
            return ColorConverter.float_to_int(value) if target_type == int else ColorConverter.int_to_float(value)

        format_length = len(format)
        if format_length == 1:
            r_type = g_type = b_type = a_type = get_type(format[0])
        elif format_length == 2:
            r_type = g_type = b_type = get_type(format[0])
            a_type = get_type(format[1])
        elif format_length == 3:
            r_type = get_type(format[0])
            g_type = get_type(format[1])
            b_type = get_type(format[2])
            a_type = float if isinstance(rgba[3], float) else int
        elif format_length == 4:
            r_type = get_type(format[0])
            g_type = get_type(format[1])
            b_type = get_type(format[2])
            a_type = get_type(format[3])
        else:
            raise ValueError("Format string length must be between 1 and 4")

        converted_values = (
            convert_value(rgba[0], r_type),
            convert_value(rgba[1], g_type),
            convert_value(rgba[2], b_type),
            convert_value(rgba[3], a_type)
        )

        return converted_values

    @staticmethod
    def _to_rgb(color: Union[str, Tuple[Num, Num, Num]], format: Optional[str] = None) -> Tuple[Num, Num, Num]:
        if isinstance(color, str):
            color = ColorConverter._hex_to_rgb(color, format)
        return ColorConverter._format_rgb(color, format)
    
    @staticmethod
    def _to_rgba(color: Union[str, Tuple[Num, Num, Num, Num], Tuple[Num, Num, Num]], format: Optional[str] = None) -> Tuple[Num, Num, Num, Num]:
        if isinstance(color, str):
            color = ColorConverter._hex_to_rgba(color, format)
        return ColorConverter._format_rgba(color, format)

    @staticmethod
    def _to_hex6(color: Union[str, Tuple[Num, Num, Num]]) -> str:
        if isinstance(color, str):
            color = ColorConverter._hex_to_rgb(color)
        elif len(color) != 3:
            raise ValueError("HEX6 requiere una tupla de 3 valores")
        return ColorConverter._rgb_to_hex6(color)

    @staticmethod
    def _to_hex8(color: Union[str, Tuple[Num, Num, Num, Num], Tuple[Num, Num, Num]]) -> str:
        if isinstance(color, str):
            color = ColorConverter._hex_to_rgba(color)
        elif len(color) == 3:
            color = (*color, 255)  # Add alpha value of 255 if not provided
        elif len(color) != 4:
            raise ValueError("HEX8 requiere una tupla de 4 valores o 3 valores más un alpha por defecto")
        return ColorConverter._rgba_to_hex8(color)

    @staticmethod
    def convert(color: Union[str, Tuple[Num, Num, Num, Num], Tuple[Num, Num, Num]], output_type: OutputColor = OutputColor.RGB, format: Optional[str] = None) -> Union[Tuple[Num, Num, Num, Num], Tuple[Num, Num, Num],  str]:
        if output_type == OutputColor.RGB:
            return ColorConverter._to_rgb(color, format)
        elif output_type == OutputColor.RGBA:
            return ColorConverter._to_rgba(color, format)
        elif output_type == OutputColor.HEX6:
            return ColorConverter._to_hex6(color)
        elif output_type == OutputColor.HEX8:
            return ColorConverter._to_hex8(color)
        else:
            raise ValueError("Tipo de salida no soportado")

