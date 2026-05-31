# skimming.py
import random
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.core.text import LabelBase
from words import WORDS
from tts import speak

try:
    LabelBase.register(name="Nanum", fn_regular="NanumGothic.ttf")
except Exception:
    pass
try:
    LabelBase.register(name="NotoJP", fn_regular="NotoSansJP-Regular.ttf")
except Exception:
    pass

class SkimmingScreen(Screen):

    def on_enter(self):
        self.clear_widgets()
        pool            = WORDS[:]
        random.shuffle(pool)
        self.words      = pool[:20]
        self.index      = 0
        self.quiz_words = []
        self._build_ui()

    def _make_bg(self, widget):
        """위젯에 연회색 배경 추가"""
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
            padding=[16, 16, 16, 16], spacing=10
        )
        self._make_bg(bg)

        # 상단 바
        top_bar = BoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=50
        )
        back_btn = Button(
            text="←", size_hint_x=None, width=50,
            font_size=20,
            background_color=(0.95, 0.95, 0.93, 1),
            color=(0, 0, 0, 1)
        )
        back_btn.bind(on_press=self.go_back)
        self.progress_label = Label(
            text=f"1 / {len(self.words)}",
            font_name="Nanum", font_size=14,
            bold=True, color=(0, 0, 0, 1)
        )
        top_bar.add_widget(back_btn)
        top_bar.add_widget(Widget())
        top_bar.add_widget(self.progress_label)

        # 진행 바
        progress_bg = BoxLayout(size_hint_y=None, height=6)
        with progress_bg.canvas.before:
            Color(0.85, 0.85, 0.85, 1)
            self._pbg_rect = Rectangle(
                pos=progress_bg.pos, size=progress_bg.size)
        progress_bg.bind(
            pos=lambda i, v: setattr(self._pbg_rect, 'pos', v),
            size=lambda i, v: setattr(self._pbg_rect, 'size', v)
        )
        self.fill_bar = Widget(
            size_hint_x=1/len(self.words), size_hint_y=1)
        with self.fill_bar.canvas:
            Color(0.1, 0.1, 0.1, 1)
            self._fill_rect = Rectangle(
                pos=self.fill_bar.pos, size=self.fill_bar.size)
        self.fill_bar.bind(
            pos=lambda i, v: setattr(self._fill_rect, 'pos', v),
            size=lambda i, v: setattr(self._fill_rect, 'size', v)
        )
        progress_bg.add_widget(self.fill_bar)

        # 단어 카드
        self.card = BoxLayout(
            orientation="vertical",
            size_hint_y=None, height=400,
            padding=[24, 20, 24, 20], spacing=12
        )
        with self.card.canvas.before:
            Color(1, 1, 1, 1)
            self._card_rect = RoundedRectangle(
                pos=self.card.pos, size=self.card.size, radius=[18])
        self.card.bind(
            pos=lambda i, v: setattr(self._card_rect, 'pos', v),
            size=lambda i, v: setattr(self._card_rect, 'size', v)
        )

        self.level_label = Label(
            text="", font_name="Nanum", font_size=12,
            color=(0.6, 0.6, 0.6, 1),
            size_hint_y=None, height=20, halign="left"
        )
        self.level_label.bind(
            size=lambda i, v: setattr(i, 'text_size', v))
        # 🔊 일본어 발음 버튼
        speak_btn = Button(
            text="🔊 발음 듣기",
            font_name="Nanum",
            font_size=13,
            size_hint_y=None,
            height=36,
            background_color=(0.2, 0.5, 0.9, 1),
            color=(1, 1, 1, 1)
        )
        speak_btn.bind(on_press=lambda x: speak(
            self.words[self.index]["japanese"] + "。" +
            self.words[self.index].get("example_jp", "")
        ))
        self.card.add_widget(speak_btn)

        self.jp_label = Label(
            text="", font_name="NotoJP", font_size=46, bold=True,
            color=(0, 0, 0, 1),
            size_hint_y=None, height=70, halign="center"
        )
        self.jp_label.bind(
            size=lambda i, v: setattr(i, 'text_size', v))
        self.furigana_label = Label(
            text="", font_name="NotoJP", font_size=14,
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None, height=26, halign="center"
        )
        self.furigana_label.bind(
            size=lambda i, v: setattr(i, 'text_size', v))
        self.kr_label = Label(
            text="", font_name="Nanum", font_size=22, bold=True,
            color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None, height=36, halign="center"
        )
        self.kr_label.bind(
            size=lambda i, v: setattr(i, 'text_size', v))

        divider = Widget(size_hint_y=None, height=1)
        with divider.canvas:
            Color(0.9, 0.9, 0.9, 1)
            _dr = Rectangle(pos=divider.pos, size=divider.size)
        divider.bind(
            pos=lambda i, v: setattr(_dr, 'pos', v),
            size=lambda i, v: setattr(_dr, 'size', v))

        self.example_jp_label = Label(
            text="", font_name="NotoJP", font_size=14,
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None, height=46,
            halign="center", text_size=(300, None)
        )
        self.example_kr_label = Label(
            text="", font_name="Nanum", font_size=13,
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None, height=36,
            halign="center", text_size=(300, None)
        )

        self.card.add_widget(self.level_label)
        self.card.add_widget(self.jp_label)
        self.card.add_widget(self.furigana_label)
        self.card.add_widget(self.kr_label)
        self.card.add_widget(divider)
        self.card.add_widget(self.example_jp_label)
        self.card.add_widget(self.example_kr_label)

        # 하단 버튼
        btn_layout = BoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=54, spacing=10
        )
        dont_know_btn = Button(
            text="잘모르겠다", font_name="Nanum", font_size=16,
            background_color=(0.85, 0.2, 0.2, 1), color=(1, 1, 1, 1)
        )
        dont_know_btn.bind(on_press=self.mark_dont_know)
        know_btn = Button(
            text="알고있다", font_name="Nanum", font_size=16,
            background_color=(0.18, 0.7, 0.35, 1), color=(1, 1, 1, 1)
        )
        know_btn.bind(on_press=self.mark_know)
        btn_layout.add_widget(dont_know_btn)
        btn_layout.add_widget(know_btn)

        bg.add_widget(top_bar)
        bg.add_widget(progress_bg)
        bg.add_widget(self.card)
        bg.add_widget(btn_layout)

        root.add_widget(bg)
        self.add_widget(root)
        self._update_card()

    def _update_card(self):
        w = self.words[self.index]
        self.level_label.text      = w["level"]
        self.jp_label.text         = w["japanese"]
        self.furigana_label.text   = w["furigana"]
        self.kr_label.text         = w["korean"]
        self.example_jp_label.text = w["example_jp"]
        self.example_kr_label.text = w["example_kr"]
        self.progress_label.text   = \
            f"{self.index + 1} / {len(self.words)}"
        self.fill_bar.size_hint_x  = \
            (self.index + 1) / len(self.words)

    def mark_dont_know(self, instance):
        w = self.words[self.index]
        self.quiz_words.extend([w, w, w])
        self._next_word()

    def mark_know(self, instance):
        w = self.words[self.index]
        self.quiz_words.append(w)
        self._next_word()

    def _next_word(self):
        if self.index < len(self.words) - 1:
            self.index += 1
            self._update_card()
        else:
            self._finish_skimming()

    def _finish_skimming(self):
        random.shuffle(self.quiz_words)
        quiz_screen = self.manager.get_screen("quiz")
        quiz_screen.receive_words(self.quiz_words, self.words)

        dont_count = sum(
            1 for w in self.words
            if self.quiz_words.count(w) >= 3
        )
        know_count = len(self.words) - dont_count

        self.clear_widgets()

        root = BoxLayout(orientation="vertical")
        bg   = BoxLayout(
            orientation="vertical",
            padding=40, spacing=16
        )
        self._make_bg(bg)

        bg.add_widget(Widget())
        bg.add_widget(Label(
            text="✅ 스키밍 완료!",
            font_name="Nanum", font_size=26, bold=True,
            color=(0, 0, 0, 1), size_hint_y=None, height=50
        ))
        bg.add_widget(Label(
            text=f"잘모르겠다 {dont_count}개  |  알고있다 {know_count}개\n"
                 f"총 퀴즈 문제: {len(self.quiz_words)}개",
            font_name="Nanum", font_size=15,
            color=(0.4, 0.4, 0.4, 1),
            size_hint_y=None, height=60, halign="center"
        ))
        bg.add_widget(Widget())

        quiz_btn = Button(
            text="퀴즈 바로 시작 →",
            font_name="Nanum", font_size=16, bold=True,
            background_color=(0.1, 0.1, 0.1, 1), color=(1, 1, 1, 1),
            size_hint_y=None, height=54
        )
        quiz_btn.bind(on_press=lambda x: setattr(
            self.manager, "current", "quiz"))

        home_btn = Button(
            text="나중에 풀기",
            font_name="Nanum", font_size=16,
            background_color=(0.95, 0.95, 0.95, 1),
            color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None, height=54
        )
        home_btn.bind(on_press=lambda x: setattr(
            self.manager, "current", "home"))

        bg.add_widget(quiz_btn)
        bg.add_widget(home_btn)
        bg.add_widget(Widget())

        root.add_widget(bg)
        self.add_widget(root)

    def go_back(self, instance):
        self.manager.current = "home"