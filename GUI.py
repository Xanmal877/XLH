import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit

class AssistantUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 600, 400)
        self.setWindowTitle("Python Assistant")

        self.response_display = QTextEdit(self)
        self.response_display.setReadOnly(True)
        self.response_display.setGeometry(10, 10, 580, 300)

        self.user_input = QTextEdit(self)
        self.user_input.setGeometry(10, 320, 450, 50)

        self.send_button = QPushButton("Send", self)
        self.send_button.setGeometry(470, 320, 120, 50)
        self.send_button.clicked.connect(self.send_command)

    def send_command(self):
        user_input = self.user_input.toPlainText()
        # Process user input using your assistant script and update the response_display
        self.response_display.append("User: " + user_input)
        self.user_input.clear()

def main():
    app = QApplication(sys.argv)
    window = AssistantUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
