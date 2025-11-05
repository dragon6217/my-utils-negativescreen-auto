import tkinter as tk
from tkinter import ttk, colorchooser, messagebox

# models.py에서 기존 클래스들을 가져옴
from models import MatrixCalculator, ConfigFileHandler
# preset_manager.py에서 새 클래스를 가져옴
from preset_manager import PresetManager

# --- 2. View & Controller (GUI 및 이벤트 처리) ---

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NegativeScreen 도우미")
        # [ ★ 1. 수정 ★ ] 창 크기(세로) 늘리기
        self.geometry("400x480") 

        # Model 인스턴스 생성
        self.calculator = MatrixCalculator()
        self.handler = ConfigFileHandler()
        # [ ★ 2. 추가 ★ ] 프리셋 매니저 인스턴스 생성
        self.preset_manager = PresetManager()

        # UI에서 사용할 변수
        self.color1_hex_var = tk.StringVar(value="#0e4700")
        self.color2_hex_var = tk.StringVar(value="#90f730")
        self.brightness_var = tk.DoubleVar(value=0.8)

        # [ ★ 3. 추가 ★ ] 프리셋 UI 요소를 저장할 리스트
        # (c1_preview, c2_preview, b_label) 튜플을 저장
        self.preset_ui_elements = []

        # 위젯 생성
        self.create_widgets()
        
        # Entry의 텍스트가 변경될 때마다 update_preview 함수를 호출
        self.color1_hex_var.trace_add("write", self.update_preview1)
        self.color2_hex_var.trace_add("write", self.update_preview2)
        
        # 프로그램 시작 시 초기 색상으로 미리보기 업데이트
        self.update_preview1()
        self.update_preview2()


    def create_widgets(self):
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 메인 색상/설정 (Grid row 0~3) ---
        # (이 부분은 동일)
        ttk.Label(self.main_frame, text="색상 1:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.color1_preview = tk.Label(self.main_frame, text="  ", bg="#0e4700", width=3, relief="sunken")
        self.color1_preview.grid(row=0, column=1, padx=5, pady=5)
        self.color1_entry = ttk.Entry(self.main_frame, textvariable=self.color1_hex_var, width=10)
        self.color1_entry.grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(self.main_frame, text="팔레트", command=self.pick_color1).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(self.main_frame, text="색상 2:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.color2_preview = tk.Label(self.main_frame, text="  ", bg="#90f730", width=3, relief="sunken")
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

        # [ ★ 4. 추가 ★ ] 프리셋 5x5 그리드 (Grid row 4)
        preset_frame = ttk.LabelFrame(self.main_frame, text="프리셋 저장 (In) / 불러오기 (Out)", padding="10")
        # main_frame의 (row=4) 위치에, 4개 열을 모두 차지하도록(columnspan=4) 배치
        preset_frame.grid(row=4, column=0, columnspan=4, padx=5, pady=10, sticky="we")
        
        all_presets = self.preset_manager.get_all_presets()

        for i in range(5): # 5개의 열(Column)
            # 1. 초기 데이터 설정
            data = all_presets[i]
            c1 = data.get('color1') or "SystemButtonFace"
            c2 = data.get('color2') or "SystemButtonFace"
            b_text = f"{data.get('brightness'):.1f}" if data.get('brightness') is not None else "N/A"
            
            # 2. UI 생성 (preset_frame 내부의 Grid)
            # Row 0: 색상 1 미리보기
            c1_preview = tk.Label(preset_frame, text="  ", bg=c1, width=5, relief="sunken")
            c1_preview.grid(row=0, column=i, padx=5, pady=2, sticky="ew")
            
            # Row 1: 색상 2 미리보기
            c2_preview = tk.Label(preset_frame, text="  ", bg=c2, width=5, relief="sunken")
            c2_preview.grid(row=1, column=i, padx=5, pady=2, sticky="ew")
            
            # Row 2: 밝기 텍스트
            b_label = ttk.Label(preset_frame, text=b_text, anchor="center")
            b_label.grid(row=2, column=i, padx=5, pady=2, sticky="ew")
            
            # Row 3: 'Out' 버튼
            # (중요!) lambda index=i: 를 사용해야 현재 i 값을 정확히 기억합니다.
            out_button = ttk.Button(preset_frame, text="Out", command=lambda index=i: self.load_preset(index))
            out_button.grid(row=3, column=i, padx=5, pady=2, sticky="ew")
            
            # Row 4: 'In' 버튼
            in_button = ttk.Button(preset_frame, text="In", command=lambda index=i: self.save_preset(index))
            in_button.grid(row=4, column=i, padx=5, pady=2, sticky="ew")

            # 3. UI 요소 리스트에 추가 (나중에 업데이트하기 위해)
            self.preset_ui_elements.append((c1_preview, c2_preview, b_label))

        # [ ★ 5. 수정 ★ ] 적용 버튼 (Grid row 5)
        # 위치를 맨 아래(row=5)로 이동
        self.apply_button = ttk.Button(self.main_frame, text="설정 파일에 적용", command=self.apply_changes)
        self.apply_button.grid(row=5, column=0, columnspan=4, padx=5, pady=15, sticky="we")

    
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

    # [ ★ 6. 추가 ★ ] 프리셋 'Out' (불러오기) 로직
    def load_preset(self, slot_index):
        """프리셋 슬롯의 데이터를 메인 UI로 불러옵니다."""
        print(f"프리셋 {slot_index}번 슬롯 불러오기...")
        data = self.preset_manager.get_preset(slot_index)
        
        if data and data.get('color1'): # 데이터가 비어있지 않다면
            self.color1_hex_var.set(data['color1'])
            self.color2_hex_var.set(data['color2'])
            self.brightness_var.set(data['brightness'])
        else:
            print("빈 슬롯입니다.")

    # [ ★ 7. 추가 ★ ] 프리셋 'In' (저장) 로직
    def save_preset(self, slot_index):
        """현재 메인 UI의 값을 프리셋 슬롯에 저장합니다."""
        print(f"프리셋 {slot_index}번 슬롯에 저장...")
        
        # 1. 현재 메인 UI의 값을 가져옴
        hex1 = self.color1_hex_var.get()
        hex2 = self.color2_hex_var.get()
        brightness = self.brightness_var.get()
        
        # 2. 프리셋 매니저를 통해 파일에 저장
        self.preset_manager.save_preset(slot_index, hex1, hex2, brightness)
        
        # 3. 프리셋 그리드 UI를 즉시 업데이트
        self._update_preset_ui_slot(slot_index)

    # [ ★ 8. 추가 ★ ] 프리셋 UI 업데이트 헬퍼
    def _update_preset_ui_slot(self, slot_index):
        """특정 프리셋 슬롯의 UI(색상, 텍스트)를 갱신합니다."""
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
        """
Changes
        """
        # (이 함수는 변경 사항 없음)
        hotkey = self.hotkey_entry.get().strip()
        
        hex1 = self.color1_hex_var.get().strip()
        hex2 = self.color2_hex_var.get().strip()
        
        brightness = self.brightness_var.get()
        
        if not hotkey:
            messagebox.showwarning("입력 오류", "단축키를 입력하세요. (예: ctrl+alt+v)")
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