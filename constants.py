# --- 1. 유일하게 수정할 곳 ---
# 여기에 원하는 프리셋 개수를 입력하세요 (예: 5, 9, 11 등)
PRESET_COUNT = 8
# -----------------------------


# --- 2. 너비 설정 값 ---
# 프리셋 개수(Key)에 따른 기본 가로 너비(Value)를 정의하는 딕셔너리
# (사용자님이 말씀하신 '살아있는 변수들')
BASE_WIDTHS = {
    5: 455,
    9: 485,
    # 나중에 11개를 테스트해보고, 적절한 너비값(예: 750)을 찾으면
    # 여기에 11: 750 을 추가하면 됩니다.
    8: 455
}

# --- 3. 알 수 없는 값 계산 (보간법) ---
# 만약 PRESET_COUNT가 5나 9가 아닌 7, 8, 10 등으로 설정될 경우를 대비한
# 비례 계산용 기준값입니다.
# (9개일 때 620, 5개일 때 370 이라는 2개의 점을 기준으로 함)
PIXELS_PER_PRESET = (BASE_WIDTHS[9] - BASE_WIDTHS[5]) / (9 - 5) # (620-370)/(9-5) = 약 62.5
BASE_ANCHOR_COUNT = 5
BASE_ANCHOR_WIDTH = BASE_WIDTHS[BASE_ANCHOR_COUNT]


# --- 4. 최종 너비 계산 ---
def get_calculated_width():
    """PRESET_COUNT에 맞는 너비를 결정합니다."""
    
    # 1. 딕셔너리(BASE_WIDTHS)에 정의된 값이 있는지 먼저 확인
    if PRESET_COUNT in BASE_WIDTHS:
        print(f"Known width found for {PRESET_COUNT} presets.")
        return BASE_WIDTHS[PRESET_COUNT]
    
    # 2. (1)에 없으면, 5개를 기준으로 비례 계산(보간)
    print(f"Warning: No explicit width for {PRESET_COUNT} presets. Interpolating...")
    calculated_width = int(BASE_ANCHOR_WIDTH + (PRESET_COUNT - BASE_ANCHOR_COUNT) * PIXELS_PER_PRESET)
    return calculated_width

# 최종 계산된 너비 (negativescreen-auto.py가 이 변수를 사용)
CALCULATED_WIDTH = get_calculated_width()

# 세로 크기 (고정)
APP_HEIGHT = 580