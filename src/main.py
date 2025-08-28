import sys
import os
import base64
import json
import subprocess
import time
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import requests

# ---------------- CONFIG ----------------
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "moondream"  # Using the default moondream model
DEFAULT_PROMPT = "Describe this image in detail for a visually impaired user."


# ---------------- CAPTION FUNCTION ----------------
def get_caption(path, prompt):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return f"(Error: invalid image → {path})"

    with open(path, "rb") as f:
        img_bytes = f.read()
        b64img = base64.b64encode(img_bytes).decode("utf-8")

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "images": [b64img],
        "stream": True
    }

    try:
        resp = requests.post(OLLAMA_URL, json=payload, stream=True)
        resp.raise_for_status()  # Raise an exception for bad status codes
        caption_parts = []
        for line in resp.iter_lines():
            if not line:
                continue
            try:
                decoded = line.decode("utf-8")
                data = json.loads(decoded)
                if "response" in data:
                    caption_parts.append(data["response"])
                if data.get("done", False):
                    break
            except json.JSONDecodeError:
                # In case of malformed JSON, skip the line
                print(f"Warning: Could not decode JSON line: {line}")
                continue
        caption = "".join(caption_parts).strip()
        return caption if caption else "(No caption returned)"
    except requests.exceptions.RequestException as e:
        return f"(Error talking to Ollama: {e})"
    except Exception as e:
        return f"(An unexpected error occurred: {e})"


