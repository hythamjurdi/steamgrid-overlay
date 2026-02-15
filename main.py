#!/usr/bin/env python3
"""
SteamGridDB Icon Downloader - Modern UI Version
Beautiful glassmorphism design with gradients
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.core.window import Window
from kivy.utils import platform
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.uix.widget import Widget

import json
import requests
from pathlib import Path
from PIL import Image
from io import BytesIO
from PIL import ImageDraw
import os

# Determine storage paths based on platform
if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path
    request_permissions([
        Permission.READ_EXTERNAL_STORAGE,
        Permission.WRITE_EXTERNAL_STORAGE,
        Permission.INTERNET
    ])
    STORAGE_PATH = primary_external_storage_path()
    CONFIG_FILE = os.path.join(STORAGE_PATH, 'SteamGridOverlay', 'config.json')
    DEFAULT_OUTPUT = os.path.join(STORAGE_PATH, 'SteamGridOverlay', 'Output')
    DEFAULT_OVERLAYS = os.path.join(STORAGE_PATH, 'SteamGridOverlay', 'icon_overlays')
else:
    # Desktop testing - use current directory
    SCRIPT_DIR = Path(__file__).parent.absolute() if hasattr(Path(__file__), 'parent') else Path.cwd()
    STORAGE_PATH = str(SCRIPT_DIR)
    CONFIG_FILE = SCRIPT_DIR / 'config_kivy.json'
    DEFAULT_OUTPUT = SCRIPT_DIR / 'Output'
    DEFAULT_OVERLAYS = SCRIPT_DIR / 'icon_overlays'


class ModernCard(BoxLayout):
    """Modern card with glassmorphism effect"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 15
        self.spacing = 10
        
        with self.canvas.before:
            # Subtle gradient background
            Color(0.15, 0.15, 0.18, 0.95)  # Dark translucent
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[15]
            )
        
        self.bind(pos=self.update_bg, size=self.update_bg)
    
    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size


class ModernButton(Button):
    """Sleek modern button with gradient"""
    def __init__(self, bg_color=(0.2, 0.6, 0.9, 1), **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.bold = True
        self.bg_color = bg_color
        
        with self.canvas.before:
            Color(*bg_color)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[10]
            )
        
        self.bind(pos=self.update_bg, size=self.update_bg)
    
    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size


class ModernTextInput(TextInput):
    """Modern text input with rounded corners"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_active = ''
        self.background_color = (0.2, 0.2, 0.25, 1)
        self.foreground_color = (1, 1, 1, 1)
        self.cursor_color = (0.3, 0.7, 1, 1)
        self.padding = [15, 10]
        
        with self.canvas.before:
            Color(0.2, 0.2, 0.25, 1)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[10]
            )
        
        self.bind(pos=self.update_bg, size=self.update_bg)
    
    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size


class ModernSpinner(Spinner):
    """Modern dropdown spinner"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0.25, 0.25, 0.3, 1)
        self.color = (1, 1, 1, 1)
        
        with self.canvas.before:
            Color(0.25, 0.25, 0.3, 1)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[10]
            )
        
        self.bind(pos=self.update_bg, size=self.update_bg)
    
    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size


class SteamGridOverlayApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = self.load_config()
        self.game_queue = []
        
    def build(self):
        # Dark gradient background
        Window.clearcolor = (0.08, 0.08, 0.12, 1)
        
        # Detect orientation
        is_landscape = Window.width > Window.height
        
        if is_landscape:
            # Landscape mode - two column layout
            main_layout = BoxLayout(orientation='horizontal', padding=20, spacing=15)
            
            # Left column - Settings and Add Game
            left_column = BoxLayout(orientation='vertical', spacing=15, size_hint_x=0.5)
            
            # Right column - Queue, Process, Status
            right_column = BoxLayout(orientation='vertical', spacing=15, size_hint_x=0.5)
        else:
            # Portrait mode - single column
            main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
            left_column = main_layout
            right_column = main_layout
        
        # Title with gradient effect
        title_card = BoxLayout(size_hint_y=None, height=60)
        with title_card.canvas.before:
            Color(0.2, 0.5, 0.9, 0.3)
            title_card.bg = RoundedRectangle(
                pos=title_card.pos,
                size=title_card.size,
                radius=[15]
            )
        title_card.bind(pos=lambda *x: setattr(title_card.bg, 'pos', title_card.pos),
                       size=lambda *x: setattr(title_card.bg, 'size', title_card.size))
        
        title = Label(
            text='SteamGrid Overlay',
            font_size='26sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        title_card.add_widget(title)
        
        if is_landscape:
            # Add title to left column in landscape
            left_column.add_widget(title_card)
        else:
            main_layout.add_widget(title_card)
        
        # Settings Card
        if is_landscape:
            settings_card = ModernCard(size_hint_y=0.6)
        else:
            settings_card = ModernCard(size_hint_y=None, height=350)
        
        settings_scroll = ScrollView()
        settings_layout = GridLayout(cols=1, spacing=12, size_hint_y=None)
        settings_layout.bind(minimum_height=settings_layout.setter('height'))
        
        # API Key
        api_label = Label(
            text='API Key',
            size_hint_y=None,
            height=25,
            color=(0.8, 0.8, 0.8, 1),
            font_size='14sp'
        )
        settings_layout.add_widget(api_label)
        
        self.api_key_input = ModernTextInput(
            text=self.config.get('api_key', ''),
            hint_text='Enter your SteamGridDB API key',
            multiline=False,
            size_hint_y=None,
            height=45,
            password=True
        )
        settings_layout.add_widget(self.api_key_input)
        
        # Console
        console_label = Label(
            text='Console',
            size_hint_y=None,
            height=25,
            color=(0.8, 0.8, 0.8, 1),
            font_size='14sp'
        )
        settings_layout.add_widget(console_label)
        
        self.console_spinner = ModernSpinner(
            text='Select Console',
            values=self.get_available_consoles(),
            size_hint_y=None,
            height=45
        )
        if self.config.get('selected_console'):
            self.console_spinner.text = self.config.get('selected_console')
        settings_layout.add_widget(self.console_spinner)
        
        # Overlays Folder
        overlays_label = Label(
            text='Overlays Folder',
            size_hint_y=None,
            height=25,
            color=(0.8, 0.8, 0.8, 1),
            font_size='14sp'
        )
        settings_layout.add_widget(overlays_label)
        
        overlays_box = BoxLayout(size_hint_y=None, height=45, spacing=8)
        
        self.overlays_path_input = ModernTextInput(
            text=self.config.get('overlays_folder', str(DEFAULT_OVERLAYS)),
            multiline=False
        )
        overlays_box.add_widget(self.overlays_path_input)
        
        browse_btn = ModernButton(
            text='Browse',
            size_hint_x=None,
            width=100,
            bg_color=(0.3, 0.3, 0.35, 1)
        )
        browse_btn.bind(on_press=self.browse_overlays_folder)
        overlays_box.add_widget(browse_btn)
        
        settings_layout.add_widget(overlays_box)
        
        # Action buttons
        buttons_box = BoxLayout(size_hint_y=None, height=45, spacing=8)
        
        refresh_btn = ModernButton(
            text='Refresh',
            bg_color=(0.5, 0.3, 0.8, 1)
        )
        refresh_btn.bind(on_press=self.refresh_consoles)
        buttons_box.add_widget(refresh_btn)
        
        save_btn = ModernButton(
            text='Save',
            bg_color=(0.2, 0.7, 0.4, 1)
        )
        save_btn.bind(on_press=self.save_settings)
        buttons_box.add_widget(save_btn)
        
        settings_layout.add_widget(buttons_box)
        
        settings_scroll.add_widget(settings_layout)
        settings_card.add_widget(settings_scroll)
        left_column.add_widget(settings_card)
        
        # Add Game Card
        add_game_card = ModernCard(size_hint_y=None, height=110)
        
        add_label = Label(
            text='Add Game',
            size_hint_y=None,
            height=25,
            color=(0.8, 0.8, 0.8, 1),
            font_size='14sp',
            halign='left'
        )
        add_label.bind(size=add_label.setter('text_size'))
        add_game_card.add_widget(add_label)
        
        add_box = BoxLayout(size_hint_y=None, height=45, spacing=8)
        
        self.game_name_input = ModernTextInput(
            hint_text='Enter game name',
            multiline=False
        )
        add_box.add_widget(self.game_name_input)
        
        add_btn = ModernButton(
            text='Add',
            size_hint_x=None,
            width=80,
            bg_color=(0.2, 0.6, 0.9, 1)
        )
        add_btn.bind(on_press=self.add_game)
        add_box.add_widget(add_btn)
        
        add_game_card.add_widget(add_box)
        left_column.add_widget(add_game_card)
        
        # Queue Card
        if is_landscape:
            queue_card = ModernCard(size_hint_y=0.55)
        else:
            queue_card = ModernCard(size_hint_y=0.25)
        
        queue_header = BoxLayout(size_hint_y=None, height=35, spacing=10)
        queue_label = Label(
            text='Queue',
            color=(0.8, 0.8, 0.8, 1),
            font_size='14sp',
            size_hint_x=0.7
        )
        queue_header.add_widget(queue_label)
        
        clear_btn = ModernButton(
            text='Clear',
            size_hint_x=0.3,
            bg_color=(0.7, 0.3, 0.3, 1)
        )
        clear_btn.bind(on_press=self.clear_queue)
        queue_header.add_widget(clear_btn)
        
        queue_card.add_widget(queue_header)
        
        scroll = ScrollView()
        self.queue_layout = GridLayout(cols=1, spacing=8, size_hint_y=None)
        self.queue_layout.bind(minimum_height=self.queue_layout.setter('height'))
        scroll.add_widget(self.queue_layout)
        queue_card.add_widget(scroll)
        
        right_column.add_widget(queue_card)
        
        # Process Button
        process_btn = ModernButton(
            text='Search & Process',
            size_hint_y=None,
            height=55,
            bg_color=(0.2, 0.6, 0.9, 1)
        )
        process_btn.bind(on_press=self.process_games)
        right_column.add_widget(process_btn)
        
        # Status Card
        if is_landscape:
            status_card = ModernCard(size_hint_y=None, height=150)
        else:
            status_card = ModernCard(size_hint_y=0.2)
        
        status_label = Label(
            text='Status',
            size_hint_y=None,
            height=25,
            color=(0.8, 0.8, 0.8, 1),
            font_size='14sp',
            halign='left'
        )
        status_label.bind(size=status_label.setter('text_size'))
        status_card.add_widget(status_label)
        
        log_scroll = ScrollView()
        self.log_label = Label(
            text='Ready!',
            size_hint_y=None,
            color=(0.9, 0.9, 0.9, 1),
            font_size='12sp',
            halign='left',
            valign='top'
        )
        self.log_label.bind(texture_size=self.log_label.setter('size'),
                           size=self.log_label.setter('text_size'))
        log_scroll.add_widget(self.log_label)
        status_card.add_widget(log_scroll)
        
        right_column.add_widget(status_card)
        
        # Add columns to main layout in landscape mode
        if is_landscape:
            main_layout.add_widget(left_column)
            main_layout.add_widget(right_column)
        
        return main_layout
    
    def load_config(self):
        """Load configuration"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def save_settings(self, instance):
        """Save settings"""
        self.config = {
            'api_key': self.api_key_input.text.strip(),
            'selected_console': self.console_spinner.text,
            'output_folder': str(DEFAULT_OUTPUT),
            'overlays_folder': self.overlays_path_input.text.strip()
        }
        
        try:
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=2)
            self.log('✓ Settings saved!')
            self.show_popup('Success', 'Settings saved successfully!')
        except Exception as e:
            self.log(f'❌ Error saving settings: {e}')
            self.show_popup('Error', f'Failed to save settings: {e}')
    
    def get_available_consoles(self):
        """Get list of available consoles from overlays folder"""
        try:
            if hasattr(self, 'overlays_path_input') and self.overlays_path_input.text:
                overlays_folder = Path(self.overlays_path_input.text)
            else:
                overlays_folder = Path(DEFAULT_OVERLAYS)
            
            if overlays_folder.exists():
                consoles = [
                    folder.name for folder in overlays_folder.iterdir()
                    if folder.is_dir() and (folder / 'overlay.png').exists()
                ]
                if consoles:
                    return sorted(consoles)
        except Exception as e:
            print(f"Error loading consoles: {e}")
        
        return ['No consoles found']
    
    def refresh_consoles(self, instance):
        """Refresh console list"""
        consoles = self.get_available_consoles()
        self.console_spinner.values = consoles
        if consoles and consoles[0] != 'No consoles found':
            self.console_spinner.text = consoles[0]
        self.log(f'Found {len(consoles)} consoles')
    
    def browse_overlays_folder(self, instance):
        """Show folder browser for overlays"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        filechooser = FileChooserListView(
            path=str(Path.home()),
            dirselect=True,
            filters=['']
        )
        content.add_widget(filechooser)
        
        button_box = BoxLayout(size_hint_y=None, height=50, spacing=5)
        
        select_btn = ModernButton(text='Select', bg_color=(0.2, 0.7, 0.4, 1))
        cancel_btn = ModernButton(text='Cancel', bg_color=(0.5, 0.5, 0.5, 1))
        
        button_box.add_widget(select_btn)
        button_box.add_widget(cancel_btn)
        content.add_widget(button_box)
        
        popup = Popup(
            title='Select Overlays Folder',
            content=content,
            size_hint=(0.9, 0.9)
        )
        
        def select_folder(instance):
            if filechooser.selection:
                selected_path = filechooser.selection[0]
                self.overlays_path_input.text = selected_path
                self.log(f'Selected: {selected_path}')
                self.refresh_consoles(None)
            popup.dismiss()
        
        select_btn.bind(on_press=select_folder)
        cancel_btn.bind(on_press=popup.dismiss)
        
        popup.open()
    
    def add_game(self, instance):
        """Add game to queue"""
        game_name = self.game_name_input.text.strip()
        if game_name:
            self.game_queue.append(game_name)
            
            # Create modern queue item
            game_card = BoxLayout(size_hint_y=None, height=45, spacing=8, padding=[5, 5])
            
            with game_card.canvas.before:
                Color(0.2, 0.2, 0.25, 1)
                game_card.bg = RoundedRectangle(
                    pos=game_card.pos,
                    size=game_card.size,
                    radius=[8]
                )
            game_card.bind(pos=lambda *x: setattr(game_card.bg, 'pos', game_card.pos),
                          size=lambda *x: setattr(game_card.bg, 'size', game_card.size))
            
            game_label = Label(
                text=game_name,
                color=(1, 1, 1, 1),
                size_hint_x=0.8,
                halign='left'
            )
            game_label.bind(size=game_label.setter('text_size'))
            game_card.add_widget(game_label)
            
            remove_btn = ModernButton(
                text='✕',
                size_hint_x=0.2,
                bg_color=(0.7, 0.3, 0.3, 1)
            )
            remove_btn.bind(on_press=lambda x: self.remove_game(game_card, game_name))
            game_card.add_widget(remove_btn)
            
            self.queue_layout.add_widget(game_card)
            
            self.game_name_input.text = ''
            self.log(f'Added: {game_name}')
    
    def remove_game(self, widget, game_name):
        """Remove a game from queue"""
        if game_name in self.game_queue:
            self.game_queue.remove(game_name)
        self.queue_layout.remove_widget(widget)
        self.log(f'Removed: {game_name}')
    
    def clear_queue(self, instance):
        """Clear game queue"""
        self.game_queue = []
        self.queue_layout.clear_widgets()
        self.log('Queue cleared')
    
    def log(self, message):
        """Add message to log"""
        current = self.log_label.text
        self.log_label.text = f'{current}\n{message}'
    
    def show_popup(self, title, message):
        """Show popup message"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message, color=(1, 1, 1, 1)))
        close_btn = ModernButton(text='OK', size_hint_y=None, height=50, bg_color=(0.2, 0.6, 0.9, 1))
        content.add_widget(close_btn)
        
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def process_games(self, instance):
        """Process all games in queue"""
        if not self.game_queue:
            self.show_popup('Empty Queue', 'Please add games first!')
            return
        
        if not self.api_key_input.text.strip():
            self.show_popup('No API Key', 'Please enter API key!')
            return
        
        if self.console_spinner.text in ['Select Console', 'No consoles found']:
            self.show_popup('No Console', 'Please select a console!')
            return
        
        self.log(f'\n🎮 Processing {len(self.game_queue)} games...')
        
        for i, game_name in enumerate(self.game_queue, 1):
            self.log(f'\n[{i}/{len(self.game_queue)}] {game_name}')
            self.process_single_game(game_name)
        
        self.log('\n✅ Processing complete!')
        self.show_popup('Complete', f'Processed {len(self.game_queue)} games!')
    
    def process_single_game(self, game_name):
        """Process a single game"""
        try:
            results = self.search_game(game_name)
            if not results:
                self.log(f'  ❌ Not found')
                return
            
            game = results[0]
            self.log(f'  ✓ Found: {game["name"]}')
            
            icons = self.get_game_icons(game['id'])
            if not icons:
                self.log(f'  ❌ No icons available')
                return
            
            icon = icons[0]
            self.log(f'  ⬇️ Downloading...')
            
            img = self.download_image(icon['url'])
            if not img:
                self.log(f'  ❌ Download failed')
                return
            
            result = self.apply_overlay(img)
            if not result:
                self.log(f'  ❌ Overlay failed')
                return
            
            output_dir = Path(DEFAULT_OUTPUT) / self.console_spinner.text
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f'{game["name"]}.png'
            
            result.save(output_path, 'PNG')
            self.log(f'  ✅ Saved!')
            
        except Exception as e:
            self.log(f'  ❌ Error: {e}')
    
    def search_game(self, game_name):
        """Search for game"""
        url = f"https://www.steamgriddb.com/api/v2/search/autocomplete/{game_name}"
        headers = {"Authorization": f"Bearer {self.api_key_input.text.strip()}"}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json().get('data', [])
        except:
            return []
    
    def get_game_icons(self, game_id):
        """Get icons for game"""
        url = f"https://www.steamgriddb.com/api/v2/grids/game/{game_id}"
        headers = {"Authorization": f"Bearer {self.api_key_input.text.strip()}"}
        params = {"dimensions": "1024x1024", "types": "static"}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            grids = response.json().get('data', [])
            return [g for g in grids if g.get('width') == 1024 and g.get('height') == 1024]
        except:
            return []
    
    def download_image(self, url):
        """Download image"""
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            return Image.open(BytesIO(response.content)).convert("RGBA")
        except:
            return None
    
    def apply_overlay(self, base_image):
        """Apply overlay to image"""
        try:
            overlays_folder = Path(self.overlays_path_input.text if hasattr(self, 'overlays_path_input') else DEFAULT_OVERLAYS)
            overlay_path = overlays_folder / self.console_spinner.text / 'overlay.png'
            
            if not overlay_path.exists():
                self.log(f'Overlay not found: {overlay_path}')
                return None
                
            overlay = Image.open(overlay_path).convert("RGBA")
            
            if overlay.size != base_image.size:
                overlay = overlay.resize(base_image.size, Image.Resampling.LANCZOS)
            
            rounded_mask = Image.new('L', base_image.size, 0)
            draw = ImageDraw.Draw(rounded_mask)
            radius = 120
            draw.rounded_rectangle([(0, 0), base_image.size], radius=radius, fill=255)
            
            base_image.putalpha(rounded_mask)
            result = Image.alpha_composite(base_image, overlay)
            
            return result
        except Exception as e:
            self.log(f'Overlay error: {e}')
            return None


if __name__ == '__main__':
    SteamGridOverlayApp().run()
