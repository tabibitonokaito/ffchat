from PyQt6.QtWidgets import QApplication
from src.shared import ExitReason, TaskType, Task, TaskPacket, TaskFunction
from src.exception import MultipleFoundError, NotFoundError
from core.vars import TaskQueue, Vars
from core.ffchat import FFChat
from src.sys_window import WindowManager
from src.sys_keyboard import SystemKeyboard
from typing import Callable, Tuple, Dict, Any
import subprocess
import time
import pyperclip


class ActionChildren:
    def __init__(self, action: "Action"):
        self._action = action 
   

class TargetAction(ActionChildren):
    def __init__(self, action: "Action"):
        super().__init__(action)
    
    def locate_or_stop_task(self):
        action = self._action
        tid = ""
        try:
            tid = action.tar.locate() 
        except MultipleFoundError:
            print(f"locate_or_stop_task() de target va a lanzar multiple targets exit")
            action.app.create_stop_task(ExitReason.MultipleTargets, 
                             "Se han encontrado multiples target válidos y esto no está implementado.")
        except NotFoundError:
            print(f"El programa va a terminar debido a que el target ya no existe")
            action.app.create_stop_task(ExitReason.TargetNotFound, 
                             "Target no encontrado, terminando la ejecución.")

        return tid

    # Target
    def locate(self) -> str:
        """
        Localiza la id del Target pero puede lanzar excepciones.
            - MultipleFoundError: -> Múltiples resultados obtenidos al tratar de localizar el Target
            - NotFoundError: -> No se ha encontrado nada 
        Ambas excepciones heredan de NotExactMatch en caso de no necesitar tanta precisión
        """
        max_retries = 10
        retry_interval = 0.05
        
        for _ in range(max_retries):
            vars = self._action.vars
            tname = vars.arg.tname
            tclass = vars.arg.tclass

            self._action.wm.update()
            results = self._action.wm.find(tname=tname, tclass=tclass) 

            if len(results) > 1:
                raise MultipleFoundError(results)
            elif len(results) == 1:
                tid: str = results[0]
                return tid

            # print(f"target no encontrado, windows: {print(self._action.wm)}")
            time.sleep(retry_interval)
        
        raise NotFoundError()

    def locate_store_tid(self):
        action = self._action
        tid = ""
        try:
            tid = action.tar.locate() 
        except MultipleFoundError:
            print(f"locate_or_stop_task() de target va a lanzar multiple targets exit")
            action.app.create_stop_task(ExitReason.MultipleTargets, 
                             "Se han encontrado multiples target válidos y esto no está implementado.")
        except NotFoundError:
            print(f"El programa va a terminar debido a que el target ya no existe")
            action.app.create_stop_task(ExitReason.TargetNotFound, 
                             "Target no encontrado desde el principio. Abre el programa antes de ejecutar esto.\n  Terminando la ejecución.")
           
        self._action.vars.tar.tid = tid

    def focus(self):
        tid = self.locate_or_stop_task()
        self._action.app.focus_bspwm_window(tid)

    def focused(self):
        return self._action.wm.get_active() == self.locate()


