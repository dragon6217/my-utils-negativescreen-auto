import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from pathlib import Path  # 파일 경로를 다루기 쉬운 라이브러리
import os  # 'APPDATA' 같은 환경 변수를 쓰기 위해

# --- 1. Model (데이터 및 파일 처리) ---

class MatrixCalculator:
    """
    두 개의 Hex 색상 코드를 받아 5x5 행렬을 계산합니다.
    """
    def calculate_matrix(self, hex_color1, hex_color2):
        # TODO: 
        # 여기에 사용자님의 "마법의 계산 공식"을 구현합니다.
        # 예: hex_color1="#0e4700", hex_color2="#90f730"
        
        # (임시 예시 데이터)
        # 실제로는 계산된 결과를 반환해야 합니다.
        # 이 5x5 리스트를 반환하도록 로직을 채워주세요.
        print(f"계산 시작: {hex_color1}, {hex_color2}")
        
        # 아래는 제공해주신 예시 매트릭스입니다.
        # 실제 계산 결과가 이런 2차원 리스트 형태가 되어야 합니다.
        calculated_matrix = [
            [ 0.11,  0.17,  0.04,  0.00,  0.00 ],
            [ 0.22,  0.33,  0.08,  0.00,  0.00 ],
            [ 0.04,  0.06,  0.02,  0.00,  0.00 ],
            [ 0.00,  0.00,  0.00,  1.00,  0.00 ],
            [ 0.02,  0.12,  0.00,  0.00,  1.00 ]
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
        with open(self.config_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

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
            for i in range(5):
                # 5x5 행렬의 각 행(row)을 가져와 포맷팅합니다.
                new_line_content = self._format_matrix_row(new_matrix[i])
                # 기존 줄의 들여쓰기를 유지하면서 내용만 교체 (혹시 모를 공백 대비)
                leading_whitespace = len(lines[matrix_line_index + i]) - len(lines[matrix_line_index + i].lstrip(' '))
                lines[matrix_line_index + i] = ' ' * leading_whitespace + new_line_content + '\n'
            
            # 3. 수정된 내용으로 파일을 다시 씁니다.
            with open(self.config_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            messagebox.showinfo("성공", f"'{hotkey}'의 색상 행렬을 성공적으로 업데이트했습니다!")
            return True
        else:
            messagebox.showerror("오류", "매트릭스 항목을 찾았으나 파일 구조가 예상과 다릅니다.")
            return False


# --- 2. View & Controller (GUI 및 이벤트 처리) ---

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NegativeScreen 도우미")
        self.geometry("350x180") # 창 크기

        # Model 인스턴스 생성
        self.calculator = MatrixCalculator()
        self.handler = ConfigFileHandler()

        # UI에서 사용할 변수
        self.color1_hex = "#0e4700"
        self.color2_hex = "#90f730"

        # 위젯 생성
        self.create_widgets()

    def create_widgets(self):
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 색상 1 ---
        ttk.Label(self.main_frame, text="색상 1 (어두운 색):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.color1_preview = tk.Label(self.main_frame, text="  ", bg=self.color1_hex, width=4, relief="sunken")
        self.color1_preview.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.main_frame, text="선택", command=self.pick_color1).grid(row=0, column=2, padx=5, pady=5)

        # --- 색상 2 ---
        ttk.Label(self.main_frame, text="색상 2 (밝은 색):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.color2_preview = tk.Label(self.main_frame, text="  ", bg=self.color2_hex, width=4, relief="sunken")
        self.color2_preview.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(self.main_frame, text="선택", command=self.pick_color2).grid(row=1, column=2, padx=5, pady=5)

        # --- 대상 단축키 ---
        ttk.Label(self.main_frame, text="대상 단축키:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.hotkey_entry = ttk.Entry(self.main_frame, width=20)
        self.hotkey_entry.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="we")
        self.hotkey_entry.insert(0, "ctrl+alt+v") # 기본값

        # --- 적용 버튼 ---
        self.apply_button = ttk.Button(self.main_frame, text="설정 파일에 적용", command=self.apply_changes)
        self.apply_button.grid(row=3, column=0, columnspan=3, padx=5, pady=15, sticky="we")

    def pick_color1(self):
        # askcolor()는 ( (R,G,B), "#hexcode" ) 튜플을 반환합니다.
        color = colorchooser.askcolor(initialcolor=self.color1_hex)
        if color[1]: # 사용자가 '확인'을 누른 경우 (취소하면 color[1]이 None)
            self.color1_hex = color[1]
            self.color1_preview.config(bg=self.color1_hex)

    def pick_color2(self):
        color = colorchooser.askcolor(initialcolor=self.color2_hex)
        if color[1]:
            self.color2_hex = color[1]
            self.color2_preview.config(bg=self.color2_hex)

    # --- 이것이 'Controller'의 핵심 로직입니다 ---
    def apply_changes(self):
        # 1. View에서 값 가져오기
        hotkey = self.hotkey_entry.get().strip()
        if not hotkey:
            messagebox.showwarning("입력 오류", "단축키를 입력하세요. (예: ctrl+alt+v)")
            return

        try:
            # 2. Model(Calculator) 호출
            new_matrix = self.calculator.calculate_matrix(self.color1_hex, self.color2_hex)
            
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