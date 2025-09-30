import random
import time
import cv2

from rmn import RMN

# List of emotions to analyse
EMOTIONS = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]
emotions_dict = {
    "angry": 0,
    "disgust": 1,
    "fear": 2,
    "happy": 3,
    "sad": 4,
    "surprise": 5,
    "neutral": 6,
}

TRANSITIONS = [
    "alright",
    "checkpoint",
    "dont_blink",
    "feeling_inspired",
    "get_ready",
    "just_checking",
    "make_us_glad",
    "next_player_turn",
    "one_emotion_down",
    "say_cheese",
    "showtime",
    "next_challenge",
    "lets_go",
]

# Load the Haar Cascade model
face_classifier = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# Create the facial expression recognition
m = RMN()


class EmoShow:
    """
    A class representing the Emo-Show game.

    Attributes:
        elmo (object): The Elmo robot.
        logger (object): The logger object for logging messages.
        move (int): The current move.
        player (int): The current player.
        points (dict): The points of each player.
        shuffled_emotions (dict): The shuffled emotions for each player.
        status (int): The status of the game (0: reset, 1: playing, 2: end game).
        emotion (string): The current emotion.
        feedback (boolean): The feedback mode (False: unequal feedback, True: equal feedback).
        remaining_transitions (list): The remaining transitions between moves.
        game_thread (object): The game thread.
        restart_flag (bool): Flag indicating if the game should be restarted.

    Methods:
        set_status(status): Sets the status of the game.
        set_feedback(feedback): Sets the feedback mode.
        get_move(): Returns the current move.
        get_status(): Returns the status of the game.
        get_emotion(): Returns the current emotion.
        get_results(): Returns the results.
        get_points(): Returns the points of each player.
        get_feedback(): Returns the feedback mode.
        toggle_feedback(): Toggles the feedback mode.
        shuffle_emotions(): Shuffles the emotions for each player.
        dynamic_intro(): Plays the dynamics for the intro of the game.
        dynamic_conclusion(): Plays the dynamics for the conclusion of the game.
        center_player(): Centers the player in the frame.
        change_player(): Changes the current player.
        play_transition(): Plays a transition sound while changing player.
        take_picture(): Takes a picture sequence.
        analyse_emotion(): Analyzes the emotion of the current move.
        give_feedback(accuracy): Gives feedback based on the accuracy of the emotion analysis.
        congrats_winner(): Congratulates the winner.
        player_move(): Performs a move by the player.
        play_game(): Starts the game.
        stop_game(): Stops the game.
        restart_game(): Restarts the game.
    """

    def __init__(self, elmo, logger):
        self.elmo = elmo  # Elmo robot
        self.logger = logger
        self.move = 0  # Current move
        self.player = 1  # Current player
        self.first_player = -1  # First player
        self.excluded_player = -1  # Excluded player
        self.points = {"1": 0, "2": 0}  # Points of each player
        self.shuffled_emotions = {"1": [], "2": []}  # Shuffled emotions for each player
        self.status = 0  # 0: reset, 1: playing, 2: end game
        self.emotion = ""  # Current emotion
        self.results = None  # Dict with the last results
        self.feedback = True  # Feedback mode
        self.remaining_transitions = TRANSITIONS.copy()  # Transitions between moves
        self.restart_flag = False  # Flag to restart the game
        self.game_thread = None  # Game thread

    def set_status(self, status):
        """
        Sets the status of the game.

        Args:
            status (int): The status of the game.
        """
        self.status = status

    def set_feedback(self, feedback):
        """
        Sets the feedback mode.

        Args:
            feedback (boolean): The feedback mode.
        """
        self.feedback = feedback

    def get_move(self):
        """
        Returns the current move.

        Returns:
            int: The current move.
        """
        return self.move

    def get_first_player(self):
        """
        Returns the first player

        Returns:
            int: first player.
        """
        return self.first_player

    def get_excluded_player(self):
        """
        Returns the excluded player

        Returns:
            int: excluded player.
        """
        return self.excluded_player

    def get_status(self):
        """
        Returns the status of the game.

        Returns:
            int: The status of the game.
        """
        return self.status

    def get_emotion(self):
        """
        Returns the current emotion.

        Returns:
            string: The current emotion.
        """
        return self.emotion

    def get_results(self):
        return self.results

    def get_shuffled_emotions(self):
        """
        Returns the shuffled emotions for each player.

        Returns:
            dict: The shuffled emotions for each player.
        """
        return self.shuffled_emotions

    def get_points(self):
        """
        Returns the points of each player.

        Returns:
            dict: The points of each player.
        """
        return self.points

    def get_feedback(self):
        """
        Returns the feedback mode.

        Returns:
            boolean: The feedback mode.
        """
        return self.feedback

    def get_player_move(self):
        """
        Returns the current move of the current player.

        Returns:
            int: The current player move.
        """
        player_move = self.move // 2
        return player_move

    def get_player_emotions(self):
        """
        Returns the list of shuffled emotions of the current player.

        Returns:
            list: The current player move.
        """
        return self.shuffled_emotions[str(self.player)]

    def toggle_feedback(self):
        """
        Toggles the feedback mode.
        """
        self.set_feedback(not self.feedback)
        self.elmo.send_message(f"feedback::{self.feedback}")

    def shuffle_emotions(self):
        """
        Shuffles the emotions for each player while minimizing similarity.
        """
        emotions_1 = random.sample(EMOTIONS, len(EMOTIONS))  # Shuffle for player 1
        
        while True:
            emotions_2 = random.sample(EMOTIONS, len(EMOTIONS))  # Shuffle for player 2
            overlap_count = sum(1 for e1, e2 in zip(emotions_1, emotions_2) if e1 == e2)
            
            if overlap_count <= len(EMOTIONS) // 3:  # Allow only minimal overlap
                break

        self.shuffled_emotions["1"] = emotions_1
        self.shuffled_emotions["2"] = emotions_2
        
        self.logger.log_message(f"EMOTIONS 1: {self.shuffled_emotions['1']}")
        self.logger.log_message(f"EMOTIONS 2: {self.shuffled_emotions['2']}")

    def dynamic_intro(self):
        """
        Plays the dynamics for the intro of the game.
        """
        self.elmo.move_left()
        self.elmo.play_sound("introduction_1.wav")
        time.sleep(6.12)
        self.elmo.move_right()
        self.elmo.play_sound("introduction_2.wav")
        time.sleep(7)

        # Show icons
        self.elmo.move_left()
        time.sleep(2)
        self.elmo.play_sound("introduction_3.wav")
        time.sleep(2.8)
        self.elmo.set_icon("3.png")
        time.sleep(1)
        self.elmo.set_icon("2.png")
        time.sleep(0.7)
        self.elmo.move_right()
        self.elmo.set_icon("1.png")
        time.sleep(0.7)
        self.elmo.set_icon("camera.png")
        time.sleep(1)
        self.elmo.set_icon("loading_4.gif")
        time.sleep(6)
        self.elmo.set_icon("black.png")

        self.elmo.move_left()
        time.sleep(2)
        self.elmo.play_sound("introduction_4.wav")
        time.sleep(5)

        self.elmo.move_right()
        time.sleep(2)
        self.elmo.play_sound("introduction_5.wav")
        time.sleep(6)

    def dynamic_conclusion(self):
        """
        Plays the dynamics for the conclusion of the game.
        """
        self.elmo.move_pan(0)
        time.sleep(4)

        self.elmo.set_icon("heart.png")
        self.elmo.play_sound("conclusion.wav")
        self.elmo.move_left()
        time.sleep(5.5)
        self.elmo.move_right()
        time.sleep(5)
        self.elmo.move_left()
        time.sleep(6)
        self.elmo.move_right()
        time.sleep(6)

        # Joke Time
        self.elmo.move_left()
        time.sleep(2)
        self.elmo.play_sound("joke_1.wav")
        time.sleep(4)

        self.elmo.move_right()
        time.sleep(2)
        self.elmo.play_sound("joke_2.wav")
        self.elmo.set_image("cookie-robot.png")
        time.sleep(4)

        self.elmo.move_left()
        self.elmo.set_image("normal.png")
        time.sleep(2)
        self.elmo.play_sound("joke_3.wav")
        time.sleep(4)
        self.elmo.move_right()
        time.sleep(5)
        self.elmo.move_left()
        self.elmo.set_image("coffee.png")
        time.sleep(5)
        self.elmo.move_pan(0)
        time.sleep(2)
        self.elmo.set_icon("black.png")  # Default icon
        self.elmo.set_image("normal.png")  # Default image

    def center_player(self):
        """
        Centers the player's face in the frame by adjusting the robot's pan and
        tilt angles. If no faces detected, returns and continues the game.
        """
        frame = self.elmo.grab_image()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.1, 5, minSize=(100, 100))

        if len(faces) == 0:
            self.logger.log_error("Cannot center player. No faces detected.")
            return

        # Get frame center and dimensions
        frame_width, frame_height = frame.shape[1], frame.shape[0]
        frame_center_x = frame_width / 2
        frame_center_y = frame_height / 2

        # Extract face bounding box
        x, y, w, h = faces[0]
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Compute offsets
        face_center_x = x + w / 2
        face_center_y = y + h / 2
        horizontal_offset = face_center_x - frame_center_x
        vertical_offset = frame_center_y - face_center_y

        # Get current pan and tilt angles
        current_pan_angle = self.elmo.get_current_pan_angle()
        current_tilt_angle = self.elmo.get_current_tilt_angle()

        # Convert pixel offsets to angle corrections using camera FOV
        horizontal_adjustment = (horizontal_offset / frame_width) * 62.2  # Use 62.2° FOV for pan
        vertical_adjustment = (vertical_offset / frame_height) * 48.8  # Use 48.8° FOV for tilt

        # Apply angle corrections and update default values
        new_pan_angle = round(current_pan_angle - horizontal_adjustment)
        new_tilt_angle = round(current_tilt_angle - vertical_adjustment)

        # Check if values are within valid range
        new_pan_angle = self.elmo.check_pan_angle(new_pan_angle)
        new_tilt_angle = self.elmo.check_tilt_angle(new_tilt_angle)

        # Update default values
        if self.player == 1:
            self.elmo.set_default_pan_left(new_pan_angle)
            self.elmo.set_default_tilt_left(new_tilt_angle)
        else:
            self.elmo.set_default_pan_right(new_pan_angle)
            self.elmo.set_default_tilt_right(new_tilt_angle)

        self.elmo.move_pan(new_pan_angle)
        time.sleep(2)
        self.elmo.move_tilt(new_tilt_angle)

        # Save changes
        self.logger.log_message(f"Face center: ({face_center_x}, {face_center_y})")
        self.logger.log_message(f"Horizontal offset: {horizontal_offset}, Adjusted pan: {horizontal_adjustment}")
        self.logger.log_message(f"Vertical offset: {vertical_offset}, Adjusted tilt: {vertical_adjustment}")
        self.logger.log_message(f"New pan angle: {new_pan_angle}, Current pan angle: {current_pan_angle}")
        self.logger.log_message(f"New tilt angle: {new_tilt_angle}, Current tilt angle: {current_tilt_angle}")

    def change_player(self):
        """
        Changes the current player.
        """
        if self.first_player == 1:
            self.player = 1 if self.move % 2 == 0 else 2
        else:
            self.player = 2 if self.move % 2 == 0 else 1

        self.logger.log_message(f"Player: {self.player}")
        self.logger.log_message(f"Move: {self.move}")

        if self.player == 1:
            self.elmo.move_left()
        else:
            self.elmo.move_right()

        time.sleep(2.5)
        self.center_player()

    def play_transition(self):
        """
        Plays a transition sound while changing player
        """
        transition = random.choice(self.remaining_transitions)
        self.remaining_transitions.remove(transition)
        self.elmo.play_sound(f"transitions/{transition}.wav")

    def take_picture(self):
        """
        Plays a sound, displays a countdown sequence of icons (3, 2, 1), and
        captures an image.

        Returns:
            np.ndarray: The captured picture.
        """
        self.elmo.play_sound("picture.wav")
        time.sleep(0.1)

        # show 3, 2, 1 and take a picture
        self.elmo.set_icon("3.png")
        time.sleep(1)
        self.elmo.set_icon("2.png")
        time.sleep(0.5)
        self.elmo.set_icon("1.png")
        time.sleep(0.7)
        self.elmo.set_icon("camera.png")

        return self.elmo.grab_image()

    def analyse_emotion(self):
        """
        Analyzes the emotion of the current move.

        Returns:
            int: The accuracy of the emotion analysis.
        """
        frame = self.take_picture()

        # Save frames to analyze later
        try:
            cv2.imwrite(f"frames/frame_{self.move}.png", frame)
        except Exception as e:
            print(e)

        time.sleep(1.5)
        self.elmo.set_icon("loading_4.gif")  # Set loading icon
        time.sleep(2.5)
        self.elmo.set_icon("black.png")  # After progress gif ended

        # Emotion Expression Analysis
        try:
            results = m.detect_emotion_for_single_frame(frame)
            self.logger.log_message(results)
            proba_list = results[0]["proba_list"]
            self.results = (
                f'Angry: {round(proba_list[0]["angry"] * 100)}  '
                f'Disgust: {round(proba_list[1]["disgust"] * 100)}  '
                f'Fear: {round(proba_list[2]["fear"] * 100)}  '
                f'Happy: {round(proba_list[3]["happy"] * 100)}  '
                f'Sad: {round(proba_list[4]["sad"] * 100)}  '
                f'Surprise: {round(proba_list[5]["surprise"] * 100)}  '
                f'Neutral: {round(proba_list[6]["neutral"] * 100)}'
            )
            self.logger.log_message(results[0])
            accuracy = round(
                proba_list[emotions_dict[self.emotion]][self.emotion] * 100
            )
            self.logger.log_message(f"{self.emotion}: {accuracy}%")

        except Exception as e:
            self.logger.log_error(e)
            accuracy = 0
            self.results = None
            self.logger.log_error("Accuracy: 0%")

        return accuracy

    def give_feedback(self, accuracy):
        """
        Gives feedback based on the detected emotion and its probability.

        Args:
            accuracy (int): The probability of the detected emotion.
        """
        if accuracy < 5: # I couldn't identify {emotion}. Keep trying, you can do it!
            feedback = ("cry.png", f"bad_{self.emotion}.wav", 6)
        elif accuracy < 70: # Good effort!
            feedback = ("blush.png", "good_effort.wav", 4)
        else: # Cheerful success chime
            feedback = ("star.png", "good_feedback.wav", 5)

        self.elmo.set_image(f"{feedback[0]}")
        self.elmo.play_sound(f"{feedback[1]}")
        time.sleep(feedback[2])
        self.elmo.set_image("normal.png")  # Set default image

    def congrats_winner(self):
        # Find winner
        winner = int(max(self.points, key=self.points.get))

        self.logger.log_message(self.points)
        self.logger.log_message(f"winner::{winner}")

        if self.excluded_player == -1:
            if winner == 1:
                self.elmo.move_left()
            else:
                self.elmo.move_right()
        else:
            if self.excluded_player == 1:
                self.elmo.move_right()
            else:
                self.elmo.move_left()

        self.elmo.set_image("normal.png")
        time.sleep(2)
        self.elmo.play_sound("winner.wav")  # Congrats winner
        time.sleep(6.3)

    def player_move(self):
        """
        Performs a move by the player.
        """
        self.elmo.set_image("normal.png")  # Set default image

        if self.move == 2 * len(EMOTIONS):
            self.status = 2  # Game Over
        else:
            self.change_player()

            if self.move == 0:
                self.elmo.play_sound("first_emotion.wav")
            else:
                self.play_transition()

            time.sleep(5)

            player_move = self.get_player_move()
            self.emotion = self.shuffled_emotions[str(self.player)][player_move]

            # Say emotion
            self.logger.log_message(f"Emotion: {self.emotion}")
            self.elmo.play_sound(f"emotions/{self.emotion}.wav")
            self.elmo.set_image(f"emotions/{self.emotion}.png")

            time.sleep(3)

            # Take a picture and analyse emotion
            accuracy = self.analyse_emotion()
            self.points[str(self.player)] += accuracy
            self.logger.log_message(
                f"Player: {str(self.player)}, points: {self.points[str(self.player)]}"
            )

            # Give feedback to the player
            if self.feedback or (
                not self.feedback and self.player != self.excluded_player
            ):
                self.give_feedback(accuracy)
            elif self.player == self.excluded_player:
                if (self.excluded_player == self.first_player and self.move == 2) or (
                    self.excluded_player != self.first_player and self.move == 3
                ):
                    self.give_feedback(accuracy)
                else:
                    time.sleep(1)

            self.move += 1

    def play_game(self):
        """
        Starts the game.
        """
        self.elmo.set_image("normal.png")
        self.elmo.set_icon("black.png")
        self.elmo.move_pan(0)  # Look in the middle

        time.sleep(4)

        self.dynamic_intro()

        self.first_player = random.randint(1, 2)

        self.logger.log_message(f"First player: {self.first_player}")

        if not self.feedback:
            self.excluded_player = random.randint(1, 2)
            self.logger.log_message(f"Excluded player: {self.excluded_player}")

        self.shuffle_emotions()

        time.sleep(0.5)

        while self.status == 1 and not self.restart_flag:
            self.logger.log_message("New emotion...")
            self.player_move()

        if self.status == 2:
            self.elmo.set_image("end_game.png")
            self.elmo.move_pan(0)  # Look in the middle
            self.elmo.set_icon("fireworks.gif")
            self.elmo.play_sound("end_game_song.wav")

            time.sleep(4.5)

            self.congrats_winner()

            self.dynamic_conclusion()  # Thanks players for playing

        if self.restart_flag:
            self.restart_flag = False
            return

    def stop_game(self):
        """
        Stops the game.
        """
        self.restart_flag = True

    def restart_game(self):
        """
        Restarts the game.
        """
        self.move = 0
        self.player = -1
        self.first_player = -1
        self.excluded_player = -1
        self.points = {"1": 0, "2": 0}
        self.shuffled_emotions = {"1": [], "2": []}
        self.status = 0
        self.emotion = ""
        self.restart_flag = False
        self.results = None

        self.remaining_transitions = TRANSITIONS.copy()

        self.elmo.move_pan(0)
        self.elmo.set_image("normal.png")
        self.elmo.set_icon("black.png")
