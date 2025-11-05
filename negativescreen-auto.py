import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from tkinter import filedialog
from pathlib import Path
import os               # [ ★ 1. 추가 ★ ] (os.startfile 용)
import subprocess       # [ ★ 2. 추가 ★ ] (taskkill 용)
import time             # [ ★ 3. 추가 ★ ] (time.sleep 용)

from models import MatrixCalculator, ConfigFileHandler
from preset_manager import PresetManager
from config_manager import ConfigManager
from constants import PRESET_COUNT, CALCULATED_WIDTH, APP_HEIGHT

# --- 2. View & Controller (GUI 및 이벤트 처리) ---

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NegativeScreen 도우미")
        
        # [ ★ 4. 수정 ★ ] 세로 크기를 재조정 (경로 UI가 1줄로 줄었으나 재시작 버튼 추가)
        # (기존 APP_HEIGHT는 580 이었음)
        self.geometry(f"{CALCULATED_WIDTH}x530") 

        # --- Model 인스턴스 생성 ---
        self.calculator = MatrixCalculator()
        
        # [ ★ 5. 수정 ★ ] 단일 폴더 경로를 읽어옴
        self.config_manager = ConfigManager()
        folder_path = self.config_manager.get_folder_path()
        
        self.preset_manager = PresetManager()
        
        # [ ★ 6. 수정 ★ ] 읽어온 폴더 경로로 .conf 파일 경로를 *조합*
        conf_path_str = ""
        if folder_path and Path(folder_path).exists():
            # str()로 감싸서 문자열로 만듦
            conf_path_str = str(Path(folder_path) / "negativescreen.conf")
            
        self.handler = ConfigFileHandler(conf_path_str=conf_path_str)

        # --- UI에서 사용할 변수 ---
        self.color1_hex_var = tk.StringVar(value="#0e4700")
        self.color2_hex_var = tk.StringVar(value="#90f730")
        self.brightness_var = tk.DoubleVar(value=0.8)

        # [ ★ 7. 수정 ★ ] 경로 UI용 변수 (단일 폴더)
        self.app_folder_path_var = tk.StringVar(value=folder_path)

        self.preset_ui_elements = []

        # 위젯 생성
        self.create_widgets()
        
        self.color1_hex_var.trace_add("write", self.update_preview1)
        self.color2_hex_var.trace_add("write", self.update_preview2)
        
        self.update_preview1()
        self.update_preview2()


    def create_widgets(self):
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # --- (Grid row 0~3) 메인 색상/설정 (변경 없음) ---
        PREVIEW_COLUMN_WIDTH = 5
        # ( ... 색상1, 색상2, 단축키, 밝기 UI 코드 ... )
        # ( ... (생략) ... )
        ttk.Label(self.main_frame, text="색상 1:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.color1_preview = tk.Label(self.main_frame, text="  ", bg="#0e4700", width=PREVIEW_COLUMN_WIDTH, relief="sunken")
        self.color1_preview.grid(row=0, column=1, padx=5, pady=5)
        self.color1_entry = ttk.Entry(self.main_frame, textvariable=self.color1_hex_var, width=10)
        self.color1_entry.grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(self.main_frame, text="팔레트", command=self.pick_color1).grid(row=0, column=3, padx=5, pady=5)
        ttk.Label(self.main_frame, text="색상 2:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.color2_preview = tk.Label(self.main_frame, text="  ", bg="#90f730", width=PREVIEW_COLUMN_WIDTH, relief="sunken")
        self.color2_preview.grid(row=1, column=1, padx=5, pady=5)
        self.color2_entry = ttk.Entry(self.main_frame, textvariable=self.color2_hex_var, width=10)
        self.color2_entry.grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(self.main_frame, text="팔레트", command=self.pick_color2).grid(row=1, column=3, padx=5, pady=5)
        ttk.Label(self.main_frame, text="대상 단축키:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.hotkey_entry = ttk.Entry(self.main_frame, width=20)
        self.hotkey_entry.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="we")
        self.hotkey_entry.insert(0, "ctrl+alt+v")
        ttk.Label(self.main_frame, text="밝기 (0.0 ~ 1.0):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.brightness_spinbox = ttk.Spinbox(
            self.main_frame, 
            from_=0.0, 
            to=1.0, 
            increment=0.05,        # [ ★ 1. 수정 ★ ] 0.1 -> 0.05
            format="%.2f",           # [ ★ 2. 추가 ★ ] 소수점 2자리까지 허용
            textvariable=self.brightness_var, 
            width=5
        )
        self.brightness_spinbox.grid(row=3, column=1, padx=5, pady=5, sticky="w")


        # --- (Grid row 4) 프리셋 그리드 (변경 없음) ---
        preset_frame = ttk.LabelFrame(self.main_frame, text="프리셋 저장 (In) / 불러오기 (Out)", padding="10", labelanchor="n")
        preset_frame.grid(row=4, column=0, columnspan=4, padx=5, pady=10, sticky="we")
        preset_grid_frame = ttk.Frame(preset_frame)
        preset_grid_frame.pack()
        all_presets = self.preset_manager.get_all_presets()
        PRESET_COLUMN_WIDTH = 4
        for i in range(PRESET_COUNT):
            data = all_presets[i]
            c1 = data.get('color1') or "SystemButtonFace"
            c2 = data.get('color2') or "SystemButtonFace"
            b_text = f"{data.get('brightness'):.1f}" if data.get('brightness') is not None else "N/A"
            c1_preview = tk.Label(preset_grid_frame, text="  ", bg=c1, width=PRESET_COLUMN_WIDTH, relief="sunken")
            c1_preview.grid(row=0, column=i, padx=5, pady=2, sticky="ew")
            c2_preview = tk.Label(preset_grid_frame, text="  ", bg=c2, width=PRESET_COLUMN_WIDTH, relief="sunken")
            c2_preview.grid(row=1, column=i, padx=5, pady=2, sticky="ew")
            b_label = ttk.Label(preset_grid_frame, text=b_text, anchor="center", width=PRESET_COLUMN_WIDTH)
            b_label.grid(row=2, column=i, padx=5, pady=2, sticky="ew")
            in_button = ttk.Button(preset_grid_frame, text="In", width=PRESET_COLUMN_WIDTH, command=lambda index=i: self.save_preset(index))
            in_button.grid(row=3, column=i, padx=5, pady=2, sticky="ew")
            out_button = ttk.Button(preset_grid_frame, text="Out", width=PRESET_COLUMN_WIDTH, command=lambda index=i: self.load_preset(index))
            out_button.grid(row=4, column=i, padx=5, pady=2, sticky="ew")
            self.preset_ui_elements.append((c1_preview, c2_preview, b_label))

        # --- (Grid row 5) 적용 버튼 (변경 없음) ---
        self.apply_button = ttk.Button(self.main_frame, text="설정 파일에 적용", command=self.apply_changes)
        self.apply_button.grid(row=5, column=0, columnspan=4, padx=5, pady=10, sticky="we")
        
        # [ ★ 8. 수정 ★ ] 경로 설정 UI (Grid row 6)
        path_frame = ttk.LabelFrame(self.main_frame, text="NegativeScreen 폴더 설정", padding="10", labelanchor="n")
        path_frame.grid(row=6, column=0, columnspan=4, padx=5, pady=10, sticky="we")
        
        ttk.Label(path_frame, text="App 폴더:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        folder_entry = ttk.Entry(path_frame, textvariable=self.app_folder_path_var, state="readonly", width=30)
        folder_entry.grid(row=0, column=1, padx=5, pady=5, sticky="we")
        ttk.Button(path_frame, text="폴더 찾기", command=self.browse_app_folder).grid(row=0, column=2, padx=5, pady=5)
        
        path_frame.columnconfigure(1, weight=1) # Entry가 가로로 늘어나도록 설정

        # [ ★ 9. 추가 ★ ] 재시작 버튼 (Grid row 7)
        self.restart_button = ttk.Button(self.main_frame, text="NegativeScreen 재시작", command=self.restart_negativescreen)
        self.restart_button.grid(row=7, column=0, columnspan=4, padx=5, pady=5, sticky="we")

    
    # --- (pick_color1 ~ _update_preset_ui_slot 함수들은 변경 없음) ---
    def pick_color1(self):
        current_hex = self.color1_hex_var.get()
        color = colorchooser.askcolor(initialcolor=current_hex)
        if color[1]:
            self.color1_hex_var.set(color[1])

    def pick_color2(self):
        current_hex = self.color2_hex_var.get()
        color = colorchooser.askcolor(initialcolor=current_hex)
        if color[1]:
            self.color2_hex_var.set(color[1])

    def update_preview1(self, *args):
        hex_code = self.color1_hex_var.get()
        try:
            self.color1_preview.config(bg=hex_code)
        except tk.TclError:
            self.color1_preview.config(bg="SystemButtonFace")

    def update_preview2(self, *args):
        hex_code = self.color2_hex_var.get()
        try:
            self.color2_preview.config(bg=hex_code)
        except tk.TclError:
            self.color2_preview.config(bg="SystemButtonFace")

    def load_preset(self, slot_index):
        print(f"프리셋 {slot_index}번 슬롯 불러오기...")
        data = self.preset_manager.get_preset(slot_index)
        if data and data.get('color1'):
            self.color1_hex_var.set(data['color1'])
            self.color2_hex_var.set(data['color2'])
            self.brightness_var.set(data['brightness'])
        else:
            print("빈 슬롯입니다.")

    def save_preset(self, slot_index):
        print(f"프리셋 {slot_index}번 슬롯에 저장...")
        hex1 = self.color1_hex_var.get()
        hex2 = self.color2_hex_var.get()
        brightness = self.brightness_var.get()
        self.preset_manager.save_preset(slot_index, hex1, hex2, brightness)
        self._update_preset_ui_slot(slot_index)

    def _update_preset_ui_slot(self, slot_index):
        data = self.preset_manager.get_preset(slot_index)
        if not data:
            return
        c1_preview, c2_preview, b_label = self.preset_ui_elements[slot_index]
        c1 = data.get('color1') or "SystemButtonFace"
        c2 = data.get('color2') or "SystemButtonFace"
        b_text = f"{data.get('brightness'):.1f}" if data.get('brightness') is not None else "N/A"
        c1_preview.config(bg=c1)
        c2_preview.config(bg=c2)
        b_label.config(text=b_text)
        
    def apply_changes(self):
        # [ ★ 10. 수정 ★ ] 폴더 경로가 비었는지 먼저 확인
        folder_path = self.app_folder_path_var.get()
        if not folder_path or not Path(folder_path).exists():
            messagebox.showwarning("폴더 필요", 
                                 "NegativeScreen 폴더가 설정되지 않았습니다.\n"
                                 "'폴더 찾기' 버튼을 눌러 설정해주세요.")
            # 새 폴더 찾기 함수를 바로 호출
            self.browse_app_folder()
            return # 적용 작업 중단

        # (이하 기존 로직)
        hotkey = self.hotkey_entry.get().strip()
        hex1 = self.color1_hex_var.get().strip()
        hex2 = self.color2_hex_var.get().strip()
        brightness = self.brightness_var.get()
        
        if not hotkey:
            messagebox.showwarning("입력 오류", "단축키를 입력하세요.")
            return
        if not (hex1.startswith('#') and len(hex1) == 7) or not (hex2.startswith('#') and len(hex2) == 7):
            messagebox.showwarning("입력 오류", "유효한 Hex 코드('#' 포함 7자리)를 입력하세요.")
            return

        try:
            new_matrix = self.calculator.calculate_matrix(hex1, hex2, brightness)
            if not new_matrix:
                messagebox.showerror("계산 오류", "매트릭스 계산에 실패했습니다.")
                return
            
            # self.handler는 __init__ 또는 browse_app_folder에서
            # 이미 올바른 경로로 업데이트 되었음.
            self.handler.update_matrix(hotkey, new_matrix)

        except Exception as e:
            messagebox.showerror("실행 오류", f"적용 중 오류가 발생했습니다:\n{e}")

    # [ ★ 11. 수정 ★ ] 
    # browse_exe_path, browse_conf_path, _save_paths 함수를 
    # 아래의 단일 함수로 교체
    
    def browse_app_folder(self):
        """NegativeScreen 폴더 탐색기 열기"""
        folder_path = filedialog.askdirectory(
            title="NegativeScreen 폴더 선택 (exe와 conf가 함께 있는 곳)"
        )
        if not folder_path: # 사용자가 '취소'를 누른 경우
            return

        # --- 선택한 폴더 검증 ---
        folder_path_obj = Path(folder_path)
        exe_path = folder_path_obj / "negativescreen.exe"
        conf_path = folder_path_obj / "negativescreen.conf"

        if not exe_path.exists() or not conf_path.exists():
            messagebox.showerror("파일 없음", 
                                 f"선택한 폴더에 'negativescreen.exe'와\n"
                                 f"'negativescreen.conf' 파일이 모두 존재해야 합니다.\n\n"
                                 f"폴더: {folder_path}")
            return
        
        # --- 검증 성공: 저장 및 업데이트 ---
        # 1. UI 변수 업데이트
        self.app_folder_path_var.set(folder_path)
        
        # 2. config.json에 영구 저장
        self.config_manager.save_folder_path(folder_path)
        
        # 3. ConfigFileHandler 인스턴스에 실시간으로 새 경로 주입
        self.handler.config_path = conf_path
        
        print(f"NegativeScreen 폴더가 '{folder_path}'로 설정되었습니다.")

    # [ ★ 12. 추가 ★ ] 재시작 로직
    def restart_negativescreen(self):
        """NegativeScreen 프로세스를 종료하고 다시 시작합니다."""
        
        folder_path = self.app_folder_path_var.get()
        if not folder_path:
            messagebox.showwarning("폴더 필요", 
                                 "NegativeScreen 폴더가 설정되지 않았습니다.\n"
                                 "'폴더 찾기' 버튼을 눌러 설정해주세요.")
            self.browse_app_folder()
            return

        exe_name = "negativescreen.exe"
        exe_full_path = Path(folder_path) / exe_name

        if not exe_full_path.exists():
             messagebox.showerror("파일 없음", 
                                 f"'negativescreen.exe' 파일을 찾을 수 없습니다.\n"
                                 f"경로: {exe_full_path}")
             return

        print(f"Trying to restart {exe_name}...")

        # 1. 종료 (taskkill)
        try:
            # shell=True: 윈도우 기본 명령어(taskkill) 실행
            # DEVNULL: 콘솔 창에 '성공' 메시지 등이 뜨지 않도록 함
            kill_command = f"taskkill /F /IM {exe_name}"
            subprocess.run(kill_command, check=True, shell=True, 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Killed process: {exe_name}")
        except subprocess.CalledProcessError as e:
            # 프로세스가 이미 꺼져있으면 오류가 발생함. 정상적인 상황임.
            print(f"Process '{exe_name}' not found (or error): {e}. Proceeding to start.")
        except Exception as e:
            messagebox.showerror("종료 오류", f"프로세스 종료 중 오류 발생: {e}")
            return

        # 2. 잠시 대기 (프로세스가 완전히 종료될 시간)
        time.sleep(0.5) # 0.5초

        # 3. 시작 (os.startfile)
        try:
            os.startfile(exe_full_path)
            print(f"Started process from: {exe_full_path}")
        except Exception as e:
            messagebox.showerror("시작 오류", 
                                 f"NegativeScreen을 시작하는 데 실패했습니다.\n"
                                 f"경로: {exe_full_path}\n"
                                 f"오류: {e}")

# --- 3. 프로그램 실행 ---
if __name__ == "__main__":
    app = App()
    app.mainloop()