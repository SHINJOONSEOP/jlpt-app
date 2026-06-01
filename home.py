# home.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.core.text import LabelBase
from datetime import date, timedelta
from storage import get_history
import api

try:
    LabelBase.register(name="Nanum", fn_regular="NanumGothic.ttf")
except Exception:
    pass
try:
    LabelBase.register(name="NotoJP", fn_regular="NotoSansJP-Regular.ttf")
except Exception:
    pass

class HomeScreen(Screen):

    def on_enter(self):
        self.clear_widgets()
        self._build()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build()

    def _build(self):
        with self.canvas.before:
            Color(0.95, 0.95, 0.93, 1)
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(
            pos=lambda i, v: setattr(self.bg, 'pos', v),
            size=lambda i, v: setattr(self.bg, 'size', v)
        )

        layout = BoxLayout(
            orientation="vertical",
            padding=[16, 16, 16, 16],
            spacing=10
        )

        # ── 상단 헤더 ─────────────────────────
        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=44
        )
        nickname = api.get_nickname() or "학습자"
        title = Label(
            text=f"JLPT  👋 {nickname}",
            font_name="Nanum",
            font_size=20, bold=True,
            color=(0, 0, 0, 1),
            size_hint_x=0.7, halign="left"
        )
        title.bind(size=lambda i, v: setattr(i, 'text_size', v))

        logout_btn = Button(
            text="로그아웃",
            font_name="Nanum", font_size=11,
            size_hint_x=0.3,
            background_color=(0.85, 0.85, 0.85, 1),
            color=(0.3, 0.3, 0.3, 1)
        )
        def do_logout(x):
            api.logout()
            self.manager.current = "login"
        logout_btn.bind(on_press=do_logout)

        header.add_widget(title)
        header.add_widget(logout_btn)

        # ── 요일 라벨 ─────────────────────────
        days_layout = GridLayout(cols=7, size_hint_y=None, height=24)
        for day in ["일", "월", "화", "수", "목", "금", "토"]:
            days_layout.add_widget(Label(
                text=day, font_name="Nanum",
                font_size=12, color=(0.6, 0.6, 0.6, 1)
            ))

        # ── 날짜 줄 ───────────────────────────
        dates_layout = GridLayout(cols=7, size_hint_y=None, height=44)
        today = date.today()
        weekday = today.weekday()
        sunday = today - timedelta(days=(weekday + 1) % 7)
        history_dates = [h["date"] for h in get_history()]

        for i in range(7):
            d = sunday + timedelta(days=i)
            is_today = (d == today)
            did_study = str(d) in history_dates

            if did_study and not is_today:
                day_text  = str(d.day) + "\n●"
                day_color = (0.18, 0.7, 0.35, 1)
            elif is_today:
                day_text  = str(d.day)
                day_color = (1, 1, 1, 1)
            else:
                day_text  = str(d.day)
                day_color = (0.3, 0.3, 0.3, 1)

            btn = Button(
                text=day_text,
                font_name="Nanum", font_size=12,
                background_color=(0.1, 0.1, 0.1, 1) if is_today
                                  else (0.95, 0.95, 0.93, 1),
                color=day_color, bold=is_today, halign="center"
            )
            dates_layout.add_widget(btn)

        # ── Day 표시 ──────────────────────────
        day_count = len(get_history())
        day_label = Label(
            text=f"Day {day_count if day_count > 0 else 1}",
            font_name="Nanum", font_size=20, bold=True,
            color=(0, 0, 0, 1),
            size_hint_y=None, height=36, halign="left"
        )
        day_label.bind(size=lambda i, v: setattr(i, 'text_size', v))

        # ── 가로 슬라이드 카드 영역 ───────────
        scroll = ScrollView(
            size_hint_y=None, height=320,
            do_scroll_x=True, do_scroll_y=False, bar_width=0
        )
        cards_container = GridLayout(
            cols=2, size_hint_x=None, width=600,
            size_hint_y=1, spacing=12, padding=[0, 4, 0, 4]
        )

        card_data = [
            {
                "title": "스키밍", "desc": "랜덤 20개 단어 학습",
                "time": "~10분", "screen": "skimming",
                "color": (0.1, 0.1, 0.1, 1), "text_color": (1, 1, 1, 1)
            },
            {
                "title": "퀴즈", "desc": "스키밍 후 자동 시작",
                "time": "~5분", "screen": "quiz",
                "color": (1, 1, 1, 1), "text_color": (0, 0, 0, 1)
            },
        ]

        for data in card_data:
            cards_container.add_widget(self._make_card(data))

        scroll.add_widget(cards_container)

        # ── 하단 버튼 행 ──────────────────────
        bottom_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=44, spacing=10
        )
        history_btn = Button(
            text="📋 기록", font_name="Nanum", font_size=14,
            background_color=(1, 1, 1, 1), color=(0.2, 0.2, 0.2, 1)
        )
        history_btn.bind(on_press=lambda x: setattr(
            self.manager, "current", "history"))

        stats_btn = Button(
            text="📊 통계", font_name="Nanum", font_size=14,
            background_color=(1, 1, 1, 1), color=(0.2, 0.2, 0.2, 1)
        )
        stats_btn.bind(on_press=lambda x: setattr(
            self.manager, "current", "stats"))

        bottom_row.add_widget(history_btn)
        bottom_row.add_widget(stats_btn)

        layout.add_widget(header)
        layout.add_widget(days_layout)
        layout.add_widget(dates_layout)
        layout.add_widget(day_label)
        layout.add_widget(scroll)
        layout.add_widget(bottom_row)
        layout.add_widget(Widget())

        self.add_widget(layout)

    def _make_card(self, data):
        card = BoxLayout(
            orientation="vertical",
            padding=20, spacing=10,
            size_hint_x=None, width=280
        )
        with card.canvas.before:
            Color(*data["color"])
            rect = RoundedRectangle(
                pos=card.pos, size=card.size, radius=[18])
        card.bind(
            pos=lambda i, v, r=rect: setattr(r, 'pos', v),
            size=lambda i, v, r=rect: setattr(r, 'size', v)
        )

        title = Label(
            text=data["title"], font_name="Nanum",
            font_size=20, bold=True, color=data["text_color"],
            size_hint_y=None, height=36, halign="left"
        )
        title.bind(size=lambda i, v: setattr(i, 'text_size', v))

        desc = Label(
            text=data["desc"], font_name="Nanum", font_size=13,
            color=(0.7, 0.7, 0.7, 1) if data["color"][0] < 0.5
                  else (0.5, 0.5, 0.5, 1),
            size_hint_y=None, height=28, halign="left"
        )
        desc.bind(size=lambda i, v: setattr(i, 'text_size', v))

        time_label = Label(
            text=data["time"], font_name="Nanum", font_size=12,
            color=(0.6, 0.6, 0.6, 1) if data["color"][0] < 0.5
                  else (0.7, 0.7, 0.7, 1),
            size_hint_y=None, height=24, halign="left"
        )
        time_label.bind(size=lambda i, v: setattr(i, 'text_size', v))

        start_btn = Button(
            text="바로 시작", font_name="Nanum",
            font_size=15, bold=True,
            size_hint_y=None, height=48,
            background_color=(1, 1, 1, 1) if data["color"][0] < 0.5
                              else (0.1, 0.1, 0.1, 1),
            color=(0, 0, 0, 1) if data["color"][0] < 0.5
                  else (1, 1, 1, 1)
        )
        target = data["screen"]
        start_btn.bind(on_press=lambda x, t=target:
                       setattr(self.manager, "current", t))

        card.add_widget(title)
        card.add_widget(desc)
        card.add_widget(time_label)
        card.add_widget(Widget())
        card.add_widget(start_btn)
        return card