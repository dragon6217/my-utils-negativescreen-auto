import json
from pathlib import Path
import os

# [ ★ 1. 추가 ★ ] 사용자가 요청한 기본 UI 상태
DEFAULT_LAST_STATE = {
    "color1": "#0e4700",
    "color2": "#90f730",
    "hotkey": "ctrl+alt+v",
    "brightness": 0.8,
    "strength": 1.0
}

class ConfigManager:
    """
    config.json 파일을 관리하여 앱 설정을 (폴더 경로, 마지막 상태) 저장합니다.
    파일 경로는 C:\\Users\\[사용자명]\\AppData\\Roaming\\NegativeScreenHelper 입니다.
    """
    def __init__(self, config_file="config.json"):
        appdata_dir = Path(os.getenv('APPDATA')) / "NegativeScreenHelper"
        appdata_dir.mkdir(parents=True, exist_ok=True)
        self.config_path = appdata_dir / config_file
        
        self.config = self.load_config()

    def load_config(self):
        """JSON 파일에서 설정을 로드합니다. 파일이 없거나 키가 없으면 기본값을 생성합니다."""
        
        # [ ★ 2. 수정 ★ ] 기본 설정에 last_state 추가
        default_config = {
            "app_folder_path": "",
            "last_state": DEFAULT_LAST_STATE
        }
        
        if not self.config_path.exists():
            print(f"config.json 파일이 없어 새로 생성: {self.config_path}")
            self.config = default_config
            self._save_to_file()
            return default_config
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
                # [ ★ 3. 수정 ★ ]
                # 각 키가 존재하는지 확인하고, 없으면 기본값으로 채워넣음
                config.setdefault("app_folder_path", default_config["app_folder_path"])
                config.setdefault("last_state", default_config["last_state"])
                
                # (하위 호환성) last_state 안에 키가 누락된 경우 대비
                config["last_state"].setdefault("color1", DEFAULT_LAST_STATE["color1"])
                config["last_state"].setdefault("color2", DEFAULT_LAST_STATE["color2"])
                config["last_state"].setdefault("hotkey", DEFAULT_LAST_STATE["hotkey"])
                config["last_state"].setdefault("brightness", DEFAULT_LAST_STATE["brightness"])
                config["last_state"].setdefault("strength", DEFAULT_LAST_STATE["strength"])
                
                return config
        except json.JSONDecodeError:
            print(f"config.json 파일이 손상되어 기본값으로 덮어씁니다: {self.config_path}")
            self.config = default_config
            self._save_to_file()
            return default_config

    def _save_to_file(self):
        """현재 설정을 JSON 파일에 저장합니다."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"config.json 저장 중 오류 발생: {e}")

    def get_folder_path(self):
        """저장된 폴더 경로 문자열을 반환합니다."""
        return self.config.get("app_folder_path", "")

    def save_folder_path(self, folder_path):
        """새 폴더 경로를 저장하고 파일에 반영합니다."""
        self.config["app_folder_path"] = folder_path
        self._save_to_file()
        print(f"폴더 경로가 config.json에 저장되었습니다: {self.config_path}")

    # [ ★ 4. 추가 ★ ] 마지막 UI 상태를 가져오는 함수
    def get_last_state(self):
        """저장된 마지막 UI 상태 딕셔너리를 반환합니다."""
        return self.config.get("last_state", DEFAULT_LAST_STATE)

    # [ ★ 5. 추가 ★ ] 마지막 UI 상태를 저장하는 함수
    def save_last_state(self, state_dict):
        """현재 UI 상태를 저장하고 파일에 반영합니다."""
        self.config["last_state"] = state_dict
        self._save_to_file()
        # (콘솔에 너무 자주 찍히면 번거로우니 print는 생략)