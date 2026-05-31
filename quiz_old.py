# quiz.py
import random
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle
from words import WORDS
from storage import mark_today_studied, save_word_review, \
                    get_due_words, get_skimmed_words

class QuizScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.words    = []
        self.index    = 0
        self.correct  = 0
        self.wrong    = 0
        self.revealed = False

    # ── 화면 들어올 때마다 실행 ───────────────
    def on_enter(self):
        self.clear_widgets()
        self.index    = 0
        self.correct  = 0
        self.wrong    = 0
        self.revealed = False

        skimmed = get_skimmed_words(WORDS)

        if not skimmed:
            self.show_no_skim_warning()
            return

        due = get_due_words(skimmed)
        self.words = due if due else skimmed[:]
        random.shuffle(self.words)
        self.build_quiz_ui()

    # ── 퀴즈 UI 만들기 ────────────────────────
    def build_quiz_ui(self):
        # 전체 배경
        with self.canvas.before:
            Color(0.95, 0.95, 0.93, 1)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size)
        self.bind(
            pos=lambda i, v: setattr(self.bg, 'pos', v),
            size=lambda i, v: setattr(self.bg, 'size', v)
        )

        self.root_layout = BoxLayout(
            orientation="vertical",
            padding=[16, 16, 16, 16],
            spacing=10
        )

        # ── 상단 바 ───────────────────────────
        top_bar = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=50
        )
        back_btn = Button(
            text="←",
            font_size=20,
            size_hint_x=None,
            width=50,
            background_color=(0.95, 0.95, 0.93, 1),
            color=(0, 0, 0, 1)
        )
        back_btn.bind(on_press=self.go_back)

        self.progress_label = Label(
            text=f"1 / {len(self.words)}",
            font_name="Nanum",
            font_size=14,
            bold=True,
            color=(0, 0, 0, 1)
        )
        self.score_label = Label(
            text="✓ 0   ✗ 0",
            font_name="Nanum",
            font_size=13,
            color=(0.4, 0.4, 0.4, 1),
            size_hint_x=None,
            width=100
        )
        top_bar.add_widget(back_btn)
        top_bar.add_widget(Widget())
        top_bar.add_widget(self.progress_label)
        top_bar.add_widget(Widget())
        top_bar.add_widget(self.score_label)

        # ── 진행 바 ───────────────────────────
        progress_bg = BoxLayout(
            size_hint_y=None,
            height=6
        )
        with progress_bg.canvas.before:
            Color(0.85, 0.85, 0.85, 1)
            self.bg_bar = RoundedRectangle(
                pos=progress_bg.pos,
                size=progress_bg.size,
                radius=[4]
            )
        progress_bg.bind(
            pos=lambda i, v: setattr(self.bg_bar, 'pos', v),
            size=lambda i, v: setattr(self.bg_bar, 'size', v)
        )
        self.fill_bar = Widget(
            size_hint_x=1/len(self.words),
            size_hint_y=1
        )
        with self.fill_bar.canvas:
            Color(0.1, 0.1, 0.1, 1)
            self.fill_rect = RoundedRectangle(
                pos=self.fill_bar.pos,
                size=self.fill_bar.size,
                radius=[4]
            )
        self.fill_bar.bind(
            pos=lambda i, v: setattr(self.fill_rect, 'pos', v),
            size=lambda i, v: setattr(self.fill_rect, 'size', v)
        )
        progress_bg.add_widget(self.fill_bar)

        # ── 단어 카드 ─────────────────────────
        self.card = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=400,
            padding=[24, 24, 24, 24],
            spacing=14
        )
        with self.card.canvas.before:
            Color(1, 1, 1, 1)
            self.card_rect = RoundedRectangle(
                pos=self.card.pos,
                size=self.card.size,
                radius=[18]
            )
        self.card.bind(
            pos=lambda i, v: setattr(self.card_rect, 'pos', v),
            size=lambda i, v: setattr(self.card_rect, 'size', v)
        )

        self.level_label = Label(
            text="",
            font_name="Nanum",
            font_size=12,
            color=(0.6, 0.6, 0.6, 1),
            size_hint_y=None,
            height=22,
            halign="left"
        )
        self.level_label.bind(
            size=lambda i, v: setattr(i, 'text_size', v))

        self.jp_label = Label(
            text="",
            font_name="NotoJP",
            font_size=48,
            bold=True,
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=70,
            halign="center"
        )
        self.jp_label.bind(
            size=lambda i, v: setattr(i, 'text_size', v))

        divider = Widget(size_hint_y=None, height=1)
        with divider.canvas:
            Color(0.9, 0.9, 0.9, 1)
            self.div_rect = RoundedRectangle(
                pos=divider.pos, size=divider.size)
        divider.bind(
            pos=lambda i, v: setattr(self.div_rect, 'pos', v),
            size=lambda i, v: setattr(self.div_rect, 'size', v))

        self.example_jp = Label(
            text="",
            font_name="NotoJP",
            font_size=15,
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=50,
            halign="center",
            text_size=(320, None)
        )
        self.example_kr = Label(
            text="",
            font_name="Nanum",
            font_size=13,
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=40,
            halign="center",
            text_size=(320, None)
        )
        self.furigana_label = Label(
            text="",
            font_name="NotoJP",
            font_size=14,
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=26,
            halign="center",
            opacity=0
        )
        self.furigana_label.bind(
            size=lambda i, v: setattr(i, 'text_size', v))

        self.kr_label = Label(
            text="",
            font_name="Nanum",
            font_size=20,
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None,
            height=36,
            halign="center",
            opacity=0
        )
        self.kr_label.bind(
            size=lambda i, v: setattr(i, 'text_size', v))

        self.card.add_widget(self.level_label)
        self.card.add_widget(self.jp_label)
        self.card.add_widget(divider)
        self.card.add_widget(self.example_jp)
        self.card.add_widget(self.example_kr)
        self.card.add_widget(self.furigana_label)
        self.card.add_widget(self.kr_label)

        # ── 정답 공개 버튼 ────────────────────
        self.reveal_btn = Button(
            text="정답 공개",
            font_name="Nanum",
            font_size=16,
            bold=True,
            size_hint_y=None,
            height=54,
            background_color=(0.1, 0.1, 0.1, 1),
            color=(1, 1, 1, 1)
        )
        self.reveal_btn.bind(on_press=self.reveal_answer)

        # ── 4단계 평가 버튼 ───────────────────
        self.answer_btns = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=54,
            spacing=8,
            opacity=0
        )
        self.btn_known = Button(
            text="알고있음\n3~5일",
            font_name="Nanum",
            font_size=12,
            background_color=(0.18, 0.7, 0.35, 1),
            color=(1, 1, 1, 1)
        )
        self.btn_known.bind(
            on_press=lambda x: self.rate_word("known"))

        self.btn_good = Button(
            text="괜찮음\n10분",
            font_name="Nanum",
            font_size=12,
            background_color=(0.2, 0.6, 0.9, 1),
            color=(1, 1, 1, 1)
        )
        self.btn_good.bind(
            on_press=lambda x: self.rate_word("good"))

        self.btn_vague = Button(
            text="애매함\n6분",
            font_name="Nanum",
            font_size=12,
            background_color=(0.95, 0.6, 0.1, 1),
            color=(1, 1, 1, 1)
        )
        self.btn_vague.bind(
            on_press=lambda x: self.rate_word("vague"))

        self.btn_forgot = Button(
            text="몰랐음\n1분",
            font_name="Nanum",
            font_size=12,
            background_color=(0.85, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        self.btn_forgot.bind(
            on_press=lambda x: self.rate_word("forgot"))

        self.answer_btns.add_widget(self.btn_known)
        self.answer_btns.add_widget(self.btn_good)
        self.answer_btns.add_widget(self.btn_vague)
        self.answer_btns.add_widget(self.btn_forgot)

        self.root_layout.add_widget(top_bar)
        self.root_layout.add_widget(progress_bg)
        self.root_layout.add_widget(self.card)
        self.root_layout.add_widget(self.reveal_btn)
        self.root_layout.add_widget(self.answer_btns)
        self.root_layout.add_widget(Widget())

        self.add_widget(self.root_layout)
        self.load_question()

    # ── 문제 불러오기 ─────────────────────────
    def load_question(self):
        self.revealed = False
        w = self.words[self.index]

        self.level_label.text    = w["level"]
        self.jp_label.text       = w["japanese"]
        self.example_jp.text     = w["example_jp"]
        self.example_kr.text     = w["example_kr"]
        self.furigana_label.text = w["furigana"]
        self.kr_label.text       = w["korean"]

        self.progress_label.text  = \
            f"{self.index + 1} / {len(self.words)}"
        self.fill_bar.size_hint_x = \
            (self.index + 1) / len(self.words)
        self.score_label.text = \
            f"✓ {self.correct}   ✗ {self.wrong}"

        self.furigana_label.opacity = 0
        self.kr_label.opacity       = 0
        self.reveal_btn.opacity     = 1
        self.reveal_btn.disabled    = False
        self.answer_btns.opacity    = 0
        self.answer_btns.disabled   = True

    # ── 정답 공개 ─────────────────────────────
    def reveal_answer(self, instance):
        if self.revealed:
            return
        self.revealed = True

        self.furigana_label.opacity = 1
        self.kr_label.opacity       = 1
        self.reveal_btn.opacity     = 0
        self.reveal_btn.disabled    = True
        self.answer_btns.opacity    = 1
        self.answer_btns.disabled   = False

    # ── 단어 평가 ─────────────────────────────
    def rate_word(self, level):
        jp = self.words[self.index]["japanese"]
        save_word_review(jp, level)
        mark_today_studied()

        if level in ("known", "good"):
            self.correct += 1
        else:
            self.wrong += 1

        self.next_question()

    # ── 다음 문제 ─────────────────────────────
    def next_question(self):
        if self.index < len(self.words) - 1:
            self.index += 1
            self.load_question()
        else:
            self.show_result()

    # ── 결과 화면 ─────────────────────────────
    def show_result(self):
        self.clear_widgets()

        with self.canvas.before:
            Color(0.95, 0.95, 0.93, 1)
            RoundedRectangle(pos=self.pos, size=self.size)

        layout = BoxLayout(
            orientation="vertical",
            padding=40,
            spacing=16
        )
        layout.add_widget(Widget())
        layout.add_widget(Label(
            text="퀴즈 완료! 🎉",
            font_name="Nanum",
            font_size=28,
            bold=True,
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=50
        ))
        layout.add_widget(Label(
            text=f"정답  {self.correct}개",
            font_name="Nanum",
            font_size=22,
            color=(0.18, 0.7, 0.35, 1),
            size_hint_y=None,
            height=40
        ))
        layout.add_widget(Label(
            text=f"다시 풀기  {self.wrong}개",
            font_name="Nanum",
            font_size=18,
            color=(0.85, 0.3, 0.3, 1),
            size_hint_y=None,
            height=36
        ))
        layout.add_widget(Widget())

        retry_btn = Button(
            text="처음부터 다시",
            font_name="Nanum",
            font_size=16,
            background_color=(0.95, 0.95, 0.95, 1),
            color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None,
            height=54
        )
        retry_btn.bind(on_press=self.retry)

        home_btn = Button(
            text="홈으로 돌아가기",
            font_name="Nanum",
            font_size=16,
            background_color=(0.1, 0.1, 0.1, 1),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=54
        )
        home_btn.bind(on_press=self.go_back)

        layout.add_widget(retry_btn)
        layout.add_widget(home_btn)
        layout.add_widget(Widget())
        self.add_widget(layout)

    # ── 다시 풀기 ─────────────────────────────
    def retry(self, instance):
        self.on_enter()

    # ── 스키밍 안 했을 때 경고 화면 ──────────
    def show_no_skim_warning(self):
        with self.canvas.before:
            Color(0.95, 0.95, 0.93, 1)
            RoundedRectangle(pos=self.pos, size=self.size)

        layout = BoxLayout(
            orientation="vertical",
            padding=40,
            spacing=20
        )
        layout.add_widget(Widget())
        layout.add_widget(Label(
            text="⚠️ 스키밍 먼저!",
            font_name="Nanum",
            font_size=26,
            bold=True,
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=50
        ))
        layout.add_widget(Label(
            text="퀴즈는 스키밍을 완료한\n단어로만 풀 수 있어요!",
            font_name="Nanum",
            font_size=16,
            color=(0.4, 0.4, 0.4, 1),
            size_hint_y=None,
            height=60,
            halign="center"
        ))
        layout.add_widget(Widget())

        go_skim_btn = Button(
            text="스키밍 하러 가기",
            font_name="Nanum",
            font_size=16,
            background_color=(0.1, 0.1, 0.1, 1),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=54
        )
        go_skim_btn.bind(on_press=self.go_skimming)

        home_btn = Button(
            text="홈으로 돌아가기",
            font_name="Nanum",
            font_size=16,
            background_color=(0.95, 0.95, 0.95, 1),
            color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None,
            height=54
        )
        home_btn.bind(on_press=self.go_back)

        layout.add_widget(go_skim_btn)
        layout.add_widget(home_btn)
        layout.add_widget(Widget())
        self.add_widget(layout)

    # ── 스키밍으로 이동 ───────────────────────
    def go_skimming(self, instance):
        self.manager.current = "skimming"

    # ── 뒤로가기 ──────────────────────────────
    def go_back(self, instance):
        self.manager.current = "home"