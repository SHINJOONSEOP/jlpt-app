# tts.py
# Android/PC 공통 TTS 모듈
 
def speak(text):
    """텍스트를 음성으로 읽어줌"""
    if not text or not text.strip():
        return
 
    try:
        # Android 환경 확인
        import android
        from jnius import autoclass
 
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Locale         = autoclass('java.util.Locale')
        TextToSpeech   = autoclass('android.speech.tts.TextToSpeech')
 
        activity = PythonActivity.mActivity
        tts      = TextToSpeech(activity, None)
        tts.setLanguage(Locale('ja'))
        tts.speak(text, TextToSpeech.QUEUE_FLUSH, None, None)
 
    except Exception:
        # PC 환경 (테스트용) — 오류 무시
        try:
            import pyttsx3
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            for voice in voices:
                if 'japan' in voice.id.lower() or 'ja' in voice.id.lower():
                    engine.setProperty('voice', voice.id)
                    break
            engine.setProperty('rate', 150)
            engine.say(text)
            engine.runAndWait()
        except Exception:
            pass
 