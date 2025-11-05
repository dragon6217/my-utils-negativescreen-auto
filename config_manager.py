import json
from pathlib import Path
import os # AppData 경로를 찾기 위해 import

class ConfigManager:
    """
    config.json 파일을 관리하여 앱 설정을 (폴더 경로) 저장합니다.
    파일 경로는 C:\Users\[사용자명]\AppData\Roaming\NegativeScreenHelper 입니다.
    """
    def __init__(self, config_file="config.json"):
        
        # os.getenv('APPDATA')가 C:\Users\[...]\AppData\Roaming 경로를 반환
        appdata_dir = Path(os.getenv('APPDATA')) / "NegativeScreenHelper"
        
        # (parents=True: 중간 폴더가 없어도 생성, exist_ok=True: 이미 있어도 오류 안 냄)
        appdata_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_path = appdata_dir / config_file
        
        self.config = self.load_config()

    def load_config(self):
        """JSON 파일에서 설정을 로드합니다. 파일이 없으면 기본값을 생성합니다."""
        default_config = {
            "app_folder_path": ""
        }
        
        if not self.config_path.exists():
            print(f"config.json 파일이 없어 새로 생성: {self.config_path}")
            self.config = default_config
            self._save_to_file()
            return default_config
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                config.setdefault("app_folder_path", "")
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