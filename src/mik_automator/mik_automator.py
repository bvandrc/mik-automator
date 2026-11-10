import ctypes
import glob
import logging
import os
import time

# where comtypes gets it from: comtypes re-exports it, but from 1.5.0 pyright counts that as private
from _ctypes import COMError
from pathlib import Path
from typing import Callable

import win32con
import win32gui
from pywinauto.application import Application, WindowSpecification
from pywinauto.base_wrapper import BaseWrapper
from pywinauto.findwindows import find_windows
from pywinauto.remote_memory_block import RemoteMemoryBlock
from pywinauto.timings import TimeoutError as WaitTimeoutError, wait_until, wait_until_passes

from mik_automator import mik_db

MIK_TITLE_RE = "Mixed In Key.*"


def _get_exe_file():
    root_dir = os.getenv("LOCALAPPDATA")
    assert root_dir, "local appdata"
    exe_files = glob.glob(
        "Programs/Mixed In Key/Mixed In Key*/MixedInKey.exe",
        root_dir=root_dir,
        recursive=True,
    )
    assert len(exe_files) != 0, "mik .exe not found"
    assert len(exe_files) == 1, "more than 1 mik .exe found"
    return os.path.join(root_dir, exe_files[0])


# Create window (or connect to existing)
def _get_mik_window(create_new_if_not_open: bool):
    app = Application(backend="uia")

    for i in range(3):
        try:
            try:
                app.connect(title_re=MIK_TITLE_RE)
            except:  # pylint: disable=bare-except
                if create_new_if_not_open:
                    app.start(_get_exe_file())

            window = app.top_window()
            window.wait("ready", timeout=20)
            window.wait("visible", timeout=20)
            return window, app
        except:  # pylint: disable=bare-except
            if i == 2:
                if create_new_if_not_open:  # otherwise, not finding it just means that it closed
                    logging.error("Could not open MIK")
                raise
        time.sleep(3)
    raise Exception("Could not open MIK")


def _is_mik_open():
    return len(find_windows(title_re=MIK_TITLE_RE)) > 0


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


def _retry_on_com_error(wait: Callable[[], object]):
    """Runs a wait on the window, again if it fails with a COMError, which reading a control as it closes can raise."""
    wait_until_passes(60 * 5, 1, wait, COMError)


def _wait_for_files_added(window: WindowSpecification):
    adding_files = window.child_window(best_match="Adding files to queue")
    try:
        _retry_on_com_error(lambda: adding_files.wait("visible", timeout=30))
    except WaitTimeoutError:
        pass  # a quick add's popup can be gone before we look
    _retry_on_com_error(lambda: adding_files.wait_not("visible", timeout=60 * 5))
    _retry_on_com_error(lambda: window.child_window(control_type="ProgressBar").wait_not("visible", timeout=60 * 5))


def _get_db_state():
    stat = os.stat(mik_db.db_file)
    return stat.st_size, stat.st_mtime_ns


def _wait_for_db_to_go_quiet(quiet_seconds: int):
    """Waits until the database stops changing. It's written to as each track finishes, so changes mean it's analyzing."""
    state = _get_db_state()
    last_change_time = time.time()
    while time.time() - last_change_time < quiet_seconds:
        time.sleep(1)
        new_state = _get_db_state()
        if new_state != state:
            state = new_state
            last_change_time = time.time()


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
    _wait_for_files_added(window)

    # Attempt to close once the database is quiet. If window closes, analysis done. If confirmation popup appears, a long
    # analysis is still going, so wait for quiet again.
    while True:
        _wait_for_db_to_go_quiet(quiet_seconds=20)
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
        except Exception:  # pylint: disable=broad-exception-caught
            # No confirmation popup, so it should be closing. Fails if it stays open, rather than leaving it analyzing.
            wait_until(30, 1, _is_mik_open, False)
            break
        no_button.click()


if __name__ == "__main__":
    dir = os.path.join(Path.home(), "Music\\DJ Tracks")
    print("adding dir: ", dir)
    run(dir)