class FFAction(ActionChildren):
    def __init__(self, ffchat: FFChat, action: "Action"):
        super().__init__(action)
        self._ffchat = ffchat

    def copy_input(self):
        contenido = self._ffchat.ff_input.text()
        pyperclip.copy(contenido)

    def clear_input(self):
        self._ffchat.ff_input.clear()
        
    def update_vars(self):
        action = self._action
        action.vars.ff.set_visible(self._ffchat.isVisible())                          

    def locate(self):
        max_retries = 10
        retry_interval = 0.05
        
        for _ in range(max_retries):
            self._action.wm.update()
            results = self._action.wm.find(tname="FFChat")
            
            if len(results) == 1:
                ffid: str = results[0]
                return ffid
            elif len(results) > 1:
                raise MultipleFoundError(results)
            
            time.sleep(retry_interval)
    
        raise NotFoundError()
    
    def focused(self):
        return self._action.wm.get_active() == self.locate()

    def show(self):
        if not self._ffchat.isVisible():
            tid = self._action.tar.locate_or_stop_task()
            self._action.app.focus_bspwm_window(tid)
            self._ffchat.show()

    def hide(self):
        if self._ffchat.isVisible():
            self._ffchat.hide()

    def toggle_show(self):
        if not self._ffchat.isVisible():
            self.show()
        else:
            self.hide()
    
    def focus(self):
        ffid = self.locate() 
        self._action.app.focus_bspwm_window(ffid)

    def restore(self, show: bool = False):
        if self._action.ff.is_visible():
            self._action.thandler.push(Task.FF.Hide)
            self._action.thandler.push(Task.Tar.Focus)
            self._action.thandler.push(Task.App.Wait, (0.1,))
            self._action.thandler.push(Task.FF.Restore, (show,))
            return

        pos = self._calc_pos(self._action.vars.arg.res,
                             self._action.vars.arg.size,
                             self._action.vars.arg.pos)
        self._ffchat.relocate(size=self._action.vars.arg.size, pos=pos)
        if show:
            self._action.thandler.push(Task.FF.Show)

    def is_visible(self):
        return self._ffchat.isVisible()

    def _calc_pos(self,
                       res: Tuple[int, int],
                       size: Tuple[int, int],
                       pos: Tuple[int, int]):
        def process_x(res_x,size_x, x):
            if x < 0:
                return res_x - size_x - abs(x)
            if x == 0:
                return 1
            return x

        res_x, res_y = res
        size_x, size_y = size
        x,y = pos
        return (process_x(res_x,size_x,x), process_x(res_y,size_y, y))


