# tts.py
import threading
import sys
 
_is_speaking = False
 
def speak(text):
    global _is_speaking
    if not text or not text.strip():
        return
    if _is_speaking:
        return
 
    def _run():
        global _is_speaking
        _is_speaking = True
        try:
            # Android 환경에서만 실행
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
            # PC에서는 TTS 미지원 (무시)
            pass
        finally:
            _is_speaking = False
 
    threading.Thread(target=_run, daemon=True).start()
 