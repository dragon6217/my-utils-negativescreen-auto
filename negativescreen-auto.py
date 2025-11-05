import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from tkinter import filedialog # [ ★ 1. 추가 ★ ] 파일 탐색기용
from pathlib import Path

from models import MatrixCalculator, ConfigFileHandler
from preset_manager import PresetManager
from config_manager import ConfigManager # [ ★ 2. 추가 ★ ]

# --- 2. View & Controller (GUI 및 이벤트 처리) ---

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NegativeScreen 도우미")
        # [ ★ 3. 수정 ★ ] 창 세로 크기 늘리기
        self.geometry("370x580") 

        # --- Model 인스턴스 생성 ---
        self.calculator = MatrixCalculator()
        
        # [ ★ 4. 수정 ★ ] ConfigManager를 먼저 실행
        self.config_manager = ConfigManager()
        config_data = self.config_manager.get_paths()
        
        self.preset_manager = PresetManager()
        
        # [ ★ 5. 수정 ★ ] ConfigFileHandler에 저장된 경로를 주입
        loaded_conf_path = config_data.get("conf_path", "")
        self.handler = ConfigFileHandler(conf_path_str=loaded_conf_path)

        # --- UI에서 사용할 변수 ---
        self.color1_hex_var = tk.StringVar(value="#0e4700")
        self.color2_hex_var = tk.StringVar(value="#90f730")
        self.brightness_var = tk.DoubleVar(value=0.8)

        # [ ★ 6. 추가 ★ ] 경로 UI용 변수
        self.exe_path_var = tk.StringVar(value=config_data.get("exe_path", ""))
        self.conf_path_var = tk.StringVar(value=loaded_conf_path)

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
            self.main_frame, from_=0.0, to=1.0, increment=0.1, 
            textvariable=self.brightness_var, width=5
        )
        self.brightness_spinbox.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # --- (Grid row 4) 프리셋 5x5 그리드 (변경 없음) ---
        preset_frame = ttk.LabelFrame(self.main_frame, text="프리셋 저장 (In) / 불러오기 (Out)", padding="10", labelanchor="n")
        preset_frame.grid(row=4, column=0, columnspan=4, padx=5, pady=10, sticky="we")
        preset_grid_frame = ttk.Frame(preset_frame)
        preset_grid_frame.pack()
        all_presets = self.preset_manager.get_all_presets()
        PRESET_COLUMN_WIDTH = 4
        for i in range(5):
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
        
        # [ ★ 7. 추가 ★ ] 경로 설정 UI (Grid row 6)
        path_frame = ttk.LabelFrame(self.main_frame, text="경로 설정", padding="10")
        path_frame.grid(row=6, column=0, columnspan=4, padx=5, pady=10, sticky="we")
        
        # EXE 경로
        ttk.Label(path_frame, text="EXE 경로:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        exe_entry = ttk.Entry(path_frame, textvariable=self.exe_path_var, state="readonly", width=30)
        exe_entry.grid(row=0, column=1, padx=5, pady=5, sticky="we")
        ttk.Button(path_frame, text="찾아보기", command=self.browse_exe_path).grid(row=0, column=2, padx=5, pady=5)
        
        # CONF 경로
        ttk.Label(path_frame, text="CONF 경로:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        conf_entry = ttk.Entry(path_frame, textvariable=self.conf_path_var, state="readonly", width=30)
        conf_entry.grid(row=1, column=1, padx=5, pady=5, sticky="we")
        ttk.Button(path_frame, text="찾아보기", command=self.browse_conf_path).grid(row=1, column=2, padx=5, pady=5)
        
        # 경로 프레임의 2번째 열(column=1)이 남는 공간을 다 차지하도록 설정
        path_frame.columnconfigure(1, weight=1)

    
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
        # (이 함수는 변경 사항 없음)
        hotkey = self.hotkey_entry.get().strip()
        hex1 = self.color1_hex_var.get()
        hex2 = self.color2_hex_var.get()
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
            
            # self.handler는 이미 올바른 경로를 알고 있음
            self.handler.update_matrix(hotkey, new_matrix)

        except Exception as e:
            messagebox.showerror("실행 오류", f"적용 중 오류가 발생했습니다:\n{e}")

    # [ ★ 8. 추가 ★ ] 경로 탐색 및 저장용 함수들
    def browse_exe_path(self):
        """EXE 파일 탐색기 열기"""
        filepath = filedialog.askopenfilename(
            title="NegativeScreen 실행 파일 선택",
            filetypes=[("Executable", "*.exe"), ("All Files", "*.*")]
        )
        if filepath: # 사용자가 '열기'를 누른 경우
            self.exe_path_var.set(filepath)
            self._save_paths()

    def browse_conf_path(self):
        """CONF 파일 탐색기 열기"""
        filepath = filedialog.askopenfilename(
            title="negativescreen.conf 파일 선택",
            filetypes=[("Config files", "*.conf"), ("All Files", "*.*")]
        )
        if filepath: # 사용자가 '열기'를 누른 경우
            self.conf_path_var.set(filepath)
            self._save_paths()
            
            # [ ★ 중요 ★ ]
            # ConfigFileHandler 인스턴스에 새 경로를 실시간으로 업데이트
            self.handler.config_path = Path(filepath)

    def _save_paths(self):
        """현재 UI의 경로 변수들을 config.json에 저장"""
        self.config_manager.save_paths(
            exe_path=self.exe_path_var.get(),
            conf_path=self.conf_path_var.get()
        )
        print("경로가 저장되었습니다.")


# --- 3. 프로그램 실행 ---
if __name__ == "__main__":
    app = App()
    app.mainloop()