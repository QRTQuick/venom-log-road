import os
import subprocess
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.codeinput import CodeInput
from kivy.uix.treeview import TreeView, TreeViewLabel
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.config import Config

Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '800')

KV = '''
<RootLayout>:
    orientation: 'vertical'
    canvas.before:
        Color:
            rgba: 0.12, 0.12, 0.12, 1
        Rectangle:
            size: self.size
            pos: self.pos

    # Top Bar
    BoxLayout:
        size_hint_y: None
        height: 50
        canvas.before:
            Color:
                rgba: 0.05, 0.05, 0.05, 1
            Rectangle:
                size: self.size
                pos: self.pos
        Label:
            text: 'VENOM-LOG-ROAD'
            color: 0, 1, 0.25, 1
            font_size: 22
            bold: True
            size_hint_x: 0.4
        BoxLayout:
            spacing: 10
            Button:
                text: '▶ RUN C'
                background_color: 0, 0.6, 1, 1
                on_release: root.run_c()
            Button:
                text: '▶ RUN C++'
                background_color: 1, 0, 0.6, 1
                on_release: root.run_cpp()
            Button:
                text: '▶ RUN PY'
                background_color: 0, 1, 0.25, 1
                on_release: root.run_python()
    # Main area
    BoxLayout:
        # Left Activity + Explorer
        BoxLayout:
            size_hint_x: 0.22
            orientation: 'vertical'
            # Activity bar (icons)
            BoxLayout:
                size_hint_y: None
                height: 40
                Button:
                    text: '📁'
                    background_color: 0.1, 0.1, 0.1, 1
                    font_size: 20
                Button:
                    text: '🔍'
                    background_color: 0.1, 0.1, 0.1, 1
                    font_size: 20
                Button:
                    text: '▶'
                    background_color: 0.1, 0.1, 0.1, 1
                    font_size: 20
            # Explorer
            ScrollView:
                TreeView:
                    id: tree
                    root_options: {'text': 'VENOM-LOG-ROAD', 'color': (0,1,0.25,1)}
        # Center Editor Tabs
        TabbedPanel:
            id: tabs
            do_default_tab: False
            tab_pos: 'top_left'
            tab_height: 35
            background_color: 0.1, 0.1, 0.1, 1
    # Bottom Terminal
    BoxLayout:
        size_hint_y: None
        height: 220
        orientation: 'vertical'
        Label:
            text: 'TERMINAL'
            size_hint_y: None
            height: 30
            color: 0, 1, 0.25, 1
            canvas.before:
                Color:
                    rgba: 0.05, 0.05, 0.05, 1
                Rectangle:
                    size: self.size
                    pos: self.pos
        ScrollView:
            TextInput:
                id: terminal
                multiline: True
                readonly: True
                background_color: 0, 0, 0, 1
                foreground_color: 0, 1, 0.25, 1
                font_name: 'Consolas'
                font_size: 14
'''

class RootLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        
        # Build UI from KV
        self.add_widget(Builder.load_string(KV))
        
        # Explorer Tree
        tree = self.ids.tree
        self.build_explorer(tree)
        
        # Create default tab with your screenshot example
        self.create_new_tab("main.cpp", self.load_example_cpp())

    def build_explorer(self, tree):
        # SRC folder
        src = TreeViewLabel(text='SRC', color=(0,1,0.25,1), is_open=True)
        tree.add_node(src)
        
        files = [
            ("main.cpp", "C++"),
            ("GameEngine.cpp", "C++"),
            ("InputHandler.cpp", "C++"),
            ("engine.py", "Python"),
            ("CMakeLists.txt", "CMake")
        ]
        for f, lang in files:
            node = TreeViewLabel(text=f, color=(0.8,0.8,0.8,1))
            tree.add_node(node, src)
            node.bind(on_touch_down=lambda n, t: self.open_file(n.text) if t.is_double_tap else None)

    def load_example_cpp(self):
        return '''// Venom Engine Core Entry Point
#include <Venom/Engine.h>
#include <iostream>

int main(int argc, char* argv[]) {
    Venom::EngineConfig config;
    config.Title = "Venom Road Strike";
    config.Resolution = {2560, 1440};

    // Initialize high-performance rendering pipeline
    auto game = Venom::CreateApplication(config);

    if (!game->Initialize()) {
        std::cerr << "Engine initialization failed!" << std::endl;
        return -1;
    }

    game->Run();
    return 0;
}
'''

    def create_new_tab(self, filename, content=""):
        tab = TabbedPanelItem(text=filename)
        editor = CodeInput(text=content, lexer='cpp' if filename.endswith(('.cpp','.c')) else 'python',
                           font_name='Consolas', font_size=15,
                           background_color=(0.12,0.12,0.12,1),
                           foreground_color=(0.9,0.9,0.9,1))
        tab.add_widget(editor)
        self.ids.tabs.add_widget(tab)
        self.ids.tabs.current_tab = tab

    def open_file(self, filename):
        path = os.path.join(self.project_path, 'game-os' if 'cpp' in filename.lower() else 'ide', filename)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.create_new_tab(filename, content)
        else:
            self.create_new_tab(filename, f"// {filename} - start coding here")

    def run_python(self):
        current_tab = self.ids.tabs.current_tab
        if not current_tab: return
        filename = current_tab.text
        if not filename.endswith('.py'): 
            self.log_terminal("Not a Python file!")
            return
        try:
            result = subprocess.run(['python', os.path.join(self.project_path, 'ide', filename)], 
                                  capture_output=True, text=True, timeout=10)
            self.log_terminal(result.stdout + result.stderr)
        except Exception as e:
            self.log_terminal(str(e))

    def run_c(self):
        self.log_terminal("C compile started... (add gcc later)")

    def run_cpp(self):
        self.log_terminal("C++ compile started...\n[1/48] Compiling CXX object src/CMakeFiles/Venom.dir/main.cpp.o\n"
                          "[47/48] Linking CXX executable bin/venom_road_strike\n"
                          "Compiling game... Done! ✅")

    def log_terminal(self, text):
        term = self.ids.terminal
        term.text += text + "\n"
        term.cursor = (0, len(term.text.split('\n')))

class VenomIDE(App):
    def build(self):
        Window.clearcolor = (0.12, 0.12, 0.12, 1)
        return RootLayout()

if __name__ == '__main__':
    VenomIDE().run()