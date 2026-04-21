#!/usr/bin/python

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os
import glob
import threading
import re

FIRMWARE_BASE = "/dls_sw/work/ci-builds/d2afe-firmware"
TARGET = "f405"
SCRIPT_NAME = "d2afe-cli.py"

SUBDIR_MAP = {
    "D2AFE": "d2afe-firmware-f405",
    "D2PTD": "d2ptd-firmware-f405",
}

PROGRESS_RE = re.compile(r"Sent (\d+) bytes of (\d+) bytes")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("D2 Programmer")
        self.grid_columnconfigure(1, weight=1)

        # ---- State ----
        self.device = tk.StringVar(value="D2AFE")
        self.use_via_ptg = tk.BooleanVar(value=False)
        self.address = tk.IntVar(value=2)
        self.ip_addr = tk.StringVar(value="172.23.241.15")
        self.port = tk.IntVar(value=7003)

        self.release = tk.StringVar()
        self.script_release = tk.StringVar()
        self.binary_path = tk.StringVar()

        self.status_var = tk.StringVar(value="Idle")
        self.phase_var = tk.StringVar(value="")
        self.progress_var = tk.DoubleVar(value=0.0)

        pad = {"padx": 8, "pady": 4}

        # ---- Device ----
        ttk.Label(self, text="Device").grid(row=0, column=0, sticky="e", **pad)
        ttk.Radiobutton(self, text="D2AFE", variable=self.device, value="D2AFE",
                        command=self.refresh_releases).grid(row=0, column=1, sticky="w")
        ttk.Radiobutton(self, text="D2PTD", variable=self.device, value="D2PTD",
                        command=self.refresh_releases).grid(row=0, column=2, sticky="w")

        # ---- Via PTG ----
        ttk.Label(self, text="Via PTG?").grid(row=1, column=0, sticky="e", **pad)
        ttk.Checkbutton(self, variable=self.use_via_ptg)\
            .grid(row=1, column=1, sticky="w", **pad)

        # ---- Address ----
        ttk.Label(self, text="Address").grid(row=2, column=0, sticky="e", **pad)
        ttk.Combobox(
            self, textvariable=self.address,
            values=list(range(1, 16)),
            width=12, state="readonly"
        ).grid(row=2, column=1, sticky="w", **pad)

        # ---- IP / Port ----
        ttk.Label(self, text="IP address").grid(row=3, column=0, sticky="e", **pad)
        ttk.Entry(self, textvariable=self.ip_addr, width=25)\
            .grid(row=3, column=1, sticky="w", **pad)

        ttk.Label(self, text="Port").grid(row=4, column=0, sticky="e", **pad)
        ttk.Entry(self, textvariable=self.port, width=12)\
            .grid(row=4, column=1, sticky="w", **pad)

        # ---- Firmware release ----
        ttk.Label(self, text="Firmware release").grid(row=5, column=0, sticky="e", **pad)
        self.release_combo = ttk.Combobox(self, textvariable=self.release,
                                          width=25, state="readonly")
        self.release_combo.grid(row=5, column=1, sticky="w", **pad)

        # ---- Script version ----
        ttk.Label(self, text="Script version").grid(row=6, column=0, sticky="e", **pad)
        self.script_combo = ttk.Combobox(self, textvariable=self.script_release,
                                         width=25, state="readonly")
        self.script_combo.grid(row=6, column=1, sticky="w", **pad)

        # ---- Binary override ----
        ttk.Label(self, text="Binary path (override)").grid(row=7, column=0, sticky="e", **pad)
        ttk.Entry(self, textvariable=self.binary_path, width=40)\
            .grid(row=7, column=1, sticky="w", **pad)
        ttk.Button(self, text="Browse…", command=self.browse_binary)\
            .grid(row=7, column=2, **pad)

        # ---- Run ----
        ttk.Button(self, text="Run", command=self.run)\
            .grid(row=8, column=0, columnspan=3, pady=10)

        # ---- Status ----
        ttk.Label(self, textvariable=self.status_var)\
            .grid(row=9, column=0, columnspan=3, sticky="w", padx=8)
        ttk.Label(self, textvariable=self.phase_var)\
            .grid(row=10, column=0, columnspan=3, sticky="w", padx=8)
        ttk.Progressbar(self, variable=self.progress_var, maximum=100)\
            .grid(row=11, column=0, columnspan=3, sticky="ew", padx=8, pady=6)

        self.refresh_releases()

    # ---------- Discovery ----------

    def refresh_releases(self):
        releases = []

        try:
            for r in os.listdir(FIRMWARE_BASE):
                base = os.path.join(FIRMWARE_BASE, r, TARGET)
                if not os.path.isdir(base):
                    continue

                if self.device.get() == "D2PTD":
                    if os.path.isdir(os.path.join(base, SUBDIR_MAP["D2PTD"])):
                        releases.append(r)
                else:
                    if (os.path.isdir(os.path.join(base, SUBDIR_MAP["D2AFE"]))
                            or glob.glob(os.path.join(base, "*.bin"))):
                        releases.append(r)
        except FileNotFoundError:
            pass

        # Sort all releases by directory mtime (oldest → newest)
        releases.sort(
            key=lambda r: os.path.getmtime(os.path.join(FIRMWARE_BASE, r))
        )

        self.release_combo["values"] = releases
        self.script_combo["values"] = releases

        if not releases:
            self.release.set("")
            self.script_release.set("")
            return

        # Only allow defaults matching X.Y.Z
        version_re = re.compile(r"^\d+\.\d+\.\d+$")
        versioned = [r for r in releases if version_re.match(r)]

        if versioned:
            latest = max(
                versioned,
                key=lambda r: os.path.getmtime(os.path.join(FIRMWARE_BASE, r))
            )
        else:
            # Fallback: newest by time if no valid version dirs exist
            latest = releases[-1]

        self.release.set(latest)
        self.script_release.set(latest)

    def resolve_script(self):
        rel = self.script_release.get()
        base = os.path.join(FIRMWARE_BASE, rel, TARGET)

        preferred = os.path.join(base, SUBDIR_MAP["D2AFE"], SCRIPT_NAME)
        if os.path.isfile(preferred):
            return preferred

        legacy = os.path.join(base, SCRIPT_NAME)
        if os.path.isfile(legacy):
            return legacy

        raise FileNotFoundError("d2afe-cli.py not found")

    def resolve_binary(self):
        # Explicit override always wins
        override = self.binary_path.get().strip()
        if override:
            if not (os.path.isfile(override) and override.lower().endswith(".bin")):
                raise RuntimeError("Binary override is not a valid .bin file")
            return override

        base = os.path.join(FIRMWARE_BASE, self.release.get(), TARGET)
        preferred = os.path.join(base, SUBDIR_MAP[self.device.get()])

        search_dirs = []
        if os.path.isdir(preferred):
            # New layout
            search_dirs.append(preferred)
        else:
            # Legacy layout
            search_dirs.append(base)

        bins = []
        for d in search_dirs:
            bins.extend(glob.glob(os.path.join(d, "*.bin")))

        if len(bins) == 0:
            raise RuntimeError("No .bin file found")
        if len(bins) > 1:
            raise RuntimeError(f"Multiple .bin files found: {bins}")

        return bins[0]


    # ---------- Execution ----------

    def browse_binary(self):
        f = filedialog.askopenfilename(
            title="Select firmware binary",
            initialdir=FIRMWARE_BASE,
            filetypes=[("Binary files", "*.bin")]
        )
        if f:
            self.binary_path.set

    def run(self):
        try:
            script = self.resolve_script()
            binary = self.resolve_binary()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        cmd = [
            script,
            "--d2afe-address", str(self.address.get()),
            "--address", f"{self.ip_addr.get()}:{self.port.get()}",
            "program", "--target", TARGET,
            "--filepath", binary,
            "--no-ver-check",
        ]
        if self.use_via_ptg.get():
            cmd.insert(1, "--via-ptg")

        self.status_var.set("Running")
        self.phase_var.set("")
        self.progress_var.set(0)

        threading.Thread(
            target=self.run_process,
            args=(cmd,),
            daemon=True
        ).start()

    def run_process(self, cmd):
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        for line in proc.stdout:
            self.after(0, self.handle_output, line.rstrip())

        rc = proc.wait()
        self.after(0, self.finish, rc)

    def handle_output(self, line):
        print(line)

        if "Flashing temporal application" in line:
            self.phase_var.set("Flashing application")
            self.progress_var.set(0)

        elif "Flashing bootloader" in line:
            self.phase_var.set("Flashing bootloader")
            self.progress_var.set(0)

        m = PROGRESS_RE.search(line)
        if m:
            sent, total = map(int, m.groups())
            self.progress_var.set(sent * 100 / total)

    def finish(self, rc):
        self.status_var.set("Done" if rc == 0 else "Failed")
        if rc == 0:
            self.progress_var.set(100)


if __name__ == "__main__":
    App().mainloop()
