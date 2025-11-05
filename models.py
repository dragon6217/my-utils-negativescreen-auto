from pathlib import Path
import os
from tkinter import messagebox

# --- 1. Model (데이터 및 파일 처리) ---

class MatrixCalculator:
    """
    두 개의 Hex 색상 코드와 밝기 값을 받아 5x5 행렬을 계산합니다.
    """

    def _hex_to_rgb(self, hex_code):
        """Helper: '#RRGGBB'를 (0.0~1.0) 범위의 (r, g, b) 튜플로 변환"""
        hex_val = hex_code.lstrip('#')
        # 2자리씩 끊어 16진수를 10진수로 변환하고 255로 나눔
        r = int(hex_val[0:2], 16) / 255.0
        g = int(hex_val[2:4], 16) / 255.0
        b = int(hex_val[4:6], 16) / 255.0
        return r, g, b

    def calculate_matrix(self, hex_color1, hex_color2, brightness):
        """
        알고리즘:
        1. 입력 R,G,B로 그레이스케일(Luma) 값을 계산합니다.
           Gray = 0.299*R + 0.587*G + 0.114*B
        2. 이 Gray 값을 사용해 Dark 색상과 Bright 색상 사이를 보간(interpolate)합니다.
           Out_R = (Bright_R - Dark_R) * Gray + Dark_R
           Out_G = (Bright_G - Dark_G) * Gray + Dark_G
           Out_B = (Bright_B - Dark_B) * Gray + Dark_B
        3. 전체 결과에 '밝기(brightness)'를 곱합니다.
           Final_Out_R = Out_R * brightness
        4. 이 공식을 5x5 행렬로 변환합니다.
        
        NegativeScreen 행렬 형식:
        [m[0][0], m[0][1], m[0][2], 0, 0]  (R 연산)
        [m[1][0], m[1][1], m[1][2], 0, 0]  (G 연산)
        [m[2][0], m[2][1], m[2][2], 0, 0]  (B 연산)
        [0,       0,       0,       1, 0]  (A 연산)
        [m[4][0], m[4][1], m[4][2], 0, 1]  (상수항 덧셈: Const_R, Const_G, Const_B)
        
        Final_Out_R = (m[0][0]*R + m[0][1]*G + m[0][2]*B) + m[4][0]
        """
        
        try:
            dr, dg, db = self._hex_to_rgb(hex_color1) # Dark (어두운 색)
            br, bg, bb = self._hex_to_rgb(hex_color2) # Bright (밝은 색)
        except Exception as e:
            print(f"Hex 코드 변환 오류: {e}")
            messagebox.showerror("계산 오류", f"잘못된 Hex 코드입니다: {e}")
            return None

        # 그레이스케일(Luma) 가중치
        LUMA_R = 0.299
        LUMA_G = 0.587
        LUMA_B = 0.114
        
        b = brightness # 편의상 변수명 변경

        # 5x5 행렬을 0.0으로 초기화
        matrix = [[0.0] * 5 for _ in range(5)]

        # --- 행렬 계산 ---

        # Row 0 (Red Output)
        # Final_Out_R = ( (br-dr)*(LUMA_R*R + LUMA_G*G + LUMA_B*B) + dr ) * b
        # Final_Out_R = ((br-dr)*LUMA_R*b)*R + ((br-dr)*LUMA_G*b)*G + ((br-dr)*LUMA_B*b)*B + (dr*b)
        matrix[0][0] = (br - dr) * LUMA_R * b
        matrix[0][1] = (br - dr) * LUMA_G * b
        matrix[0][2] = (br - dr) * LUMA_B * b
        matrix[4][0] = dr * b  # 상수항 (Const_R)

        # Row 1 (Green Output)
        # Final_Out_G = ( (bg-dg)*(LUMA_R*R + ... ) + dg ) * b
        matrix[1][0] = (bg - dg) * LUMA_R * b
        matrix[1][1] = (bg - dg) * LUMA_G * b
        matrix[1][2] = (bg - dg) * LUMA_B * b
        matrix[4][1] = dg * b  # 상수항 (Const_G)

        # Row 2 (Blue Output)
        # Final_Out_B = ( (bb-db)*(LUMA_R*R + ... ) + db ) * b
        matrix[2][0] = (bb - db) * LUMA_R * b
        matrix[2][1] = (bb - db) * LUMA_G * b
        matrix[2][2] = (bb - db) * LUMA_B * b
        matrix[4][2] = db * b  # 상수항 (Const_B)

        # Row 3 (Alpha Output)
        matrix[3][3] = 1.0  # 알파 채널 통과

        # Row 4 (Constant Row)
        matrix[4][4] = 1.0  # 상수항의 상수
        
        print(f"계산 완료: {hex_color1}, {hex_color2}, 밝기: {brightness}")
        
        return matrix

class ConfigFileHandler:
    """
    negativescreen.conf 파일을 찾아 읽고, 수정합니다.
    (이 클래스는 변경 사항 없음)
    """
    def __init__(self):
        # 사용자님이 지정한 경로를 'r' (Raw String)을 붙여서 직접 입력합니다.
        config_string_path = r"C:\Users\drago\Desktop\바탕화면\files, programs\negativescreen - Binary\negativescreen.conf"
        
        # 문자열 경로를 Path 객체로 변환합니다.
        self.config_path = Path(config_string_path)
        
        # 파일이 실제로 해당 경로에 존재하는지 확인합니다.
        if not self.config_path.exists():
            messagebox.showerror("오류", f"설정 파일을 찾_ 수 없습니다:\n{self.config_path}\n경로를 다시 확인해주세요.")

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