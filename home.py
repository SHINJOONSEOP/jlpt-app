# home.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle
from kivy.core.text import LabelBase
from datetime import date, timedelta

from storage import get_history
#from storage import get_day_count 

# 한글 폰트 등록
try:
    LabelBase.register(name="Nanum", fn_regular="NanumGothic.ttf")
except Exception:
    pass

# ↓ 일본어 폰트 등록
try:
    LabelBase.register(name="NotoJP", fn_regular="NotoSansJP-Regular.ttf")
except Exception:
    pass

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # 전체 배경 연회색
        with self.canvas.before:
            Color(0.95, 0.95, 0.93, 1)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size)
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
        title = Label(
            text="JLPT",
            font_name="Nanum",
            font_size=26,
            bold=True,
            color=(0, 0, 0, 1),
            size_hint_x=0.4,
            halign="left"
        )
        title.bind(size=lambda i, v: setattr(i, 'text_size', v))

        d_label = Label(
            text="D-222  1.9%",
            font_name="Nanum",
            font_size=13,
            color=(0.4, 0.4, 0.4, 1),
            size_hint_x=0.6,
            halign="right"
        )
        d_label.bind(size=lambda i, v: setattr(i, 'text_size', v))

        header.add_widget(title)
        header.add_widget(d_label)

        # ── 요일 라벨 ─────────────────────────
        days_layout = GridLayout(
            cols=7,
            size_hint_y=None,
            height=24
        )
        for day in ["일", "월", "화", "수", "목", "금", "토"]:
            days_layout.add_widget(Label(
                text=day,
                font_name="Nanum",
                font_size=12,
                color=(0.6, 0.6, 0.6, 1)
            ))

        # ── 날짜 줄 ───────────────────────────
        dates_layout = GridLayout(
            cols=7,
            size_hint_y=None,
            height=44
        )
        today = date.today()
        weekday = today.weekday()
        sunday = today - timedelta(days=(weekday + 1) % 7)
        history_dates = [h["date"] for h in get_history()]

        for i in range(7):
            d = sunday + timedelta(days=i)
            is_today = (d == today)
            did_study = str(d) in history_dates

            # 공부한 날은 초록 점 추가
            if did_study and not is_today:
                day_text = str(d.day) + "\n●"   # ← 점 추가
                day_color = (0.18, 0.7, 0.35, 1)  # 초록
            elif is_today:
                day_text = str(d.day)
                day_color = (1, 1, 1, 1)          # 흰색 (검은 배경)
            else:
                day_text = str(d.day)
                day_color = (0.3, 0.3, 0.3, 1)   # 회색

            btn = Button(
                text=day_text,
                font_name="Nanum",
                font_size=12,
                background_color=(0.1, 0.1, 0.1, 1) if is_today
                                else (0.95, 0.95, 0.93, 1),
                color=day_color,
                bold=is_today,
                halign="center"
            )
            dates_layout.add_widget(btn)

        # ── Day 표시 ──────────────────────────
        day_count = len(get_history())   # ← 기록 개수 = 학습 일수
        day_label = Label(
            text=f"Day {day_count if day_count > 0 else 1}",
            font_name="Nanum",
            font_size=20,
            bold=True,
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=36,
            halign="left"
        )
        day_label.bind(size=lambda i, v: setattr(i, 'text_size', v))

        # ── 가로 슬라이드 카드 영역 ───────────
        scroll = ScrollView(
            size_hint_y=None,
            height=320,
            do_scroll_x=True,     # 가로 스크롤만
            do_scroll_y=False,
            bar_width=0           # 스크롤바 숨김
        )

        # 카드들을 가로로 나열할 컨테이너
        cards_container = GridLayout(
            cols=3,               # 카드 3개
            size_hint_x=None,
            width=900,            # 카드 3개 * 300px
            size_hint_y=1,
            spacing=12,
            padding=[0, 4, 0, 4]
        )

        # 카드 데이터
        card_data = [
            {
                "title": "스키밍",
                "desc": "랜덤 20개 단어 학습",
                "time": "~10분",
                "screen": "skimming",
                "color": (0.1, 0.1, 0.1, 1),
                "text_color": (1, 1, 1, 1)
            },
            {
                "title": "퀴즈",
                "desc": "스키밍 후 자동 시작",
                "time": "~5분",
                "screen": "quiz",
                "color": (1, 1, 1, 1),
                "text_color": (0, 0, 0, 1)
            },
        ]

        for data in card_data:
            card = self.make_card(data)
            cards_container.add_widget(card)

        scroll.add_widget(cards_container)

        # ── 점 인디케이터 (• • •) ─────────────
        dots_layout = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=20,
            spacing=6
        )
        dots_layout.add_widget(Widget())
        for i in range(3):
            dot = Label(
                text="●" if i == 0 else "○",
                font_size=10,
                color=(0.3, 0.3, 0.3, 1) if i == 0
                      else (0.7, 0.7, 0.7, 1),
                size_hint_x=None,
                width=16
            )
            dots_layout.add_widget(dot)
        dots_layout.add_widget(Widget())

        # 전부 레이아웃에 추가
        layout.add_widget(header)
        layout.add_widget(days_layout)
        layout.add_widget(dates_layout)
        layout.add_widget(day_label)
        layout.add_widget(scroll)
        layout.add_widget(dots_layout)
        layout.add_widget(Widget())     # 하단 여백

        self.add_widget(layout)

    # ── 카드 만들기 ───────────────────────────
    def make_card(self, data):
        # 카드 전체 박스
        card = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=10,
            size_hint_x=None,
            width=280
        )

        # 카드 배경색
        with card.canvas.before:
            Color(*data["color"])
            rect = RoundedRectangle(
                pos=card.pos,
                size=card.size,
                radius=[18]
            )
        card.bind(
            pos=lambda i, v, r=rect: setattr(r, 'pos', v),
            size=lambda i, v, r=rect: setattr(r, 'size', v)
        )

        # 카드 제목
        title = Label(
            text=data["title"],
            font_name="Nanum",
            font_size=20,
            bold=True,
            color=data["text_color"],
            size_hint_y=None,
            height=36,
            halign="left"
        )
        title.bind(size=lambda i, v: setattr(i, 'text_size', v))

        # 카드 설명
        desc = Label(
            text=data["desc"],
            font_name="Nanum",
            font_size=13,
            color=(
                (0.7, 0.7, 0.7, 1) if data["color"][0] < 0.5
                else (0.5, 0.5, 0.5, 1)
            ),
            size_hint_y=None,
            height=28,
            halign="left"
        )
        desc.bind(size=lambda i, v: setattr(i, 'text_size', v))

        # 예상 시간
        time_label = Label(
            text=data["time"],
            font_name="Nanum",
            font_size=12,
            color=(
                (0.6, 0.6, 0.6, 1) if data["color"][0] < 0.5
                else (0.7, 0.7, 0.7, 1)
            ),
            size_hint_y=None,
            height=24,
            halign="left"
        )
        time_label.bind(size=lambda i, v: setattr(i, 'text_size', v))

        # 시작 버튼
        start_btn = Button(
            text="바로 시작",
            font_name="Nanum",
            font_size=15,
            bold=True,
            size_hint_y=None,
            height=48,
            background_color=(
                (1, 1, 1, 1) if data["color"][0] < 0.5
                else (0.1, 0.1, 0.1, 1)
            ),
            color=(
                (0, 0, 0, 1) if data["color"][0] < 0.5
                else (1, 1, 1, 1)
            )
        )
        # 화면 전환 연결
        target = data["screen"]
        start_btn.bind(
            on_press=lambda x, t=target:
                setattr(self.manager, "current", t)
        )

        card.add_widget(title)
        card.add_widget(desc)
        card.add_widget(time_label)
        card.add_widget(Widget())    # 여백
        card.add_widget(start_btn)

        return card