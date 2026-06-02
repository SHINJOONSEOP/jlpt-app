# main.py
import traceback
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.text import LabelBase

# 폰트 가장 먼저 등록
try:
    LabelBase.register(name="Nanum", fn_regular="NanumGothic.ttf")
except Exception:
    pass
try:
    LabelBase.register(name="NotoJP", fn_regular="NotoSansJP-Regular.ttf")
except Exception:
    pass

class JLPTApp(App):
    def build(self):
        try:
            from login import LoginScreen
            from home import HomeScreen
            from skimming import SkimmingScreen
            from quiz import QuizScreen
            from history import HistoryScreen
            from stats import StatsScreen
            import api

            sm = ScreenManager()
            sm.add_widget(LoginScreen(name="login"))
            sm.add_widget(HomeScreen(name="home"))
            sm.add_widget(SkimmingScreen(name="skimming"))
            sm.add_widget(QuizScreen(name="quiz"))
            sm.add_widget(HistoryScreen(name="history"))
            sm.add_widget(StatsScreen(name="stats"))

            if api.try_auto_login():
                sm.current = "home"
            else:
                sm.current = "login"

            return sm

        except Exception:
            err_text = traceback.format_exc()
            scroll = ScrollView()
            lbl = Label(
                text=err_text,
                font_size=11,
                text_size=(400, None),
                size_hint_y=None,
                color=(1, 0.3, 0.3, 1)
            )
            lbl.bind(texture_size=lbl.setter('size'))
            scroll.add_widget(lbl)
            return scroll

if __name__ == "__main__":
    JLPTApp().run()