# 🎭 The Emo-Show Game

**The Emo-Show** is a two-player, interactive game inspired by the classic *Simon Says* — but with a twist of emotional intelligence! Guided by the **Elmo** robot, players are challenged to express **seven distinct emotions** across **14 dynamic rounds**.

Using real-time emotion recognition powered by [**Residual Masking Network (RMN)**](https://github.com/phamquiluan/ResidualMaskingNetwork) and **OpenCV**, Elmo evaluates the players’ facial expressions and scores them based on accuracy.

🏆 The player with the **highest total score** at the end wins!

---

## ⚙️ System Overview

This Python-based system integrates several modules:

- 🧠 **RMN (Residual Masking Network)**  
  Deep-learning-based model for facial emotion classification.

- 🎥 **OpenCV**  
  Detects each player's face and adjusts Elmo's head movement to keep them centered in the frame.

- 🔌 **Socket Communication**  
  Enables real-time command exchange between the computer and the robot.

---

## 🌐 Network Requirements

To enable communication between your computer and the Elmo robot, **both devices must be connected to the same local network**.

### Recommended Setup:
- Connect the **Elmo robot** to a **router** via **Ethernet cable**.
- Connect your **computer** to the **same router**, either via Ethernet or Wi-Fi.

Once both devices are on the same network, you'll need to:
- ✅ Identify the **IP address of the robot**
- ✅ Identify the **IP address of your computer**
- ✅ Choose a **port** for communication (default is `4000`)

---

## 🎮 How to Play

### 1. **Start the Robot Command Handler**

On the Elmo robot:
```bash
python src/emoshow_handler.py [ElmoIP] [ElmoPort]
```
  This script listens for commands and controls Elmo’s behavior during gameplay.

### 2. **Launch the Emo-Show App**

On your computer:
```bash
python src/emoshow_app.py [ElmoIP] [ElmoPort] [YourIP]
```

- `[ElmoIP]`: IP address of the robot  
- `[ElmoPort]`: Port for communication (default: `4000`)  
- `[YourIP]`: IP address of your computer

#### Optional Flags:
- `--connect`: Start a debug socket session  
  ```bash
  python src/emoshow_app.py [ElmoIP] [ElmoPort] [YourIP] --connect
  ```
- Run the GUI only (no connection):  
  ```bash
  python src/emoshow_app.py
  ```

---

## 🛠️ Interface Configuration

Before starting the game, make sure to configure the interface correctly:

- ✅ Set **positive pan and tilt** values  
- ✅ Enable **Toggle Motors**  
- ❌ Disable **Toggle Behaviour**  
- ✅ Check **speakers**  
- 🎮 Choose your preferred **game mode**  
- 📈 Monitor **real-time emotion and system data**

![Demos Interface](emoshow_app.png)

---

## 💡 Tips

- Ensure all connections are stable before starting the game.
- For the best experience, run the game in a well-lit environment with both players clearly visible on camera.

---
