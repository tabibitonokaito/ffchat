import sys, os
from typing import Optional
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject
from src.shared import ExitReason
from src.sys_window import WindowManager
from src.sys_keyboard import SystemKeyboard
from core.ffchat import FFChat
from core.vars import Vars
from core.thread import ThreadManager
from core.action import Action
from core.event import EventManager

os.environ['QT_IM_MODULE'] = 'fcitx5'

# args = {
#     "tname": None,
#     "tclass": "discord.discord",
#     # "tclass": None,
#     # "tclass": "ffxiv_dx11.exe",
#     "size": (900, 160),
#     # size aureo chulo para cuando se avance en el proyecto
#     # "size": (730, 450),
#     # centrada
#     # "pos": (595,315),
#     "pos": (510, -200),
#     "qtargs": [],
#     "res": (1920, 1080)
# }

args = {
    "tname": "FINAL FANTASY XIV",
    # "tclass": "kitty.kitty",
    "tclass": None,
    # "tclass": "ffxiv_dx11.exe",
    "size": (900, 160),
    # size aureo chulo para cuando se avance en el proyecto
    # "size": (730, 450),
    # centrada
    # "pos": (595,315),
    "pos": (510, -200),
    "qtargs": [],
    "res": (1920, 1080)
}


class Main(QObject):
    def __init__(self, app: "QApplication", ffchat: FFChat):
        super().__init__()

        self._vars = Vars(args) 
        self._app: QApplication = app
        self._ffchat: FFChat = ffchat
        self._wm = WindowManager()
        self._sys_kb = SystemKeyboard()
        self._action = Action(self._vars, self._app, 
                               self._ffchat, self._wm, self._sys_kb, 
                               self.stop)

        self._tm = ThreadManager(self._action)
        self._em = EventManager(self._ffchat, self._sys_kb, self._action)

    def run(self):
        self._tm.run_starting(wait=True)
        self._tm.run_working()
        self._tm.run_control()

        self._em.run_ff_events()
        self._em.run_sys_kb_events()

        return self._app.exec()
    
    def stop(self, reason: ExitReason, extra_msg: Optional[str] = None):
        print(f"\n")
        print(f"  Deteniendo programa.")
        print(f"    Razón:    {reason.msg}")
        print(f"    ExtraMsg: {extra_msg}")
        print(f"\n")
        
        self._tm.stop_control()
        self._tm.stop_working()
        self._em.stop_ffevents()
        self._ffchat.close()
        self._app.quit()
        self._em.stop_sys_kb_events()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ffchat = FFChat()
    controller = Main(app, ffchat)
    controller.run()
