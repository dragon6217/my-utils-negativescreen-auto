import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from tkinter import filedialog
from pathlib import Path
import os
import subprocess
import time

from models import MatrixCalculator, ConfigFileHandler
from preset_manager import PresetManager
from config_manager import ConfigManager
# [ ★ 1. 수정 ★ ] APP_HEIGHT 값을 새것(570)으로 가져옴
from constants import PRESET_COUNT, CALCULATED_WIDTH, APP_HEIGHT

# --- 2. View & Controller (GUI 및 이벤트 처리) ---

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NegativeScreen 도우미")
        
        # [ ★ 2. 수정 ★ ] constants.py에서 계산된 새 높이(570) 적용
        self.geometry(f"{CALCULATED_WIDTH}x{APP_HEIGHT}") 

        # --- Model 인스턴스 생성 ---
        self.calculator = MatrixCalculator()
        self.config_manager = ConfigManager()
        folder_path = self.config_manager.get_folder_path()
        self.preset_manager = PresetManager()
        
        conf_path_str = ""
        if folder_path and Path(folder_path).exists():
            conf_path_str = str(Path(folder_path) / "negativescreen.conf")
        self.handler = ConfigFileHandler(conf_path_str=conf_path_str)

        # --- UI에서 사용할 변수 ---
        self.color1_hex_var = tk.StringVar(value="#0e4700")
        self.color2_hex_var = tk.StringVar(value="#90f730")
        self.brightness_var = tk.DoubleVar(value=0.8)
        
        # [ ★ 3. 추가 ★ ] 필터 강도(Strength) 변수 (기본값 1.0 = 100%)
        self.strength_var = tk.DoubleVar(value=1.0) 

        self.app_folder_path_var = tk.StringVar(value=folder_path)
        
        # [ ★ 4. 수정 ★ ] 프리셋 UI 요소에 s_label(강도 라벨) 추가
        self.preset_ui_elements = [] # (c1_preview, c2_preview, b_label, s_label) 튜플 저장

        # 위젯 생성
        self.create_widgets()
        
        self.color1_hex_var.trace_add("write", self.update_preview1)
        self.color2_hex_var.trace_add("write", self.update_preview2)
        
        self.update_preview1()
        self.update_preview2()


    def create_widgets(self):
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # --- (Grid row 0~3) 메인 색상/설정 ---
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
            self.main_frame, from_=0.0, to=1.0, increment=0.05, 
            format="%.2f", textvariable=self.brightness_var, width=5
        )
        self.brightness_spinbox.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # [ ★ 5. 추가 ★ ] 필터 강도 슬라이더 (Grid row 4)
        ttk.Label(self.main_frame, text="필터 강도:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        # Scale (슬라이더) 위젯 추가. 0.0 부터 1.0 까지
        strength_slider = ttk.Scale(
            self.main_frame, from_=0.0, to=1.0, 
            orient=tk.HORIZONTAL, variable=self.strength_var
        )
        # columnspan=3 으로 넓게
        strength_slider.grid(row=4, column=1, columnspan=3, padx=5, pady=5, sticky="we")


        # --- (Grid row 5) 프리셋 그리드 ---
        # [ ★ 6. 수정 ★ ] row=4 -> row=5
        preset_frame = ttk.LabelFrame(self.main_frame, text="프리셋 저장 (In) / 불러오기 (Out)", padding="10", labelanchor="n")
        preset_frame.grid(row=5, column=0, columnspan=4, padx=5, pady=10, sticky="we")
        preset_grid_frame = ttk.Frame(preset_frame)
        preset_grid_frame.pack()
        all_presets = self.preset_manager.get_all_presets()
        PRESET_COLUMN_WIDTH = 4
        
        for i in range(PRESET_COUNT):
            data = all_presets[i]
            c1 = data.get('color1') or "SystemButtonFace"
            c2 = data.get('color2') or "SystemButtonFace"
            
            # [ ★ 1. 수정 ★ ] 
            # data.get('brightness')가 None을 반환할 수 있으므로, 
            # 'or 0.8'을 사용해 None일 경우 0.8을 사용하도록 수정
            brightness_val = data.get('brightness') or 0.8 
            b_text = f"{brightness_val:.2f}"
            
            # [ ★ 2. 수정 ★ ] 
            # strength도 만약의 경우(수동 json 수정)를 대비해 방어 코드 추가
            strength_val = data.get('strength') or 1.0
            s_text = f"{strength_val:.2f}"
            
            c1_preview = tk.Label(preset_grid_frame, text="  ", bg=c1, width=PRESET_COLUMN_WIDTH, relief="sunken")
            c1_preview.grid(row=0, column=i, padx=5, pady=2, sticky="ew")
            c2_preview = tk.Label(preset_grid_frame, text="  ", bg=c2, width=PRESET_COLUMN_WIDTH, relief="sunken")
            c2_preview.grid(row=1, column=i, padx=5, pady=2, sticky="ew")
            
            # [ ★ 8. 수정 ★ ] 프리셋 그리드 행(row) 재배치
            # Row 2: 밝기 텍스트
            b_label = ttk.Label(preset_grid_frame, text=f"{b_text}", anchor="center", width=PRESET_COLUMN_WIDTH)
            b_label.grid(row=2, column=i, padx=5, pady=1, sticky="ew")
            # Row 3: 강도 텍스트 (신규)
            s_label = ttk.Label(preset_grid_frame, text=f"{s_text}", anchor="center", width=PRESET_COLUMN_WIDTH)
            s_label.grid(row=3, column=i, padx=5, pady=1, sticky="ew")
            # Row 4: In 버튼
            in_button = ttk.Button(preset_grid_frame, text="In", width=PRESET_COLUMN_WIDTH, command=lambda index=i: self.save_preset(index))
            in_button.grid(row=4, column=i, padx=5, pady=2, sticky="ew")
            # Row 5: Out 버튼
            out_button = ttk.Button(preset_grid_frame, text="Out", width=PRESET_COLUMN_WIDTH, command=lambda index=i: self.load_preset(index))
            out_button.grid(row=5, column=i, padx=5, pady=2, sticky="ew")

            # [ ★ 9. 수정 ★ ] s_label을 튜플에 추가
            self.preset_ui_elements.append((c1_preview, c2_preview, b_label, s_label))

        # --- (Grid row 6) 적용 버튼 ---
        # [ ★ 10. 수정 ★ ] row=5 -> row=6
        self.apply_button = ttk.Button(self.main_frame, text="설정 파일에 적용", command=self.apply_changes)
        self.apply_button.grid(row=6, column=0, columnspan=4, padx=5, pady=10, sticky="we")
        
        # --- (Grid row 7) 경로 설정 UI ---
        # [ ★ 11. 수정 ★ ] row=6 -> row=7
        path_frame = ttk.LabelFrame(self.main_frame, text="NegativeScreen 폴더 설정", padding="10", labelanchor="n")
        path_frame.grid(row=7, column=0, columnspan=4, padx=5, pady=10, sticky="we")
        ttk.Label(path_frame, text="App 폴더:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        folder_entry = ttk.Entry(path_frame, textvariable=self.app_folder_path_var, state="readonly", width=30)
        folder_entry.grid(row=0, column=1, padx=5, pady=5, sticky="we")
        ttk.Button(path_frame, text="폴더 찾기", command=self.browse_app_folder).grid(row=0, column=2, padx=5, pady=5)
        path_frame.columnconfigure(1, weight=1)

        # --- (Grid row 8) 재시작 버튼 ---
        # [ ★ 12. 수정 ★ ] row=7 -> row=8
        self.restart_button = ttk.Button(self.main_frame, text="NegativeScreen 재시작", command=self.restart_negativescreen)
        self.restart_button.grid(row=8, column=0, columnspan=4, padx=5, pady=5, sticky="we")

    
    # --- (pick_color1, pick_color2, update_preview... 로직은 변경 없음) ---
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
        try: self.color1_preview.config(bg=hex_code)
        except tk.TclError: self.color1_preview.config(bg="SystemButtonFace")
    def update_preview2(self, *args):
        hex_code = self.color2_hex_var.get()
        try: self.color2_preview.config(bg=hex_code)
        except tk.TclError: self.color2_preview.config(bg="SystemButtonFace")

    # --- (load/save/update 프리셋 함수 수정) ---
    
    def load_preset(self, slot_index):
        """프리셋 슬롯의 데이터를 메인 UI로 불러옵니다."""
        print(f"프리셋 {slot_index}번 슬롯 불러오기...")
        data = self.preset_manager.get_preset(slot_index)
        
        if data and data.get('color1'):
            self.color1_hex_var.set(data['color1'])
            self.color2_hex_var.set(data['color2'])
            self.brightness_var.set(data.get('brightness', 0.8))
            # [ ★ 13. 추가 ★ ] strength 값 로드 (없으면 1.0)
            self.strength_var.set(data.get('strength', 1.0))
        else:
            print("빈 슬롯입니다.")

    
    def save_preset(self, slot_index):
        """현재 메인 UI의 값을 프리셋 슬롯에 저장합니다."""
        print(f"프리셋 {slot_index}번 슬롯에 저장...")
        
        hex1 = self.color1_hex_var.get()
        hex2 = self.color2_hex_var.get()
        brightness = self.brightness_var.get()
        # [ ★ 14. 추가 ★ ] strength 값 가져오기
        strength = self.strength_var.get()
        
        # [ ★ 15. 수정 ★ ] strength 인자 전달
        self.preset_manager.save_preset(slot_index, hex1, hex2, brightness, strength)
        
        self._update_preset_ui_slot(slot_index) # UI 갱신

    
    def _update_preset_ui_slot(self, slot_index):
        """특정 프리셋 슬롯의 UI(색상, 텍스트)를 갱신합니다."""
        data = self.preset_manager.get_preset(slot_index)
        if not data: return
            
        # [ ★ 16. 수정 ★ ] 튜플에서 s_label도 가져옴
        c1_preview, c2_preview, b_label, s_label = self.preset_ui_elements[slot_index]
        
        c1 = data.get('color1') or "SystemButtonFace"
        c2 = data.get('color2') or "SystemButtonFace"
        b_text = f"{data.get('brightness', 0.8):.2f}"
        # [ ★ 17. 추가 ★ ] strength 텍스트 생성
        s_text = f"{data.get('strength', 1.0):.2f}"
        
        c1_preview.config(bg=c1)
        c2_preview.config(bg=c2)
        b_label.config(text=b_text)
        # [ ★ 18. 추가 ★ ] s_label 텍스트 업데이트
        s_label.config(text=s_text)
        

    def apply_changes(self):
        """설정 파일에 적용 (apply)"""
        folder_path = self.app_folder_path_var.get()
        if not folder_path or not Path(folder_path).exists():
            messagebox.showwarning("폴더 필요", 
                                 "NegativeScreen 폴더가 설정되지 않았습니다.\n"
                                 "'폴더 찾기' 버튼을 눌러 설정해주세요.")
            self.browse_app_folder()
            return

        hotkey = self.hotkey_entry.get().strip()
        hex1 = self.color1_hex_var.get().strip()
        hex2 = self.color2_hex_var.get().strip()
        brightness = self.brightness_var.get()
        # [ ★ 19. 추가 ★ ] strength 값 가져오기
        strength = self.strength_var.get()
        
        if not hotkey:
            messagebox.showwarning("입력 오류", "단축키를 입력하세요.")
            return
        if not (hex1.startswith('#') and len(hex1) == 7) or not (hex2.startswith('#') and len(hex2) == 7):
            messagebox.showwarning("입력 오류", "유효한 Hex 코드('#' 포함 7자리)를 입력하세요.")
            return

        try:
            # [ ★ 20. 수정 ★ ] strength 인자 전달
            new_matrix = self.calculator.calculate_matrix(
                hex1, hex2, brightness, strength
            )
            
            if not new_matrix:
                messagebox.showerror("계산 오류", "매트릭스 계산에 실패했습니다.")
                return
            
            self.handler.update_matrix(hotkey, new_matrix)

        except Exception as e:
            messagebox.showerror("실행 오류", f"적용 중 오류가 발생했습니다:\n{e}")

    # --- (browse_app_folder, restart_negativescreen 함수는 변경 없음) ---
    def browse_app_folder(self):
        folder_path = filedialog.askdirectory(title="NegativeScreen 폴더 선택 (exe와 conf가 함께 있는 곳)")
        if not folder_path: return
        folder_path_obj = Path(folder_path)
        exe_path = folder_path_obj / "negativescreen.exe"
        conf_path = folder_path_obj / "negativescreen.conf"
        if not exe_path.exists() or not conf_path.exists():
            messagebox.showerror("파일 없음", 
                                 f"선택한 폴더에 'negativescreen.exe'와\n"
                                 f"'negativescreen.conf' 파일이 모두 존재해야 합니다.\n\n"
                                 f"폴더: {folder_path}")
            return
        self.app_folder_path_var.set(folder_path)
        self.config_manager.save_folder_path(folder_path)
        self.handler.config_path = conf_path
        print(f"NegativeScreen 폴더가 '{folder_path}'로 설정되었습니다.")

    def restart_negativescreen(self):
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
        try:
            kill_command = f"taskkill /F /IM {exe_name}"
            subprocess.run(kill_command, check=True, shell=True, 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Killed process: {exe_name}")
        except subprocess.CalledProcessError as e:
            print(f"Process '{exe_name}' not found (or error): {e}. Proceeding to start.")
        except Exception as e:
            messagebox.showerror("종료 오류", f"프로세스 종료 중 오류 발생: {e}")
            return
        time.sleep(0.5)
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