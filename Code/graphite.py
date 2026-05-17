import os
import gi
import shelve
import requests
import threading
from translate import translate
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk

RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"
NAME = "GRAPHITE"
LANG= None

PATH = os.path.dirname(__file__)

API_KEY = None
URL = None

SYSTEM_PROMPT = '''
    You are a quick assistant for a desktop launcher.
    Structure every answer like this:

    <b>What:</b> [Brief definition/explanation] \n
    <b>Why:</b> [Reason or context] \n
    <b>How:</b> [Process or usage] \n

    Use <b> for section headers. Keep each section 1 sentences max.
    Use <tt> for code or monospace code. 
    No other text. Just these three sections.
    '''


GEMINI_ERRORS = {
    200: "Success",
    400: "Bad request — check your payload or model name.",
    401: "Invalid API key.",
    403: "Invalid API key.",
    429: "Rate limit reached — try again shortly.",
    500: "Gemini internal error — try again.",
    503: "Gemini is overloaded — try again later.",
}

def show_error_log(text):
    print(f'[{GREEN}{NAME}{RESET}] {RED}LOG: {RESET}{text}')

def show_success_log(text):
    print(f'[{GREEN}{NAME}{RESET}] {GREEN}LOG: {RESET}{text}')

class db:

    @staticmethod
    def get(key):
        with shelve.open('config.db') as f:
            return f.get(key)
        
    @staticmethod
    def add(key, data):
        with shelve.open('config.db') as f:
            f[key] = str(data)
            return True


