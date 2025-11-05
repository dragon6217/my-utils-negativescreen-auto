from pathlib import Path
import os
from tkinter import messagebox
# (MatrixCalculator 클래스는 변경 없음, 그대로 둡니다)

class MatrixCalculator:
    """
    두 개의 Hex 색상 코드와 밝기 값을 받아 5x5 행렬을 계산합니다.
    (이 클래스 코드는 변경 사항 없음)
    """

    def _hex_to_rgb(self, hex_code):
        hex_val = hex_code.lstrip('#')
        r = int(hex_val[0:2], 16) / 255.0
        g = int(hex_val[2:4], 16) / 255.0
        b = int(hex_val[4:6], 16) / 255.0
        return r, g, b

    def calculate_matrix(self, hex_color1, hex_color2, brightness):
        
        try:
            dr, dg, db = self._hex_to_rgb(hex_color1) # Dark (어두운 색)
            br, bg, bb = self._hex_to_rgb(hex_color2) # Bright (밝은 색)
        except Exception as e:
            print(f"Hex 코드 변환 오류: {e}")
            messagebox.showerror("계산 오류", f"잘못된 Hex 코드입니다: {e}")
            return None

        LUMA_R = 0.299
        LUMA_G = 0.587
        LUMA_B = 0.114
        
        b = brightness
        matrix = [[0.0] * 5 for _ in range(5)]

        # --- 행렬 계산 (Column-Major) ---
        matrix[0][0] = (br - dr) * LUMA_R * b # R -> R
        matrix[1][0] = (br - dr) * LUMA_G * b # G -> R
        matrix[2][0] = (br - dr) * LUMA_B * b # B -> R
        matrix[4][0] = dr * b                # Const -> R

        matrix[0][1] = (bg - dg) * LUMA_R * b # R -> G
        matrix[1][1] = (bg - dg) * LUMA_G * b # G -> G
        matrix[2][1] = (bg - dg) * LUMA_B * b # B -> G
        matrix[4][1] = dg * b                # Const -> G

        matrix[0][2] = (bb - db) * LUMA_R * b # R -> B
        matrix[1][2] = (bb - db) * LUMA_G * b # G -> B
        matrix[2][2] = (bb - db) * LUMA_B * b # B -> B
        matrix[4][2] = db * b                # Const -> B

        matrix[3][3] = 1.0
        matrix[4][4] = 1.0
        
        return matrix

# ----------------------------------------------------
# [ ★ 여기가 수정되었습니다 ★ ]
# ----------------------------------------------------
class ConfigFileHandler:
    """
    negativescreen.conf 파일을 찾아 읽고, 수정합니다.
    """
    def __init__(self, conf_path_str):
        """
        메인 앱(GUI)으로부터 .conf 파일의 '문자열 경로'를 주입받습니다.
        """
        if conf_path_str:
            self.config_path = Path(conf_path_str)
        else:
            self.config_path = None # 경로가 아직 설정되지 않음

    def _format_matrix_row(self, row):
        formatted_row = ", ".join([f"{val: 6.2f}" for val in row])
        return f"{{ {formatted_row} }}"

    def update_matrix(self, hotkey, new_matrix):
        # [ ★ 중요 ★ ]
        # 이제 이 함수가 경로 유효성을 검사하는 것이 매우 중요해졌습니다.
        if not self.config_path or not self.config_path.exists():
            messagebox.showerror("경로 오류", 
                                 f"negativescreen.conf 파일 경로가 유효하지 않습니다.\n"
                                 f"경로: {self.config_path}\n\n"
                                 f"앱 하단의 '경로 설정'에서 .conf 파일을 지정해주세요.")
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