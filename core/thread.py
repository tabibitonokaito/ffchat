from PyQt6.QtCore import QThread, QEventLoop, pyqtSignal
from abc import ABC, abstractmethod
import time
from core.action import Action

"""
quit(): Usado para salir del QEventLoop de manera ordenada y procesar los eventos pendientes.
exit(): Usado para salir del QEventLoop y opcionalmente devolver un código de salida.
"""

class ThreadBase(QThread):
    def __init__(self, action: Action):
        super().__init__()
        self._action = action

    def stop(self):
        self.requestInterruption()
        self.wait()

    @abstractmethod
    def connect_signals(self):
        pass


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class ThreadHandlerBase(ABC):
    def __init__(self, action: Action):
        self._action = action
        self._th = None 

    @abstractmethod
    def connect_signals(self):
        pass

    def run(self, wait=False):
        assert self._th is not None
        self._th.start()
        if wait:
            self._th.wait()

    def stop(self):
        assert self._th is not None
        self._th.stop()


#########################################
#########################################


class StartingThread(ThreadBase):
    def __init__(self, action: Action):
        super().__init__(action)
    restore_ffchat = pyqtSignal()

    def run(self):
        action = self._action
        action.app.update_windows()
        action.tar.locate_store_tid()
        self.restore_ffchat.emit()


class StartingHandler(ThreadHandlerBase):
    def __init__(self, action: Action):
        super().__init__(action)
        self._th = StartingThread(action)
   
    def connect_signals(self):
        # print("Se invoca connect signals de StartingHandler")
        self._th.restore_ffchat.connect(self._action.ff.restore)


#########################################


class ControlThread(ThreadBase):
    def __init__(self, action: Action):
        super().__init__(action)
        self.stop_handler = QEventLoop()

    # Signals
    # ffchatLabel = pyqtSignal(str)
    run_tasks = pyqtSignal(int, float)
    
    def run(self):
        action = self._action
        app_stopping = self._action.app.stopping
        interrupted = self.isInterruptionRequested

        while not interrupted() and not app_stopping():
            wait_until = action.vars.app.wait
            if wait_until is not None:
                if time.time() < wait_until:
                    continue
                else:
                    print(f"espera de {wait_until - time.time()} terminada")
                    action.vars.app.wait = None
                    continue

            time.sleep(0.005)
            self.run_tasks.emit(1,1)
        self.run_tasks.emit(0,0)


class ControlHandler(ThreadHandlerBase):
    def __init__(self, action: Action):
        super().__init__(action)
        self._th = ControlThread(action)

    def connect_signals(self):
        self._th.run_tasks.connect(self._action.thandler.run_tasks)


#########################################


class WorkingThread(ThreadBase):
    def __init__(self, action: Action):
        super().__init__(action)

    updateSignal = pyqtSignal(int)
    restore_ffchat = pyqtSignal()
    update_windows = pyqtSignal()


    def run(self):
        app_stopping = self._action.app.stopping
        interrupted = self.isInterruptionRequested

        while not interrupted() and not app_stopping(): 
            self._action.tar.locate_or_stop_task()
            time.sleep(1)
            # time.sleep(0.01)
            # wait_a_bit = time.time() + 0.1
            # while time.time() < wait_a_bit:
            #     continue
            # continue


        # for i in range(100):
        #     if self.isInterruptionRequested():  # Comprobar si se ha solicitado la interrupción
        #         break  # Salir del bucle si se solicita una interrupción
        #     time.sleep(1) 
        #     self.updateSignal.emit(i)


class WorkingHandler(ThreadHandlerBase):
    def __init__(self, action: Action):
        super().__init__(action)
        self._th = WorkingThread(action)
    
    def connect_signals(self):
        self._th.update_windows.connect(self._action.app.update_windows)
        # self._th.updateSignal.connect(self.thread_update)
        self._th.restore_ffchat.connect(self._action.ff.restore)

    def thread_update(self, result):
        print(f"Working Update: {result}")


#########################################
#########################################


class ThreadManager:
    def __init__(self, action: Action):
        self._action = action
        self._starting = StartingHandler(self._action)
        self._control = ControlHandler(self._action)
        self._working = WorkingHandler(self._action)
        self._connect_signals()
        
    def _connect_signals(self):
        self._starting.connect_signals()
        self._control.connect_signals()
        self._working.connect_signals()
        
    def run_starting(self, wait: bool):
        self._starting.run(wait)
        
    def stop_starting(self):
        self._starting.stop()

    def run_working(self):
        self._working.run(wait=False)

    def stop_working(self):
        self._working.stop()

    def run_control(self):
        self._control.run(wait=False)

    def stop_control(self):
        self._control.stop()




