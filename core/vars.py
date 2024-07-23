from typing import Tuple, List, Optional
from src.shared import ExitReason, TaskPacket
from queue import Queue, Empty
import copy
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from core.action import Action


arg = {
    "tname": None,
    "tclass": "kitty.kitty",
    "size": (400, 200),
    "pos": (50,-50),
    "qtarg": [],
    "res": (1920, 1080)
}


class VarsChildren:
    def __init__(self):
        pass


######################################


class Args(VarsChildren):
    default_arg = {
        "tname": None,
        "tclass": None,
        "size": (400, 200),
        "pos": (50,-50),
        "qtarg": [],
        "res": (1920, 1080)
    }

    def __init__(self, arg):
        s = self.default_arg["size"] if arg["size"] is None else arg["size"]
        p = self.default_arg["pos"] if arg["pos"] is None else arg["pos"]
        r = self.default_arg["res"] if arg["res"] is None else arg["res"]
        tn = self.default_arg["tname"] if arg["tname"] is None else arg["tname"]
        tc = self.default_arg["tclass"] if arg["tclass"] is None else arg["tclass"]

        self._size: Tuple[int, int] = s
        self._pos: Tuple[int, int] = p 
        self._res: Tuple[int, int] = r
        self._tname:  str = tn
        self._tclass: str = tc 

    @property
    def size(self) -> Tuple[int, int]:
        return self._size

    @size.setter
    def size(self, value):
        self._size = value
    
    @property
    def pos(self) -> Tuple[int, int]:
        return self._pos

    @pos.setter
    def pos(self, value):
        self._pos = value

    @property
    def res(self) -> Tuple[int, int]:
        return self._res

    @res.setter
    def res(self, value):
        self._res = value

    @property
    def tname(self) -> str:
        return self._tname

    @tname.setter
    def tname(self, value: str):
        self._tname = value
    
    @property
    def tclass(self) -> str:
        return self._tclass

    @tclass.setter
    def tclass(self, value: str):
        self._tclass = value

    
    def __str__(self):
        msg = ""
        msg += f"size: {self.size}, "
        msg += f"pos: {self.pos}, "
        msg += f"res: {self.res}, "
        msg += f"tname: {self._tname}, "
        msg += f"tclass: {self._tclass}"
        return msg


class AppVars(VarsChildren):
    def __init__(self):
        self._wait_until: Optional[float] = None
        self._stop_reason: Optional[ExitReason] = None
        self._stop_extra_msg: str = ""
        self._stored_clipboard: str = ""

    @property
    def wait(self):
        return self._wait_until

    @wait.setter
    def wait(self, value: Optional[float]):
        self._wait_until = value 

    @property
    def stored_clipboard(self):
        return self._stored_clipboard

    @stored_clipboard.setter
    def stored_clipboard(self, value: str):
        self._stored_clipboard = value

    def assign_stop_vars(self, reason: ExitReason = ExitReason.Unknown, extra_msg = ""):
        if not self.stopping():
            self._stop_reason = reason
            self._stop_extra_msg = extra_msg

    def stopping(self):
        return self._stop_reason is not None

    def __str__(self):
        msg = ""
        msg += f"stop_reason: {self._stop_reason}, "
        msg += f"stop_extra_msg: {self._stop_extra_msg}, "
        msg += f"stopping: {self.stopping()}"
        return msg


class TargetVars(VarsChildren):
    def __init__(self):
        self._tid = Optional[str]

    @property
    def tid(self):
        assert self._tid is not None, \
            "Target ID is None but tried to get it"
        return self._tid

    @tid.setter
    def tid(self, value: str):
        self._tid = value

    def __str__(self):
        msg = ""
        msg += f"tid: {self._tid}"


class FFVars(VarsChildren):
    def __init__(self, last_pos_: Tuple[int, int], last_size_: Tuple[int, int]):
        self._is_visible = False
        self._is_opened = False

    # Métodos para obtener el valor de _is_visible
    def is_visible(self) -> bool:
        return self._is_visible

    # Métodos para establecer el valor de _is_visible
    def set_visible(self, value: bool):
        self._is_visible = value

    # Métodos para obtener el valor de _is_opened
    def is_opened(self) -> bool:
        return self._is_opened

    # Métodos para establecer el valor de _is_opened
    def set_opened(self, value: bool):
        self._is_opened = value

    def __str__(self):
        msg = ""
        msg += f", is_visible: {self._is_visible}"
        msg += f", is_opened: {self._is_opened}"
        return msg


class TaskQueue(VarsChildren):
    def __init__(self):
        self._queue: Queue[TaskPacket] = Queue()
        self._running_tasks = False
    
    @property
    def running_tasks(self):
        return self._running_tasks
    
    @running_tasks.setter
    def running_tasks(self, value: bool):
        self._running_tasks = value

    def get(self) -> Optional[TaskPacket]:
        try:
            return self._queue.get(block=False)
        except Empty:
            return None

    def push(self, task_packet: TaskPacket):
        self._queue.put(task_packet)

    def len(self):
        return self._queue.qsize()

    def empty(self):
        return self._queue.empty()

    def clear(self):
        while not self._queue.empty():
            try:
                self._queue.get(block=False)
            except Empty:
                break

    def __str__(self) -> str:
        queue_copy = copy.deepcopy(self._queue)
        items: List[str] = []

        # Transferir los elementos de la cola copiada a una lista de cadenas
        while not queue_copy.empty():
            item = queue_copy.get(block=False)
            items.append(str(item))

        # Convertir los elementos en una cadena
        items_str = ', '.join(items)
        return f"TaskQueue([{items_str}])"


######################################


class Vars:
    def __init__(self, arg_):
        self.arg = Args(arg_)
        self.app = AppVars()
        self.ff = FFVars(last_pos_ = self.arg.pos,
                         last_size_= self.arg.size)
        self.tar = TargetVars()
        self.tqueue = TaskQueue()

    def __str__(self):
        msg = "\n [ Vars ]"
        msg += f"\narg -> {self.arg}"
        msg += f"\napp  -> {self.app}"
        msg += f"\nff   -> {self.ff}"
        msg += f"\ntqueue  -> {self.tqueue}"
        return msg


if __name__ == "__main__":
    vars = Vars(arg) 
    print(vars)


