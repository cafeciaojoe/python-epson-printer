import os
import random
from PIL import Image, ImageDraw
from .epsonprinter import EpsonPrinter

# Parameters for the maze
MAZE_SIZE = 21  # Size of the maze (must be an odd number for proper walls)
CELL_SIZE = 200  # Size of each cell in pixels
NUM_LOOPS = 5  # Number of random loops to add to the maze

def generate_recursive_backtracking_maze(size):
    """
    Generate a maze using the Recursive Backtracking algorithm.
    :param size: Size of the maze grid (must be an odd number).
    :return: A 2D list representing the maze (0 = wall, 1 = path).
    """
    # Initialize the grid with walls
    maze = [[0 for _ in range(size)] for _ in range(size)]

    # Define the directions for moving (right, down, left, up)
    directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]

    def carve_passages(x, y):
        """Recursive function to carve passages in the maze."""
        maze[y][x] = 1  # Mark the current cell as a path
        random.shuffle(directions)  # Shuffle directions for randomness
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 < nx < size - 1 and 0 < ny < size - 1 and maze[ny][nx] == 0:
                # Carve a passage between the current cell and the next cell
                maze[y + dy // 2][x + dx // 2] = 1
                carve_passages(nx, ny)

    # Start carving from the top-left corner
    carve_passages(1, 1)

    # Add start and end points
    maze[1][0] = 1  # Start point (top-left, just outside the maze)
    maze[size - 2][size - 1] = 1  # End point (bottom-right, just outside the maze)

    return maze

def add_loops(maze, num_loops):
    """
    Add random loops to the maze by breaking walls.
    :param maze: The 2D list representing the maze (0 = wall, 1 = path).
    :param num_loops: Number of random walls to break.
    """
    size = len(maze)
    for _ in range(num_loops):
        # Pick a random wall to break
        x = random.randint(1, size - 2)
        y = random.randint(1, size - 2)
        if maze[y][x] == 0:  # Only break walls
            maze[y][x] = 1

def maze_to_image(maze, cell_size):
    """
    Convert a maze grid to a PIL Image.
    :param maze: 2D list representing the maze (0 = wall, 1 = path).
    :param cell_size: Size of each cell in pixels.
    :return: A PIL Image object of the maze.
    """
    size = len(maze) * cell_size
    image = Image.new("1", (size, size), 1)  # Create a white image
    draw = ImageDraw.Draw(image)

    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == 0:  # Draw walls as black
                x0, y0 = x * cell_size, y * cell_size
                x1, y1 = x0 + cell_size, y0 + cell_size
                draw.rectangle([x0, y0, x1, y1], fill=0)

    return image

def main():
    # Printer vendor and product IDs
    ID_VENDOR = 0x04b8  # Replace with your printer's vendor ID
    ID_PRODUCT = 0x0202  # Replace with your printer's product ID

    # Generate the maze
    print("Generating maze...")
    maze = generate_recursive_backtracking_maze(MAZE_SIZE)

    # Add loops to the maze
    add_loops(maze, NUM_LOOPS)

    # Convert the maze to an image
    maze_image = maze_to_image(maze, CELL_SIZE)

    # Save the maze as a PNG file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    maze_file = os.path.join(current_dir, "generated_maze.png")
    maze_image.save(maze_file)
    print(f"Maze saved as {maze_file}")

    # Initialize the printer
    printer = EpsonPrinter(ID_VENDOR, ID_PRODUCT)

    # Print the maze
    print("Printing maze...")
    printer.print_image_from_file(maze_file)
    printer.linefeed(10)
    printer.cut()
    print("Maze printed successfully.")

if __name__ == '__main__':
    main()