import time
import threading
import random
import tkinter as tk
from tkinter import ttk
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, KeyCode


BUTTON_CHOICES = {
    "Left": Button.left,
    "Right": Button.right,
}

MODE_CHOICES = ["Continuous", "Burst (150+40)"]


class ClickMouse(threading.Thread):
    def __init__(self, mouse_controller):
        super().__init__(daemon=True)
        self.mouse = mouse_controller
        self.delay = 0.01
        self.button = Button.left
        self.mode = "Continuous"
        self.variance_enabled = False
        self.variance = 0.0
        self.running = False
        self.program_running = True

    def configure(self, delay, button, mode, variance_enabled=False, variance=0.0):
        self.delay = delay
        self.button = button
        self.mode = mode
        self.variance_enabled = variance_enabled
        self.variance = variance

    def start_clicking(self):
        self.running = True

    def stop_clicking(self):
        self.running = False

    def exit(self):
        self.stop_clicking()
        self.program_running = False

    def run(self):
        while self.program_running:
            if self.running:
                if self.mode == "Continuous":
                    self._run_continuous()
                else:
                    self._run_burst()
            else:
                time.sleep(0.05)

    def _sleep_delay(self):
        if self.variance_enabled and self.variance > 0:
            jitter = random.uniform(-self.variance, self.variance)
            time.sleep(max(self.delay * 0.25, self.delay + jitter))
        else:
            time.sleep(self.delay)

    def _run_continuous(self):
        while self.running:
            self.mouse.click(self.button)
            self._sleep_delay()

    def _run_burst(self):
        while self.running:
            time.sleep(1)
            self.mouse.click(self.button)
            time.sleep(0.5)
            counter = 0
            while counter < 150 and self.running:
                self.mouse.click(self.button)
                self._sleep_delay()
                counter += 1
            time.sleep(1)
            counter = 0
            while counter < 40 and self.running:
                self.mouse.click(self.button)
                self._sleep_delay()
                counter += 1


class AutoClickerUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PotatoClicker")
        self.resizable(False, False)

        # Uppercase P requires Shift — intentional guard against accidental toggles.
        self.hotkey = KeyCode(char='P')
        self.listener = None
        self.rebind_listener = None

        self.mouse = Controller()
        self.click_thread = ClickMouse(self.mouse)
        self.click_thread.start()

        self._build_ui()
        self._start_listener()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        frame = ttk.Frame(self, padding=12)
        frame.grid(row=0, column=0)

        ttk.Label(frame, text="Delay (seconds):").grid(row=0, column=0, sticky="w", pady=4)
        self.delay_var = tk.DoubleVar(value=0.1)
        self.delay_spin = ttk.Spinbox(
            frame, from_=0.001, to=10.0, increment=0.01,
            textvariable=self.delay_var, width=10, format="%.3f",
        )
        self.delay_spin.grid(row=0, column=1, sticky="w", pady=4)

        ttk.Label(frame, text="Mouse button:").grid(row=1, column=0, sticky="w", pady=4)
        self.button_var = tk.StringVar(value="Left")
        self.button_combo = ttk.Combobox(
            frame, textvariable=self.button_var,
            values=list(BUTTON_CHOICES.keys()), state="readonly", width=8,
        )
        self.button_combo.grid(row=1, column=1, sticky="w", pady=4)

        ttk.Label(frame, text="Click mode:").grid(row=2, column=0, sticky="w", pady=4)
        self.mode_var = tk.StringVar(value="Continuous")
        self.mode_combo = ttk.Combobox(
            frame, textvariable=self.mode_var,
            values=MODE_CHOICES, state="readonly", width=16,
        )
        self.mode_combo.grid(row=2, column=1, sticky="w", pady=4)

        self.variance_enabled_var = tk.BooleanVar(value=False)
        self.variance_check = ttk.Checkbutton(
            frame, text="Add variance (±s)",
            variable=self.variance_enabled_var, command=self._on_variance_toggle,
        )
        self.variance_check.grid(row=3, column=0, sticky="w", pady=4)
        self.variance_var = tk.DoubleVar(value=0.0)
        self.variance_spin = ttk.Spinbox(
            frame, from_=0.0, to=5.0, increment=0.01,
            textvariable=self.variance_var, width=10, format="%.3f",
            state="disabled",
        )
        self.variance_spin.grid(row=3, column=1, sticky="w", pady=4)

        ttk.Label(frame, text="Toggle hotkey:").grid(row=4, column=0, sticky="w", pady=4)
        hotkey_frame = ttk.Frame(frame)
        hotkey_frame.grid(row=4, column=1, sticky="w", pady=4)
        self.hotkey_label = ttk.Label(
            hotkey_frame, text=self._hotkey_display(),
            width=8, relief="sunken", anchor="center",
        )
        self.hotkey_label.pack(side="left", padx=(0, 6))
        self.rebind_btn = ttk.Button(hotkey_frame, text="Rebind…", command=self._rebind)
        self.rebind_btn.pack(side="left")

        self.status_var = tk.StringVar(value="Status: Stopped")
        ttk.Label(frame, textvariable=self.status_var).grid(
            row=5, column=0, columnspan=2, sticky="w", pady=(12, 4)
        )

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=6, column=0, columnspan=2, sticky="w")
        ttk.Button(btn_frame, text="Start", command=self._start).pack(side="left", padx=(0, 6))
        ttk.Button(btn_frame, text="Stop", command=self._stop).pack(side="left")

    def _hotkey_display(self):
        if isinstance(self.hotkey, KeyCode) and self.hotkey.char:
            return self.hotkey.char
        return str(self.hotkey).replace("Key.", "")

    def _on_variance_toggle(self):
        if self.click_thread.running:
            return
        state = "normal" if self.variance_enabled_var.get() else "disabled"
        self.variance_spin.configure(state=state)

    def _set_config_widgets_enabled(self, enabled):
        state = "normal" if enabled else "disabled"
        combo_state = "readonly" if enabled else "disabled"
        self.delay_spin.configure(state=state)
        self.button_combo.configure(state=combo_state)
        self.mode_combo.configure(state=combo_state)
        self.rebind_btn.configure(state=state)
        self.variance_check.configure(state=state)
        if enabled and self.variance_enabled_var.get():
            self.variance_spin.configure(state="normal")
        else:
            self.variance_spin.configure(state="disabled")

    def _start(self):
        if self.click_thread.running:
            return
        try:
            delay = float(self.delay_var.get())
        except (tk.TclError, ValueError):
            return
        delay = max(delay, 0.001)
        button = BUTTON_CHOICES[self.button_var.get()]
        mode = "Continuous" if self.mode_var.get() == "Continuous" else "Burst"
        try:
            variance = float(self.variance_var.get())
        except (tk.TclError, ValueError):
            variance = 0.0
        variance = max(variance, 0.0)
        variance_enabled = self.variance_enabled_var.get()
        self.click_thread.configure(delay, button, mode, variance_enabled, variance)
        self.click_thread.start_clicking()
        self._set_config_widgets_enabled(False)
        self.status_var.set("Status: Running")

    def _stop(self):
        if not self.click_thread.running:
            return
        self.click_thread.stop_clicking()
        self._set_config_widgets_enabled(True)
        self.status_var.set("Status: Stopped")

    def _toggle(self):
        if self.click_thread.running:
            self._stop()
        else:
            self._start()

    def _on_key_press(self, key):
        if key == self.hotkey:
            self.after(0, self._toggle)

    def _start_listener(self):
        self.listener = Listener(on_press=self._on_key_press)
        self.listener.daemon = True
        self.listener.start()

    def _stop_listener(self):
        if self.listener is not None:
            self.listener.stop()
            self.listener = None

    def _rebind(self):
        if self.click_thread.running:
            return
        dialog = tk.Toplevel(self)
        dialog.title("Rebind hotkey")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)
        ttk.Label(dialog, text="Press any key to bind…", padding=20).pack()

        def on_press(key):
            self.after(0, lambda: self._apply_rebind(key, dialog))
            return False

        self._stop_listener()
        self.rebind_listener = Listener(on_press=on_press)
        self.rebind_listener.daemon = True
        self.rebind_listener.start()

        dialog.protocol("WM_DELETE_WINDOW", lambda: self._cancel_rebind(dialog))

    def _apply_rebind(self, key, dialog):
        self.hotkey = key
        self.hotkey_label.configure(text=self._hotkey_display())
        dialog.destroy()
        self.rebind_listener = None
        self._start_listener()

    def _cancel_rebind(self, dialog):
        if self.rebind_listener is not None:
            self.rebind_listener.stop()
            self.rebind_listener = None
        dialog.destroy()
        self._start_listener()

    def _on_close(self):
        self.click_thread.exit()
        self._stop_listener()
        if self.rebind_listener is not None:
            self.rebind_listener.stop()
        self.destroy()


def main():
    app = AutoClickerUI()
    app.mainloop()


if __name__ == "__main__":
    main()
