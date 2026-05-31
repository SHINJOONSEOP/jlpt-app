# flashcard.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.graphics import Color, RoundedRectangle
from words import WORDS

class FlashcardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.words = WORDS
        self.index = 0
        self.is_flipped = False

        # 전체 레이아웃
        layout = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=12
        )

        # ── 상단 바 ───────────────────────────
        top_bar = BoxLayout(
            orientation="horizontal",
            size_hint_y=0.08
        )
        back_btn = Button(
            text="←",
            size_hint_x=0.15,
            background_color=(1, 1, 1, 1),
            color=(0, 0, 0, 1),
            font_size=20
        )
        back_btn.bind(on_press=self.go_back)

        self.progress_label = Label(
            text=f"1 / {len(self.words)}",
            font_name="Nanum",
            font_size=14,
            color=(0, 0, 0, 1),
            bold=True
        )
        top_bar.add_widget(back_btn)
        top_bar.add_widget(Widget())
        top_bar.add_widget(self.progress_label)

        # ── 안내 문구 ─────────────────────────
        hint = Label(
            text="카드를 탭하면 정답이 보여요",
            font_name="Nanum",
            font_size=13,
            color=(0.6, 0.6, 0.6, 1),
            size_hint_y=0.06
        )

        # ── 카드 영역 (FloatLayout으로 교체) ──
        # 흰 배경 박스 역할
        self.card_bg = BoxLayout(
            orientation="vertical",
            size_hint_y=0.55,
            padding=24,
            spacing=14
        )
        # 흰 배경색 그리기
        with self.card_bg.canvas.before:
            Color(1, 1, 1, 1)
            self.card_rect = RoundedRectangle(
                pos=self.card_bg.pos,
                size=self.card_bg.size,
                radius=[16]
            )
        # 크기/위치 바뀔 때 배경도 같이 업데이트
        self.card_bg.bind(
            pos=self.update_card_rect,
            size=self.update_card_rect
        )
        # 카드 전체 탭 감지용 투명 버튼 (맨 위에 올림)
        self.card_touch = Button(
            background_color=(0, 0, 0, 0),   # 완전 투명
            size_hint=(1, 1)
        )
        self.card_touch.bind(on_press=self.flip_card)

        # 앞면: 일본어
        self.jp_label = Label(
            text=self.words[self.index]["japanese"],
            font_name="NotoJP",
            font_size=46,
            bold=True,
            color=(0, 0, 0, 1),
            size_hint_y=0.4
        )

        # 뒷면: 한국어 뜻
        self.kr_label = Label(
            text=self.words[self.index]["korean"],
            font_name="Nanum",
            font_size=22,
            color=(0.1, 0.1, 0.1, 1),
            opacity=0,
            size_hint_y=0.3
        )

        # 뒷면: 예문
        self.example_label = Label(
            text=self.words[self.index]["example_jp"] + "\n" +
                 self.words[self.index]["example_kr"],
            font_name="Nanum",
            font_size=13,
            color=(0.5, 0.5, 0.5, 1),
            opacity=0,
            text_size=(280, None),
            halign="center",
            size_hint_y=0.3
        )

        # 카드 안에 라벨들 추가
        self.card_bg.add_widget(self.jp_label)
        self.card_bg.add_widget(self.kr_label)
        self.card_bg.add_widget(self.example_label)
        self.card_bg.add_widget(self.card_touch)  # 투명 버튼 맨 마지막

        # ── 하단 버튼 2개 ─────────────────────
        self.btn_layout = BoxLayout(
            orientation="horizontal",
            size_hint_y=0.12,
            spacing=10,
            opacity=0
        )

        wrong_btn = Button(
            text="몰라요",
            font_name="Nanum",
            font_size=16,
            background_color=(0.95, 0.95, 0.95, 1),
            color=(0.1, 0.1, 0.1, 1)
        )
        wrong_btn.bind(on_press=self.next_card)

        know_btn = Button(
            text="알고 있어요",
            font_name="Nanum",
            font_size=16,
            background_color=(0.1, 0.1, 0.1, 1),
            color=(1, 1, 1, 1)
        )
        know_btn.bind(on_press=self.next_card)

        self.btn_layout.add_widget(wrong_btn)
        self.btn_layout.add_widget(know_btn)

        # 전부 레이아웃에 추가
        layout.add_widget(top_bar)
        layout.add_widget(hint)
        layout.add_widget(self.card_bg)
        layout.add_widget(self.btn_layout)

        self.add_widget(layout)

    # ── 카드 배경 크기 동기화 ─────────────────
    def update_card_rect(self, instance, value):
        self.card_rect.pos  = instance.pos
        self.card_rect.size = instance.size

    # ── 카드 뒤집기 ───────────────────────────
    def flip_card(self, instance):
        if self.is_flipped:
            return

        self.is_flipped = True

        anim_out = Animation(opacity=0, duration=0.15)
        anim_out.bind(on_complete=self.show_back)
        anim_out.start(self.jp_label)

    def show_back(self, animation, widget):
        self.btn_layout.opacity = 1

        anim_kr = Animation(opacity=1, duration=0.2)
        anim_ex = Animation(opacity=1, duration=0.2)
        anim_kr.start(self.kr_label)
        anim_ex.start(self.example_label)

    # ── 다음 카드로 ───────────────────────────
    def next_card(self, instance):
        self.is_flipped = False

        if self.index < len(self.words) - 1:
            self.index += 1
        else:
            self.index = 0

        w = self.words[self.index]
        self.jp_label.text       = w["japanese"]
        self.kr_label.text       = w["korean"]
        self.example_label.text  = w["example_jp"] + "\n" + w["example_kr"]
        self.progress_label.text = f"{self.index + 1} / {len(self.words)}"

        # 앞면 다시 보이기, 뒷면 숨기기
        self.jp_label.opacity      = 1
        self.kr_label.opacity      = 0
        self.example_label.opacity = 0
        self.btn_layout.opacity    = 0

    # ── 뒤로가기 ──────────────────────────────
    def go_back(self, instance):
        self.manager.current = "home"