# Ares's Adventure
Ares's Adventure is a game inspired by the classic Sokoban. According to legend, hidden deep within a distant kingdom is a gate that leads to mysterious treasure. To open the gate, one must solve a maze by moving heavy stones onto hidden switches. But be warned—one small mistake could trap the challenger in the maze forever.

# What is This Project About
Our team created this project not only to provide an engaging experience in a Sokoban-style game but also to showcase four powerful search algorithms: Breadth-First Search (BFS), Depth-First Search (DFS), Uniform Cost Search (UCS), and A Search*.

In Ares's Adventure, players navigate through a series of challenging levels, pushing boxes into designated positions to solve each puzzle. Players can see how each algorithm operates in real-time, gaining insight into their strengths and weaknesses in solving pathfinding problems.

# Installation
Clone the repository and install the necessary packages:
bash
Copy code
git clone https://github.com/Dzivilord/Sokoban.git
pip install pygame numpy heap psutil

# Game Environment
The maze is depicted as a grid of size n×m, where each cell represents either a free space, a wall, a stone, or a switch. Ares (the player’s character) can move one square at a time in four directions: Up, Down, Left, and Right. He cannot pass through walls or stones.

## Movement Rules
If the adjacent space contains a stone and the space beyond it is free, Ares can push the stone forward. However, he cannot pull stones, and stones cannot be pushed into walls or other stones.
Objective: The game is completed when all stones are successfully pushed onto the designated switches.
## Symbols in the Maze
Wall: #
Free space: (space)
Stone: $
Ares (the player): @
Switch: .
Stone placed on a switch: *
Ares on a switch: +


# Game Assistance and Hints
During the game, you can get assistance by selecting one of four search algorithms displayed beside the map. After a few seconds, Ares will follow the path generated by the chosen algorithm. A hint showing the solution path will appear on the screen, and you can pause the automated movement at any time to take control and continue solving the puzzle on your own.

You may also change levels at any time; however, note that any progress made in the current level will be lost.

# Connect & Contribute
## Contribute
We welcome your contributions! Here’s how you can get involved:

Fork the Repository: Start by forking the repository to create your own copy.
Create a Branch: Make a new branch for your changes with a descriptive name (e.g., feature-improve-algorithm).
Make Changes: Add new features, fix bugs, or improve documentation. Please follow the project’s coding style and guidelines.
Create a Pull Request: Once you’re ready, submit a pull request with a description of your changes. We’ll review it and provide feedback as soon as possible.
## Connect
If you'd like to discuss this project or collaborate on future ones, feel free to reach out! You can create an issue for questions or suggestions, or contact our team directly via email.

Team Contacts:

22120181@student.hcmus.edu.vn
22120186@student.hcmus.edu.vn
22120188@student.hcmus.edu.vn
22120190@student.hcmus.edu.vn