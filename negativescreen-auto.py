import tkinter as tk
from tkinter import ttk, colorchooser, messagebox

from models import MatrixCalculator, ConfigFileHandler
from preset_manager import PresetManager

# --- 2. View & Controller (GUI 및 이벤트 처리) ---

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NegativeScreen 도우미")
        # [ ★ 1. 수정 ★ ] 창 가로폭 소폭 증가 (360 -> 370)
        self.geometry("370x480") 

        # Model 인스턴스 생성
        self.calculator = MatrixCalculator()
        self.handler = ConfigFileHandler()
        self.preset_manager = PresetManager()

        # UI에서 사용할 변수
        self.color1_hex_var = tk.StringVar(value="#0e4700")
        self.color2_hex_var = tk.StringVar(value="#90f730")
        self.brightness_var = tk.DoubleVar(value=0.8)

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

        # --- 메인 색상/설정 (Grid row 0~3) ---
        
        PREVIEW_COLUMN_WIDTH = 5
        
        ttk.Label(self.main_frame, text="색상 1:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        # [ ★ 2. 수정 ★ ] 미리보기 너비 (width=3 -> 4) (하단과 통일)
        self.color1_preview = tk.Label(self.main_frame, text="  ", bg="#0e4700", width=PREVIEW_COLUMN_WIDTH, relief="sunken")
        self.color1_preview.grid(row=0, column=1, padx=5, pady=5)
        self.color1_entry = ttk.Entry(self.main_frame, textvariable=self.color1_hex_var, width=10)
        self.color1_entry.grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(self.main_frame, text="팔레트", command=self.pick_color1).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(self.main_frame, text="색상 2:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        # [ ★ 3. 수정 ★ ] 미리보기 너비 (width=3 -> 4) (하단과 통일)
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

        # --- 프리셋 5x5 그리드 (Grid row 4) ---
        preset_frame = ttk.LabelFrame(self.main_frame, text="프리셋 저장 (In) / 불러오기 (Out)", padding="10", labelanchor="n")
        preset_frame.grid(row=4, column=0, columnspan=4, padx=5, pady=10, sticky="we")
        
        # [ ★ 4. 추가 ★ ] 5열 그리드를 가운데 정렬하기 위한 inner_frame
        preset_grid_frame = ttk.Frame(preset_frame)
        preset_grid_frame.pack() # .pack()의 기본값은 상하좌우 중앙 정렬
        
        all_presets = self.preset_manager.get_all_presets()
        
        # 프리셋 열의 공통 너비 (상단 미리보기와 동일하게)
        PRESET_COLUMN_WIDTH = 4

        for i in range(5): # 5개의 열(Column)
            data = all_presets[i]
            c1 = data.get('color1') or "SystemButtonFace"
            c2 = data.get('color2') or "SystemButtonFace"
            b_text = f"{data.get('brightness'):.1f}" if data.get('brightness') is not None else "N/A"
            
            # [ ★ 5. 수정 ★ ] 
            # 모든 위젯의 부모를 'preset_frame' -> 'preset_grid_frame'으로 변경
            
            # Row 0: 색상 1 미리보기
            c1_preview = tk.Label(preset_grid_frame, text="  ", bg=c1, width=PRESET_COLUMN_WIDTH, relief="sunken")
            c1_preview.grid(row=0, column=i, padx=5, pady=2, sticky="ew")
            
            # Row 1: 색상 2 미리보기
            c2_preview = tk.Label(preset_grid_frame, text="  ", bg=c2, width=PRESET_COLUMN_WIDTH, relief="sunken")
            c2_preview.grid(row=1, column=i, padx=5, pady=2, sticky="ew")
            
            # Row 2: 밝기 텍스트
            b_label = ttk.Label(preset_grid_frame, text=b_text, anchor="center", width=PRESET_COLUMN_WIDTH)
            b_label.grid(row=2, column=i, padx=5, pady=2, sticky="ew")
            
            # Row 3: 'In' 버튼 (먼저 나오도록)
            in_button = ttk.Button(preset_grid_frame, text="In", width=PRESET_COLUMN_WIDTH, command=lambda index=i: self.save_preset(index))
            in_button.grid(row=3, column=i, padx=5, pady=2, sticky="ew")
            
            # Row 4: 'Out' 버튼 (아래로)
            out_button = ttk.Button(preset_grid_frame, text="Out", width=PRESET_COLUMN_WIDTH, command=lambda index=i: self.load_preset(index))
            out_button.grid(row=4, column=i, padx=5, pady=2, sticky="ew")

            self.preset_ui_elements.append((c1_preview, c2_preview, b_label))

        # --- 적용 버튼 (Grid row 5) ---
        self.apply_button = ttk.Button(self.main_frame, text="설정 파일에 적용", command=self.apply_changes)
        self.apply_button.grid(row=5, column=0, columnspan=4, padx=5, pady=15, sticky="we")

    
    def pick_color1(self):
        # (이하 모든 로직 함수는 변경 사항 없음)
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
        hotkey = self.hotkey_entry.get().strip()
        
        hex1 = self.color1_hex_var.get().strip()
        hex2 = self.color2_hex_var.get().strip()
        
        brightness = self.brightness_var.get()
        
        if not hotkey:
            messagebox.showwarning("입력 오류", "단축키를 입력하세요. (예: ctrl+alt=v)")
            return
        if not (hex1.startswith('#') and len(hex1) == 7) or not (hex2.startswith('#') and len(hex2) == 7):
            messagebox.showwarning("입력 오류", "유효한 Hex 코드('#' 포함 7자리)를 입력하세요.")
            return

        try:
            new_matrix = self.calculator.calculate_matrix(hex1, hex2, brightness)
            if not new_matrix:
                messagebox.showerror("계산 오류", "매트릭스 계산에 실패했습니다. (공식 확인 필요)")
                return

            self.handler.update_matrix(hotkey, new_matrix)

        except Exception as e:
            messagebox.showerror("실행 오류", f"적용 중 오류가 발생했습니다:\n{e}")

# --- 3. 프로그램 실행 ---
if __name__ == "__main__":
    app = App()
    app.mainloop()