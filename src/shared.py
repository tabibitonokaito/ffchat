from enum import Enum, auto
from typing import Any, Dict, Tuple, Callable
import time


class OperacionPesada:
    def __init__(self, limite=3100000):
        self.limite = limite
        self.tiempo = 0  # Tiempo por defecto en segundos
        self.recalcular()

    def _es_primo(self, n):
        if n <= 1:
            return False
        if n <= 3:
            return True
        if n % 2 == 0 or n % 3 == 0:
            return False
        i = 5
        while i * i <= n:
            if n % i == 0 or n % (i + 2) == 0:
                return False
            i += 6
        return True

    def recalcular(self):
        start_time = time.time()  # Empieza a contar el tiempo
        self.primos = [num for num in range(2, self.limite) if self._es_primo(num)]
        end_time = time.time()  # Termina de contar el tiempo
        self.tiempo = end_time - start_time  # Calcula el tiempo transcurrido
        print(self)

    def set_limite(self, nuevo_limite):
        self.limite = nuevo_limite
        self.recalcular()  # Recalcular con el nuevo límite

    def get_tiempo(self):
        return self.tiempo

    def __str__(self):
        return f"Se encontraron {len(self.primos)} números primos hasta {self.limite}. Tiempo de cálculo: {self.tiempo:.2f} segundos."


class FFEnum(Enum):
    """
    Base class for enums with shared behavior.
    """
    @property
    def msg(self) -> str:
        """
        Return a descriptive message for the enum value.
        """
        messages = self._messages()
        return messages.get(self, "No message available.")

    @classmethod
    def _messages(cls) -> Dict["FFEnum", str]:
        """
        Return a dictionary of messages for the enum values.
        """
        return {}

###########################

class ExitReason(FFEnum):
    ExitKeyPress = auto()
    TargetDied = auto()
    MultipleTargets = auto()
    MultipleFFChats = auto()
    TargetNotFound = auto()
    Unknown = auto()
    WMProblems = auto()

    @classmethod
    def _messages(cls) -> Dict[FFEnum, str]:
        return {
            cls.ExitKeyPress: "Exit due to key press.",
            cls.TargetDied: "The target process has died.",
            cls.MultipleTargets: "More targets than expected were found.",
            cls.MultipleFFChats: "More FFChat windows than expected were found.",
            cls.TargetNotFound: "The target process could not be found.",
            cls.Unknown: "An unknown reason for exit occurred."
        }

###########################

print(ExitReason.ExitKeyPress.msg)
print(ExitReason.ExitKeyPress)


TaskFunction = Callable[..., None]


class TaskType(FFEnum):
    """
    Base class for command types. All command types should inherit from taskType.
    """
    pass


class Task:
    class Tar(TaskType):
        Focus = auto()
        @classmethod
        def _messages(cls) -> Dict[TaskType, str]:
            return {
                cls.Focus: "Focus the Target Window.",
        }

    class FF(TaskType):
        Show = auto()
        Hide = auto()
        ToggleShow = auto()
        Focus = auto()
        Restore = auto()
        BetaRestore = auto()

        CopyInput = auto()
        ClearInput = auto()

        @classmethod
        def _messages(cls) -> Dict[TaskType, str]:
            return {
                cls.Show: "Show the FFChat",
                cls.Hide: "Hide the FFChat",
                cls.ToggleShow: "Show/Hiddes (Toggle) the FFChat",
                cls.Focus: "Focus the FFChat",
                cls.Restore: "Restore the position of FFChat",
            }

    class App(TaskType):
        Exit = auto()
        ToggleFocus = auto()

        SaveClipboard = auto()
        RestoreClipboard = auto()
        SendKeystroke = auto()
        SwitchToKeyboard = auto()

        Wait = auto()
        UpdateWindows = auto()
        
        @classmethod
        def _messages(cls) -> Dict[TaskType, str]:
            return {
                cls.Exit: "Exit the application.",
                cls.ToggleFocus: "Toggles the focus between Target and FFChat",
                cls.SaveClipboard: "Saves the user clipboard before launching an action",
                cls.RestoreClipboard: "Restored the saved clipboard",
                cls.SendKeystroke: "Sends a keystroke",
                cls.SwitchToInputKeyboard: "Switch to the choosen input keyboard"
            }


class TaskPacket:
    def __init__(self, task_type: TaskType, args: Tuple[Any, ...] = (), kwargs: Dict[str, Any] = {}):
        self._task_type = task_type
        self._args = args
        self._kwargs = kwargs

    @property
    def task_type(self):
        return self._task_type

    @property
    def args(self):
        return self._args

    @property
    def kwargs(self):
        return self._kwargs

    def deploy(self):
        return (self._task_type, *self._args, self._kwargs)

    def __str__(self):
        args_str = ', '.join(map(str, self.args))
        kwargs_str = ', '.join(f"{key}={value}" for key, value in self.kwargs.items())
        return f"Command(task_type={self.task_type}, args=({args_str}), kwargs={{ {kwargs_str} }})"


