# quiz.py
import random
from datetime import date
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle, RoundedRectangle
from storage import save_daily_record

# 일본어 키보드 데이터
JP_KEYBOARD = {
    "あ": ["あ","い","う","え","お"],
    "か": ["か","き","く","け","こ"],
    "が": ["が","ぎ","ぐ","げ","ご"],
    "さ": ["さ","し","す","せ","そ"],
    "ざ": ["ざ","じ","ず","ぜ","ぞ"],
    "た": ["た","ち","つ","て","と"],
    "だ": ["だ","ぢ","づ","で","ど"],
    "な": ["な","に","ぬ","ね","の"],
    "は": ["は","ひ","ふ","へ","ほ"],
    "ば": ["ば","び","ぶ","べ","ぼ"],
    "ぱ": ["ぱ","ぴ","ぷ","ぺ","ぽ"],
    "ま": ["ま","み","む","め","も"],
    "や": ["や","ゆ","よ","ゃ","ゅ"],
    "ら": ["ら","り","る","れ","ろ"],
    "わ": ["わ","を","ん","ゎ","ー"],
    "小": ["ぁ","ぃ","ぅ","ぇ","ぉ"],
    "記": ["っ","ょ","ゆ","。","、"],
}

class QuizScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.quiz_words      = []
        self.origin_words    = []
        self.index           = 0
        self.correct         = 0
        self.total           = 0
        self.mode            = "hiragana"
        self.selected_row    = None   # 현재 선택된 행 (あ, か 등)

    def receive_words(self, quiz_words, origin_words):
        self.quiz_words   = quiz_words[:]
        self.origin_words = origin_words[:]
        self.index        = 0
        self.correct      = 0
        self.total        = len(quiz_words)

    def on_enter(self):
        self.clear_widgets()
        if not self.quiz_words:
            self._show_no_words()
        else:
            self._build_ui()

    def _make_bg(self, widget):
        with widget.canvas.before:
            Color(0.95, 0.95, 0.93, 1)
            rect = Rectangle(pos=widget.pos, size=widget.size)
        widget.bind(
            pos=lambda i, v: setattr(rect, 'pos', v),
            size=lambda i, v: setattr(rect, 'size', v)
        )

    def _build_ui(self):
        root = BoxLayout(orientation="vertical")
        bg   = BoxLayout(
            orientation="vertical",
            padding=[16, 12, 16, 12], spacing=6
        )
        self._make_bg(bg)

        # ── 상단 바 ───────────────────────────
        top_bar = BoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=46
        )
        back_btn = Button(
            text="←", font_size=20,
            size_hint_x=None, width=50,
            background_color=(0.95, 0.95, 0.93, 1),
            color=(0, 0, 0, 1)
        )
        back_btn.bind(on_press=self.go_back)
        self.progress_label = Label(
            text=f"1 / {self.total}",
            font_name="Nanum", font_size=14,
            bold=True, color=(0, 0, 0, 1)
        )
        self.score_label = Label(
            text=f"O 0 / {self.total}",
            font_name="Nanum", font_size=13,
            color=(0.4, 0.4, 0.4, 1),
            size_hint_x=None, width=110
        )
        top_bar.add_widget(back_btn)
        top_bar.add_widget(Widget())
        top_bar.add_widget(self.progress_label)
        top_bar.add_widget(Widget())
        top_bar.add_widget(self.score_label)

        # ── 모드 표시 ─────────────────────────
        self.mode_label = Label(
            text="", font_name="Nanum", font_size=13,
            size_hint_y=None, height=24, halign="center"
        )
        self.mode_label.bind(
            size=lambda i, v: setattr(i, 'text_size', v))

        # ── 진행 바 ───────────────────────────
        progress_bg = BoxLayout(size_hint_y=None, height=5)
        with progress_bg.canvas.before:
            Color(0.85, 0.85, 0.85, 1)
            self._pbg_rect = Rectangle(
                pos=progress_bg.pos, size=progress_bg.size)
        progress_bg.bind(
            pos=lambda i, v: setattr(self._pbg_rect, 'pos', v),
            size=lambda i, v: setattr(self._pbg_rect, 'size', v)
        )
        self.fill_bar = Widget(
            size_hint_x=1/self.total if self.total else 1,
            size_hint_y=1
        )
        with self.fill_bar.canvas:
            Color(0.1, 0.1, 0.1, 1)
            self._fill_rect = Rectangle(
                pos=self.fill_bar.pos, size=self.fill_bar.size)
        self.fill_bar.bind(
            pos=lambda i, v: setattr(self._fill_rect, 'pos', v),
            size=lambda i, v: setattr(self._fill_rect, 'size', v)
        )
        progress_bg.add_widget(self.fill_bar)

        # ── 단어 카드 ─────────────────────────
        self.card = BoxLayout(
            orientation="vertical",
            size_hint_y=None, height=220,
            padding=[20, 14, 20, 14], spacing=6
        )
        with self.card.canvas.before:
            Color(1, 1, 1, 1)
            self._card_rect = RoundedRectangle(
                pos=self.card.pos, size=self.card.size, radius=[16])
        self.card.bind(
            pos=lambda i, v: setattr(self._card_rect, 'pos', v),
            size=lambda i, v: setattr(self._card_rect, 'size', v)
        )

        self.level_label = Label(
            text="", font_name="Nanum", font_size=11,
            color=(0.6, 0.6, 0.6, 1),
            size_hint_y=None, height=18, halign="left"
        )
        self.level_label.bind(
            size=lambda i, v: setattr(i, 'text_size', v))

        self.jp_label = Label(
            text="", font_name="NotoJP", font_size=44, bold=True,
            color=(0, 0, 0, 1),
            size_hint_y=None, height=64, halign="center"
        )
        self.jp_label.bind(
            size=lambda i, v: setattr(i, 'text_size', v))

        self.example_jp = Label(
            text="", font_name="NotoJP", font_size=13,
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=None, height=36,
            halign="center", text_size=(300, None)
        )

        # 정답 공개 후
        self.furigana_label = Label(
            text="", font_name="NotoJP", font_size=13,
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None, height=20,
            halign="center", opacity=0
        )
        self.furigana_label.bind(
            size=lambda i, v: setattr(i, 'text_size', v))
        self.kr_label = Label(
            text="", font_name="Nanum", font_size=18, bold=True,
            color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None, height=28,
            halign="center", opacity=0
        )
        self.kr_label.bind(
            size=lambda i, v: setattr(i, 'text_size', v))
        self.example_kr = Label(
            text="", font_name="Nanum", font_size=12,
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None, height=22,
            halign="center", text_size=(300, None), opacity=0
        )

        self.card.add_widget(self.level_label)
        self.card.add_widget(self.jp_label)
        self.card.add_widget(self.example_jp)
        self.card.add_widget(self.furigana_label)
        self.card.add_widget(self.kr_label)
        self.card.add_widget(self.example_kr)

        # ── 입력창 + 삭제버튼 ─────────────────
        input_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=46, spacing=8
        )
        self.answer_input = TextInput(
            hint_text="", font_name="Nanum", font_size=18,
            size_hint_x=0.82,
            multiline=False,
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            readonly=True   # 키보드로만 입력
        )
        del_btn = Button(
            text="⌫",
            font_size=20,
            size_hint_x=0.18,
            background_color=(0.9, 0.3, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        del_btn.bind(on_press=self._delete_char)
        input_row.add_widget(self.answer_input)
        input_row.add_widget(del_btn)

        # ── 피드백 라벨 ───────────────────────
        self.feedback_label = Label(
            text="", font_name="Nanum", font_size=14,
            color=(0, 0, 0, 1),
            size_hint_y=None, height=26, halign="center"
        )
        self.feedback_label.bind(
            size=lambda i, v: setattr(i, 'text_size', v))

        # ── 히라가나 키보드 영역 ───────────────
        self.keyboard_area = BoxLayout(
            orientation="vertical",
            size_hint_y=None, height=196, spacing=4
        )

        # 행 선택 버튼들 (2줄로 배치)
        row_btns = GridLayout(
            cols=9, size_hint_y=None, height=96, spacing=3
        )
        self.row_btn_map = {}
        for row_key in JP_KEYBOARD.keys():
            btn = Button(
                text=row_key,
                font_name="NotoJP", font_size=16,
                background_color=(0.88, 0.88, 0.88, 1),
                color=(0, 0, 0, 1)
            )
            btn.bind(on_press=lambda x, k=row_key: self._select_row(k))
            self.row_btn_map[row_key] = btn
            row_btns.add_widget(btn)

        # 글자 선택 버튼들 (선택한 행의 글자)
        self.char_btns_layout = GridLayout(
            cols=5, size_hint_y=None, height=46, spacing=3
        )
        # 처음엔 あ행 표시
        self._render_char_btns("あ")

        self.keyboard_area.add_widget(row_btns)
        self.keyboard_area.add_widget(self.char_btns_layout)

        # ── 한국어 모드용 일반 키보드 안내 ──────
        self.kr_input_hint = Label(
            text="한국어를 직접 입력하세요",
            font_name="Nanum", font_size=13,
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None, height=36,
            halign="center", opacity=0
        )
        self.kr_input_hint.bind(
            size=lambda i, v: setattr(i, 'text_size', v))

        # ── 제출/다음 버튼 ────────────────────
        self.submit_btn = Button(
            text="제출", font_name="Nanum", font_size=16, bold=True,
            size_hint_y=None, height=50,
            background_color=(0.1, 0.1, 0.1, 1), color=(1, 1, 1, 1)
        )
        self.submit_btn.bind(on_press=self.submit_answer)

        self.next_btn = Button(
            text="다음 →", font_name="Nanum", font_size=16, bold=True,
            size_hint_y=None, height=50,
            background_color=(0.18, 0.7, 0.35, 1), color=(1, 1, 1, 1),
            opacity=0, disabled=True
        )
        self.next_btn.bind(on_press=self.next_question)

        bg.add_widget(top_bar)
        bg.add_widget(self.mode_label)
        bg.add_widget(progress_bg)
        bg.add_widget(self.card)
        bg.add_widget(input_row)
        bg.add_widget(self.feedback_label)
        bg.add_widget(self.keyboard_area)
        bg.add_widget(self.kr_input_hint)
        bg.add_widget(self.submit_btn)
        bg.add_widget(self.next_btn)

        root.add_widget(bg)
        self.add_widget(root)
        self._load_question()

    # ── 행 선택 (あ か た...) ─────────────────
    def _select_row(self, row_key):
        self.selected_row = row_key
        # 선택된 행 버튼 하이라이트
        for k, btn in self.row_btn_map.items():
            if k == row_key:
                btn.background_color = (0.1, 0.1, 0.1, 1)
                btn.color            = (1, 1, 1, 1)
            else:
                btn.background_color = (0.88, 0.88, 0.88, 1)
                btn.color            = (0, 0, 0, 1)
        self._render_char_btns(row_key)

    # ── 글자 버튼 렌더링 ──────────────────────
    def _render_char_btns(self, row_key):
        self.char_btns_layout.clear_widgets()
        chars = JP_KEYBOARD[row_key]
        for ch in chars:
            btn = Button(
                text=ch,
                font_name="NotoJP", font_size=18,
                background_color=(1, 1, 1, 1),
                color=(0, 0, 0, 1)
            )
            btn.bind(on_press=lambda x, c=ch: self._input_char(c))
            self.char_btns_layout.add_widget(btn)
        # 빈 칸 채우기 (5칸 맞추기)
        for _ in range(5 - len(chars)):
            self.char_btns_layout.add_widget(Widget())

    # ── 글자 입력 ─────────────────────────────
    def _input_char(self, ch):
        if self.answer_input.disabled:
            return
        self.answer_input.text += ch

    # ── 글자 삭제 ─────────────────────────────
    def _delete_char(self, instance):
        if self.answer_input.disabled:
            return
        self.answer_input.text = self.answer_input.text[:-1]

    # ── 문제 불러오기 ─────────────────────────
    def _load_question(self):
        self.mode         = random.choice(["hiragana", "korean"])
        self.selected_row = "あ"
        w = self.quiz_words[self.index]

        self.level_label.text    = w["level"]
        self.jp_label.text       = w["japanese"]
        self.example_jp.text     = w["example_jp"]
        self.furigana_label.text = w["furigana"]
        self.kr_label.text       = w["korean"]
        self.example_kr.text     = w["example_kr"]

        self.furigana_label.opacity = 0
        self.kr_label.opacity       = 0
        self.example_kr.opacity     = 0
        self.answer_input.text      = ""
        self.answer_input.disabled  = False
        self.answer_input.font_name = "NotoJP"
        self.feedback_label.text    = ""
        self.feedback_label.color   = (0, 0, 0, 1)

        self.submit_btn.opacity  = 1
        self.submit_btn.disabled = False
        self.next_btn.opacity    = 0
        self.next_btn.disabled   = True

        self.progress_label.text  = \
            f"{self.index + 1} / {self.total}"
        self.fill_bar.size_hint_x = \
            (self.index + 1) / self.total
        self.score_label.text = \
            f"O {self.correct} / {self.total}"

        if self.mode == "hiragana":
            self.answer_input.font_name   = "NotoJP"
            self.answer_input.hint_text   = "아래 키보드로 입력하세요"
            self.answer_input.readonly    = True
            self.mode_label.text          = "히라가나 입력 모드"
            self.mode_label.color         = (0.2, 0.5, 0.9, 1)
            self.keyboard_area.opacity    = 1
            self.keyboard_area.disabled   = False
            self.kr_input_hint.opacity    = 0
            self._select_row("あ")
        else:
            # 한국어 모드 → 일반 키보드
            self.answer_input.font_name   = "Nanum"
            self.answer_input.hint_text   = "한국어 뜻을 입력하세요"
            self.answer_input.readonly    = False
            self.mode_label.text          = "한국어 뜻 입력 모드"
            self.mode_label.color         = (0.7, 0.3, 0.9, 1)
            self.keyboard_area.opacity    = 0
            self.keyboard_area.disabled   = True
            self.kr_input_hint.opacity    = 1

    # ── 정답 제출 ─────────────────────────────
    def submit_answer(self, instance):
        value = self.answer_input.text.strip()
        if not value:
            return

        w            = self.quiz_words[self.index]
        correct_text = w["furigana"] if self.mode == "hiragana" \
                       else w["korean"]

        is_correct = value.replace(" ", "") == \
                     correct_text.replace(" ", "")

        # 정답 정보 공개
        self.furigana_label.opacity = 1
        self.kr_label.opacity       = 1
        self.example_kr.opacity     = 1
        self.answer_input.disabled  = True
        self.keyboard_area.disabled = True
        self.submit_btn.opacity     = 0
        self.submit_btn.disabled    = True
        self.next_btn.opacity       = 1
        self.next_btn.disabled      = False

        if is_correct:
            self.correct += 1
            self.score_label.text     = \
                f"O {self.correct} / {self.total}"
            self.feedback_label.text  = "정답!"
            self.feedback_label.color = (0.18, 0.7, 0.35, 1)
        else:
            # 몇 글자 맞았는지 계산
            matched = sum(
                1 for a, b in zip(value, correct_text) if a == b
            )
            total_ch = len(correct_text)
            self.feedback_label.text  = \
                f"오답  |  {matched}/{total_ch}글자 일치  |  정답: {correct_text}"
            self.feedback_label.color = (0.85, 0.2, 0.2, 1)

    # ── 다음 문제 ─────────────────────────────
    def next_question(self, instance=None):
        if self.index < len(self.quiz_words) - 1:
            self.index += 1
            self._load_question()
        else:
            self._show_result()

    # ── 결과 화면 ─────────────────────────────
    def _show_result(self):
        save_daily_record(self.origin_words, self.total, self.correct)
        self.clear_widgets()

        root = BoxLayout(orientation="vertical")
        bg   = BoxLayout(
            orientation="vertical", padding=40, spacing=16)
        self._make_bg(bg)

        percent   = int(self.correct / self.total * 100) \
                    if self.total else 0
        today_str = date.today().strftime("%Y년 %m월 %d일")

        bg.add_widget(Widget())
        bg.add_widget(Label(
            text="퀴즈 완료!",
            font_name="Nanum", font_size=28, bold=True,
            color=(0, 0, 0, 1), size_hint_y=None, height=50
        ))
        bg.add_widget(Label(
            text=today_str,
            font_name="Nanum", font_size=14,
            color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height=28
        ))
        bg.add_widget(Label(
            text=f"학습 단어  {len(self.origin_words)}개",
            font_name="Nanum", font_size=18,
            color=(0.2, 0.2, 0.2, 1), size_hint_y=None, height=36
        ))
        bg.add_widget(Label(
            text=f"정답  {self.correct} / {self.total}",
            font_name="Nanum", font_size=22,
            color=(0.18, 0.7, 0.35, 1), size_hint_y=None, height=40
        ))
        bg.add_widget(Label(
            text=f"정답률  {percent}%",
            font_name="Nanum", font_size=18,
            color=(0.4, 0.4, 0.4, 1), size_hint_y=None, height=36
        ))
        bg.add_widget(Widget())

        home_btn = Button(
            text="홈으로 돌아가기",
            font_name="Nanum", font_size=16,
            background_color=(0.1, 0.1, 0.1, 1), color=(1, 1, 1, 1),
            size_hint_y=None, height=54
        )
        home_btn.bind(on_press=self.go_back)
        bg.add_widget(home_btn)
        bg.add_widget(Widget())

        root.add_widget(bg)
        self.add_widget(root)
        self.quiz_words = []

    # ── 스키밍 안 했을 때 ─────────────────────
    def _show_no_words(self):
        root = BoxLayout(orientation="vertical")
        bg   = BoxLayout(
            orientation="vertical", padding=40, spacing=20)
        self._make_bg(bg)

        bg.add_widget(Widget())
        bg.add_widget(Label(
            text="스키밍 먼저!",
            font_name="Nanum", font_size=26, bold=True,
            color=(0, 0, 0, 1), size_hint_y=None, height=50
        ))
        bg.add_widget(Label(
            text="스키밍을 완료하면\n퀴즈가 자동으로 시작돼요!",
            font_name="Nanum", font_size=16,
            color=(0.4, 0.4, 0.4, 1),
            size_hint_y=None, height=60, halign="center"
        ))
        bg.add_widget(Widget())

        skim_btn = Button(
            text="스키밍 하러 가기",
            font_name="Nanum", font_size=16,
            background_color=(0.1, 0.1, 0.1, 1), color=(1, 1, 1, 1),
            size_hint_y=None, height=54
        )
        skim_btn.bind(on_press=lambda x: setattr(
            self.manager, "current", "skimming"))

        home_btn = Button(
            text="홈으로",
            font_name="Nanum", font_size=16,
            background_color=(0.95, 0.95, 0.95, 1),
            color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None, height=54
        )
        home_btn.bind(on_press=self.go_back)

        bg.add_widget(skim_btn)
        bg.add_widget(home_btn)
        bg.add_widget(Widget())

        root.add_widget(bg)
        self.add_widget(root)

    def go_back(self, instance):
        self.manager.current = "home"