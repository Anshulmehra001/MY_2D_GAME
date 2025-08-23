Project Title:
Doraemon: Nobita's Visionary Swordsmen
Description:
"Doraemon: Nobita's Visionary Swordsmen" is a 2D adventure game developed using the Pygame library in Python. The game appears to be inspired by the 1994 anime film of the same name.[1][2] The film's plot revolves around Nobita, who, tired of his mundane life, uses one of Doraemon's gadgets to venture into a dream world.[3] In this fantasy realm, he and his friends become swordsmen to defeat an evil sorcerer.[3] The game brings this adventure to life, allowing players to progress through multiple levels, each presenting unique challenges.
Features:
The game boasts a variety of features to enhance the user experience:
Dynamic Splash Screen: An animated splash screen introduces the game's creator.
Main Menu: A user-friendly main menu provides options to either start the game or quit.
Multi-Level Gameplay: The game is structured with a total of 10 levels for players to conquer.
Immersive Audio: To set the mood, the game includes distinct background music for the introduction, main menu, and gameplay.
Cheat Mode: A "Master Control" cheat menu is available, allowing players to jump to any level of their choice.
Game State Transitions: Smooth fade-out transitions are implemented between different game states, such as the main menu, gameplay, and game over or victory screens.
Installation and Execution
To run "Doraemon: Nobita's Visionary Swordsmen," you will need to have Python and the Pygame library installed on your system.
Prerequisites:
Python: Ensure that you have Python 3.x installed. If not, it can be downloaded from python.org.
Pygame: The Pygame library can be installed by executing the following command in your terminal or command prompt:
pip install pygame
Running the Game:
Confirm that all the game files are located in the same directory.
Open a terminal or command prompt and navigate to the game's root directory.
Run the main script using the following command:
code
python <your_main_game_file>.py
How to Play
Main Menu: Use your mouse to select "Start Game" to begin the adventure or "Quit" to exit the application.
Gameplay: The controls for each level are defined within their respective logic.
Cheat Menu:
Press the 'h' key at any time to access the "Master Control" cheat menu.
Enter a level number between 1 and 10.
Press 'Enter' to instantly transport to the selected level.
Press 'Escape' to close the cheat menu and return to the previous screen.
Asset Requirements
For the game to function as intended, an assets folder must be present in the same directory as the main script. This folder should contain the following files:
title_logo.png: The main title image displayed on the menu screen.
bgm_intro.wav: The background music for the introductory sequence.
bgm.wav: The background music for the main menu.
bgm_gameplay.wav: The background music for the gameplay levels.
