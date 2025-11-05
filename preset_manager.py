import json
from pathlib import Path

from constants import PRESET_COUNT

class PresetManager:
    """
    presets.json 파일을 관리하여 프리셋을 로드하고 저장합니다.
    """
    def __init__(self, preset_file="presets.json"):
        self.preset_path = Path(preset_file)
        self.presets = self.load_presets()

    def load_presets(self):
        """JSON 파일에서 프리셋을 로드합니다. 파일이 없으면 5개의 빈 슬롯을 생성합니다."""
        if not self.preset_path.exists():
            # 기본 5개 빈 슬롯
            print("presets.json 파일이 없어 새로 생성합니다.")
            default_presets = [
                {"color1": None, "color2": None, "brightness": None} for _ in range(PRESET_COUNT)
            ]
            self.presets = default_presets
            self._save_to_file()
            return default_presets
        
        try:
            with open(self.preset_path, 'r', encoding='utf-8') as f:
                presets = json.load(f)
                
                # 데이터 무결성 검사 (항상 5개 슬롯 유지)
                if len(presets) < PRESET_COUNT:
                    # 5개보다 적으면 빈 슬롯 추가
                    presets.extend([{"color1": None, "color2": None, "brightness": None}] * (PRESET_COUNT - len(presets)))
                elif len(presets) > PRESET_COUNT:
                    # 5개보다 많으면 자름
                    presets = presets[:PRESET_COUNT]
                
                return presets
        except json.JSONDecodeError:
            print("presets.json 파일이 손상되어 기본값으로 덮어씁니다.")
            # 파일이 깨졌을 경우
            default_presets = [
                {"color1": None, "color2": None, "brightness": None} for _ in range(PRESET_COUNT)
            ]
            self.presets = default_presets
            self._save_to_file()
            return default_presets

    def _save_to_file(self):
        """현재 프리셋 데이터를 JSON 파일에 저장합니다. (사람이 읽기 쉽게 indent=2)"""
        try:
            with open(self.preset_path, 'w', encoding='utf-8') as f:
                json.dump(self.presets, f, indent=2)
        except Exception as e:
            print(f"presets.json 저장 중 오류 발생: {e}")

    def get_preset(self, slot_index):
        """특정 슬롯의 프리셋 데이터를 반환합니다."""
        if 0 <= slot_index < len(self.presets):
            return self.presets[slot_index]
        return None

    def get_all_presets(self):
        """모든 프리셋 데이터를 리스트로 반환합니다."""
        return self.presets

    def save_preset(self, slot_index, color1, color2, brightness):
        """특정 슬롯에 새 프리셋 데이터를 저장하고 파일에 반영합니다."""
        if not (0 <= slot_index < len(self.presets)):
            print(f"잘못된 슬롯 인덱스: {slot_index}")
            return
            
        new_data = {
            "color1": color1,
            "color2": color2,
            "brightness": brightness
        }
        
        self.presets[slot_index] = new_data
        self._save_to_file()
        print(f"프리셋 {slot_index}번 슬롯에 저장 완료.")