# ---------------- APP ----------------
class SnapCaptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SnapSense")
        self.root.geometry("800x700")
        self.root.resizable(True, True)

        # Set modern theme
        ctk.set_appearance_mode("dark")  # "light" or "dark"
        ctk.set_default_color_theme("blue")  # themes: "blue", "green", "dark-blue"

        # --------- Header ----------
        self.header = ctk.CTkLabel(root, text="📸 SnapSense: Image to Speech",
                                     font=ctk.CTkFont(size=24, weight="bold"))
        self.header.pack(pady=15)

        # --------- Prompt Frame ----------
        prompt_frame = ctk.CTkFrame(root, corner_radius=15)
        prompt_frame.pack(padx=20, pady=(0,10), fill="x")

        prompt_label = ctk.CTkLabel(prompt_frame, text="Custom Prompt:",
                                      font=ctk.CTkFont(size=16))
        prompt_label.pack(side="left", padx=10, pady=10)

        self.prompt_entry = ctk.CTkEntry(prompt_frame)
        self.prompt_entry.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        self.prompt_entry.insert(0, DEFAULT_PROMPT)

        # --------- Buttons Frame ----------
        button_frame = ctk.CTkFrame(root, corner_radius=15)
        button_frame.pack(pady=10, padx=20, fill="x")

        self.snap_btn = ctk.CTkButton(button_frame, text="📸 Snap Screenshot", command=self.snap_screenshot)
        self.snap_btn.pack(side="left", padx=10, pady=10, expand=True)

        self.choose_btn = ctk.CTkButton(button_frame, text="📂 Choose Image", command=self.choose_image)
        self.choose_btn.pack(side="left", padx=10, pady=10, expand=True)

        self.speak_btn = ctk.CTkButton(button_frame, text="🔊 Speak Caption", fg_color="green", hover_color="darkgreen",
                                       command=self.speak_caption)
        self.speak_btn.pack(side="left", padx=10, pady=10, expand=True)

        self.copy_btn = ctk.CTkButton(button_frame, text="📋 Copy Caption", fg_color="orange", hover_color="darkorange",
                                      command=self.copy_caption)
        self.copy_btn.pack(side="left", padx=10, pady=10, expand=True)

        self.save_btn = ctk.CTkButton(button_frame, text="💾 Save Caption", fg_color="purple", hover_color="darkviolet",
                                      command=self.save_caption)
        self.save_btn.pack(side="left", padx=10, pady=10, expand=True)

        # --------- Image Preview ----------
        self.image_label = ctk.CTkLabel(root, text="🖼 Image preview will appear here",
                                          font=ctk.CTkFont(size=16), height=300)
        self.image_label.pack(pady=20, padx=20, fill="both", expand=True)

        # --------- Caption Box ----------
        caption_frame = ctk.CTkFrame(root, corner_radius=15)
        caption_frame.pack(padx=20, pady=15, fill="both", expand=True)

        caption_label = ctk.CTkLabel(caption_frame, text="Generated Caption:",
                                       font=ctk.CTkFont(size=18, weight="bold"))
        caption_label.pack(anchor="w", padx=10, pady=5)

        self.caption_text = ctk.CTkTextbox(caption_frame, height=150, wrap="word", font=ctk.CTkFont(size=14))
        self.caption_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.caption_text.insert("1.0", "Your captions will appear here...")
        self.caption_text.configure(state="disabled")

        self.image_path = None

    # ---------------- UTIL ----------------
    @staticmethod
    def command_exists(cmd):
        return subprocess.call(
            f"type {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) == 0

    def raise_window(self):
        # This is a bit of a best-effort approach and might not work on all window managers
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)
        self.root.focus_force()

    # ---------------- SCREENSHOT ----------------
    def snap_screenshot(self):
        # Check for Wayland (grim) first, then X11 (scrot)
        screenshot_tool = None
        if self.command_exists("grim") and self.command_exists("slurp"):
             screenshot_tool = "grim"
        elif self.command_exists("scrot"):
            screenshot_tool = "scrot"
        else:
            messagebox.showerror("Error", "Screenshot tool not found. Please install 'grim' and 'slurp' (for Wayland) or 'scrot' (for X11).")
            return

        save_dir = os.path.expanduser("~/Pictures/SnapSenseCaptions")
        os.makedirs(save_dir, exist_ok=True)
        timestamp = int(time.time())
        img_path = os.path.join(save_dir, f"screenshot_{timestamp}.png")

        try:
            # Minimize window before capture
            self.root.iconify()
            time.sleep(0.5)  # allow time to minimize

            if screenshot_tool == "grim":
                subprocess.run(["grim", "-g", "$(slurp)", img_path], check=True, shell=True)
            else: # scrot
                subprocess.run(["scrot", "-s", img_path], check=True) # -s for selection

            # Wait for the file to be created and non-empty
            timeout = 5.0
            interval = 0.1
            waited = 0.0
            while (not os.path.exists(img_path) or os.path.getsize(img_path) == 0) and waited < timeout:
                time.sleep(interval)
                waited += interval

            if not os.path.exists(img_path) or os.path.getsize(img_path) == 0:
                messagebox.showerror("Error", f"Screenshot failed or was cancelled. File not created at {img_path}")
                return

        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to take screenshot: {e}")
            return
        finally:
            # Restore window after capture
            self.root.deiconify()
            self.raise_window()

        self.load_image(img_path)

    # ---------------- CHOOSE IMAGE ----------------
    def choose_image(self):
        path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
        )
        if path:
            self.load_image(path)

    # ---------------- LOAD IMAGE ----------------
    def load_image(self, path):
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            self.update_caption(f"Error: invalid image → {path}")
            return

        self.image_path = path
        
        # Calculate aspect ratio to fit image in preview box
        preview_width = self.image_label.winfo_width() - 20
        preview_height = self.image_label.winfo_height() - 20
        
        img = Image.open(path)
        img.thumbnail((preview_width, preview_height))
        
        tk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
        
        self.image_label.configure(image=tk_img, text="")

        self.update_caption("⏳ Generating caption...")

        # Use current prompt text
        prompt = self.prompt_entry.get().strip()
        if not prompt:
            prompt = DEFAULT_PROMPT

        threading.Thread(target=self.generate_caption, args=(path, prompt), daemon=True).start()

    # ---------------- THREADED CAPTION ----------------
    def generate_caption(self, path, prompt):
        caption = get_caption(path, prompt)
        # Schedule the UI update on the main thread
        self.root.after(0, self.update_caption, caption)

    # ---------------- UPDATE CAPTION ----------------
    def update_caption(self, text):
        self.caption_text.configure(state="normal")
        self.caption_text.delete("1.0", "end")
        self.caption_text.insert("1.0", text)
        self.caption_text.configure(state="disabled")

    # ---------------- SPEAK ----------------
    def speak_caption(self):
        caption = self.caption_text.get("1.0", "end-1c").strip()
        if caption and "Generating" not in caption and "Error" not in caption:
            if self.command_exists("espeak-ng"):
                subprocess.Popen(["espeak-ng", "-s", "150", caption])
            else:
                messagebox.showwarning("Warning", "espeak-ng not found. Cannot speak caption.")
        elif not caption:
             messagebox.showwarning("Warning", "No caption to speak.")

    # ---------------- COPY ----------------
    def copy_caption(self):
        caption = self.caption_text.get("1.0", "end-1c").strip()
        if caption:
            self.root.clipboard_clear()
            self.root.clipboard_append(caption)
            messagebox.showinfo("Copied", "Caption copied to clipboard!")

    # ---------------- SAVE CAPTION ----------------
    def save_caption(self):
        caption = self.caption_text.get("1.0", "end-1c").strip()
        if not caption or "Generating" in caption or "Error" in caption:
            messagebox.showwarning("Warning", "No valid caption to save.")
            return

        save_path = filedialog.asksaveasfilename(
            title="Save Caption As",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile="caption.txt"
        )
        if save_path:
            try:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(f"Image Source: {self.image_path}\n")
                    f.write("-" * 20 + "\n")
                    f.write(caption)
                messagebox.showinfo("Saved", f"Caption saved to:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save caption:\n{e}")


# ---------------- RUN ----------------
if __name__ == "__main__":
    root = ctk.CTk()
    app = SnapCaptionApp(root)
    root.mainloop()
