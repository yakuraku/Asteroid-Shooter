# Asteroid Shooter

Asteroid Shooter is an engaging and challenging 2D space shooter game developed in Python using the Pygame library. In this game, you control a spaceship navigating through space, avoiding and destroying meteors. With immersive gameplay, a ship hangar to unlock and choose your vessel, a credits system, dynamic GUI elements, and an integrated soundtrack, Asteroid Shooter provides a captivating gaming experience.

## Table of Contents

- [Game Overview](#game-overview)
- [Installation](#installation)
- [How to Play](#how-to-play)
  - [Controls](#controls)
  - [Game Mechanics](#game-mechanics)
  - [The Hangar](#the-hangar)
  - [Scoring and Credits](#scoring-and-credits)
- [Perspective Projection](#perspective-projection)
  - [Understanding Perspective Projection](#understanding-perspective-projection)
  - [References](#references)
- [Contributing](#contributing)
- [License](#license)

## Game Overview

In Asteroid Shooter, you pilot a spaceship, navigating through a meteor-filled space. The goal is to survive as long as possible while avoiding indestructible stone meteors and shooting down regular meteors. As you progress, your score increases, and you earn credits to unlock new ships. The game features:

- **Ship Hangar:** A selection of ships to unlock and fly, each with a unique design.
- **Credits System:** Earn credits by playing the game and use them to expand your ship collection.
- **Two types of meteors:** Regular meteors (destructible) and Stone meteors (indestructible).
- **Power-ups:** A 10% chance for regular meteors to drop a shield that can protect your spaceship.
- **Damage System:** The spaceship can sustain up to 4 hits, with visual damage effects indicating the severity of the damage.
- **GUI Elements:** Integrated menus and game-over screens with dynamic sound effects and music.
- **Advanced Graphics:** Menu and game-over screens utilize perspective projection for added depth and realism.

## Installation

To play Asteroid Shooter, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Yashwanth-Kumar-Kurakula/Asteroid-Shooter.git
   ```

2. **Navigate to the project directory:**

   ```bash
   cd Asteroid-Shooter
   ```

3. **Install the required dependencies:**

   Ensure you have Python and Pygame installed. If not, you can install Pygame using pip:

   ```bash
   pip install pygame
   ```

4. **Run the game:**

   ```bash
   python asteroid_shooter.py
   ```

## How to Play

### Controls

- **Move the spaceship:** Move your mouse.
- **Shoot lasers:** Left-click.
- **Activate shield:** Right-click (Note: The shield lasts for 10 seconds unless you get hit).
- **Pause/Return to menu:** Press the `Escape` key.

### Game Mechanics

- **Meteors:** 
  - **Regular Meteors:** Can be destroyed by lasers. There is a 10% chance that a destroyed meteor will drop a shield.
  - **Stone Meteors:** Indestructible. These must be avoided as they cannot be destroyed even with a shield. They also exhibit a collision effect, changing direction upon hitting another stone meteor.

- **Shields:** 
  - Shields provide temporary protection against meteors. A shield lasts for 10 seconds unless hit. If you collide with a stone meteor, the shield will be destroyed, and your spaceship will take damage.

- **Damage System:** 
  - Your spaceship can withstand up to 4 hits. After each hit, a damage overlay will appear on the spaceship, becoming more pronounced with each subsequent hit.

- **Collision Effects:** 
  - Stone meteors interact with each other upon collision, changing direction similarly to how two balls would collide and bounce off.

### The Hangar

Before you start a new game, you'll visit the Ship Hangar. Here you can:

- **Select Your Ship:** Choose from any of the ships you have unlocked. To start the game with a specific ship, double-click on it.
- **Unlock New Ships:** Use the credits you've earned to purchase new ships. Each ship has a different design, but all share the same performance characteristics.
- **Default Ship:** Every player starts with the "Star Ranger" ship unlocked by default.

### Scoring and Credits

- **Score Calculation:** 
  - Your score is based on how long you survive. The longer you stay alive, the higher your score.

- **Earning Credits:**
  - For every 10 seconds you survive in the game, you will earn 1 credit. These credits are saved automatically and can be used to unlock new ships in the Hangar.

## Perspective Projection

### Understanding Perspective Projection

In Asteroid Shooter, perspective projection is used to create a sense of depth in the 2D game environment. This technique is primarily applied in the menu and game-over screens, where meteors are simulated to appear as if they are coming from a 3D scene onto the 2D screen.

Perspective projection involves projecting 3D objects onto a 2D plane (the screen) while maintaining the illusion of depth. This is achieved by scaling objects based on their distance from the "camera" (the viewpoint of the player). Objects closer to the camera appear larger, while those further away appear smaller, creating a sense of three-dimensionality.

#### Example in Asteroid Shooter:
- **Menu and Game Over Screens:** The meteors on these screens are displayed with varying sizes to simulate depth. Larger meteors appear closer, while smaller meteors seem farther away, giving the scene a more realistic and immersive feel.

#### Technical Implementation:
- The game uses mathematical formulas for perspective projection, where the size and position of meteors are dynamically calculated based on their "depth" values. This is crucial for maintaining a consistent and realistic visual experience.

### References

- Explore the official [Pygame Documentation](https://www.pygame.org/docs/) to understand the library used in this project.
- The game draws inspiration from Clear Code's tutorials. Check out his insightful videos [here](https://www.youtube.com/@ClearCode).
- The perspective projection technique used in the Menu and Game Over screens is inspired by Coder Space - Voxel Starfield video. You can watch it [here](https://www.youtube.com/watch?v=qr4siL4Wktc).
- For a deeper dive into the concept of perspective projection implemented in the game, refer to this [Wikipedia article](https://en.wikipedia.org/wiki/3D_projection#Perspective_projection).

## Contributing

Contributions are welcome! If you'd like to contribute to Asteroid Shooter, please fork the repository and submit a pull request. For major changes, please open an issue to discuss what you would like to change.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

