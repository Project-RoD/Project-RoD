import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER, LEFT, RIGHT, BOLD, START, END

# Import your 'brain'
# STEP 1: Import the "brain"
from .services.api_service import get_rod_response

class RoD(toga.App):

    def startup(self):
        """
        Construct and show the Toga application.
        This is where we build the UI from your vision.
        """
        # --- App State ---
        # We define our app's "state" (data) here.
        self.streak_count = 0 
        self.recommended_media = ['recommendation']
        
        # STEP 2: Add "memory" for the conversation
        self.conversation_history = []
        
        # --- Main Window & Navigation ---
        # We create the main window.
        self.main_window = toga.MainWindow(title=self.formal_name)
        
        # We build the shared navigation bar ONCE and store it.
        self.nav_bar = self.build_nav_bar()

        # STEP 5: Pre-build layouts for faster navigation
        self.homepage_layout = self.build_homepage_layout()
        self.chat_layout = self.build_chat_layout()

        # --- FIX 1: Create a persistent layout ---
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

        # Build the homepage layout and show it first.
        self.main_content_area.add(self.homepage_layout)
        self.main_window.content = app_container
        
        # Show the window
        self.main_window.show()

    def build_homepage_layout(self):
        """
        Builds and returns the widget Box for the Homepage.
        This is all the code you've already written for the main page.
        """
        # --- 1. The Top Row (Header) ---
        try:
            streak_icon_image = toga.Image("resources/fire_icon.png")
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
            profile_icon = toga.Icon("resources/profile_icon.png")
        except FileNotFoundError:
            print("WARNING: 'profile_icon.png' not found. Using a placeholder.")
            profile_icon = toga.Icon.DEFAULT_ICON
    
        profile_button = toga.Button(
            icon=profile_icon,
            on_press=self.go_to_profile,
            # FIX 4: padding -> margin
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

        # --- 2. Main Chat Area ---
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

        # --- 3. The Media Hub ---
        media_hub_title_button = toga.Button(
            "Media Hub", # Added '>' to imply navigation
            on_press=self.go_to_media,
            style=Pack(
                margin=(0, 200, 5, 20), 
                font_weight=BOLD, 
                font_size=14, 
                background_color='transparent' # Make it look less like a button
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
        
        # --- Assemble The Homepage Window ---
        main_box = toga.Box(
            children=[
                header_box,
                chat_button_main,
                media_preview_box,
                toga.Box(style=Pack(flex=1)), # This is the spacer
                # FIX 1: Nav bar is no longer built here
            ],
            style=Pack(direction=COLUMN, flex=1) # Add flex=1 to fill the content area
        )
        return main_box

    def build_chat_layout(self):
        """
        Builds and returns the widget Box for the Chat Page.
        This is a new, simple layout based on your Figma.
        """
        
        # --- 1. The New Header ---
        # Your idea: Hamburger menu on the left, profile on the right.
        try:
            menu_icon = toga.Icon("resources/menu_icon.png") # You'll need to find this icon
        except FileNotFoundError:
            print("WARNING: 'menu_icon.png' not found. Using a placeholder.")
            menu_icon = toga.Icon.DEFAULT_ICON
            
        menu_button = toga.Button(
            icon=menu_icon,
            on_press=self.open_menu,
            # FIX 4: padding -> margin
            style=Pack(width=44, height=44, margin=0)
        )
        left_header_box = toga.Box(
            children=[menu_button],
            style=Pack(direction=ROW, align_items=START, margin=10)
        )
        
        # Re-using the profile button logic
        try:
            profile_icon = toga.Icon("resources/profile_icon.png")
        except FileNotFoundError:
            print("WARNING: 'profile_icon.png' not found. Using a placeholder.")
            profile_icon = toga.Icon.DEFAULT_ICON
    
        profile_button = toga.Button(
            icon=profile_icon,
            on_press=self.go_to_profile,
            # FIX 4: padding -> margin
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

        # --- 2. The Chat Log Area ---
        # This is the "meat" of the page.
        # We use a ScrollContainer so the messages can scroll.
        self.chat_log_display = toga.Box(
            # FIX 4: padding -> margin
            style=Pack(direction=COLUMN, flex=1, margin=10)
        )
        # Store the ScrollContainer as self.chat_scroll to scroll it later
        self.chat_scroll = toga.ScrollContainer(
            content=self.chat_log_display,
            style=Pack(flex=1)
        )
        
        # --- 3. The Input Area ---
        # Your idea: A text box and a microphone button.
        self.chat_input = toga.TextInput(
            placeholder="Message...",
            # STEP 3: Connect the "Enter" key to the new send function
            on_confirm=self.handle_text_send,
            style=Pack(flex=1, height=44)
        )
        
        try:
            mic_icon = toga.Icon("resources/mic_icon.png") # You'll need to find this icon
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
            # FIX 3: padding -> margin
            style=Pack(direction=ROW, align_items=CENTER, margin=(10, 10, 10, 10))
        )

        # --- Assemble The Chat Page Window ---
        main_box = toga.Box(
            children=[
                header_box,
                self.chat_scroll, # The scrollable chat area
                input_box,   # The text input
                # FIX 1: Nav bar is no longer built here
            ],
            style=Pack(direction=COLUMN, flex=1) # Add flex=1 to fill the content area
        )
        return main_box

    def build_nav_bar(self):
        """
        Builds and returns the shared Bottom Navigation Bar.
        """
        # Chat Button
        try:
            chat_nav_icon = toga.Icon("resources/chat_icon.png")
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
            home_icon = toga.Icon("resources/home_icon.png")
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
            game_nav_icon = toga.Icon("resources/game_icon.png")
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
        

    # --- Button Functions (Navigation) -----------------------------------
    
    def go_to_homepage(self, widget):
        print("Homepage button clicked!")
        # FIX 1: New navigation logic
        for child in self.main_content_area.children:
            self.main_content_area.remove(child)
        self.main_content_area.add(self.homepage_layout)

    def go_to_profile(self, widget):
        print("Profile button clicked!")
        # Later, this will navigate to a new "Profile" screen
        # self.main_content_area.remove(self.main_content_area.children[0])
        # self.main_content_area.add(self.build_profile_layout())

    def open_chat(self, widget):
        print("Open Chat button clicked!")
        # FIX 1: New navigation logic
        for child in self.main_content_area.children:
            self.main_content_area.remove(child)
        self.main_content_area.add(self.chat_layout)


    def go_to_media(self, widget):
        print("Media Hub button clicked!")
        # This will navigate to the full "Media Hub" screen
        # ...
    
    def go_to_games(self, widget):
        print("Game Hub button clicked!")
        # This will navigate to the "Game Hub" screen
        # ...
        
    # --- Button Functions (Chat Page) ------------------------------------
    
    def open_menu(self, widget):
        print("Menu button clicked!")
    
    # STEP 4: Create the new "send" function
    async def handle_text_send(self, widget):
        """
        Fires when the user presses 'Enter' in the chat_input.
        """
        user_text = self.chat_input.value
        if user_text == "":
            return # Do nothing if the input is empty

        # 1. Add user's message to the UI
        # FIX 2: Use a Box for the bubble to allow wrapping and alignment
        user_bubble_text = toga.Label(
            user_text,
            # FIX 4: padding -> margin
            style=Pack(margin=10, color="white")
        )
        user_bubble_box = toga.Box(
            children=[user_bubble_text],
            style=Pack(
                align_items=END, # Aligns the whole box to the right
                margin=5, 
                background_color="#007AFF"
            )
        )
        self.chat_log_display.add(user_bubble_box)

        # 2. Add user's message to the "memory"
        self.conversation_history.append({"role": "user", "content": user_text})
        
        # 3. Clear the input box
        self.chat_input.value = ""
        
        # 4. Show a "typing" indicator
        typing_indicator = toga.Label(
            "Rod is typing...",
            style=Pack(text_align=LEFT, margin=5, font_style='italic', color='gray')
        )
        self.chat_log_display.add(typing_indicator)
        
        # Scroll to the bottom
        self.chat_scroll.vertical_position = self.chat_scroll.max_vertical_position

        # 5. Call the "brain" (This is the async part)
        ai_response = await get_rod_response(self.conversation_history)
        
        # 6. Add AI's response to the "memory"
        self.conversation_history.append({"role": "assistant", "content": ai_response})

        # 7. Remove the "typing" indicator
        self.chat_log_display.remove(typing_indicator)

        # 8. Add AI's message to the UI
        # FIX 2: Use a Box for the bubble to allow wrapping and alignment
        ai_bubble_text = toga.Label(
            ai_response,
            # FIX 4: padding -> margin
            style=Pack(margin=10)
        )
        ai_bubble_box = toga.Box(
            children=[ai_bubble_text],
            style=Pack(
                align_items=START, # Aligns the whole box to the left
                margin=5, 
                background_color="#E5E5EA"
            )
        )
        self.chat_log_display.add(ai_bubble_box)
        
        # Scroll to the bottom
        self.chat_scroll.vertical_position = self.chat_scroll.max_vertical_position
        

    def start_voice_input(self, widget):
        print("Mic button clicked! Voice input is not implemented yet.")
        # We'll wire this up later


def main():
    return RoD()