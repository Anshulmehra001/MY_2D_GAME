A 2D adventure game built with Pygame, inspired by the classic anime film. Join Nobita and his friends as they journey through a dream world, battling foes and becoming legendary heroes.
🌟 Features
Engaging Story: Progress through 10 unique levels, each with its own challenges and logic.
Dynamic Splash Screen: A professional, animated splash screen that introduces the creator.
Immersive Audio: Unique background music for the intro, main menu, and in-game levels to set the mood.
Seamless Transitions: Smooth fade-in/fade-out effects for a polished user experience between game states.
Cutscenes & Transitions: In-game cutscenes and level transitions to advance the narrative.
Cheat Menu: A built-in "Master Control" cheat menu to jump directly to any level.
Robust Asset Handling: Gracefully handles missing image files by substituting them with placeholders to prevent crashes.
🛠️ Installation
To play this game, you'll need Python and the Pygame library installed on your system.
1. Prerequisites:
Python: Make sure you have Python 3.x installed. You can download it from python.org.
Game Assets: Clone or download this repository to get all the necessary code and assets.
2. Clone the Repository:
code
Bash
git clone https://github.com/your-username/doraemon-nobitas-visionary-swordsmen.git
cd doraemon-nobitas-visionary-swordsmen
3. Install Pygame:
Open your terminal or command prompt and run the following command:
code
Bash
pip install pygame
🚀 How to Play
1. Run the Game:
Navigate to the game's root directory in your terminal and execute the main script:
code
Bash
python main.py
(Note: Rename your main game file to main.py if it has a different name.)
2. Controls:
Action	Key / Input	Description
Navigate Menu	Mouse	Hover over buttons and click to select.
Start Game	Click "Start Game"	Begin the adventure from Level 1.
Quit Game	Click "Quit"	Exit the game from the main menu.
Open Cheat Menu	H	Press 'h' at any time to open the Master Control.
Close Cheat Menu	Escape	Close the cheat menu and return to the previous screen.
Confirm Cheat	Enter	After typing a level number, press Enter to warp.
In-Game Controls	Varies by level	Gameplay controls are defined within each level's logic.
📁 File Structure
The game requires a specific folder structure to locate all necessary assets. Ensure your project directory looks like this:
code
Code
.
├── assets/
│   ├── bgm_intro.wav
│   ├── bgm.wav
│   ├── bgm_gameplay.wav
│   ├── title_logo.png
│   └── ... (other level-specific images and sounds)
│
├── level_logic.py
├── level4.py
├── ... (other level modules from level4 to level10)
└── main.py
🔧 Development
The game is designed with a modular structure, where each level's logic can be contained in its own Python file.
Game States: The main loop (main_game_loop) manages the overall game state, switching between the intro, main menu, gameplay, victory/game over screens, and the cheat menu.
Level Loading: The game dynamically imports level modules (level_logic.py, level4.py, etc.) based on the current_level variable. This makes it easy to add new levels without modifying the core game loop.
Music Manager: A simple music manager (play_music) handles loading and playing background tracks, ensuring music changes smoothly between game states.
🤝 Contributing
Contributions are welcome! If you have ideas for new features, levels, or bug fixes, feel free to fork the repository and submit a pull request.
Fork the Project
Create your Feature Branch (git checkout -b feature/AmazingFeature)
Commit your Changes (git commit -m 'Add some AmazingFeature')
Push to the Branch (git push origin feature/AmazingFeature)
Open a Pull Request
📜 License
This project is open source and available to everyone.
