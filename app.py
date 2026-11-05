"""
app.py  –  TestLink CR XML Generator
GUI entry point (tkinter).

Workflow:
  1. Browse for the ISD .docx  → auto-detects API name & parameters
  2. Enter the CR number
  3. Edit the output filename if needed   (auto-filled as suggestion)
  4. Click Generate XML → Save-As dialog → done

Hardened against silent startup failures (common cause of "exe does not run"):
  - Any uncaught exception is written to TestLinkCRXMLGen_error.log next to the EXE
    and also shown in a message box.
"""

import os
import re
import sys
import traceback
import tkinter as tk
from tkinter import filedialog, messagebox

from extract_isd import extract_from_isd
from build_xml import build_xml

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------
CLR_HEADER_BG  = "#5B2D8E"   # WE / TelecomEgypt purple
CLR_HEADER_FG  = "#FFFFFF"
CLR_BTN_BG     = "#5B2D8E"
CLR_BTN_FG     = "#FFFFFF"
CLR_BTN_HOVER  = "#7B3DBE"
CLR_BODY_BG    = "#F7F5FA"
CLR_LABEL      = "#2D2040"
CLR_SUBLABEL   = "#6B5A85"
CLR_ENTRY_BG   = "#FFFFFF"
CLR_BORDER     = "#C8B8E8"
CLR_OK         = "#2E7D32"
CLR_WARN       = "#E65100"
CLR_ERR        = "#C62828"
CLR_DISABLED   = "#9E9E9E"


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _sanitize_filename(name: str) -> str:
    """Remove characters that Windows filesystems reject."""
    return re.sub(r'[/\\:*?"<>|]', "_", name)


def _make_button(parent, text, command, state="normal", **kw):
    # defaults that can be overridden by the caller
    opts = {
        "bg": CLR_BTN_BG,
        "fg": CLR_BTN_FG,
        "activebackground": CLR_BTN_HOVER,
        "activeforeground": CLR_BTN_FG,
        "relief": "flat",
        "padx": 14,
        "pady": 6,
        "font": ("Segoe UI", 10, "bold"),
        "cursor": "hand2",
        "state": state,
    }
    opts.update(kw)
    btn = tk.Button(parent, text=text, command=command, **opts)
    btn.bind("<Enter>", lambda _: btn.config(bg=CLR_BTN_HOVER) if btn["state"] == "normal" else None)
    btn.bind("<Leave>", lambda _: btn.config(bg=CLR_BTN_BG))
    return btn


def _make_label(parent, text, bold=False, sub=False):
    weight = "bold" if bold else "normal"
    color  = CLR_SUBLABEL if sub else CLR_LABEL
    return tk.Label(
        parent, text=text,
        font=("Segoe UI", 10, weight),
        bg=CLR_BODY_BG, fg=color,
        anchor="w",
    )


def _make_entry(parent, textvariable, width=52):
    return tk.Entry(
        parent, textvariable=textvariable,
        font=("Segoe UI", 10),
        bg=CLR_ENTRY_BG, fg=CLR_LABEL,
        relief="solid", bd=1,
        highlightthickness=1,
        highlightcolor=CLR_HEADER_BG,
        highlightbackground=CLR_BORDER,
        width=width,
    )