class MAIN_APP(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='com.carbon.graphite')
        self.mode = True # True for Q/A and False for Translation
        self.query = None
        self.is_visible = False

    def do_activate(self):
        styler = Gtk.CssProvider()
        styler.load_from_path(PATH+"/style.css")
        display = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(display, styler, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.window = Gtk.Window(application=self)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.set_decorated(False)
        self.window.set_resizable(False)

        self.body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.query_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=180)

        self.label = Gtk.Label(label=NAME)
        self.log_label = Gtk.Label(label='')

        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text('Type')

        self.label.set_halign(Gtk.Align.START)
        self.log_label.set_halign(Gtk.Align.END)

        self.header_box.pack_start(self.label, True, True, 0)
        self.header_box.pack_end(self.log_label, False, False, 0)
        self.query_box.pack_start(self.header_box, True, False, 0)
        self.query_box.pack_start(self.entry, True, False, 0)

        self.answer_box = Gtk.ScrolledWindow()
        self.answer_box.set_propagate_natural_width(True)
        self.answer_box.set_propagate_natural_height(True)
        self.answer_box.set_max_content_width(200)
        self.answer_box.set_max_content_height(600)
        self.answer_box.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.answer_label = Gtk.Label(label='Answer goes here')
        self.answer_label.set_line_wrap(True)      
        self.answer_label.set_max_width_chars(60)

        self.answer_box.add(self.answer_label)

        self.loading_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        self.spinner = Gtk.Spinner()
        self.spinner.set_size_request(22, 22)

        self.loading_label = Gtk.Label(label='Wait a moment!')

        self.spinner.set_halign(Gtk.Align.CENTER)
        self.loading_label.set_halign(Gtk.Align.CENTER)
        self.loading_box.set_halign(Gtk.Align.CENTER)
        
        self.loading_box.pack_start(self.spinner, False, True, 0)
        self.loading_box.pack_start(self.loading_label, False, True, 0)

        self.options_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        self.options_box.set_halign(Gtk.Align.END)

        self.google_it_bt = Gtk.Button(label='G')
        self.copy_response_bt = Gtk.Button.new_from_icon_name('edit-copy-symbolic', Gtk.IconSize.BUTTON)

        self.options_box.pack_end(self.copy_response_bt, True, False, 0)
        self.options_box.pack_end(self.google_it_bt, True, False, 0)

        self.window.add_events(Gdk.EventMask.KEY_PRESS_MASK)
        self.window.connect('destroy', self.kill)
        self.window.connect('key-press-event', self.on_key_press)
        self.entry.connect('activate', self.handle_query)
        self.google_it_bt.connect('clicked', self.google_it)
        self.copy_response_bt.connect('clicked', self.paste_text)

        self.body.pack_start(self.query_box, False, True, 0)
        self.body.pack_start(self.answer_box, False, True, 0)
        self.body.pack_end(self.loading_box, False, True, 0)
        self.body.pack_start(self.options_box, False, True, 0)

        self.body.set_name('window')
        self.entry.set_name('query')
        self.label.set_name('logo')
        self.answer_box.set_name('answer')
        self.google_it_bt.set_name('G-of-google')
        self.copy_response_bt.set_name('copy')

        self.window.add(self.body)
        self.spinner.start()
        self.window.show_all()

        self.answer_box.set_visible(False)
        self.loading_box.set_visible(False)
        self.options_box.set_visible(False)
        self.init_vars()
        return
    
    def init_vars(self):
        global LANG
        global API_KEY
        global URL
        LANG = db.get('language')
        API_KEY = db.get('gemini-api')
        URL = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={API_KEY}'
        return
    
    def show_log(self, state, text):
        if state:
            self.log_label.set_name('success')
        
        else:
            self.log_label.set_name('error')

        self.log_label.set_text(text)
        self.log_label.set_visible(True)
        GLib.timeout_add(3000, self.hide_log_label)
        return
    
    def hide_log_label(self):
        self.log_label.hide()
        return False
    
    def on_key_press(self, widget, event):
        ctrl = event.state & Gdk.ModifierType.CONTROL_MASK
        if event.keyval == Gdk.KEY_Escape:
            self.kill()

        if ctrl and event.keyval == Gdk.KEY_q:
            self.kill()        

        if ctrl and event.keyval == Gdk.KEY_g and self.query:
            self.google_it()

        if ctrl and event.keyval == Gdk.KEY_p:
            self.paste_text()
        
        if ctrl and event.keyval == Gdk.KEY_c:
            self.hide_response()
    
    def handle_query(self, widget=None):
        text = self.entry.get_text()

        if not text and not len(text) > 3:
            return self.kill()
        self.query = text
        state = self.check_input(text)
        self.hide_response()
        if state:
            if not API_KEY and self.mode:
                    return self.show_log(False, GEMINI_ERRORS[401])
            
            self.loading_box.set_visible(True)
            self.entry.set_sensitive(False)
            if self.mode:
                threading.Thread(target=self.ask_gemini, args=(text, ), daemon=True).start()
            else:
                threading.Thread(target=self.translate_txt, args=(text, ), daemon=True).start()

        return True

    def check_input(self, text):
        key = text[0].lower()
        if key == 'l':
            self.mode = False
            self.change_language(text[2:])
            return False
        
        if key == 'k':
            self.mode = False
            self.change_key(text[2:])
            return False
        
        if key == 't':
            self.mode = False
            return True

        self.mode = True
        return True
    
    def show_response(self, response):
        self.loading_box.set_visible(False)
        self.answer_box.set_visible(True)
        self.options_box.set_visible(True)
        self.entry.set_sensitive(True)
        self.entry.grab_focus_without_selecting()
        self.answer_label.set_markup(response)
        self.is_visible = True

    def hide_response(self):
        self.loading_box.set_visible(False)
        self.answer_box.set_visible(False)
        self.options_box.set_visible(False)
        self.answer_label.set_text('')
        self.is_visible = False

    def send_request(self, query):
        try:
            payload = {
                "system_instruction": {
                    "parts": [{"text": SYSTEM_PROMPT}]
                },
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text":query}]
                    }
                ]
            }

            response = requests.post(url=URL, json=payload)
            code = response.status_code
            if code == 200:
                result = response.json()
                return result["candidates"][0]["content"]["parts"][0]["text"]
            else:
                return GEMINI_ERRORS[code] 
        except Exception as e:
            return e
    
    def ask_gemini(self, query):
        result = self.send_request(query) 
        GLib.idle_add(self.show_response, result)
        return
    
    def send_trans_request(self, query):
        try:
            language = LANG if LANG else 'ur'
            text = translate(query, 'auto', language)
            if text and len(text) > 1:
                return text
            
            return 'No output'
        
        except Exception as e:
            return str(e)

    def translate_txt(self, query):
        result = self.send_trans_request(query[1:])
        if result:
            GLib.idle_add(self.show_response, result)
        return
    
    def paste_text(self, widget=None):
        try:
            text = self.answer_label.get_text()
            if text:
                clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
                clipboard.set_text(text, -1)
                clipboard.store()
                self.show_log(True,'Copied to Clipboard')
            return True
        except Exception as e:
            show_error_log(e)
            self.show_log(False, 'Unable to Copy text')
            return True
    
    def google_it(self, widget=None):
        try:
            if self.query:
                import webbrowser
                if not self.mode:
                    self.query = f'Translate: {self.query[1:]}, into Language with code: {LANG}'
                show_success_log('Opening Browser')
                self.show_log(True, 'Searching via Google')
                webbrowser.open(f'https://www.google.com/search?q={self.query}')
            return True
        except Exception as e:
            show_error_log(e)
            self.show_log(False, 'Something went wrong')
            return True
        
    def change_key(self, data):
        if db.add('gemini-api', str(data)):
            self.entry.set_text('')
            self.init_vars()
            self.show_log(True, 'API Key Updated')
            return True
        
    def change_language(self, data):
        if db.add('language', str(data)):
            self.entry.set_text('')
            self.init_vars()
            self.show_log(True, 'Language Updated')
            return True
    
    def kill(self, widget=None):
        self.quit()

if __name__=='__main__':
    app = MAIN_APP()
    app.run()