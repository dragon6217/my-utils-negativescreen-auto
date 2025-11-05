import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from pathlib import Path
import os

# --- 1. Model (데이터 및 파일 처리) ---

class MatrixCalculator:
    """
    두 개의 Hex 색상 코드와 밝기 값을 받아 5x5 행렬을 계산합니다.
    """
    def calculate_matrix(self, hex_color1, hex_color2, brightness):
        # TODO: 
        # 여기에 사용자님의 "마법의 계산 공식"을 구현합니다.
        # hex_color1 (str), hex_color2 (str), brightness (float)
        # 이 세 변수를 사용해서 5x5 행렬을 계산하세요.
        
        print(f"계산 시작: {hex_color1}, {hex_color2}, 밝기: {brightness}")

        # (임시 예시 데이터)
        # 이 5x5 리스트를 반환하도록 로직을 채워주세요.
        calculated_matrix = [
            [ 0.11,  0.17,  0.04,  0.00,  0.00 ],
            [ 0.22,  0.33,  0.08,  0.00,  0.00 ],
            [ 0.04,  0.06,  0.02,  0.00,  0.00 ],
            [ 0.00,  0.00,  0.00,  1.00,  0.00 ],
            [ 0.02 * brightness,  0.12 * brightness,  0.00,  0.00,  1.00 ] # 예시: 밝기 값 적용
        ]
        
        return calculated_matrix

class ConfigFileHandler:
    """
    negativescreen.conf 파일을 찾아 읽고, 수정합니다.
    """
    def __init__(self):
        # 사용자님이 지정한 경로를 'r' (Raw String)을 붙여서 직접 입력합니다.
        config_string_path = r"C:\Users\drago\Desktop\바탕화면\files, programs\negativescreen - Binary\negativescreen.conf"
        
        # 문자열 경로를 Path 객체로 변환합니다.
        self.config_path = Path(config_string_path)
        
        # 파일이 실제로 해당 경로에 존재하는지 확인합니다.
        if not self.config_path.exists():
            messagebox.showerror("오류", f"설정 파일을 찾을 수 없습니다:\n{self.config_path}\n경로를 다시 확인해주세요.")

    def _format_matrix_row(self, row):
        # [ 0.11, 0.17, ... ] -> "{ 0.11,  0.17,  0.04,  0.00,  0.00 }"
        # 소수점 2자리로 포맷팅하고, 6칸을 차지하도록 정렬 (모양을 이쁘게)
        formatted_row = ", ".join([f"{val: 6.2f}" for val in row])
        return f"{{ {formatted_row} }}"

    def update_matrix(self, hotkey, new_matrix):
        if not self.config_path or not self.config_path.exists():
            print("설정 파일 경로가 유효하지 않습니다.")
            return False

        hotkey_tag = f"={hotkey}" # 예: "=ctrl+alt+v"
        lines = []
        found = False
        matrix_line_index = -1

        # 1. 파일을 읽고, 수정할 위치를 찾습니다.
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            messagebox.showerror("파일 읽기 오류", f"파일을 읽는 중 오류 발생:\n{e}")
            return False

        for i, line in enumerate(lines):
            if line.strip().endswith(hotkey_tag):
                found = True
                matrix_line_index = i + 1 # 매트릭스가 시작되는 줄
                break
        
        if not found:
            messagebox.showerror("오류", f"설정 파일에서 '{hotkey_tag}' 항목을 찾지 못했습니다.")
            return False

        # 2. 새 매트릭스로 5줄을 교체합니다.
        if matrix_line_index + 4 < len(lines):
            try:
                for i in range(5):
                    # 5x5 행렬의 각 행(row)을 가져와 포맷팅합니다.
                    new_line_content = self._format_matrix_row(new_matrix[i])
                    # 기존 줄의 들여쓰기를 유지하면서 내용만 교체
                    original_line = lines[matrix_line_index + i]
                    leading_whitespace = len(original_line) - len(original_line.lstrip(' '))
                    lines[matrix_line_index + i] = ' ' * leading_whitespace + new_line_content + '\n'
                
                # 3. 수정된 내용으로 파일을 다시 씁니다.
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                messagebox.showinfo("성공", f"'{hotkey}'의 색상 행렬을 성공적으로 업데이트했습니다!")
                return True
            except Exception as e:
                 messagebox.showerror("파일 쓰기 오류", f"파일을 쓰는 중 오류 발생:\n{e}")
                 return False
        else:
            messagebox.showerror("오류", "매트릭스 항목을 찾았으나 파일 구조가 예상과 다릅니다.")
            return False


