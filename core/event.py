from PyQt6.QtCore import QObject, QEvent, Qt
from src.shared import ExitReason, Task 
from src.sys_keyboard import SystemKeyboard
from pynput import keyboard
from abc import ABC, abstractmethod
from core.action import Action
from core.ffchat import FFChat


class EventHandler(ABC):
    @abstractmethod
    def __init__(self, action: Action):
        self._action = action


################################################
################################################


class FFEvent(QObject):
    def __init__(self, ffchat: FFChat, action: Action):
        # we send the parent to super
        super().__init__(ffchat)
        self._action = action

    def _preparar_mensaje(self):
        self._action.thandler.push(Task.App.SaveClipboard)
        self._action.thandler.push(Task.FF.CopyInput)
        self._action.thandler.push(Task.Tar.Focus)
        self._action.thandler.push(Task.FF.Hide)

    def _limpiar(self):
        self._action.thandler.push(Task.FF.ClearInput)
        self._action.thandler.push(Task.App.RestoreClipboard)
        self._action.thandler.push(Task.App.SwitchToKeyboard,("keyboard-es",))

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            key_event = event  # No es necesario convertir a QKeyEvent en PyQt6
            if key_event.key() == Qt.Key.Key_Return and key_event.modifiers() == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier):
                pass
            elif key_event.key() == Qt.Key.Key_Return and key_event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                # self.envio_simple()
                pass
            elif key_event.key() == Qt.Key.Key_Return:
                self._preparar_mensaje() 
                self._action.thandler.push(Task.App.Wait, (0.1,)) 
                self._action.thandler.push(Task.App.SendKeystroke, 
                                           ([keyboard.Key.ctrl_l, keyboard.KeyCode.from_char('v')],))
                self._action.thandler.push(Task.App.Wait, (0.15,)) 
                self._limpiar()
                self._action.thandler.push(Task.App.SendKeystroke, ([keyboard.Key.enter],))
                
        return super().eventFilter(obj, event)


class FFEventHandler(EventHandler):
    def __init__(self, ffchat: FFChat, action: Action):
        super().__init__(action)
        self._ffchat = ffchat 
        self._ffevent = FFEvent(ffchat, action)
                
    def run(self):
        # self._ffchat.button.installEventFilter(self._ffevent)
        self._ffchat.installEventFilter(self._ffevent)
        pass

    def stop(self):
        # self._ffchat.button.removeEventFilter(self._ffevent)
        self._ffchat.removeEventFilter(self._ffevent)
        pass


################################################

        
class SystemKeyboardHandler(EventHandler):
    def __init__(self, sys_kb: SystemKeyboard, action: Action):
        super().__init__(action)
        self._sys_kb = sys_kb
        self._pressed_keys = self._sys_kb.pressed_keys
        self._sys_kb.assign_functions(self._keydown, self._keyup)

    def _keydown(self, key):
        if keyboard.Key.ctrl_l in self._pressed_keys and key == keyboard.Key.enter:
            if self._action.tar.focused():
                self._action.thandler.push(Task.App.Wait, (0.1, ))
                self._action.thandler.push(
                    Task.FF.Show,
                    (),
                    {}
                )
                self._action.thandler.push(
                    Task.FF.Focus,
                        (),
                        {}
                    )
                self._action.thandler.push(
                    Task.App.SwitchToKeyboard,
                    ("mozc",),
                    {}
                )
            pass
        elif key == keyboard.Key.esc:
            pass 
        elif keyboard.Key.ctrl_l in self._pressed_keys and key == keyboard.Key.space:
            pass
        elif keyboard.Key.ctrl_l in self._pressed_keys and key == keyboard.KeyCode.from_char('d'):
            if self._action.ff.is_visible() and self._action.ff.focused():
                self._action.thandler.push(
                    Task.FF.Hide,
                    (),
                    {}
                )
                self._action.thandler.push(Task.FF.ClearInput)
                self._action.thandler.push(Task.App.SwitchToKeyboard,("keyboard-es",))
                self._action.thandler.push(Task.App.Wait, (0.1, ))
                self._action.thandler.push(Task.App.SendKeystroke, ([keyboard.Key.esc],))
        elif keyboard.Key.ctrl_l in self._pressed_keys and key == keyboard.KeyCode.from_char('e'):
            if self._action.ff.is_visible() and self._action.ff.focused():
                self._action.thandler.push(
                    Task.FF.Hide,
                    (),
                    {}
                )
                self._action.thandler.push(Task.App.SwitchToKeyboard,("keyboard-es",))
                self._action.thandler.push(Task.App.Wait, (0.1, ))
                self._action.thandler.push(Task.App.SendKeystroke, ([keyboard.Key.esc],))
        elif keyboard.Key.ctrl_l in self._pressed_keys and key == keyboard.KeyCode.from_char('l'):
            if self._action.ff.is_visible() and self._action.ff.focused():
                self._action.thandler.push(
                    Task.FF.ClearInput,
                    (),
                    {}
                )
        elif keyboard.Key.ctrl_l in self._pressed_keys and key == keyboard.KeyCode.from_char('f'):
            if self._action.tar.focused() and self._action.ff.is_visible():
                self._action.thandler.push(Task.FF.Focus)
                
        elif keyboard.Key.ctrl_l in self._pressed_keys and key == keyboard.KeyCode.from_char('r'):
            if self._action.ff.is_visible() and self._action.ff.focused():
                self._action.thandler.push(Task.FF.Restore, (True,))
        elif keyboard.Key.shift in self._pressed_keys and key == keyboard.Key.f1:
            pass
        elif keyboard.Key.shift in self._pressed_keys and key == keyboard.Key.f8:
            self._action.app.create_stop_task(
                ExitReason.ExitKeyPress, 
                "Thanks you for using my software",
                False
        )
          
    def _keyup(self, key):
        pass

    def run(self):
        self._sys_kb.run()

    def stop(self):
        self._sys_kb.stop()


################################################
################################################

class EventManager:
    def __init__(self, ffchat: FFChat, sys_kb: SystemKeyboard, action: Action):
        self._sys_kb_handler = SystemKeyboardHandler(sys_kb, action)
        self._ffhand = FFEventHandler(ffchat, action)
        if self._ffhand is None:
            raise RuntimeError("No se ha podido crear FFEvent")

        self.action = action 
    
    def run_ff_events(self):
        self._ffhand.run()

    def run_sys_kb_events(self):
        self._sys_kb_handler.run()

    def stop_ffevents(self):
        self._ffhand.stop()

    def stop_sys_kb_events(self):
        self._sys_kb_handler.stop()