def _log_error(exc: BaseException) -> str:
    """Write full traceback next to the executable and return a short message."""
    try:
        if getattr(sys, "frozen", False):
            base = os.path.dirname(sys.executable)
        else:
            base = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(base, "TestLinkCRXMLGen_error.log")
        with open(log_path, "w", encoding="utf-8") as fh:
            fh.write(traceback.format_exc())
        return f"Error details written to:\n{log_path}\n\n{exc}"
    except Exception:
        return str(exc)


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TestLink CR XML Generator")
        self.resizable(False, False)
        self.configure(bg=CLR_BODY_BG)

        # State
        self._isd_path   = tk.StringVar()
        self._api_name   = tk.StringVar()
        self._params     : list = []
        self._cr_number  = tk.StringVar()
        self._out_name   = tk.StringVar()

        self._build_ui()

        # Traces
        self._cr_number.trace_add("write", self._on_cr_changed)
        self._api_name .trace_add("write", self._on_field_changed)
        self._out_name .trace_add("write", self._on_field_changed)

        self._refresh_state()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        # ── Header ──────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=CLR_HEADER_BG, height=58)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(
            hdr,
            text="  🔗  TestLink CR XML Generator",
            font=("Segoe UI", 13, "bold"),
            bg=CLR_HEADER_BG, fg=CLR_HEADER_FG,
            anchor="w",
        ).pack(side="left", padx=16, pady=0, fill="y")

        # ── Body ─────────────────────────────────────────────────────────
        body = tk.Frame(self, bg=CLR_BODY_BG, padx=22, pady=16)
        body.pack(fill="both", expand=True)

        # ── 1. ISD Document ──────────────────────────────────────────────
        _make_label(body, "1  ISD Document (.docx)", bold=True).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 2))

        isd_entry = _make_entry(body, self._isd_path, width=46)
        isd_entry.config(state="readonly")
        isd_entry.grid(row=1, column=0, columnspan=2, sticky="w")

        browse_btn = _make_button(body, "Browse…", self._pick_isd)
        browse_btn.grid(row=1, column=2, sticky="w", padx=(6, 0))

        # ── Detected API + params (shown after ISD is loaded) ────────────
        _make_label(body, "Detected API Name", bold=True).grid(
            row=2, column=0, columnspan=3, sticky="w", pady=(12, 2))

        api_entry = _make_entry(body, self._api_name, width=36)
        api_entry.grid(row=3, column=0, columnspan=2, sticky="w")

        self._params_lbl = _make_label(body, "", sub=True)
        self._params_lbl.grid(row=4, column=0, columnspan=3, sticky="w", pady=(4, 0))

        # ── 2. CR Number ─────────────────────────────────────────────────
        _make_label(body, "2  CR Number", bold=True).grid(
            row=5, column=0, columnspan=3, sticky="w", pady=(14, 2))

        cr_entry = _make_entry(body, self._cr_number, width=18)
        cr_entry.grid(row=6, column=0, sticky="w")

        # ── 3. Output Filename ────────────────────────────────────────────
        _make_label(body, "3  Output Filename", bold=True).grid(
            row=7, column=0, columnspan=3, sticky="w", pady=(14, 2))

        name_row = tk.Frame(body, bg=CLR_BODY_BG)
        name_row.grid(row=8, column=0, columnspan=3, sticky="w")

        name_entry = _make_entry(name_row, self._out_name, width=44)
        name_entry.pack(side="left")
        tk.Label(
            name_row, text=" .xml",
            font=("Segoe UI", 10), bg=CLR_BODY_BG, fg=CLR_SUBLABEL,
        ).pack(side="left")

        # ── Generate button ───────────────────────────────────────────────
        btn_row = tk.Frame(body, bg=CLR_BODY_BG)
        btn_row.grid(row=9, column=0, columnspan=3, sticky="w", pady=(18, 0))

        self._gen_btn = _make_button(
            btn_row, "  ✦  Generate XML  ", self._generate,
            state="disabled", padx=20, pady=8,
        )
        self._gen_btn.pack(side="left")

        # ── Status bar ────────────────────────────────────────────────────
        self._status = tk.Label(
            self, text="  Select an ISD .docx to begin.",
            font=("Segoe UI", 9), bg=CLR_BODY_BG, fg=CLR_SUBLABEL,
            anchor="w",
        )
        self._status.pack(fill="x", padx=10, pady=(4, 10))

        # Separator above status
        tk.Frame(self, bg=CLR_BORDER, height=1).pack(fill="x", before=self._status)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _pick_isd(self):
        path = filedialog.askopenfilename(
            title="Select ISD Document",
            filetypes=[("Word Documents", "*.docx"), ("All files", "*.*")],
        )
        if not path:
            return

        self._isd_path.set(path)
        try:
            api, params = extract_from_isd(path)
        except ValueError as exc:
            self._set_status(f"⚠  {exc}", CLR_ERR)
            self._api_name.set("")
            self._params = []
            self._params_lbl.config(text="")
            self._refresh_state()
            return
        except Exception as exc:
            msg = _log_error(exc)
            self._set_status(f"✗  Failed to read ISD", CLR_ERR)
            messagebox.showerror("Error reading ISD", msg)
            return

        self._api_name.set(api)
        self._params = params

        if params:
            preview = ", ".join(params[:6])
            if len(params) > 6:
                preview += f" … (+{len(params)-6} more)"
            self._params_lbl.config(
                text=f"Parameters ({len(params)}):  {preview}", fg=CLR_OK)
        else:
            self._params_lbl.config(
                text="⚠  No parameters detected — check the ISD table.", fg=CLR_WARN)

        self._rebuild_out_name()
        self._refresh_state()
        self._set_status(f"✓  Loaded: {os.path.basename(path)}", CLR_OK)

    def _on_cr_changed(self, *_):
        self._rebuild_out_name()
        self._refresh_state()

    def _on_field_changed(self, *_):
        self._refresh_state()

    def _rebuild_out_name(self):
        """Auto-fill the output filename from API + CR number."""
        api = self._api_name.get().strip()
        cr  = self._cr_number.get().strip()
        if api and cr:
            self._out_name.set(f"Message Broker13 Cloud - CR {cr} - {api}")
        elif cr:
            self._out_name.set(f"Message Broker13 Cloud - CR {cr}")

    def _refresh_state(self):
        ready = (
            bool(self._isd_path.get())
            and bool(self._api_name.get().strip())
            and bool(self._cr_number.get().strip())
            and bool(self._out_name.get().strip())
        )
        self._gen_btn.config(state="normal" if ready else "disabled")

    def _generate(self):
        api      = self._api_name.get().strip()
        cr_num   = self._cr_number.get().strip()
        out_name = self._out_name.get().strip()
        params   = self._params

        # Warn about missing parameters but don't block
        if not params:
            if not messagebox.askyesno(
                "No parameters detected",
                "No input parameters were found in the ISD document.\n"
                "The Success test case precondition will be empty.\n\n"
                "Generate anyway?",
            ):
                return

        safe_name = _sanitize_filename(out_name)
        out_path = filedialog.asksaveasfilename(
            title="Save TestLink XML",
            initialfile=safe_name + ".xml",
            defaultextension=".xml",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")],
        )
        if not out_path:
            return

        try:
            build_xml(
                api_name=api,
                params=params,
                cr_number=cr_num,
                suite_name=out_name,
                out_path=out_path,
            )
        except Exception as exc:
            msg = _log_error(exc)
            self._set_status(f"✗  Error writing XML", CLR_ERR)
            messagebox.showerror("Error", msg)
            return

        self._set_status(f"✓  Saved → {out_path}", CLR_OK)
        messagebox.showinfo("Done", f"XML saved to:\n{out_path}")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _set_status(self, msg: str, color: str = CLR_SUBLABEL):
        self._status.config(text=f"  {msg}", fg=color)


# ---------------------------------------------------------------------------
# Entry point – never let a crash be silent
# ---------------------------------------------------------------------------

def main():
    try:
        app = App()
        # Center window on screen
        app.update_idletasks()
        w, h = app.winfo_width(), app.winfo_height()
        sw, sh = app.winfo_screenwidth(), app.winfo_screenheight()
        app.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")
        app.mainloop()
    except Exception as exc:
        # Last-resort: write log + try to show a message box
        msg = _log_error(exc)
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "TestLink CR XML Generator – Startup Error",
                "The application failed to start.\n\n" + msg,
            )
            root.destroy()
        except Exception:
            # Even the message box failed – just print so a console build can see it
            print("FATAL:", msg, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
