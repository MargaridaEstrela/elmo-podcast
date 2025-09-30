## 🌐 Network Requirements

To enable communication between your computer and the Elmo robot, **both devices must be connected to the same local network**.

### Recommended Setup:
- Connect the **Elmo robot** to a **router** via **Ethernet cable**.
- Connect your **computer** to the **same router**, either via Ethernet or Wi-Fi.

Once both devices are on the same network, you'll need to:
- ✅ Identify the **IP address of the robot**
- ✅ Identify the **IP address of your computer**
- ✅ Choose a **port** for communication (default is `4000`)


### 1. **Start the Robot Command Handler**

On the Elmo robot:
```bash
python src/emoshow_handler.py [ElmoIP] [ElmoPort]
```
  This script listens for commands and controls Elmo’s behavior during gameplay.

### 2. **Launch the Elmo App**

On your computer:
```bash
python src/elmo_app.py [ElmoIP] [ElmoPort] [YourIP]
```

- `[ElmoIP]`: IP address of the robot  
- `[ElmoPort]`: Port for communication (default: `4000`)  
- `[YourIP]`: IP address of your computer

#### Optional Flags:
- Run the GUI only (no connection):
  ```bash
  python src/elmo_app.py
  ```

---

## 🛠️ Interface Configuration

Before starting, make sure to configure the interface correctly:

- ✅ Set **positive pan and tilt** values  
- ✅ Enable **Toggle Motors**  
- ❌ Disable **Toggle Behaviour**  
- ✅ Check **speakers**  
