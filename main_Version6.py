from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.properties import ObjectProperty

# AdMob Setup
try:
    from jnius import autoclass
    PythonJavaClass = autoclass('org.kivy.android.PythonJavaClass')
    PythonService = autoclass('org.kivy.android.PythonService')
    
    MobileAds = autoclass('com.google.android.gms.ads.MobileAds')
    AdRequest = autoclass('com.google.android.gms.ads.AdRequest')
    InterstitialAd = autoclass('com.google.android.gms.ads.interstitial.InterstitialAd')
    AdView = autoclass('com.google.android.gms.ads.AdView')
    AdSize = autoclass('com.google.android.gms.ads.AdSize')
    
    ADMOB_AVAILABLE = True
except:
    ADMOB_AVAILABLE = False

from snake_game import SnakeGame

# Set window size after imports
if Window:
    Window.size = (400, 700)
    Window.bind(on_request_close=lambda w: True)

# AdMob IDs (REPLACE WITH YOUR OWN!)
ADMOB_APP_ID = "ca-app-pub-3940256099942544~3347511713"
ADMOB_BANNER_ID = "ca-app-pub-3940256099942544/6300978111"
ADMOB_INTERSTITIAL_ID = "ca-app-pub-3940256099942544/1033173712"
ADMOB_REWARDED_ID = "ca-app-pub-3940256099942544/5224354917"

class AdMobHelper:
    """Helper class for AdMob integration"""
    
    def __init__(self):
        self.banner_ad = None
        self.interstitial_ad = None
        self.rewarded_ad = None
        self.is_rewarded = False
        
        if ADMOB_AVAILABLE:
            self._init_admob()
    
    def _init_admob(self):
        """Initialize AdMob"""
        try:
            MobileAds.initialize(PythonService.mActivity)
        except:
            pass
    
    def show_interstitial(self):
        """Show interstitial ad (full screen)"""
        if not ADMOB_AVAILABLE:
            return
        
        try:
            print("[AdMob] Showing Interstitial Ad")
        except:
            pass
    
    def show_rewarded(self):
        """Show rewarded video ad"""
        if not ADMOB_AVAILABLE:
            return
        
        try:
            self.is_rewarded = True
            print("[AdMob] Showing Rewarded Ad")
        except:
            pass

class GameScreen(FloatLayout):
    def __init__(self, mode, ad_helper, **kwargs):
        super().__init__(**kwargs)
        self.mode = mode
        self.ad_helper = ad_helper
        self.snake_game = SnakeGame(mode=mode, ad_helper=ad_helper)
        self.add_widget(self.snake_game)
        
        # HUD
        self.hud = BoxLayout(orientation='vertical', size_hint=(1, 0.12), pos_hint={'x': 0, 'top': 1})
        with self.hud.canvas.before:
            Color(0.02, 0.02, 0.04, 0.9)
            self.hud_bg = Rectangle(size=self.hud.size, pos=self.hud.pos)
        
        self.hud.bind(pos=self._update_hud_bg, size=self._update_hud_bg)
        
        hud_content = BoxLayout(spacing=10, padding=5)
        
        self.score_label = Label(text='SCORE: 0', font_size='14sp', bold=True, color=(1, 0.5, 0, 1), size_hint_x=0.6)
        self.meme_label = Label(text='🧠 OK', font_size='11sp', color=(0, 1, 0, 1), size_hint_x=0.4)
        
        hud_content.add_widget(self.score_label)
        hud_content.add_widget(self.meme_label)
        
        self.hud.add_widget(hud_content)
        self.add_widget(self.hud)
        
        Clock.schedule_interval(self._update_hud, 0.2)
    
    def _update_hud_bg(self, *args):
        self.hud_bg.pos = self.hud.pos
        self.hud_bg.size = self.hud.size
    
    def _update_hud(self, dt):
        self.score_label.text = f'SCORE: {self.snake_game.score}'
        self.meme_label.text = self.snake_game.get_brain_status()

class MenuScreen(FloatLayout):
    def __init__(self, app, ad_helper, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.ad_helper = ad_helper
        
        with self.canvas.before:
            Color(0.05, 0.05, 0.08)
            Rectangle(size=self.size, pos=self.pos)
        
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=15)
        
        # Title
        title = Label(
            text='[b]BRAINROT[/b]\n[i]SNAKE[/i]',
            markup=True,
            font_size='48sp',
            color=(1, 0.5, 0, 1),
            size_hint_y=0.2
        )
        main_layout.add_widget(title)
        
        # Buttons
        button_box = GridLayout(cols=1, spacing=8, size_hint_y=0.65)
        
        modes = [
            ("🎮 CLASSIC", "CLASSIC"),
            ("⏱️ TIME ATTACK", "TIME_ATTACK"),
            ("🌀 CHAOS", "CHAOS"),
            ("🎯 SURVIVAL", "SURVIVAL"),
        ]
        
        for text, mode in modes:
            btn = Button(
                text=text,
                font_size='18sp',
                background_color=(0.2, 0.3, 0.5, 1)
            )
            btn.bind(on_press=lambda x, m=mode: self.start_game(m))
            button_box.add_widget(btn)
        
        main_layout.add_widget(button_box)
        
        # Ad button
        ad_btn = Button(
            text='▶️ WATCH AD FOR +500 POINTS',
            font_size='14sp',
            background_color=(0.3, 0.2, 0.5, 1),
            size_hint_y=0.1
        )
        ad_btn.bind(on_press=self.watch_rewarded_ad)
        main_layout.add_widget(ad_btn)
        
        self.add_widget(main_layout)
    
    def start_game(self, mode):
        # Show interstitial ad before game
        self.ad_helper.show_interstitial()
        
        self.app.root.clear_widgets()
        self.app.root.add_widget(GameScreen(mode=mode, ad_helper=self.ad_helper))
    
    def watch_rewarded_ad(self, instance):
        """Watch rewarded video ad"""
        self.ad_helper.show_rewarded()
        if self.ad_helper.is_rewarded:
            print("[Game] +500 Points Granted!")

class BrainrotSnakeApp(App):
    title = 'Brainrot Snake'
    icon = 'data/icon.png'
    
    def build(self):
        self.ad_helper = AdMobHelper()
        
        root = FloatLayout()
        root.add_widget(MenuScreen(app=self, ad_helper=self.ad_helper))
        return root
    
    def on_pause(self):
        return True
    
    def on_resume(self):
        pass



if __name__ == '__main__':
    BrainrotSnakeApp().run()