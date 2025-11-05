from pathlib import Path
import os
from tkinter import messagebox
import copy 

IDENTITY_MATRIX = [
    [ 1.0, 0.0, 0.0, 0.0, 0.0 ],
    [ 0.0, 1.0, 0.0, 0.0, 0.0 ],
    [ 0.0, 0.0, 1.0, 0.0, 0.0 ],
    [ 0.0, 0.0, 0.0, 1.0, 0.0 ],
    [ 0.0, 0.0, 0.0, 0.0, 1.0 ]
]

# [ ★ 1. 추가 ★ ] 원본 반전(네거티브) 행렬 (Out = 1 - In)
IDENTITY_INVERTED_MATRIX = [
    [ -1.0,  0.0,  0.0, 0.0, 0.0 ], # R' = -1*R
    [  0.0, -1.0,  0.0, 0.0, 0.0 ], # G' = -1*G
    [  0.0,  0.0, -1.0, 0.0, 0.0 ], # B' = -1*B
    [  0.0,  0.0,  0.0, 1.0, 0.0 ], # A' = 1*A
    [  1.0,  1.0,  1.0, 0.0, 1.0 ]  # R', G', B'에 각각 +1.0
]


class MatrixCalculator:
    """
    두 개의 Hex 색상 코드, 밝기, 강도, 반전 여부를 받아 5x5 행렬을 계산합니다.
    """

    def _hex_to_rgb(self, hex_code):
        hex_val = hex_code.lstrip('#')
        r = int(hex_val[0:2], 16) / 255.0
        g = int(hex_val[2:4], 16) / 255.0
        b = int(hex_val[4:6], 16) / 255.0
        return r, g, b

    def _blend_matrices(self, matrix_a, matrix_b, strength_a):
        """ matrix_a * strength_a + matrix_b * (1.0 - strength_a) """
        final_matrix = [[0.0] * 5 for _ in range(5)]
        strength_b = 1.0 - strength_a
        
        for i in range(5):
            for j in range(5):
                final_matrix[i][j] = (matrix_a[i][j] * strength_a) + (matrix_b[i][j] * strength_b)
        return final_matrix

    def _negate_3x3(self, matrix):
        """ 5x5 행렬의 3x3 (색상) 부분의 부호만 뒤집습니다. """
        inv_matrix = copy.deepcopy(matrix)
        for i in range(3):
            for j in range(3):
                inv_matrix[i][j] = -inv_matrix[i][j]
        return inv_matrix

    def calculate_matrix(self, hex_color1, hex_color2, brightness, strength, invert_state):
        """
        [ ★ 2. 수정 ★ ] "시도 2" (Attempt 2) 로직 적용
        """
        
        try:
            dr, dg, db = self._hex_to_rgb(hex_color1) # Dark
            br, bg, bb = self._hex_to_rgb(hex_color2) # Bright
        except Exception as e:
            print(f"Hex 코드 변환 오류: {e}")
            messagebox.showerror("계산 오류", f"잘못된 Hex 코드입니다: {e}")
            return None

        LUMA_R = 0.299
        LUMA_G = 0.587
        LUMA_B = 0.114
        
        b = brightness

        # --- 1. 듀오톤 행렬 (Matrix_A) 계산 ---
        # 1a. 3x3 부분 계산
        duotone_matrix = [[0.0] * 5 for _ in range(5)]
        
        duotone_matrix[0][0] = (br - dr) * LUMA_R * b
        duotone_matrix[1][0] = (br - dr) * LUMA_G * b
        duotone_matrix[2][0] = (br - dr) * LUMA_B * b
        
        duotone_matrix[0][1] = (bg - dg) * LUMA_R * b
        duotone_matrix[1][1] = (bg - dg) * LUMA_G * b
        duotone_matrix[2][1] = (bg - dg) * LUMA_B * b
        
        duotone_matrix[0][2] = (bb - db) * LUMA_R * b
        duotone_matrix[1][2] = (bb - db) * LUMA_G * b
        duotone_matrix[2][2] = (bb - db) * LUMA_B * b
        
        # 1b. 'invert_state'에 따라 3x3 부호 및 5행 상수항을 결정
        if invert_state:
            active_filter_matrix = self._negate_3x3(duotone_matrix)
            active_filter_matrix[4][0] = br * b
            active_filter_matrix[4][1] = bg * b
            active_filter_matrix[4][2] = bb * b
        else:
            active_filter_matrix = duotone_matrix
            active_filter_matrix[4][0] = dr * b
            active_filter_matrix[4][1] = dg * b
            active_filter_matrix[4][2] = db * b
        
        # 1c. 나머지 (Alpha, Const) 설정
        active_filter_matrix[3][3] = 1.0
        active_filter_matrix[4][4] = 1.0
        
        # --- 2. 'invert_state'에 따라 혼합할 "원본" (Matrix_B)을 결정 ---
        if invert_state:
            # "시도 2": 원본_반전 행렬 사용
            identity_matrix_to_blend = IDENTITY_INVERTED_MATRIX
        else:
            # "시도 1": 원본_긍정 행렬 사용
            identity_matrix_to_blend = IDENTITY_MATRIX
        
        # --- 3. 두 행렬을 'strength' 값으로 혼합 ---
        final_matrix = self._blend_matrices(
            matrix_a=active_filter_matrix, 
            matrix_b=identity_matrix_to_blend, 
            strength_a=strength
        )
        
        print(f"계산 완료 (Blend): B:{brightness}, S:{strength}, I:{invert_state}")
        
        return final_matrix

#
# (ConfigFileHandler 클래스는 변경 사항 없음)
#
class ConfigFileHandler:
    def __init__(self, conf_path_str):
        if conf_path_str:
            self.config_path = Path(conf_path_str)
        else:
            self.config_path = None
    # ... (이하 모든 코드 동일) ...
    def _format_matrix_row(self, row):
        formatted_row = ", ".join([f"{val: 6.2f}" for val in row])
        return f"{{ {formatted_row} }}"
    def update_matrix(self, hotkey, new_matrix):
        if not self.config_path or not self.config_path.exists():
            messagebox.showerror("경로 오류", 
                                 f"negativescreen.conf 파일 경로가 유효하지 않습니다.\n"
                                 f"경로: {self.config_path}\n\n"
                                 f"앱 하단의 '폴더 찾기'에서 .conf 파일을 지정해주세요.")
            return False
        hotkey_tag = f"={hotkey}"
        lines = []
        found = False
        matrix_line_index = -1
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            messagebox.showerror("파일 읽기 오류", f"파일을 읽는 중 오류 발생:\n{e}")
            return False
        for i, line in enumerate(lines):
            if line.strip().endswith(hotkey_tag):
                found = True
                matrix_line_index = i + 1
                break
        if not found:
            messagebox.showerror("오류", f"설정 파일에서 '{hotkey_tag}' 항목을 찾지 못했습니다.")
            return False
        if matrix_line_index + 4 < len(lines):
            try:
                for i in range(5):
                    new_line_content = self._format_matrix_row(new_matrix[i])
                    original_line = lines[matrix_line_index + i]
                    leading_whitespace = len(original_line) - len(original_line.lstrip(' '))
                    lines[matrix_line_index + i] = ' ' * leading_whitespace + new_line_content + '\n'
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