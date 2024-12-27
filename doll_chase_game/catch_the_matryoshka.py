import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont, QLinearGradient, QBrush
from PyQt5.QtCore import Qt, QTimer, QRect

class MatryoshkaScreensaver(QMainWindow):
    def __init__(self):
        super().__init__()

        # Full-screen window with gradient background
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setGeometry(0, 0, QApplication.desktop().width(), QApplication.desktop().height())

        self.dolls_images = [
            QPixmap("assets/doll1.png"),
            QPixmap("assets/doll2.png"),
            QPixmap("assets/doll3.png"),
            QPixmap("assets/doll4.png"),
            QPixmap("assets/doll5.png"),
            QPixmap("assets/doll6.png"),
            QPixmap("assets/doll7.png"),
            QPixmap("assets/doll8.png"),
            QPixmap("assets/doll9.png"),
            QPixmap("assets/doll10.png"),
        ]
        for image in self.dolls_images:
            if image.isNull():
                print("Failed to load image!")

        # Create initial state
        self.initialize_game()

        # Timer for updating positions and animations
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_positions)
        self.timer.start(16)  # ~60 FPS

        self.showFullScreen()

    def initialize_game(self):
        """Initialize the game state."""
        self.dolls = [self.create_doll() for _ in range(15)]
        self.confetti = []
        self.all_faded = False
        self.generate_confetti()

        # "Play Again" button
        self.play_again_button = QPushButton("Play Again", self)
        self.play_again_button.setStyleSheet(self.button_style())
        self.play_again_button.setGeometry(self.width() // 2 - 100, self.height() // 2 + 50, 200, 50)
        self.play_again_button.clicked.connect(self.restart_game)
        self.play_again_button.hide()  # Initially hidden

        # "Exit" button
        self.exit_button = QPushButton("Exit", self)
        self.exit_button.setStyleSheet(self.button_style())
        self.exit_button.setGeometry(self.width() // 2 - 100, self.height() // 2 + 120, 200, 50)
        self.exit_button.clicked.connect(self.close_game)
        self.exit_button.hide()  # Initially hidden

    def button_style(self):
        """Return a stylesheet for buttons."""
        return """
            QPushButton {
                font-size: 18px;
                font-weight: bold;
                color: white;
                background-color: black;
                border: 2px solid white;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: white;
                color: black;
            }
        """

    def close_game(self):
        """Exit the game."""
        self.close()

    def restart_game(self):
        """Restart the game."""
        self.play_again_button.hide()
        self.exit_button.hide()
        self.initialize_game()

    def create_doll(self):
        """Create a matryoshka doll with random properties."""
        doll = {
            "pixmap": random.choice(self.dolls_images),
            "rect": QRect(random.randint(0, self.width() - 100),
                          random.randint(0, self.height() - 200),
                          100, 200),
            "speed_x": random.randint(1, 4) * random.choice([-1, 1]),
            "speed_y": random.randint(1, 4) * random.choice([-1, 1]),
            "caught": False,  # Flag to indicate if the doll has been caught
            "opacity": 1.0  # Initial opacity (fully visible)
        }
        return doll

    def generate_confetti(self):
        """Generate random confetti particles."""
        self.confetti = [{
            "x": random.randint(0, self.width()),
            "y": random.randint(-self.height(), 0),  # Start above the screen
            "size": random.randint(5, 10),
            "color": QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
            "speed_y": random.randint(2, 5),
            "speed_x": random.choice([-1, 1]) * random.randint(1, 3)
        } for _ in range(100)]  # Number of confetti particles

    def update_positions(self):
        """Update the positions of all dolls, confetti, and repaint."""
        if not self.all_faded:  # Only move and fade dolls if not all have faded
            for doll in self.dolls[:]:
                if not doll["caught"]:  # Only move uncaught dolls
                    doll["rect"].moveLeft(doll["rect"].x() + doll["speed_x"])
                    doll["rect"].moveTop(doll["rect"].y() + doll["speed_y"])

                    # Bounce off the edges
                    if doll["rect"].left() <= 0 or doll["rect"].right() >= self.width():
                        doll["speed_x"] *= -1
                    if doll["rect"].top() <= 0 or doll["rect"].bottom() >= self.height():
                        doll["speed_y"] *= -1
                elif doll["caught"]:  # Gradually fade caught dolls
                    doll["opacity"] -= 0.02  # Adjust fade speed here
                    if doll["opacity"] <= 0:  # Remove fully faded dolls
                        self.dolls.remove(doll)

            # Check if all dolls have faded
            if not self.dolls:  # List is empty when all dolls are faded
                self.all_faded = True
                self.play_again_button.show()
                self.exit_button.show()

        if self.all_faded:  # Update confetti positions
            for conf in self.confetti:
                conf["x"] += conf["speed_x"]
                conf["y"] += conf["speed_y"]
                if conf["y"] > self.height():  # Reset confetti when it falls off-screen
                    conf["y"] = random.randint(-self.height(), 0)
                    conf["x"] = random.randint(0, self.width())

        self.repaint()

    def paintEvent(self, event):
        """Draw the gradient background, all dolls, the final message, and confetti."""
        painter = QPainter(self)

        # Draw gradient background
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor(135, 206, 250))  # Sky blue
        gradient.setColorAt(1.0, QColor(30, 144, 255))   # Dodger blue
        painter.setBrush(QBrush(gradient))
        painter.drawRect(0, 0, self.width(), self.height())

        for doll in self.dolls:
            painter.setOpacity(doll["opacity"])  # Apply fade-out effect
            painter.drawPixmap(doll["rect"], doll["pixmap"])

        if self.all_faded:
            # Draw confetti
            for conf in self.confetti:
                painter.setBrush(conf["color"])
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(conf["x"], conf["y"], conf["size"], conf["size"])

            # Draw the big message
            font = QFont("Arial", 36, QFont.Bold)
            painter.setFont(font)

            # White text with black shadow
            big_message = "Well done, you caught them all!"
            text_width = painter.fontMetrics().width(big_message)
            text_height = painter.fontMetrics().height()

            # Center the big message on the screen
            text_x = self.width() // 2 - text_width // 2
            text_y = self.height() // 2 - text_height // 2

            # Black shadow
            painter.setPen(QColor(0, 0, 0))
            painter.drawText(text_x + 3, text_y + 3, big_message)

            # White text
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(text_x, text_y, big_message)

    def mousePressEvent(self, event):
        """Detect clicks on dolls and mark them as caught."""
        for doll in self.dolls:
            if doll["rect"].contains(event.pos()) and not doll["caught"]:
                doll["caught"] = True
                self.repaint()  # Trigger a repaint
                break

if __name__ == "__main__":
    app = QApplication(sys.argv)
    screensaver = MatryoshkaScreensaver()
    sys.exit(app.exec_())