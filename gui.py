import tkinter as tk
from tkinter import scrolledtext
import threading
import os
import sys
import json
import subprocess
import webbrowser
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

CONFIG_FILE = "config.json"


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class DonationDialog(ttk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("감사합니다!")

        # 부모 창 중앙에 위치시키기
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        dialog_width = 400
        dialog_height = 150
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        self.transient(parent)  # 부모 창 위에 항상 유지
        self.grab_set()  # 모달 창으로 만들어 다른 창과 상호작용 방지

        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(expand=True, fill=BOTH)

        message = "프로그램이 도움이 되셨다면,\n따뜻한 후원 부탁드립니다! ❤️"
        label = ttk.Label(main_frame, text=message, justify=CENTER, font=("-size", 12))
        label.pack(pady=(0, 20), expand=True)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(expand=True)

        close_button = ttk.Button(button_frame, text="시작하기", command=self.destroy, bootstyle="secondary")
        close_button.pack(side=LEFT, padx=10)

        donate_button = ttk.Button(button_frame, text="후원하기", command=self.donate_and_close, bootstyle="primary")
        donate_button.pack(side=LEFT, padx=10)

    def donate_and_close(self):
        self.parent.open_donation_link()
        self.destroy()
class CafeBotGUI(ttk.Window):
    def __init__(self):
        super().__init__(themename="litera")  # 모던한 'litera' 테마 적용
        self.title("네이버 카페 댓글 자동화 봇 @developearl")
        self.geometry("700x750")

        # Set application icon
        icon_path = resource_path("app_icon.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

        self.bot_thread = None
        self.bot_instance = None

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Help Links Frame ---
        help_frame = ttk.Frame(main_frame)
        help_frame.pack(fill=tk.X, pady=(10, 0), anchor=W)

        api_key_button = ttk.Button(help_frame, text="🔑 OpenAI API Key 발급 방법", command=self.open_api_key_guide,
                                    bootstyle="link-primary")
        api_key_button.pack(side=tk.LEFT, padx=5)

        manual_button = ttk.Button(help_frame, text="📖 프로그램 사용법", command=self.open_manual, bootstyle="link-primary")
        manual_button.pack(side=tk.LEFT, padx=5)

        dev_button = ttk.Button(help_frame, text="👨‍💻 개발자 소개", command=self.open_dev_page, bootstyle="link-primary")
        dev_button.pack(side=tk.LEFT, padx=5)

        # --- Input Frame ---
        input_frame = ttk.LabelFrame(main_frame, text="자동화 설정", padding="15")
        input_frame.pack(fill=tk.X, pady=(0, 10), expand=True)
        input_frame.columnconfigure(1, weight=1)

        # Labels and Entries
        labels = ["Naver ID:", "Naver PW:", "Cafe URL:", "Board ID:", "OPENAI_API_KEY"]
        self.entries = {}

        for i, label_text in enumerate(labels):
            label = ttk.Label(input_frame, text=label_text)
            label.grid(row=i, column=0, padx=5, pady=10, sticky=tk.W)

            entry = ttk.Entry(input_frame, width=50)
            if "PW" in label_text:
                entry.config(show="*")
            if "Cafe URL" in label_text:
                entry.insert(0, "https://cafe.naver.com/directwedding")
            elif "Board ID" in label_text:
                entry.insert(0, "menuLink113")

            entry.grid(row=i, column=1, padx=5, pady=10, sticky=tk.EW)
            self.entries[label_text.split(':')[0].replace(" ", "_")] = entry

        self.save_var = tk.BooleanVar()
        save_check = ttk.Checkbutton(input_frame, text="입력 정보 저장", variable=self.save_var, bootstyle="primary")
        save_check.grid(row=len(labels), column=0, columnspan=2, pady=10, sticky=tk.W)

        # --- System Prompt Frame ---
        prompt_frame = ttk.LabelFrame(main_frame, text="사용자 지정 프롬프트 (선택)", padding="15")
        prompt_frame.pack(fill=tk.BOTH, pady=10, expand=True)

        self.prompt_text = scrolledtext.ScrolledText(prompt_frame, wrap=tk.WORD, height=5, relief=tk.FLAT)
        self.prompt_text.pack(fill=tk.BOTH, expand=True)
        self.prompt_text.bind("<KeyRelease>", self.limit_prompt_length)



        # --- Control Frame ---
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        control_frame.columnconfigure((0, 1, 2), weight=1)

        self.start_button = ttk.Button(control_frame, text="시작하기", command=self.start_bot, bootstyle="success-outline")
        self.start_button.grid(row=0, column=0, padx=5, pady=5, sticky=tk.EW)

        self.stop_button = ttk.Button(control_frame, text="중지하기", command=self.stop_bot, state=tk.DISABLED, bootstyle="danger-outline")
        self.stop_button.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)

        donation_button = ttk.Button(control_frame, text="❤️ 후원하기", command=self.open_donation_link, bootstyle="primary")
        donation_button.grid(row=0, column=2, padx=5, pady=5, sticky=tk.EW)


        # --- Log Frame ---
        log_frame = ttk.LabelFrame(main_frame, text="로그", padding="15")
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state='disabled', height=10, relief=tk.FLAT)
        self.log_area.pack(fill=tk.BOTH, expand=True)

        self.load_config()

    def open_manual(self):
        """프로그램 사용법 웹사이트를 엽니다."""
        # !!! 아래 URL을 실제 사용법 안내 페이지 주소로 변경하세요 !!!
        url = "https://developerpearl.tistory.com/121"
        webbrowser.open_new_tab(url)
        self.log("프로그램 사용법 페이지를 엽니다.")

    def open_api_key_guide(self):
        """API 키 발급 안내 웹사이트를 엽니다."""
        url = "https://developerpearl.tistory.com/122"
        webbrowser.open_new_tab(url)
        self.log("OpenAI API Key 발급 안내 페이지를 엽니다.")

    def open_donation_link(self):
        """후원 웹사이트를 엽니다."""
        # !!! 아래 URL을 실제 후원 페이지 주소로 변경하세요 !!!
        url = "https://buymeacoffee.com/developearl"
        webbrowser.open_new_tab(url)
        self.log("후원 페이지를 엽니다. 감사합니다!")

    def limit_prompt_length(self, event=None):
        text_content = self.prompt_text.get("1.0", "end-1c")
        if len(text_content) > 2000:
            self.prompt_text.delete("1.0 + 2000c", tk.END)

    def open_dev_page(self):
        """개발자 소개 페이지를 엽니다."""
        # !!! 아래 URL을 실제 개발자 소개 페이지 주소로 변경하세요 !!!
        url = "https://github.com/dhdnjswnd"
        webbrowser.open_new_tab(url)
        self.log("개발자 소개 페이지를 엽니다.")

    def log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.config(state='disabled')
        self.log_area.see(tk.END)
        self.update_idletasks()




    def start_bot(self):
        # 후원 다이얼로그를 먼저 띄움
        dialog = DonationDialog(self)
        self.wait_window(dialog)  # 다이얼로그가 닫힐 때까지 대기

        if self.save_var.get():
            self.save_config()
        else:
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)

        login_id = self.entries["Naver_ID"].get()
        pw = self.entries["Naver_PW"].get()
        cafe_url = self.entries["Cafe_URL"].get()
        board_id = self.entries["Board_ID"].get()
        additional_prompt = self.prompt_text.get("1.0", tk.END).strip()

        if not all([login_id, pw, cafe_url, board_id]):
            self.log("오류: 모든 필드를 채워주세요.")
            return

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.log("봇을 시작합니다...")

        self.bot_thread = threading.Thread(
            target=self.run_bot_logic,
            args=(login_id, pw, cafe_url, board_id, additional_prompt),
            daemon=True
        )
        self.bot_thread.start()

    def run_bot_logic(self, login_id, pw, cafe_url, board_id, additional_prompt):
        try:
            from autologin_key import WeddingAssistantBot
            self.bot_instance = WeddingAssistantBot(login_id, pw, log_callback=self.log, additional_prompt=additional_prompt)
            self.bot_instance.execute(cafe_url, board_id)
            self.log("봇 작업이 완료되었습니다.")
        except Exception as e:
            self.log(f"오류가 발생했습니다: {e}")
        finally:
            if self.bot_instance:
                self.bot_instance.close()
            self.bot_instance = None
            self.after(0, self.reset_ui)

    def stop_bot(self):
        if self.bot_instance:
            self.log("봇을 중지합니다...")
            self.bot_instance.stop()
            self.after(0, self.reset_ui)
        else:
            self.log("봇이 실행 중이 아닙니다.")

    def reset_ui(self):
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def on_closing(self):
        if self.bot_thread and self.bot_thread.is_alive():
            if self.bot_instance:
                self.bot_instance.stop()
        self.destroy()

    def save_config(self):
        config_data = {}
        for key, entry in self.entries.items():
            if "PW" not in key:
                config_data[key] = entry.get()

        if "OPENAI_API_KEY" in config_data and config_data["OPENAI_API_KEY"]:
            os.environ["OPENAI_API_KEY"] = config_data["OPENAI_API_KEY"]
            set_windows_env_var("OPENAI_API_KEY", config_data["OPENAI_API_KEY"])

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            for key, value in config_data.items():
                if key in self.entries:
                    self.entries[key].delete(0, tk.END)
                    self.entries[key].insert(0, value)
            self.save_var.set(True)


def set_windows_env_var(name, value):
    subprocess.run(["setx", name, value], shell=True, capture_output=True)


if __name__ == "__main__":
    app = CafeBotGUI()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()