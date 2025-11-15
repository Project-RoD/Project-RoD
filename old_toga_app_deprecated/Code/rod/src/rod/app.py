import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER, LEFT, RIGHT, BOLD, START, END
from pathlib import Path
import asyncio

# Import ALL the brains
from .services.textgen_service import get_rod_response
from .services.stt_service import speech_to_text
from .services.memory_service import load_memory, append_memory
# MISSING TTS

class RoD(toga.App):

    def startup(self):
        """
        Construct and show the Toga application.
        """
        # App State
        self.streak_count = 0 
        self.recommended_media = ['recommendation']
        
        # Create placeholder "memory"
        self.conversation_history = []
        
        # Main Window & Navigation
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.nav_bar = self.build_nav_bar()
        self.homepage_layout = self.build_homepage_layout()
        self.chat_layout = self.build_chat_layout()

        # This Box will hold the content that changes
        self.main_content_area = toga.Box(style=Pack(flex=1, direction=COLUMN))
        
        # This is the main container that holds the content AND the nav bar
        app_container = toga.Box(
            children=[
                self.main_content_area,
                self.nav_bar
            ],
            style=Pack(direction=COLUMN)
        )

        self.main_content_area.add(self.homepage_layout)
        self.main_window.content = app_container
        
        # Show the window
        self.main_window.show()

        asyncio.create_task(self.async_startup_tasks())


    async def async_startup_tasks(self):
        """
        Run all the async tasks that couldn't be run in startup().
        """
        # Load the real memory from file
        self.conversation_history = await load_memory()
        # Now, populate the chat UI with the history we just loaded
        await self.load_chat_history_into_ui()


    def build_homepage_layout(self):
        """
        Builds and returns the widget Box for the Homepage.
        """
        # The Top Row (Header)
        try:
            streak_icon_image = toga.Image("resources/icons/fire_icon.png")
            streak_icon = toga.ImageView(
                image=streak_icon_image,
                style=Pack(width=32, height=32)
            )
        except FileNotFoundError:
            print("WARNING: 'fire_icon.png' not found. Using a placeholder.")
            streak_icon = toga.Label("🔥", style=Pack(width=32, height=32, font_size=20))

        self.streak_label = toga.Label(
            f"{self.streak_count} Days", 
            style=Pack(margin=(8, 10, 10, 5), font_size=13, font_weight=BOLD)
        )
        
        left_header_box = toga.Box(
            children=[streak_icon, self.streak_label],
            style=Pack(direction=ROW, align_items=START, margin=10)
        )

        try:
            profile_icon = toga.Icon("resources/icons/profile_icon.png")
        except FileNotFoundError:
            print("WARNING: 'profile_icon.png' not found. Using a placeholder.")
            profile_icon = toga.Icon.DEFAULT_ICON
    
        profile_button = toga.Button(
            icon=profile_icon,
            on_press=self.go_to_profile,
            style=Pack(width=44, height=44, margin=0)
        )
        right_header_box = toga.Box(
            children=[profile_button],
            style=Pack(direction=ROW, align_items=END, margin=10)
        )
        header_box = toga.Box(
            children=[left_header_box, toga.Box(style=Pack(flex=1)), right_header_box],
            style=Pack(direction=ROW, height=60)
        )

        # Main Chat Area
        chat_button_main = toga.Button(
            "Chat with RoD",
            on_press=self.open_chat, 
            style=Pack(
                height=150, 
                margin=20, 
                font_size=18, 
                font_weight=BOLD
            )
        )

        # The Media Hub
        media_hub_title_button = toga.Button(
            "Media Hub",
            on_press=self.go_to_media,
            style=Pack(
                margin=(0, 200, 5, 20), 
                font_weight=BOLD, 
                font_size=14, 
                background_color='transparent'
            )
        )
        media_preview_title = toga.Label(
            "What's New in the Media Hub:",
            style=Pack(margin=(5, 20, 5, 20), font_weight=BOLD)
        )
        media_preview_content = toga.Box(
            style=Pack(height=225, background_color="#EEEEEE", margin=10)
        )
        media_preview_box = toga.Box(
            children=[media_hub_title_button, media_preview_title, media_preview_content],
            style=Pack(direction=COLUMN)
        )
        
        # Assemble The Homepage Window
        main_box = toga.Box(
            children=[
                header_box,
                chat_button_main,
                media_preview_box,
                toga.Box(style=Pack(flex=1)), # This is the spacer
            ],
            style=Pack(direction=COLUMN, flex=1) 
        )
        return main_box

    def build_chat_layout(self):
        """
        Builds and returns the widget Box for the Chat Page.
        """
        
        # The New Header
        try:
            menu_icon = toga.Icon("resources/icons/menu_icon.png") 
        except FileNotFoundError:
            print("WARNING: 'menu_icon.png' not found. Using a placeholder.")
            menu_icon = toga.Icon.DEFAULT_ICON
            
        menu_button = toga.Button(
            icon=menu_icon,
            on_press=self.open_menu,
            style=Pack(width=44, height=44, margin=0)
        )
        left_header_box = toga.Box(
            children=[menu_button],
            style=Pack(direction=ROW, align_items=START, margin=10)
        )
        
        try:
            profile_icon = toga.Icon("resources/icons/profile_icon.png")
        except FileNotFoundError:
            print("WARNING: 'profile_icon.png' not found. Using a placeholder.")
            profile_icon = toga.Icon.DEFAULT_ICON
    
        profile_button = toga.Button(
            icon=profile_icon,
            on_press=self.go_to_profile,
            style=Pack(width=44, height=44, margin=0)
        )
        right_header_box = toga.Box(
            children=[profile_button],
            style=Pack(direction=ROW, align_items=END, margin=10) 
        )
        
        header_box = toga.Box(
            children=[left_header_box, toga.Box(style=Pack(flex=1)), right_header_box],
            style=Pack(direction=ROW, height=60)
        )

        # The Chat Log Area
        self.chat_log_display = toga.Box(
            style=Pack(direction=COLUMN, flex=1, margin=10)
        )
        self.chat_scroll = toga.ScrollContainer(
            content=self.chat_log_display,
            style=Pack(flex=1)
        )
        
        # The Input Area
        self.chat_input = toga.TextInput(
            placeholder="Message...",
            on_confirm=self.handle_text_send_sync,
            style=Pack(flex=1, height=44)
        )
        
        try:
            mic_icon = toga.Icon("resources/icons/mic_icon.png") 
        except FileNotFoundError:
            print("WARNING: 'mic_icon.png' not found. Using a placeholder.")
            mic_icon = toga.Icon.DEFAULT_ICON

        mic_button = toga.Button(
            icon=mic_icon,
            on_press=self.start_voice_input,
            style=Pack(width=44, height=44, margin=(10, 10, 30, 10))
        )

        input_box = toga.Box(
            children=[self.chat_input, mic_button],
            style=Pack(direction=ROW, align_items=CENTER, margin=(10, 10, 10, 10))
        )

        # Assemble The Chat Page Window
        main_box = toga.Box(
            children=[
                header_box,
                self.chat_scroll, # The scrollable chat area
                input_box,   # The text input
            ],
            style=Pack(direction=COLUMN, flex=1) 
        )
        return main_box

    def build_nav_bar(self):
        """
        Builds and returns the shared Bottom Navigation Bar.
        """
        # Chat Button
        try:
            chat_nav_icon = toga.Icon("resources/icons/chat_icon.png")
        except FileNotFoundError:
            print("WARNING: 'chat_icon.png' not found. Using a placeholder.")
            chat_nav_icon = toga.Icon.DEFAULT_ICON

        chat_nav_button = toga.Button(
            icon=chat_nav_icon,
            on_press=self.open_chat, 
            style=Pack(width=48, height=48, margin=(10, 10, 10, 10))
        )

        # Home Button
        try:
            home_icon = toga.Icon("resources/icons/home_icon.png")
        except FileNotFoundError:
            print("WARNING: 'home_icon.png' not found. Using a placeholder.")
            home_icon = toga.Icon.DEFAULT_ICON

        home_button = toga.Button(
            icon=home_icon,
            on_press=self.go_to_homepage, 
            style=Pack(width=48, height=48, margin=(10, 10, 10, 10))
        )

        # Game Button
        try:
            game_nav_icon = toga.Icon("resources/icons/game_icon.png")
        except FileNotFoundError:
            print("WARNING: 'game_icon.png' not found. Using a placeholder.")
            game_nav_icon = toga.Icon.DEFAULT_ICON

        game_nav_button = toga.Button(
            icon=game_nav_icon,
            on_press=self.go_to_games, 
            style=Pack(width=48, height=48, margin=(10, 10, 10, 10))
        )
        
        nav_bar = toga.Box(
            children=[
                toga.Box(style=Pack(flex=1)),
                chat_nav_button,
                toga.Box(style=Pack(flex=1)),
                home_button,
                toga.Box(style=Pack(flex=1)),
                game_nav_button,
                toga.Box(style=Pack(flex=1)),
            ],
            style=Pack(
                direction=ROW, 
                align_items=CENTER, 
                margin=(10, 0, 10, 0), 
                height=60,
                background_color="#F8F8F800"
            )
        )
        return nav_bar
        
    # UI Helper Functions
    async def load_chat_history_into_ui(self):
        """Clears the chat UI and rebuilds it from the history state."""
        self.chat_log_display.clear()
        for message in self.conversation_history:
            if message['role'] == 'user':
                bubble_style = Pack(align_items=END, margin=5, background_color="#007AFF")
                text_style = Pack(margin=10, color="white")
            else: # 'assistant'
                bubble_style = Pack(align_items=START, margin=5, background_color="#E5E5EA")
                text_style = Pack(margin=10)
            
            self.chat_log_display.add(
                toga.Box(
                    children=[toga.Label(message['content'], style=text_style)],
                    style=bubble_style
                )
            )
        await self.scroll_to_bottom()

    async def scroll_to_bottom(self):
        """Scrolls the chat log to the most recent message."""
        await asyncio.sleep(0.01) # A small delay to ensure UI updates
        self.chat_scroll.vertical_position = self.chat_scroll.max_vertical_position

    # --- Button Functions (Navigation) -----------------------------------
    
    def go_to_homepage(self, widget):
        print("Homepage button clicked!")
        for child in self.main_content_area.children:
            self.main_content_area.remove(child)
        self.main_content_area.add(self.homepage_layout)

    def go_to_profile(self, widget):
        print("Profile button clicked!")

    async def open_chat(self, widget):
        print("Open Chat button clicked!")
        # Reload the history from file every time we open the chat
        self.conversation_history = await load_memory()
        await self.load_chat_history_into_ui()
        
        for child in self.main_content_area.children:
            self.main_content_area.remove(child)
        self.main_content_area.add(self.chat_layout)

    def go_to_media(self, widget):
        print("Media Hub button clicked!")
    
    def go_to_games(self, widget):
        print("Game Hub button clicked!")
        
    # --- Button Functions (Chat Page) ------------------------------------
    
    def open_menu(self, widget):
        print("Menu button clicked!")
    
    # Create a SYNC wrapper for the on_confirm handler
    def handle_text_send_sync(self, widget):
        """
        This is the SYNCHRONOUS function Toga calls when "Enter" is pressed.
        """
        # asyncio.create_task schedules the async function to run
        # without blocking the UI.
        asyncio.create_task(self.handle_text_send_async(widget))

    async def handle_text_send_async(self, widget):
        """
        This is the ASYNC function that contains our actual chat logic.
        """
        user_text = self.chat_input.value
        if user_text == "":
            return # Do nothing if the input is empty

        # Add user's message to UI and memory
        await self.add_message_to_chat(user_text, 'user')
        
        # Clear the input box
        self.chat_input.value = ""
        
        # Show a "typing" indicator
        typing_indicator = toga.Label(
            "Rod is typing...",
            style=Pack(text_align=LEFT, margin=5, font_style='italic', color='gray')
        )
        self.chat_log_display.add(typing_indicator)
        await self.scroll_to_bottom()

        # Call the "brain" and get a response
        ai_response = await get_rod_response(self.conversation_history)
        
        # Remove the "typing" indicator
        self.chat_log_display.remove(typing_indicator)

        # Add AI's message to UI and memory
        await self.add_message_to_chat(ai_response, 'assistant')
        
    async def start_voice_input(self, widget):
        print("Mic button clicked!")
        
        # Open a file dialog to select an audio file
        try:
            filepath_str = await self.main_window.open_file_dialog(
                title="Select an Audio File",
                multiple_select=False 
            )
            if not filepath_str:
                 print("No file selected.")
                 return # User cancelled the dialog

            filepath = Path(filepath_str)
        except Exception as e:
            print(f"File dialog error: {e}")
            return # User cancelled

        # Show a "transcribing" indicator
        self.chat_input.value = "Transcribing audio..."
        
        # Call the STT "brain"
        transcribed_text = await speech_to_text(filepath)
        
        if "Error" in transcribed_text:
            self.chat_input.value = transcribed_text
            return
        
        # Put the transcribed text in the input box for the user to see
        self.chat_input.value = transcribed_text
        
        # Automatically send this text
        # We can call the same function that "Enter" uses
        await self.handle_text_send_async(self.chat_input)

    async def add_message_to_chat(self, text, role):
        """Helper function to add a message to the UI and memory."""
        # Add to UI
        if role == 'user':
            bubble_style = Pack(align_items=END, margin=5, background_color="#007AFF")
            text_style = Pack(margin=10, color="white")
        else: # 'assistant'
            bubble_style = Pack(align_items=START, margin=5, background_color="#E5E5EA")
            text_style = Pack(margin=10)
        
        self.chat_log_display.add(
            toga.Box(
                children=[toga.Label(text, style=text_style)],
                style=bubble_style
            )
        )
        await self.scroll_to_bottom()
        
        # Add to "memory" (both local state and file)
        self.conversation_history.append({"role": role, "content": text})
        await append_memory(role, text)


def main():
    return RoD()