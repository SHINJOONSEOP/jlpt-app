# main.py
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from login import LoginScreen
from home import HomeScreen
from skimming import SkimmingScreen
from quiz import QuizScreen
from history import HistoryScreen
from stats import StatsScreen
import api

class JLPTApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(SkimmingScreen(name="skimming"))
        sm.add_widget(QuizScreen(name="quiz"))
        sm.add_widget(HistoryScreen(name="history"))
        sm.add_widget(StatsScreen(name="stats"))

        # ── 자동 로그인 시도 ──────────────────
        # 저장된 토큰이 있으면 홈으로 바로 이동
        if api.try_auto_login():
            sm.current = "home"
        else:
            sm.current = "login"

        return sm

if __name__ == "__main__":
    JLPTApp().run()