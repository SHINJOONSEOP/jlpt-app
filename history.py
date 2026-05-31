# history.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, RoundedRectangle
from storage import get_history
import api

class HistoryScreen(Screen):

    def on_enter(self):
        self.clear_widgets()
        self._build()

    def _make_bg(self, widget, color=(0.95, 0.95, 0.93, 1)):
        with widget.canvas.before:
            Color(*color)
            rect = Rectangle(pos=widget.pos, size=widget.size)
        widget.bind(
            pos=lambda i, v: setattr(rect, 'pos', v),
            size=lambda i, v: setattr(rect, 'size', v)
        )

    def _make_card(self, widget, radius=14):
        with widget.canvas.before:
            Color(1, 1, 1, 1)
            rect = RoundedRectangle(
                pos=widget.pos, size=widget.size, radius=[radius])
        widget.bind(
            pos=lambda i, v: setattr(rect, 'pos', v),
            size=lambda i, v: setattr(rect, 'size', v)
        )

    def _build(self):
        root = BoxLayout(orientation="vertical")
        bg   = BoxLayout(
            orientation="vertical",
            padding=[16, 16, 16, 16],
            spacing=12
        )
        self._make_bg(bg)

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

        title = Label(
            text="학습 기록",
            font_name="Nanum",
            font_size=20,
            bold=True,
            color=(0, 0, 0, 1),
            halign="center"
        )
        title.bind(size=lambda i, v: setattr(i, 'text_size', v))

        # 오른쪽 빈 공간 (대칭 맞추기)
        spacer = Widget(size_hint_x=None, width=50)

        top_bar.add_widget(back_btn)
        top_bar.add_widget(title)
        top_bar.add_widget(spacer)

        # ── 요약 카드 (전체 통계) ─────────────
        summary_card = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=90,
            padding=[20, 12, 20, 12],
            spacing=0
        )
        self._make_card(summary_card)

        # 기록 불러오기
        records = self._load_records()

        total_days    = len(records)
        total_words   = sum(len(r.get("words", [])) for r in records)
        total_correct = sum(r.get("correct", 0) for r in records)
        total_quiz    = sum(r.get("total_quiz", 0) for r in records)
        avg_percent   = int(total_correct / total_quiz * 100) \
                        if total_quiz else 0

        for label_text, value_text in [
            ("총 학습일", f"{total_days}일"),
            ("총 단어",  f"{total_words}개"),
            ("평균 정답률", f"{avg_percent}%"),
        ]:
            col = BoxLayout(orientation="vertical", spacing=2)
            val = Label(
                text=value_text,
                font_name="Nanum",
                font_size=22,
                bold=True,
                color=(0, 0, 0, 1),
                halign="center"
            )
            val.bind(size=lambda i, v: setattr(i, 'text_size', v))
            lbl = Label(
                text=label_text,
                font_name="Nanum",
                font_size=11,
                color=(0.6, 0.6, 0.6, 1),
                halign="center"
            )
            lbl.bind(size=lambda i, v: setattr(i, 'text_size', v))
            col.add_widget(val)
            col.add_widget(lbl)
            summary_card.add_widget(col)

        # ── 기록 목록 ─────────────────────────
        scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=0
        )

        records_layout = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=10,
            padding=[0, 4, 0, 4]
        )
        records_layout.bind(
            minimum_height=records_layout.setter("height"))

        if not records:
            # 기록 없을 때
            empty_box = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=200,
                padding=[20, 40, 20, 40]
            )
            self._make_card(empty_box)
            empty_box.add_widget(Label(
                text="아직 학습 기록이 없어요",
                font_name="Nanum",
                font_size=16,
                color=(0.6, 0.6, 0.6, 1),
                halign="center"
            ))
            empty_box.add_widget(Label(
                text="스키밍 → 퀴즈를 완료하면\n기록이 쌓여요!",
                font_name="Nanum",
                font_size=13,
                color=(0.75, 0.75, 0.75, 1),
                halign="center"
            ))
            records_layout.add_widget(empty_box)
        else:
            for record in records:
                card = self._make_record_card(record)
                records_layout.add_widget(card)

        scroll.add_widget(records_layout)

        bg.add_widget(top_bar)
        bg.add_widget(summary_card)
        bg.add_widget(scroll)

        root.add_widget(bg)
        self.add_widget(root)

    # ── 기록 카드 1개 만들기 ──────────────────
    def _make_record_card(self, record):
        date_str   = record.get("date", "")
        words      = record.get("words", [])
        total_quiz = record.get("total_quiz", 0)
        correct    = record.get("correct", 0)
        percent    = int(correct / total_quiz * 100) \
                     if total_quiz else 0

        # 날짜 포맷 변환 "2026-05-25" → "2026년 05월 25일"
        try:
            y, m, d  = date_str.split("-")
            date_fmt = f"{y}년 {m}월 {d}일"
        except Exception:
            date_fmt = date_str

        # 정답률에 따른 색상
        if percent >= 80:
            percent_color = (0.18, 0.7, 0.35, 1)   # 초록
        elif percent >= 60:
            percent_color = (0.95, 0.6, 0.1, 1)    # 주황
        else:
            percent_color = (0.85, 0.2, 0.2, 1)    # 빨강

        # 카드 전체
        card = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=160,
            padding=[18, 14, 18, 14],
            spacing=10
        )
        self._make_card(card)

        # ── 상단: 날짜 + 정답률 ───────────────
        header_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=32
        )
        date_label = Label(
            text=date_fmt,
            font_name="Nanum",
            font_size=15,
            bold=True,
            color=(0, 0, 0, 1),
            halign="left"
        )
        date_label.bind(
            size=lambda i, v: setattr(i, 'text_size', v))

        percent_label = Label(
            text=f"{percent}%",
            font_name="Nanum",
            font_size=18,
            bold=True,
            color=percent_color,
            halign="right",
            size_hint_x=None,
            width=60
        )
        percent_label.bind(
            size=lambda i, v: setattr(i, 'text_size', v))

        header_row.add_widget(date_label)
        header_row.add_widget(percent_label)

        # ── 중간: 학습 통계 ───────────────────
        stats_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=24,
            spacing=16
        )

        stats_items = [
            ("단어", f"{len(words)}개"),
            ("문제", f"{total_quiz}문제"),
            ("정답", f"{correct}개"),
        ]
        for lbl, val in stats_items:
            item = BoxLayout(orientation="horizontal", spacing=4)
            item.add_widget(Label(
                text=lbl,
                font_name="Nanum",
                font_size=12,
                color=(0.6, 0.6, 0.6, 1),
                size_hint_x=None,
                width=30
            ))
            item.add_widget(Label(
                text=val,
                font_name="Nanum",
                font_size=12,
                bold=True,
                color=(0.2, 0.2, 0.2, 1),
                size_hint_x=None,
                width=40
            ))
            stats_row.add_widget(item)
        stats_row.add_widget(Widget())

        # ── 정답률 바 ─────────────────────────
        bar_bg = BoxLayout(
            size_hint_y=None,
            height=8
        )
        with bar_bg.canvas.before:
            Color(0.9, 0.9, 0.9, 1)
            bar_bg_rect = RoundedRectangle(
                pos=bar_bg.pos,
                size=bar_bg.size,
                radius=[4]
            )
        bar_bg.bind(
            pos=lambda i, v: setattr(bar_bg_rect, 'pos', v),
            size=lambda i, v: setattr(bar_bg_rect, 'size', v)
        )

        bar_fill = Widget(
            size_hint_x=percent/100,
            size_hint_y=1
        )
        with bar_fill.canvas:
            Color(*percent_color)
            bar_fill_rect = RoundedRectangle(
                pos=bar_fill.pos,
                size=bar_fill.size,
                radius=[4]
            )
        bar_fill.bind(
            pos=lambda i, v: setattr(bar_fill_rect, 'pos', v),
            size=lambda i, v: setattr(bar_fill_rect, 'size', v)
        )
        bar_bg.add_widget(bar_fill)

        # ── 단어 목록 (최대 5개 미리보기) ──────
        word_preview = ", ".join(words[:5])
        if len(words) > 5:
            word_preview += f" 외 {len(words)-5}개"

        word_label = Label(
            text=word_preview,
            font_name="NotoJP",
            font_size=12,
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=22,
            halign="left",
            text_size=(None, None)
        )
        word_label.bind(
            size=lambda i, v: setattr(i, 'text_size', (v[0], None)))

        card.add_widget(header_row)
        card.add_widget(stats_row)
        card.add_widget(bar_bg)
        card.add_widget(word_label)

        return card

    # ── 기록 불러오기 (로컬 + 서버) ──────────
    def _load_records(self):
        # 서버 로그인 상태면 서버에서, 아니면 로컬에서
        if api.is_logged_in() and api._token != "offline":
            server_records = api.get_records()
            if server_records:
                return server_records

        # 로컬 기록 사용
        local = get_history()
        # 최신순 정렬
        return sorted(local, key=lambda x: x.get("date", ""),
                      reverse=True)

    def go_back(self, instance):
        self.manager.current = "home"