class AppAction(ActionChildren):
    def __init__(self, app: QApplication, stop_function, action: "Action"):
        super().__init__(action)
        self._app = app
        self._stop_function = stop_function

    def update_windows(self):
        self._action.wm.update()

    def wait(self, value: float):
        self._action.vars.app.wait = time.time() + value

    def save_clipboard(self):
        clipboard = pyperclip.paste() 
        self._action.vars.app.stored_clipboard = clipboard
        print(f"cliboard guardado: {self._action.vars.app.stored_clipboard}")

    def restore_clipboard(self):
        clipboard = self._action.vars.app.stored_clipboard
        pyperclip.copy(clipboard)

    def send_keystroke(self, keys):
        self._action.sys_kb.send_keystroke(keys)

    def switch_to_keyboard(self, keyboard_name):
        # fcitx5-remote -s keyboard-es | mozc
        try:
            # Ejecutar el comando fcitx5-remote con el nombre del teclado proporcionado
            result = subprocess.run(
                ['fcitx5-remote', '-s', keyboard_name], 
                check=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            print(f"Switched to input keyboard: {keyboard_name}")
            print(result.stdout.decode('utf-8'))
        except subprocess.CalledProcessError as e:
            print(f"Failed to switch to input keyboard: {keyboard_name}")
            print(e.stderr.decode('utf-8'))

    def toggle_focus(self):
        ffvisible = self._action.ff.is_visible()

        if not ffvisible or self._action.ff.focused():
            self._action.tar.focus()
        
        else:
            self._action.ff.focus()

    def focus_bspwm_window(self, id: str):
        subprocess.run(["bspc", "node", id, "-f"])

    def create_stop_task(self,
                            reason: ExitReason = ExitReason.Unknown,
                            extra_msg = "", 
                            clear_tasks_before: bool = False):
        
        if self.stopping():
            print("Se ha intentado crear una task de salida extra antes de procesar la primera: ", end="")
            print(f"reason: {reason}, extra_msg: {extra_msg}")
            print("Acción: no la procesamos y abandonamos create_stop_task")
        self._action.vars.app.assign_stop_vars(reason, extra_msg)

        if clear_tasks_before:
            self._action.thandler.clear()

        self._action.thandler.push(
                Task.App.Exit,
                (reason, extra_msg),
                {}
            ) 

    def stop_caller(self, reason: ExitReason, extra_msg: str):
        self._stop_function(reason, extra_msg)

    def stopping(self):
        return self._action.vars.app.stopping()


class TaskHandler(ActionChildren):
    def __init__(self, task_queue: TaskQueue, action: "Action"):
        super().__init__(action)
        self._queue = task_queue
        self.task_functions: Dict[TaskType, TaskFunction] = {
            Task.FF.Show: self._action.ff.show,
            Task.FF.Hide: self._action.ff.hide,
            Task.FF.ToggleShow: self._action.ff.toggle_show,
            Task.FF.Focus: self._action.ff.focus,
            Task.FF.Restore: self._action.ff.restore,
            Task.FF.CopyInput: self._action.ff.copy_input,
            Task.FF.ClearInput: self._action.ff.clear_input,

            Task.Tar.Focus: self._action.tar.focus,

            Task.App.ToggleFocus: self._action.app.toggle_focus,
            Task.App.Exit: self._action.app.stop_caller,
            Task.App.SaveClipboard: self._action.app.save_clipboard,
            Task.App.RestoreClipboard: self._action.app.restore_clipboard,
            Task.App.SendKeystroke: self._action.app.send_keystroke,
            Task.App.SwitchToKeyboard: self._action.app.switch_to_keyboard,
            Task.App.Wait: self._action.app.wait,
            Task.App.UpdateWindows: self._action.app.update_windows,
        }

    def run_tasks(self, max_tasks: int, duration: float):
        assert isinstance(max_tasks, int), "max_tasks debe ser int"
        assert isinstance(duration, float), "duration debe ser un float"

        """
        Execute tasks from the queue.
        
        :param max_tasks: Maximum number of tasks to execute. If None, execute all available tasks.
        :param duration: Time in seconds to run the task execution. If None, run until the queue is empty.
        """
        start_time = time.time()
        tasks_executed = 0

        if self._action.vars.app.wait is not None:
            return 
        if self._action.vars.tqueue.running_tasks:
            return

        self._action.vars.tqueue.running_tasks = True
        
        while True:
            if max_tasks > 0 and \
                tasks_executed >= max_tasks:
                break
            if duration > 0 and \
                (time.time() - start_time) >= duration:
                break

            task_packet = self._queue.get()
            if task_packet:
                task_type = task_packet.task_type
                handler = self.task_functions.get(task_type)

                if handler:
                    handler(*task_packet.args, **task_packet.kwargs)
                else:
                    raise Exception(f"No handler defined for task"
                                    f" type: {task_type}")

                tasks_executed += 1

                # If we have to wait we can't rush all the tasks!
                if task_type == Task.App.Wait:
                    break
            else:
                break
        self._action.vars.tqueue.running_tasks = False 

    def get(self):
        return self._queue.get()

    def push(self, task_type: TaskType, args: Tuple[Any, ...] = (), kwargs: Dict[str, Any] = {}):
        task_packet = TaskPacket(task_type, args, kwargs)
        self._queue.push(task_packet)
    
    def len(self):
        return self._queue.len()

    def empty(self):
        return self._queue.empty()

    def clear(self):
        self._queue.clear()


class Action():
    def __init__(self, vars: Vars, app: QApplication,
                 ffchat: FFChat, wm: WindowManager, 
                 sys_kb: SystemKeyboard,
                 stop_function: Callable):
        """
        En un futuro programar para que no se pase el objeto
        action al completo, sino solamente los que necesite
        cada sección
        """
        self.vars = vars
        self.wm = wm
        self.sys_kb = sys_kb
        self.ff = FFAction(ffchat, self)
        self.app = AppAction(app, stop_function, self)
        self.tar = TargetAction(self)
        self.thandler = TaskHandler(self.vars.tqueue, self)

    


    # # Testing
    # def show_ffchat(self):
    #     self.ffchat.show()
    #
    # def update_ffchat_label(self, text: str):
    #     self.ffchat.label.setText(text)
