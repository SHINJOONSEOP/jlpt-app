# login.py
import threading
import re
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.clock import Clock
import api

class LoginScreen(Screen):

    def on_enter(self):
        self.clear_widgets()
        self._mode = "login"
        self._build()

    def _build(self):
        layout = BoxLayout(
            orientation="vertical",
            padding=[24, 30, 24, 20],
            spacing=12
        )

        # ── 로고 ──────────────────────────────
        layout.add_widget(Label(
            text="JLPT",
            font_name="Nanum", font_size=42, bold=True,
            color=(0, 0, 0, 1),
            size_hint_y=None, height=60
        ))
        layout.add_widget(Label(
            text="일본어 단어 학습앱",
            font_name="Nanum", font_size=14,
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None, height=24
        ))

        # ── 탭 ────────────────────────────────
        tab_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=46
        )
        self.login_tab = Button(
            text="로그인",
            font_name="Nanum", font_size=15, bold=True,
            background_color=(0.1, 0.1, 0.1, 1),
            color=(1, 1, 1, 1)
        )
        self.login_tab.bind(on_press=lambda x: self._switch("login"))
        self.reg_tab = Button(
            text="회원가입",
            font_name="Nanum", font_size=15,
            background_color=(0.7, 0.7, 0.7, 1),
            color=(1, 1, 1, 1)
        )
        self.reg_tab.bind(on_press=lambda x: self._switch("register"))
        tab_row.add_widget(self.login_tab)
        tab_row.add_widget(self.reg_tab)
        layout.add_widget(tab_row)

        # ── 닉네임 (회원가입만) ───────────────
        self.nick_lbl = Label(
            text="닉네임",
            font_name="Nanum", font_size=12,
            color=(0.4, 0.4, 0.4, 1),
            size_hint_y=None, height=0, opacity=0
        )
        self.nick_input = TextInput(
            hint_text="닉네임 입력",
            font_name="Nanum", font_size=15,
            size_hint_y=None, height=0,
            multiline=False, opacity=0
        )
        layout.add_widget(self.nick_lbl)
        layout.add_widget(self.nick_input)

        # ── 아이디 ────────────────────────────
        layout.add_widget(Label(
            text="아이디 (영어 + 숫자, 4~20자)",
            font_name="Nanum", font_size=12,
            color=(0.4, 0.4, 0.4, 1),
            size_hint_y=None, height=22
        ))
        self.id_input = TextInput(
            hint_text="영어와 숫자만 입력하세요",
            font_name="Nanum", font_size=15,
            size_hint_y=None, height=46,
            multiline=False
        )
        # 영어/숫자 이외 문자 자동 차단
        self.id_input.bind(text=self._filter_username)
        layout.add_widget(self.id_input)

        # ── 비밀번호 ──────────────────────────
        layout.add_widget(Label(
            text="비밀번호 (6자리 이상)",
            font_name="Nanum", font_size=12,
            color=(0.4, 0.4, 0.4, 1),
            size_hint_y=None, height=22
        ))
        self.pw_input = TextInput(
            hint_text="6자리 이상 입력하세요",
            font_name="Nanum", font_size=15,
            size_hint_y=None, height=46,
            multiline=False, password=True
        )
        layout.add_widget(self.pw_input)

        # ── 메시지 ────────────────────────────
        self.msg = Label(
            text="",
            font_name="Nanum", font_size=13,
            color=(0.85, 0.2, 0.2, 1),
            size_hint_y=None, height=30
        )
        layout.add_widget(self.msg)

        # ── 메인 버튼 ─────────────────────────
        self.main_btn = Button(
            text="로그인",
            font_name="Nanum", font_size=17, bold=True,
            size_hint_y=None, height=54,
            background_color=(0.1, 0.1, 0.1, 1),
            color=(1, 1, 1, 1)
        )
        self.main_btn.bind(on_press=self._submit)
        layout.add_widget(self.main_btn)

        layout.add_widget(Widget())

        # ── 오프라인 ──────────────────────────
        skip = Button(
            text="서버 없이 시작 (오프라인)",
            font_name="Nanum", font_size=13,
            size_hint_y=None, height=44,
            background_color=(0.8, 0.8, 0.8, 1),
            color=(0.2, 0.2, 0.2, 1)
        )
        skip.bind(on_press=self._offline)
        layout.add_widget(skip)

        self.add_widget(layout)

    # ── 아이디 입력 필터 (영어+숫자만) ───────
    def _filter_username(self, instance, value):
        filtered = re.sub(r'[^a-zA-Z0-9]', '', value)
        if filtered != value:
            instance.text = filtered

    # ── 탭 전환 ───────────────────────────────
    def _switch(self, mode):
        self._mode      = mode
        self.msg.text   = ""
        self.msg.color  = (0.85, 0.2, 0.2, 1)

        if mode == "login":
            self.login_tab.background_color = (0.1, 0.1, 0.1, 1)
            self.reg_tab.background_color   = (0.7, 0.7, 0.7, 1)
            self.nick_lbl.height   = 0
            self.nick_lbl.opacity  = 0
            self.nick_input.height = 0
            self.nick_input.opacity = 0
            self.main_btn.text     = "로그인"
        else:
            self.reg_tab.background_color   = (0.1, 0.1, 0.1, 1)
            self.login_tab.background_color = (0.7, 0.7, 0.7, 1)
            self.nick_lbl.height   = 22
            self.nick_lbl.opacity  = 1
            self.nick_input.height = 46
            self.nick_input.opacity = 1
            self.main_btn.text     = "회원가입"

    # ── 제출 전 클라이언트 유효성 검사 ───────
    def _validate(self):
        username = self.id_input.text.strip()
        password = self.pw_input.text.strip()

        if not username:
            return False, "아이디를 입력하세요"
        if len(username) < 4:
            return False, "아이디는 4자리 이상이어야 해요"
        if not re.match(r'^[a-zA-Z0-9]+$', username):
            return False, "아이디는 영어와 숫자만 사용할 수 있어요"
        if not password:
            return False, "비밀번호를 입력하세요"
        if len(password) < 6:
            return False, "비밀번호는 6자리 이상이어야 해요"

        if self._mode == "register":
            nick = self.nick_input.text.strip()
            if not nick:
                return False, "닉네임을 입력하세요"

        return True, ""

    # ── 제출 ──────────────────────────────────
    def _submit(self, instance):
        ok, msg = self._validate()
        if not ok:
            self.msg.color = (0.85, 0.2, 0.2, 1)
            self.msg.text  = msg
            return

        self.main_btn.disabled = True
        self.main_btn.text     = "처리 중..."
        self.msg.text          = ""

        username = self.id_input.text.strip()
        password = self.pw_input.text.strip()
        nickname = self.nick_input.text.strip()

        def task():
            if self._mode == "login":
                ok, msg = api.login(username, password)
            else:
                ok, msg = api.register(username, password, nickname)
            Clock.schedule_once(
                lambda dt: self._done(ok, msg), 0)

        threading.Thread(target=task, daemon=True).start()

    # ── 결과 ──────────────────────────────────
    def _done(self, ok, msg):
        self.main_btn.disabled = False
        self.main_btn.text     = "로그인" if self._mode == "login" \
                                 else "회원가입"
        if ok:
            self.msg.color = (0.18, 0.7, 0.35, 1)
            self.msg.text  = msg
            Clock.schedule_once(
                lambda dt: setattr(
                    self.manager, "current", "home"), 0.5)
        else:
            self.msg.color = (0.85, 0.2, 0.2, 1)
            self.msg.text  = msg

    # ── 오프라인 ──────────────────────────────
    def _offline(self, instance):
        api.set_token("offline", "오프라인 사용자")
        self.manager.current = "home"