# --- 2. View & Controller (GUI 및 이벤트 처리) ---

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NegativeScreen 도우미")
        # 창 크기 조정 (너비 증가)
        self.geometry("400x230")

        # Model 인스턴스 생성
        self.calculator = MatrixCalculator()
        self.handler = ConfigFileHandler()

        # [ ★ 1. 수정 ★ ]
        # UI에서 사용할 변수 (문자열 변수 StringVars로 변경)
        self.color1_hex_var = tk.StringVar(value="#0e4700")
        self.color2_hex_var = tk.StringVar(value="#90f730")
        
        # 밝기 값을 저장할 변수
        self.brightness_var = tk.DoubleVar()
        self.brightness_var.set(0.8)

        # 위젯 생성
        self.create_widgets()
        
        # [ ★ 2. 추가 ★ ]
        # Entry의 텍스트가 변경될 때마다 update_preview 함수를 호출 (실시간 미리보기)
        self.color1_hex_var.trace_add("write", self.update_preview1)
        self.color2_hex_var.trace_add("write", self.update_preview2)
        
        # 프로그램 시작 시 초기 색상으로 미리보기 업데이트
        self.update_preview1()
        self.update_preview2()


    def create_widgets(self):
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # [ ★ 3. 수정 ★ ] (UI 레이아웃 변경)
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
        # columnspan=3 하여 4개 열에 걸쳐 배치
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
        # columnspan=4 하여 4개 열에 걸쳐 배치
        self.apply_button.grid(row=4, column=0, columnspan=4, padx=5, pady=15, sticky="we")

    # [ ★ 4. 수정 ★ ] (StringVar에서 값 가져오고, 설정)
    def pick_color1(self):
        # Entry에 있는 값을 초기 색상으로 사용
        current_hex = self.color1_hex_var.get()
        color = colorchooser.askcolor(initialcolor=current_hex)
        if color[1]: # 사용자가 '확인'을 누른 경우 (취소하면 color[1]이 None)
            # Entry의 값을 업데이트 (StringVar.set() 사용)
            self.color1_hex_var.set(color[1])
            # (set()을 하면 trace가 자동으로 update_preview1을 호출)

    def pick_color2(self):
        current_hex = self.color2_hex_var.get()
        color = colorchooser.askcolor(initialcolor=current_hex)
        if color[1]:
            self.color2_hex_var.set(color[1])

    # [ ★ 5. 추가 ★ ] (실시간 미리보기 함수)
    def update_preview1(self, *args):
        """StringVar(color1)가 변경될 때 호출되어 미리보기를 업데이트합니다."""
        hex_code = self.color1_hex_var.get()
        try:
            # Entry의 hex 코드로 미리보기 라벨의 배경색(bg)을 설정
            self.color1_preview.config(bg=hex_code)
        except tk.TclError:
            # 유효하지 않은 hex 코드일 경우 (예: "#12345")
            self.color1_preview.config(bg="SystemButtonFace") # 기본 배경색

    def update_preview2(self, *args):
        """StringVar(color2)가 변경될 때 호출되어 미리보기를 업데이트합니다."""
        hex_code = self.color2_hex_var.get()
        try:
            self.color2_preview.config(bg=hex_code)
        except tk.TclError:
            self.color2_preview.config(bg="SystemButtonFace")

    # [ ★ 6. 수정 ★ ] (StringVar에서 값 가져오기)
    def apply_changes(self):
        # 1. View에서 값 가져오기
        hotkey = self.hotkey_entry.get().strip()
        
        # StringVar에서 .get()으로 최종 값을 가져옴
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