import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, BOLD

from .services.api_service import get_rod_response

class RoD(toga.App):

    def startup(self):
        """
        Construct and show the Toga application.
        """
        # Data Storage
        # This will store our conversation history in the app's state.
        self.conversation_history = []

        # UI Widgets (The "Body" components)
        # A scrollable box to show the chat history.
        self.chat_log = toga.MultilineTextInput(readonly=True, style=Pack(flex=1))
        # A text input for the user to type their message.
        self.text_input = toga.TextInput(style=Pack(flex=1))
        # The send button.
        send_button = toga.Button(
            "Send",
            on_press=self.handle_send,
            style=Pack(padding_left=5)
        )

        # Layout
        # An input box that holds the text field and send button side-by-side.
        input_box = toga.Box(children=[self.text_input, send_button], style=Pack(direction=ROW, padding=5))
        # The main container for the whole window.
        main_box = toga.Box(children=[self.chat_log, input_box], style=Pack(direction=COLUMN, padding=5))

        # Window Setup
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

    async def handle_send(self, widget):
        """
        This function is called when the "Send" button is pressed.
        It is asynchronous to work with our async API call.
        """
        user_text = self.text_input.value
        if not user_text:
            return  # Do nothing if the input is empty

        # 1. Update the UI and history immediately with the user's message.
        self.chat_log.value += f"You: {user_text}\n\n"
        self.conversation_history.append({"role": "user", "content": user_text})
        self.text_input.value = "" # Clear the input field

        # 2. Call the "brain" and wait for the response.
        self.chat_log.value += "Rod is typing...\n\n"
        ai_response = await get_rod_response(self.conversation_history)

        # 3. Update the UI and history with the AI's response.
        # (We remove the "typing..." message here by overwriting the log value)
        current_log = self.chat_log.value.replace("Rod is typing...\n\n", "")
        self.chat_log.value = current_log + f"Rod: {ai_response}\n\n"
        self.conversation_history.append({"role": "assistant", "content": ai_response})

def main():
    return RoD()