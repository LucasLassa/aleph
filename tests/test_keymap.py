
from src.core import keymap
from src.core.state import State


def test_keymap_actions_exist():
    assert set(keymap.KEYMAP.values()) <= set(keymap.ACTIONS)

def test_documented_keys_are_wired():
    assert set(keymap.KEYMAP) >= {
        "Left", "Right", "Up", "Down", "Shift+M", "Esc", "Tab", "Shift+D",
    }

def test_tab_toggles_panel_action():
    assert keymap.KEYMAP["Tab"] == "toggle_panel"
    s = State()
    assert keymap.handle("Tab", s) == "toggle_panel"

def test_guide_cycle_wraps():
    s = State(guide_index=0)
    keymap.handle("Left", s)
    assert s.guide_index == 10
    s2 = State(guide_index=10)
    keymap.handle("Right", s2)
    assert s2.guide_index == 0
    s3 = State(guide_index=0)
    keymap.handle("Right", s3)
    assert s3.guide_index == 1
    s4 = State(guide_index=3)
    keymap.handle("Left", s4)
    assert s4.guide_index == 2

def test_default_guide_is_thirds():
    from src.core import guides

    assert State().guide_index == guides.POOL.index("Regla de tercios")

def test_toggle_frame_flips_flags():
    s = State()
    assert s.frame_mode is True
    keymap.handle("M", s, shift=True)
    assert s.frame_mode is False
    assert s.click_through is True
    keymap.handle("M", s, shift=True)
    assert s.frame_mode is True
    assert s.click_through is False

def test_guide_and_opacity_work_with_frame_off():
    s = State(frame_mode=False, guide_index=3, opacity=0.5)
    assert keymap.handle("Right", s) == "guide_next"
    assert s.guide_index != 3
    assert keymap.handle("Left", s) == "guide_prev"
    assert keymap.handle("Up", s) == "opacity_up"
    assert s.opacity == 0.6
    assert keymap.handle("Down", s) == "opacity_down"
    assert s.opacity == 0.5

def test_frame_gate_allows_quit():
    s = State(frame_mode=False)
    assert keymap.handle("Esc", s) == "quit"

def test_opacity_is_clamped():
    s = State(opacity=0.98)
    keymap.handle("Up", s)
    assert s.opacity == 1.0
    keymap.handle("Up", s)
    assert s.opacity == 1.0
    s2 = State(opacity=0.05)
    keymap.handle("Down", s2)
    assert s2.opacity == 0.0
    keymap.handle("Down", s2)
    assert s2.opacity == 0.0

def test_quit_is_reported_and_state_untouched():
    s = State()
    assert keymap.handle("Esc", s) == "quit"
    assert s.to_dict() == State().to_dict()

def test_unknown_key_returns_none():
    s = State()
    assert keymap.handle("Z", s) is None
    assert keymap.handle("", s) is None
    assert s.to_dict() == State().to_dict()

def test_fullscreen_bind_is_gone():
    s = State()
    assert "toggle_fullscreen" not in keymap.ACTIONS
    assert "Shift+F" not in keymap.KEYMAP
    assert keymap.handle("F", s, shift=True) is None
    assert s.fullscreen is True

def test_plain_m_no_longer_toggles_frame():
    s = State()
    assert keymap.handle("M", s, shift=False) is None
    assert s.frame_mode is True

def test_shift_d_clears_rules_instead_of_backspace():
    s = State()
    from src.core.state import Rule

    s.rules.append(Rule(kind="h", x=0.5, y=0.5))
    assert keymap.handle("Backspace", s, shift=True) is None
    assert keymap.handle("D", s, shift=True) == "clear_rules"
    assert s.rules == []

def test_line_white_and_black_set_the_color():
    s = State()
    assert s.line_dark is False
    keymap.ACTIONS["line_black"](s)
    assert s.line_dark is True
    keymap.ACTIONS["line_white"](s)
    assert s.line_dark is False
    keymap.ACTIONS["line_black"](s)
    keymap.ACTIONS["line_black"](s)
    assert s.line_dark is True

def test_shift_keeps_plain_keys_working():
    s = State(guide_index=0)
    assert keymap.handle("Left", s, shift=True) == "guide_prev"
    assert s.guide_index == 10

def test_shift_s_requests_capture():
    s = State()
    assert s.pending_capture is False
    assert keymap.handle("S", s, shift=True) == "capture"
    assert s.pending_capture is True

def test_s_without_shift_does_nothing():
    s = State()
    assert keymap.handle("S", s, shift=False) is None
    assert s.pending_capture is False

def test_capture_works_with_frame_off():
    s = State(frame_mode=False)
    assert keymap.handle("S", s, shift=True) == "capture"
    assert s.pending_capture is True
