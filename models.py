from pathlib import Path
import os
from tkinter import messagebox  # ConfigFileHandler가 오류 메시지를 띄우기 위해 필요

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