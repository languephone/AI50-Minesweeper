import itertools
import random
import copy


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        else:
            return set()


    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        print("Adding knowledge-----------------------------------------------")

        # Mark the cell as a move that has been made
        self.moves_made.add(cell)
        
        # Mark the cell as safe
        self.mark_safe(cell)

        # 1) Add a new sentence to the AI's knowledge base
        # based on the value of `cell` and `count`
        
        # Get neighbouring cells
        neighbouring_cells = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # Check that cell is within bounds of grid
                if 0 <= i < self.height and 0 <= j < self.width:
                    # Prevent adding current cell to set
                    if (i, j) == cell:
                        continue
                    neighbouring_cells.add((i, j))
        
        # Create new sentence based on neighbouring cells and count
        new_sentence = Sentence(neighbouring_cells, count)
        
        # Remove cells known to be safe or mines
        for mine_cell in self.mines:
            new_sentence.mark_mine(mine_cell)
        for safe_cell in self.safes:
            new_sentence.mark_safe(safe_cell)
        
        self.knowledge.append(new_sentence)
        print(f"Adding {new_sentence} based on neighbouring cells")
        
        # Print statements to test logic
        self.show_current_knowledge()

        # Run the following repeatedly until no changes detected:
        while True:
            starting_knowledge = copy.deepcopy(self.knowledge)
            # 4) Mark any additional cells as safe or as mines
            # if it can be concluded based on the AI's knowledge base
            self.refresh_knowledge()
            self.remove_stale_sentences()
            # 5) add any new sentences to the AI's knowledge base
            # if they can be inferred from existing knowledge
            self.infer_new_sentences()
            # If no changes made to knowledge, then everything is up to date
            if self.knowledge == starting_knowledge:
                break
            # Print statements to test logic
            print("Completed Loop")
            print("Reprinting knowledge after updating sentences--------------")
            self.show_current_knowledge()
            
            # Stop loop if going to be infinite
            if len(self.knowledge) > 50:
                break

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        available_moves = self.safes.difference(self.moves_made)
        if available_moves:
            # random choice can't work on a set, so convert to list
            available_moves = list(available_moves)
            return random.choice(available_moves)
        else:
            return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        
        # Generate all available spaces
        available_moves = set()
        for i in range(self.height):
            for j in range(self.width):
                available_moves.add((i, j))

        # Eliminate moves already made
        available_moves = available_moves.difference(self.moves_made)
        # Eliminate spaces with mines
        available_moves = available_moves.difference(self.mines)
        
        # random choice can't work on a set, so convert to list
        available_moves = list(available_moves)
        
        if available_moves:
            return random.choice(available_moves)
        else:
            return None

    def show_current_knowledge(self):
        print(f"Known mines: {self.mines}")
        print(f"Known safes: {self.safes}")
        if self.knowledge:
            for position, sentence in enumerate(self.knowledge):
                print(f"Knowledge {position}: {sentence}")

    def refresh_knowledge(self):
        """
        4) Mark any additional cells as safe or as mines
        if it can be concluded based on the AI's knowledge base
        """
        starting_knowledge = copy.deepcopy(self.knowledge)
        for sentence in starting_knowledge:
            for known_mine in sentence.known_mines():
                self.mark_mine(known_mine)
                print(f"Adjusting {sentence} for known mine {known_mine}")
            for known_safe in sentence.known_safes():
                self.mark_safe(known_safe)
                print(f"Adjusting {sentence} for known safe {known_safe}")

    def infer_new_sentences(self):
        """
        5) add any new sentences to the AI's knowledge base
        if they can be inferred from existing knowledge
        """
        starting_knowledge = copy.deepcopy(self.knowledge)
        # For each sentence, check if it's a subset of another sentence
        for sentence_1 in starting_knowledge:
            for sentence_2 in starting_knowledge:
                # Check for subset using '<' symbol, which excludes equal sets
                if sentence_1.cells < sentence_2.cells:
                    # If it's a subset, create a new set from the difference
                    # and set the count equal the difference in count 
                    unique_set = sentence_2.cells.difference(sentence_1.cells)
                    new_sentence = Sentence(unique_set,
                        sentence_2.count - sentence_1.count)
                    # Prevent adding in a duplicate sentence
                    if new_sentence not in self.knowledge:
                        self.knowledge.append(new_sentence)
                        print(f"New sentence inferred: {new_sentence}")

    def remove_stale_sentences(self):
        """
        Remove sentences that return empty sets of cells
        """
        starting_knowledge = copy.deepcopy(self.knowledge)
        for sentence in starting_knowledge:
            if not sentence.cells:
                self.knowledge.remove(sentence)
                print(f"Removing stale sentence {sentence}")

    def get_neighbouring_cells(self):
        neighbouring_cells = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if 0 <= i < self.height and 0 <= j < self.width:
                    # Prevent adding current cell to set
                    if (i, j) == cell:
                        continue
                    neighbouring_cells.add((i, j))
        return neighbouring_cells