import json
from pathlib import Path
import os # AppData 경로를 찾기 위해 import
from constants import PRESET_COUNT # 8개로 고정된 값을 가져옴

class PresetManager:
    """
    presets.json 파일을 관리하여 프리셋을 로드하고 저장합니다.
    파일 경로는 C:\Users\[사용자명]\AppData\Roaming\NegativeScreenHelper 입니다.
    """
    def __init__(self, preset_file="presets.json"):
        
        appdata_dir = Path(os.getenv('APPDATA')) / "NegativeScreenHelper"
        
        appdata_dir.mkdir(parents=True, exist_ok=True)
        
        self.preset_path = appdata_dir / preset_file

        self.presets = self.load_presets()

    def load_presets(self):
        """JSON 파일에서 프리셋을 로드합니다. 파일이 없으면 N개의 빈 슬롯을 생성합니다."""
        if not self.preset_path.exists():
            print(f"presets.json 파일이 없어 새로 생성: {self.preset_path}")
            # PRESET_COUNT (8개) 만큼 빈 슬롯 생성
            default_presets = [
                {"color1": None, "color2": None, "brightness": None} for _ in range(PRESET_COUNT)
            ]
            self.presets = default_presets
            self._save_to_file()
            return default_presets
        
        try:
            with open(self.preset_path, 'r', encoding='utf-8') as f:
                presets = json.load(f)
                
                # (하위 호환성 로직) - PRESET_COUNT(8)에 맞춰 자동 조절
                if len(presets) < PRESET_COUNT:
                    presets.extend([{"color1": None, "color2": None, "brightness": None}] * (PRESET_COUNT - len(presets)))
                elif len(presets) > PRESET_COUNT:
                    presets = presets[:PRESET_COUNT]
                
                return presets
        except json.JSONDecodeError:
            print(f"presets.json 파일이 손상되어 기본값으로 덮어씁니다: {self.preset_path}")
            default_presets = [
                {"color1": None, "color2": None, "brightness": None} for _ in range(PRESET_COUNT)
            ]
            self.presets = default_presets
            self._save_to_file()
            return default_presets

    def _save_to_file(self):
        """현재 프리셋 데이터를 JSON 파일에 저장합니다."""
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