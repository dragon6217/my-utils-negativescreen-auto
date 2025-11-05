import tkinter as tk
from tkinter import ttk, colorchooser, messagebox

# [ ★ 1. 수정 ★ ]
# 같은 폴더에 있는 models.py 파일에서 두 클래스를 가져옵니다.
from models import MatrixCalculator, ConfigFileHandler

# --- 2. View & Controller (GUI 및 이벤트 처리) ---

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NegativeScreen 도우미")
        self.geometry("400x230")

        # Model 인스턴스 생성 (import 해온 클래스 사용)
        self.calculator = MatrixCalculator()
        self.handler = ConfigFileHandler()

        # UI에서 사용할 변수
        self.color1_hex_var = tk.StringVar(value="#0e4700")
        self.color2_hex_var = tk.StringVar(value="#90f730")
        
        # 밝기 값을 저장할 변수
        self.brightness_var = tk.DoubleVar()
        self.brightness_var.set(0.8)

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

        # --- 색상 1 ---
        ttk.Label(self.main_frame, text="색상 1:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.color1_preview = tk.Label(self.main_frame, text="  ", bg="#0e4700", width=3, relief="sunken")
        self.color1_preview.grid(row=0, column=1, padx=5, pady=5)
        self.color1_entry = ttk.Entry(self.main_frame, textvariable=self.color1_hex_var, width=10)
        self.color1_entry.grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(self.main_frame, text="팔레트", command=self.pick_color1).grid(row=0, column=3, padx=5, pady=5)

        # --- 색상 2 ---
        ttk.Label(self.main_frame, text="색상 2:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.color2_preview = tk.Label(self.main_frame, text="  ", bg="#90f730", width=3, relief="sunken")
        self.color2_preview.grid(row=1, column=1, padx=5, pady=5)
        self.color2_entry = ttk.Entry(self.main_frame, textvariable=self.color2_hex_var, width=10)
        self.color2_entry.grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(self.main_frame, text="팔레트", command=self.pick_color2).grid(row=1, column=3, padx=5, pady=5)

        # --- 대상 단축키 ---
        ttk.Label(self.main_frame, text="대상 단축키:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.hotkey_entry = ttk.Entry(self.main_frame, width=20)
        self.hotkey_entry.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="we")
        self.hotkey_entry.insert(0, "ctrl+alt+v") # 기본값

        # --- 밝기 조절 (Spinbox) ---
        ttk.Label(self.main_frame, text="밝기 (0.0 ~ 1.0):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.brightness_spinbox = ttk.Spinbox(
            self.main_frame, 
            from_=0.0, 
            to=1.0, 
            increment=0.1, 
            textvariable=self.brightness_var, 
            width=5
        )
        self.brightness_spinbox.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # --- 적용 버튼 ---
        self.apply_button = ttk.Button(self.main_frame, text="설정 파일에 적용", command=self.apply_changes)
        self.apply_button.grid(row=4, column=0, columnspan=4, padx=5, pady=15, sticky="we")

    
    def pick_color1(self):
        # Entry에 있는 값을 초기 색상으로 사용
        current_hex = self.color1_hex_var.get()
        color = colorchooser.askcolor(initialcolor=current_hex)
        if color[1]: # 사용자가 '확인'을 누른 경우
            # Entry의 값을 업데이트
            self.color1_hex_var.set(color[1])

    def pick_color2(self):
        current_hex = self.color2_hex_var.get()
        color = colorchooser.askcolor(initialcolor=current_hex)
        if color[1]:
            self.color2_hex_var.set(color[1])

    
    def update_preview1(self, *args):
        """StringVar(color1)가 변경될 때 호출되어 미리보기를 업데이트합니다."""
        hex_code = self.color1_hex_var.get()
        try:
            # Entry의 hex 코드로 미리보기 라벨의 배경색(bg)을 설정
            self.color1_preview.config(bg=hex_code)
        except tk.TclError:
            # 유효하지 않은 hex 코드일 경우
            self.color1_preview.config(bg="SystemButtonFace") # 기본 배경색

    def update_preview2(self, *args):
        """StringVar(color2)가 변경될 때 호출되어 미리보기를 업데이트합니다."""
        hex_code = self.color2_hex_var.get()
        try:
            self.color2_preview.config(bg=hex_code)
        except tk.TclError:
            self.color2_preview.config(bg="SystemButtonFace")

    
    def apply_changes(self):
        # 1. View에서 값 가져오기
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
            # 2. Model(Calculator) 호출
            new_matrix = self.calculator.calculate_matrix(
                hex1, 
                hex2, 
                brightness
            )
            
            if not new_matrix:
                messagebox.showerror("계산 오류", "매트릭스 계산에 실패했습니다. (공식 확인 필요)")
                return

            # 3. Model(Handler) 호출
            self.handler.update_matrix(hotkey, new_matrix)

        except Exception as e:
            messagebox.showerror("실행 오류", f"적용 중 오류가 발생했습니다:\n{e}")

# --- 3. 프로그램 실행 ---
if __name__ == "__main__":
    app = App()
    app.mainloop()