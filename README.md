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

Enter Elmo robot:
```bash
ssh idmind@<ElmoIP>
```

On the Elmo robot:
```bash
python src/emoshow_handler.py [ElmoIP] [ElmoPort]
```
  This script listens for commands and controls Elmo’s behavior during gameplay.

### 2. **Launch the Podcast App**

On your computer:
```bash
python nvb/podcast_v2.py [ElmoIP] [ElmoPort] [YourIP]
```

- `[ElmoIP]`: IP address of the robot  
- `[ElmoPort]`: Port for communication (default: `4000`)  
- `[YourIP]`: IP address of your computer

#### Interface:

```bash
streamlit run podcast_interface_v2.py [GuestName]
```
- `[ElmoIP]`: Name of the 4th person
---
