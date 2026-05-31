# stats.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from datetime import date, timedelta
from storage import get_history
from words import WORDS
import api

class StatsScreen(Screen):

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

    def _load_records(self):
        if api.is_logged_in() and api._token != "offline":
            server = api.get_records()
            if server:
                return server
        return sorted(
            get_history(),
            key=lambda x: x.get("date", ""),
            reverse=True
        )

    def _build(self):
        records = self._load_records()

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
            text="←", font_size=20,
            size_hint_x=None, width=50,
            background_color=(0.95, 0.95, 0.93, 1),
            color=(0, 0, 0, 1)
        )
        back_btn.bind(on_press=self.go_back)
        title = Label(
            text="학습 통계",
            font_name="Nanum", font_size=20, bold=True,
            color=(0, 0, 0, 1), halign="center"
        )
        title.bind(size=lambda i, v: setattr(i, 'text_size', v))
        spacer = Widget(size_hint_x=None, width=50)
        top_bar.add_widget(back_btn)
        top_bar.add_widget(title)
        top_bar.add_widget(spacer)

        # ── 스크롤 영역 ───────────────────────
        scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=0
        )
        content = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=12,
            padding=[0, 4, 0, 4]
        )
        content.bind(minimum_height=content.setter("height"))

        # ── 전체 요약 카드 ────────────────────
        content.add_widget(self._build_summary(records))

        # ── 주간 정답률 그래프 ────────────────
        content.add_widget(self._build_weekly_chart(records))

        # ── 연속 학습 스트릭 ──────────────────
        content.add_widget(self._build_streak(records))

        # ── 레벨별 학습 현황 ──────────────────
        content.add_widget(self._build_level_stats(records))

        # ── 요일별 학습 패턴 ──────────────────
        content.add_widget(self._build_weekday_pattern(records))

        scroll.add_widget(content)

        bg.add_widget(top_bar)
        bg.add_widget(scroll)

        root.add_widget(bg)
        self.add_widget(root)

    # ── 1. 전체 요약 ──────────────────────────
    def _build_summary(self, records):
        card = BoxLayout(
            orientation="vertical",
            size_hint_y=None, height=130,
            padding=[18, 14, 18, 14], spacing=8
        )
        self._make_card(card)

        title = Label(
            text="전체 요약",
            font_name="Nanum", font_size=13,
            color=(0.6, 0.6, 0.6, 1),
            size_hint_y=None, height=20, halign="left"
        )
        title.bind(size=lambda i, v: setattr(i, 'text_size', v))

        stats_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=70
        )

        total_days    = len(records)
        total_words   = sum(len(r.get("words", [])) for r in records)
        total_correct = sum(r.get("correct", 0) for r in records)
        total_quiz    = sum(r.get("total_quiz", 0) for r in records)
        avg_percent   = int(total_correct / total_quiz * 100) \
                        if total_quiz else 0

        # 최장 스트릭 계산
        max_streak = self._calc_max_streak(records)

        items = [
            ("📅", f"{total_days}일", "총 학습일"),
            ("📖", f"{total_words}개", "총 단어"),
            ("✓",  f"{avg_percent}%", "평균 정답률"),
            ("🔥", f"{max_streak}일", "최장 연속"),
        ]
        for icon, val, lbl in items:
            col = BoxLayout(orientation="vertical", spacing=2)
            col.add_widget(Label(
                text=val,
                font_name="Nanum", font_size=18, bold=True,
                color=(0, 0, 0, 1), halign="center"
            ))
            col.add_widget(Label(
                text=lbl,
                font_name="Nanum", font_size=10,
                color=(0.6, 0.6, 0.6, 1), halign="center"
            ))
            stats_row.add_widget(col)

        card.add_widget(title)
        card.add_widget(stats_row)
        return card

    # ── 2. 주간 정답률 막대 그래프 ───────────
    def _build_weekly_chart(self, records):
        card = BoxLayout(
            orientation="vertical",
            size_hint_y=None, height=200,
            padding=[18, 14, 18, 14], spacing=8
        )
        self._make_card(card)

        title = Label(
            text="최근 7일 정답률",
            font_name="Nanum", font_size=13,
            color=(0.6, 0.6, 0.6, 1),
            size_hint_y=None, height=20, halign="left"
        )
        title.bind(size=lambda i, v: setattr(i, 'text_size', v))

        # 날짜별 정답률 계산
        today     = date.today()
        date_map  = {r["date"]: r for r in records}
        week_data = []
        day_names = ["일", "월", "화", "수", "목", "금", "토"]

        for i in range(6, -1, -1):
            d       = today - timedelta(days=i)
            rec     = date_map.get(str(d))
            percent = 0
            if rec and rec.get("total_quiz", 0) > 0:
                percent = int(
                    rec["correct"] / rec["total_quiz"] * 100)
            week_data.append({
                "day"    : day_names[d.weekday()],  # 파이썬 weekday 0=월
                "date"   : str(d),
                "percent": percent,
                "is_today": (d == today)
            })

        # 그래프 영역
        chart = BoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=130,
            spacing=6
        )

        for item in week_data:
            col = BoxLayout(orientation="vertical", spacing=4)

            # 막대 + 퍼센트
            bar_area = BoxLayout(
                orientation="vertical",
                spacing=2
            )

            # 퍼센트 숫자
            pct_label = Label(
                text=f"{item['percent']}%" if item['percent'] > 0 else "-",
                font_name="Nanum", font_size=10,
                color=(0.4, 0.4, 0.4, 1),
                size_hint_y=None, height=16,
                halign="center"
            )
            pct_label.bind(
                size=lambda i, v: setattr(i, 'text_size', v))

            # 막대 배경
            bar_bg = Widget()
            bar_color = (0.18, 0.7, 0.35, 1) if item['percent'] >= 80 \
                        else (0.95, 0.6, 0.1, 1) if item['percent'] >= 60 \
                        else (0.85, 0.85, 0.85, 1) if item['percent'] == 0 \
                        else (0.85, 0.2, 0.2, 1)

            # 오늘 강조
            if item['is_today']:
                bar_color_bg = (0.9, 0.9, 0.9, 1)
            else:
                bar_color_bg = (0.93, 0.93, 0.93, 1)

            pct = item['percent'] / 100

            _pct = pct
            _fg  = bar_color
            _bg  = bar_color_bg
            def draw_bar(w, val, pct=_pct, fg=_fg, bg=_bg):
                w.canvas.clear()
                with w.canvas:
                    Color(*bg)
                    RoundedRectangle(
                        pos=w.pos, size=w.size, radius=[4])
                    if pct > 0:
                        Color(*fg)
                        fill_h = w.size[1] * pct
                        RoundedRectangle(
                            pos=(w.x, w.y),
                            size=(w.width, fill_h),
                            radius=[4]
                        )

            bar_bg.bind(pos=draw_bar, size=draw_bar)

            bar_area.add_widget(pct_label)
            bar_area.add_widget(bar_bg)

            # 요일 라벨
            day_lbl = Label(
                text=item['day'],
                font_name="Nanum",
                font_size=12,
                bold=item['is_today'],
                color=(0.1, 0.1, 0.1, 1) if item['is_today']
                      else (0.5, 0.5, 0.5, 1),
                size_hint_y=None, height=18,
                halign="center"
            )
            day_lbl.bind(
                size=lambda i, v: setattr(i, 'text_size', v))

            col.add_widget(bar_area)
            col.add_widget(day_lbl)
            chart.add_widget(col)

        card.add_widget(title)
        card.add_widget(chart)
        return card

    # ── 3. 연속 학습 스트릭 ───────────────────
    def _build_streak(self, records):
        card = BoxLayout(
            orientation="vertical",
            size_hint_y=None, height=110,
            padding=[18, 14, 18, 14], spacing=8
        )
        self._make_card(card)

        title = Label(
            text="연속 학습",
            font_name="Nanum", font_size=13,
            color=(0.6, 0.6, 0.6, 1),
            size_hint_y=None, height=20, halign="left"
        )
        title.bind(size=lambda i, v: setattr(i, 'text_size', v))

        cur_streak = self._calc_current_streak(records)
        max_streak = self._calc_max_streak(records)

        row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=54
        )

        # 현재 스트릭
        cur_box = BoxLayout(orientation="vertical", spacing=2)
        cur_box.add_widget(Label(
            text=f"🔥 {cur_streak}일",
            font_name="Nanum", font_size=22, bold=True,
            color=(0.95, 0.5, 0.1, 1), halign="center"
        ))
        cur_box.add_widget(Label(
            text="현재 연속",
            font_name="Nanum", font_size=11,
            color=(0.6, 0.6, 0.6, 1), halign="center"
        ))

        # 구분선
        divider = Widget(size_hint_x=None, width=1)
        with divider.canvas:
            Color(0.9, 0.9, 0.9, 1)
            Rectangle(pos=divider.pos, size=divider.size)
        divider.bind(
            pos=lambda i, v: Rectangle(pos=v, size=i.size),
            size=lambda i, v: Rectangle(pos=i.pos, size=v)
        )

        # 최장 스트릭
        max_box = BoxLayout(orientation="vertical", spacing=2)
        max_box.add_widget(Label(
            text=f"🏆 {max_streak}일",
            font_name="Nanum", font_size=22, bold=True,
            color=(0.2, 0.2, 0.2, 1), halign="center"
        ))
        max_box.add_widget(Label(
            text="최장 연속",
            font_name="Nanum", font_size=11,
            color=(0.6, 0.6, 0.6, 1), halign="center"
        ))

        # 오늘 학습 여부 안내
        today        = str(date.today())
        studied_today = any(r["date"] == today for r in records)
        status_text  = "✅ 오늘 학습 완료!" if studied_today \
                       else "⚠️ 오늘 아직 학습 안 했어요"
        status_color = (0.18, 0.7, 0.35, 1) if studied_today \
                       else (0.85, 0.4, 0.1, 1)

        row.add_widget(cur_box)
        row.add_widget(Widget(size_hint_x=None, width=16))
        row.add_widget(max_box)

        status_lbl = Label(
            text=status_text,
            font_name="Nanum", font_size=12,
            color=status_color,
            size_hint_y=None, height=0,   # 공간 없으면 숨김
            halign="center"
        )

        card.add_widget(title)
        card.add_widget(row)
        return card

    # ── 4. 레벨별 학습 현황 ───────────────────
    def _build_level_stats(self, records):
        card = BoxLayout(
            orientation="vertical",
            size_hint_y=None, height=220,
            padding=[18, 14, 18, 14], spacing=10
        )
        self._make_card(card)

        title = Label(
            text="레벨별 학습 현황",
            font_name="Nanum", font_size=13,
            color=(0.6, 0.6, 0.6, 1),
            size_hint_y=None, height=20, halign="left"
        )
        title.bind(size=lambda i, v: setattr(i, 'text_size', v))

        # 전체 단어에서 레벨별 총 단어 수
        level_total = {}
        for w in WORDS:
            lv = w.get("level", "?")
            level_total[lv] = level_total.get(lv, 0) + 1

        # 학습한 단어 (기록에 나온 단어)
        learned_words = set()
        for r in records:
            for w in r.get("words", []):
                learned_words.add(w)

        # 단어별 레벨 매핑
        word_level = {w["japanese"]: w.get("level", "?") for w in WORDS}

        level_learned = {}
        for w in learned_words:
            lv = word_level.get(w, "?")
            level_learned[lv] = level_learned.get(lv, 0) + 1

        # 레벨 순서
        levels = ["N5", "N4", "N3", "N2", "N1"]
        level_colors = {
            "N5": (0.18, 0.7, 0.35, 1),
            "N4": (0.2, 0.6, 0.9, 1),
            "N3": (0.7, 0.3, 0.9, 1),
            "N2": (0.95, 0.6, 0.1, 1),
            "N1": (0.85, 0.2, 0.2, 1),
        }

        bars_layout = BoxLayout(
            orientation="vertical",
            spacing=8
        )

        for lv in levels:
            total   = level_total.get(lv, 0)
            learned = level_learned.get(lv, 0)
            if total == 0:
                continue

            pct = learned / total

            row = BoxLayout(
                orientation="horizontal",
                size_hint_y=None, height=28,
                spacing=8
            )

            # 레벨 라벨
            lv_lbl = Label(
                text=lv,
                font_name="Nanum", font_size=13, bold=True,
                color=level_colors.get(lv, (0.3, 0.3, 0.3, 1)),
                size_hint_x=None, width=36,
                halign="left"
            )
            lv_lbl.bind(
                size=lambda i, v: setattr(i, 'text_size', v))

            # 막대 배경
            bar_bg = Widget()
            fg = level_colors.get(lv, (0.5, 0.5, 0.5, 1))

            _pct2 = pct
            _fg2  = fg
            def draw(w, val, pct=_pct2, fg=_fg2):
                w.canvas.clear()
                with w.canvas:
                    Color(0.9, 0.9, 0.9, 1)
                    RoundedRectangle(
                        pos=w.pos, size=w.size, radius=[5])
                    if pct > 0:
                        Color(*fg)
                        RoundedRectangle(
                            pos=w.pos,
                            size=(w.width * pct, w.height),
                            radius=[5]
                        )

            bar_bg.bind(pos=draw, size=draw)

            # 숫자
            num_lbl = Label(
                text=f"{learned}/{total}",
                font_name="Nanum", font_size=12,
                color=(0.4, 0.4, 0.4, 1),
                size_hint_x=None, width=50,
                halign="right"
            )
            num_lbl.bind(
                size=lambda i, v: setattr(i, 'text_size', v))

            row.add_widget(lv_lbl)
            row.add_widget(bar_bg)
            row.add_widget(num_lbl)
            bars_layout.add_widget(row)

        card.add_widget(title)
        card.add_widget(bars_layout)
        return card

    # ── 5. 요일별 학습 패턴 ───────────────────
    def _build_weekday_pattern(self, records):
        card = BoxLayout(
            orientation="vertical",
            size_hint_y=None, height=160,
            padding=[18, 14, 18, 14], spacing=10
        )
        self._make_card(card)

        title = Label(
            text="요일별 학습 패턴",
            font_name="Nanum", font_size=13,
            color=(0.6, 0.6, 0.6, 1),
            size_hint_y=None, height=20, halign="left"
        )
        title.bind(size=lambda i, v: setattr(i, 'text_size', v))

        # 요일별 학습 횟수 집계
        day_count  = [0] * 7   # 0=월 ~ 6=일
        day_names  = ["월", "화", "수", "목", "금", "토", "일"]

        for r in records:
            try:
                y, m, d  = r["date"].split("-")
                d_obj    = date(int(y), int(m), int(d))
                day_count[d_obj.weekday()] += 1
            except Exception:
                pass

        max_count = max(day_count) if any(day_count) else 1

        chart = BoxLayout(
            orientation="horizontal",
            spacing=6
        )

        for i, (cnt, name) in enumerate(zip(day_count, day_names)):
            col = BoxLayout(orientation="vertical", spacing=4)
            pct = cnt / max_count if max_count > 0 else 0

            # 주말 색상 다르게
            if i >= 5:
                bar_color = (0.85, 0.2, 0.2, 0.7)
            else:
                bar_color = (0.2, 0.5, 0.9, 0.8)

            bar = Widget()

            _pct3   = pct
            _color3 = bar_color
            def draw_bar(w, val, pct=_pct3, color=_color3):
                w.canvas.clear()
                with w.canvas:
                    Color(0.92, 0.92, 0.92, 1)
                    RoundedRectangle(
                        pos=w.pos, size=w.size, radius=[4])
                    if pct > 0:
                        Color(*color)
                        fill_h = w.size[1] * pct
                        RoundedRectangle(
                            pos=(w.x, w.y),
                            size=(w.width, fill_h),
                            radius=[4]
                        )

            bar.bind(pos=draw_bar, size=draw_bar)

            cnt_lbl = Label(
                text=str(cnt) if cnt > 0 else "",
                font_name="Nanum", font_size=10,
                color=(0.4, 0.4, 0.4, 1),
                size_hint_y=None, height=16,
                halign="center"
            )
            cnt_lbl.bind(
                size=lambda i, v: setattr(i, 'text_size', v))

            day_lbl = Label(
                text=name,
                font_name="Nanum", font_size=12,
                color=(0.85, 0.2, 0.2, 1) if i >= 5
                      else (0.3, 0.3, 0.3, 1),
                size_hint_y=None, height=18,
                halign="center"
            )
            day_lbl.bind(
                size=lambda i, v: setattr(i, 'text_size', v))

            col.add_widget(cnt_lbl)
            col.add_widget(bar)
            col.add_widget(day_lbl)
            chart.add_widget(col)

        card.add_widget(title)
        card.add_widget(chart)
        return card

    # ── 스트릭 계산 ───────────────────────────
    def _calc_current_streak(self, records):
        if not records:
            return 0
        studied = sorted(
            {r["date"] for r in records}, reverse=True)
        streak   = 0
        check    = date.today()
        for d_str in studied:
            try:
                y, m, d = d_str.split("-")
                d_obj   = date(int(y), int(m), int(d))
            except Exception:
                continue
            if d_obj == check:
                streak += 1
                check  = check - timedelta(days=1)
            elif d_obj == check - timedelta(days=1):
                # 어제까지는 ok
                check = d_obj - timedelta(days=1)
                streak += 1
            else:
                break
        return streak

    def _calc_max_streak(self, records):
        if not records:
            return 0
        studied  = sorted({r["date"] for r in records})
        max_s    = 1
        cur_s    = 1
        for i in range(1, len(studied)):
            try:
                prev = date(*[int(x) for x in studied[i-1].split("-")])
                curr = date(*[int(x) for x in studied[i].split("-")])
                if (curr - prev).days == 1:
                    cur_s += 1
                    max_s  = max(max_s, cur_s)
                else:
                    cur_s = 1
            except Exception:
                pass
        return max_s

    def go_back(self, instance):
        self.manager.current = "home"