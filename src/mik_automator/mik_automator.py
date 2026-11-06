import glob
import logging
import os
import time
from pathlib import Path
import ctypes

import win32con
import win32gui
from pywinauto.application import Application, WindowSpecification
from pywinauto.base_wrapper import BaseWrapper
from pywinauto.remote_memory_block import RemoteMemoryBlock

root_dir = os.getenv("LOCALAPPDATA")
assert root_dir, "local appdata"
exe_files = glob.glob(
    "Programs/Mixed In Key/Mixed In Key*/MixedInKey.exe",
    root_dir=root_dir,
    recursive=True,
)
assert len(exe_files) != 0, "mik .exe not found"
assert len(exe_files) == 1, "more than 1 mik .exe found"
exe_file = os.path.join(root_dir, exe_files[0])


# Create window (or connect to existing)
def _get_mik_window(create_new_if_not_open: bool):
    app = Application(backend="uia")

    for i in range(3):
        try:
            try:
                app.connect(title_re="Mixed In Key.*")
            except:  # pylint: disable=bare-except
                if create_new_if_not_open:
                    app.start(exe_file)

            window = app.top_window()
            window.wait("ready", timeout=20)
            window.wait("visible", timeout=20)
            return window, app
        except:  # pylint: disable=bare-except
            if i == 2:
                logging.error("Could not open MIK")
                raise
        time.sleep(3)
    raise Exception("Could not open MIK")


def _select_folder(dialog: BaseWrapper, dir: str):
    """Selects a folder in a Browse For Folder dialog, which has no box to type a path in. The message's path is read
    by the dialog's process, so it has to be written into that process's memory."""
    path = ctypes.create_unicode_buffer(dir)
    memory = RemoteMemoryBlock(dialog, ctypes.sizeof(path))
    try:
        memory.Write(path)
        # 0x0467 is BFFM_SETSELECTIONW, the Windows message that selects a folder. True says it's given a path string.
        win32gui.SendMessage(dialog.handle, 0x0467, True, memory.Address())
    finally:
        memory.CleanUp()


def _add_folder(window: WindowSpecification, dir: str):
    # Add Files button has no identifier, so open its dialog with the keyboard shortcut.
    window.set_focus()
    window.type_keys("^o")

    # Add Folder button in dialog
    add_folder_btn = window.child_window(best_match="ADD FOLDERButton")
    add_folder_btn.click()

    folder_browser_popup = window.child_window(best_match="Browse For Folder")
    folder_browser_popup.wait("visible", timeout=20)
    dialog = folder_browser_popup.wrapper_object()
    _select_folder(dialog, os.path.abspath(dir))
    time.sleep(1)

    # OK after selected folder.
    win32gui.PostMessage(dialog.handle, win32con.WM_COMMAND, win32con.IDOK, 0)


def run(dir: str):
    window, app = _get_mik_window(create_new_if_not_open=True)
    # window.print_control_identifiers()

    # Maximize window to make coordinate clicking consistent.
    try:
        maximize_btn = window.child_window(auto_id="MaximizeButton")
        maximize_btn.click()
    except:  # pylint: disable=bare-except
        pass  # already maximized

    window.child_window(control_type="ProgressBar").wait_not("visible", timeout=60 * 5)

    _add_folder(window, dir)

    # Wait for files to be added
    ADDING_FILES = "Adding files to queue"
    window.child_window(best_match=ADDING_FILES).wait("visible", timeout=60 * 5)
    window.child_window(best_match=ADDING_FILES).wait_not("visible", timeout=60 * 5)
    window.child_window(control_type="ProgressBar").wait_not("visible", timeout=60 * 5)

    # Attempt to close. If window closes, analysis done. If confirmation popup appears, is not done.
    while True:
        close_button = window.child_window(auto_id="CloseButton")
        close_button.click()
        try:
            # Window item gets all weird here, sometimes can't find the NO button. Re-connect to the window.
            del app
            window, app = _get_mik_window(create_new_if_not_open=False)
            no_button = window.child_window(best_match="NOButton")
            no_button.wait("visible", timeout=5)
        except KeyboardInterrupt:
            input("press any key to continue checking mik")
            break
        except:  # pylint: disable=bare-except
            break
        no_button.click()
        time.sleep(10)


if __name__ == "__main__":
    dir = os.path.join(Path.home(), "Music\\DJ Tracks")
    print("adding dir: ", dir)
    run(dir)
