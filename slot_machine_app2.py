import streamlit as st
import random
import time

# ---------------- 세션 상태 초기화 ----------------
if "tokens" not in st.session_state:
    st.session_state.tokens = 999999  # 무한 포인트
if "last_result" not in st.session_state:
    st.session_state.last_result = ["❔", "❔", "❔"]
if "message" not in st.session_state:
    st.session_state.message = ""
if "game_message" not in st.session_state:
    st.session_state.game_message = "같은 심볼 3개가 나오면 **베팅액 × 1000** 보상! 🎲 3개가 나오면 **JACKPOT! (베팅액 × 10000)**"
if "symbols" not in st.session_state:
    st.session_state.symbols = ["🍒", "🍋", "🍀", "🎁", "💎", "🎲"]
if "symbol_probs" not in st.session_state:
    st.session_state.symbol_probs = [1/6] * 6  # 기본 동일 확률
if "jackpot_probs" not in st.session_state:
    st.session_state.jackpot_probs = [0.05] * 6  # 기본 5% 잭팟 확률

default_values = {
    "tokens": 100,
    "bet": 10,
    "win_multiplier": 1000,      # 일반 당첨 배율
    "jackpot_multiplier": 10000  # 잭팟 배율
}
for key, value in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------------- 슬롯머신 한 번 돌리기 ----------------
def spin_slot():
    symbols = st.session_state.symbols
    probs = st.session_state.symbol_probs
    jackpot_probs = st.session_state.jackpot_probs

    # 잭팟 심볼 강제 생성 여부
    for i, sym in enumerate(symbols):
        if random.random() < jackpot_probs[i]:
            return [sym, sym, sym]

    # 일반 확률 기반 랜덤 선택
    return random.choices(symbols, weights=probs, k=3)


# ---------------- 탭 생성 ----------------
tab_game, tab_settings = st.tabs(["🎰 게임 플레이", "⚙ 설정"])

# ---------------- 게임 플레이 탭 ----------------
with tab_game:
    st.title("🎰 슬롯머신 게임")
    st.markdown(st.session_state.game_message)  # 안내 문구 표시

    bet = st.number_input("베팅 금액", min_value=1, value=1, step=1)

    # ✅ 먼저 placeholder 생성
    slot_placeholder = st.empty()

    # ✅ 초기 슬롯 표시
    with slot_placeholder.container():
        cols = st.columns(3)
        for i, col in enumerate(cols):
            col.markdown(
                f"<div style='text-align:center; font-size:4rem'>{st.session_state.last_result[i]}</div>",
                unsafe_allow_html=True
            )

# 슬롯 돌리기 버튼
if st.button("🎲 슬롯 돌리기", use_container_width=True):
    for delay in [0.05] * 5 + [0.1] * 5 + [0.15] * 5:
        result = spin_slot()
        with slot_placeholder.container():
            cols = st.columns(3)
            for i, col in enumerate(cols):
                col.markdown(
                    f"<div style='text-align:center; font-size:4rem'>{result[i]}</div>",
                    unsafe_allow_html=True
                )
        time.sleep(delay)

    # ✅ 버튼 클릭 시에만 result 저장
    st.session_state.last_result = result


    # 잭팟 여부 판별
    def check_jackpot(res):
        return len(set(res)) == 1 and res[0] == "🎲"

    # 일반 당첨 여부 판별
    def check_win(res):
        return len(set(res)) == 1

    if check_jackpot(result):
        reward = bet * st.session_state.jackpot_multiplier
        st.success(f"🎉 JACKPOT! {reward}포인트 획득!")
    elif check_win(result):
        reward = bet * st.session_state.win_multiplier
        st.success(f"🎯 당첨! {reward}포인트 획득!")
    else:
        reward = -bet
        st.error(f"❌ 꽝! {abs(reward)}포인트 잃음")

        st.session_state.tokens += reward

# ---------------- 설정 탭 ----------------
with tab_settings:
    st.subheader("📢 안내 문구 설정")
    st.session_state.game_message = st.text_area(
        "게임 안내 문구",
        value=st.session_state.game_message
    )

    st.subheader("⚙ 배율 설정")
    st.session_state.win_multiplier = st.number_input(
        "🎯 일반 당첨 배율",
        min_value=1,
        value=st.session_state.win_multiplier,
        step=10
    )
    st.session_state.jackpot_multiplier = st.number_input(
        "🎉 잭팟 배율",
        min_value=1,
        value=st.session_state.jackpot_multiplier,
        step=100
    )

    st.subheader("🎨 심볼 & 확률 설정")
    num_symbols = st.number_input(
        "심볼 개수", 
        min_value=2, 
        max_value=10, 
        value=len(st.session_state.symbols), 
        step=1
    )

    new_symbols = []
    new_probs = []
    new_jackpots = []

    for i in range(num_symbols):
        col1, col2, col3 = st.columns([2, 2, 2])
        with col1:
            symbol = st.text_input(f"심볼 {i+1}", value=st.session_state.symbols[i] if i < len(st.session_state.symbols) else "")
        with col2:
            prob = st.number_input(
                f"등장 확률 {i+1} (%)", 
                min_value=0.0, 
                max_value=100.0, 
                value=(st.session_state.symbol_probs[i] * 100) if i < len(st.session_state.symbol_probs) else 0.0, 
                step=0.1
            )
        with col3:
            # ✅ 심볼 6번만 잭팟 확률 조정 가능
            if i == 5:  # 인덱스 5 → 6번째 심볼
                jackpot_prob = st.number_input(
                    f"잭팟 확률  (%)", 
                    min_value=0.0, 
                    max_value=100.0, 
                    value=(st.session_state.jackpot_probs[i] * 100) if i < len(st.session_state.jackpot_probs) else 0.0, 
                    step=0.1
                )
            else:
                jackpot_prob = 0.0  # 나머지는 0 고정

        new_symbols.append(symbol)
        new_probs.append(prob)
        new_jackpots.append(jackpot_prob)

    # 등장 확률 합 체크 (100% 기준)
    if abs(sum(new_probs) - 100.0) > 1e-6:
        st.warning("⚠ 심볼 등장 확률의 합이 100이 되도록 설정하세요.")

    if st.button("💾 설정 저장"):
        if abs(sum(new_probs) - 100.0) <= 1e-6:
            st.session_state.symbols = new_symbols
            # 내부 저장 시 0~1 비율로 변환
            st.session_state.symbol_probs = [p / 100 for p in new_probs]
            st.session_state.jackpot_probs = [p / 100 for p in new_jackpots]
            st.success("✅ 설정이 저장되었습니다.")
        else:
            st.error("❌ 등장 확률 합이 100이 아닙니다. 수정 후 저장하세요.")

