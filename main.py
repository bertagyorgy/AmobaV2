import os
from itertools import chain
from functools import lru_cache
from colorama import init, Fore, Style
import random
import time
from logo import logoprint

# Colorama inicializálása a színek megjelenítéséhez a konzolban
init(autoreset=True)

MATRIX_SIZE_X = 10  # Tábla szélessége
MATRIX_SIZE_Y = 10  # Tábla magassága
WINNING_LENGTH = 5  # Győzelemhez szükséges jelek hossza
RECURSION_DEPTH = 3  # Mélység a minimax algoritmushoz

class Game:
    def __init__(self):
        self.matrix = [[0 for _ in range(MATRIX_SIZE_Y)] for _ in range(MATRIX_SIZE_X)]  # 10x10-es mátrix
        self.moves = []
        self.player_move = True
        self.number_of_moves = 0
        self.moves_number = 0
        self.moves_processed = 0
        self.last_evaluation = 0
        self.two_player_mode = False  # Kétjátékos mód
        self.chaos_mode = False  # Káosz mód
        self.power_up_available = False
        self.power_up_position = None
        self.choose_mode()

    def choose_mode(self):
        print(logoprint)
        print("Amőba játék - Végtelen kiadás 1.2.2\nFejlesztő: Berta György")
        time.sleep(7)
        self.clear_screen()
        # Játék módjának kiválasztása (1 játékos vs bot, 2 játékos, 3 káosz mód)
        while True:
            mode = input("Válassz játékmódot\n 1: Bot ellen\n 2: Két játékos\n 3: Káosz mód\n ")
            if mode == '1':
                print("Bot ellen játszol.")
                break
            elif mode == '2':
                print("Kétjátékos mód.")
                self.two_player_mode = True
                break
            elif mode == '3':
                print("Káosz mód aktiválva!")
                self.two_player_mode = True
                self.chaos_mode = True
                break
            else:
                print("Érvénytelen választás. Próbáld újra.")

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_board(self):
        # Játéktábla megjelenítése a konzolon (1-től 10-ig indexelve)
        print("  " + " ".join([str(i + 1) for i in range(MATRIX_SIZE_Y)]))  # Fejléc megjelenítése 1-10-ig
        for i, row in enumerate(self.matrix):
            print(str(i + 1).rjust(2), " ".join([self.get_symbol(cell, i, j) for j, cell in enumerate(row)]))

    def get_symbol(self, cell, x, y):
        # A cella értékét konvertálja színes "O", "X", "?" vagy "." karakterekké
        if self.chaos_mode and self.power_up_available and (x, y) == self.power_up_position:
            return Fore.YELLOW + "?" + Style.RESET_ALL
        if cell == 1:
            return Fore.BLUE + "O" + Style.RESET_ALL
        elif cell == -1:
            return Fore.RED + "X" + Style.RESET_ALL
        else:
            return Fore.WHITE + "." + Style.RESET_ALL

    def player_turn(self, player_symbol):
        # Játékos lépésének kezelése
        while True:
            try:
                x, y = map(int, input(f"Játékos {player_symbol}, add meg a lépésed (sor és oszlop pl. 3 4): ").split())
                x -= 1  # Átkonvertáljuk 0-index alapúra
                y -= 1  # Átkonvertáljuk 0-index alapúra
                if 0 <= x < MATRIX_SIZE_X and 0 <= y < MATRIX_SIZE_Y:  # Ellenőrizzük a határokat
                    if self.matrix[x][y] == 0:
                        if self.chaos_mode and self.power_up_available and (x, y) == self.power_up_position:
                            self.activate_power_up(player_symbol)
                        else:
                            self.make_move(x, y, 1 if player_symbol == 'O' else -1)
                        break
                    else:
                        print("A cella foglalt, próbáld újra.")
                else:
                    print(f"Érvénytelen lépés. Kérlek adj meg egy sort 1 és {MATRIX_SIZE_X} között.")
            except (ValueError, IndexError):
                print(f"Érvénytelen lépés. Kérlek adj meg egy sort 1 és {MATRIX_SIZE_X} között.")

    def activate_power_up(self, player_symbol):
        power_up_type = random.choice(['double_move', 'erase_move', 'bomb_move'])
        self.power_up_available = False  # Power-up felhasználva, eltűnik a tábláról

        if power_up_type == 'double_move':
            print(f"{player_symbol} aktiválta a dupla lépés power-upot! Két lépést tehetsz egymás után.")
            self.double_move(player_symbol)
        elif power_up_type == 'erase_move':
            print(f"{player_symbol} aktiválta a törlő power-upot! Törölhetsz egy korábbi lépést.")
            self.erase_move()
        elif power_up_type == 'bomb_move':
            print(f"{player_symbol} aktiválta a bomba power-upot! Egy sor vagy oszlop elemei törlődnek.")
            self.bomb_move()

    def double_move(self, player_symbol):
        self.player_turn(player_symbol)  # Azonnal újra léphet a játékos

    def erase_move(self):
        while True:
            try:
                x, y = map(int, input("Add meg a törlendő lépés koordinátáit (sor oszlop pl. 3 4): ").split())
                x -= 1  # Átkonvertáljuk 0-index alapúra
                y -= 1  # Átkonvertáljuk 0-index alapúra
                if 0 <= x < MATRIX_SIZE_X and 0 <= y < MATRIX_SIZE_Y:
                    if self.matrix[x][y] != 0:
                        self.matrix[x][y] = 0  # Töröljük a lépést a tábláról
                        # Töröljük a lépést a moves listából is
                        self.moves = [(mx, my, c) for (mx, my, c) in self.moves if not (mx == x and my == y)]
                        print("A lépés törölve!")
                        break
                    else:
                        print("A cella üres, nincs mit törölni.")
                else:
                    print(f"Érvénytelen lépés. Kérlek adj meg egy sort 1 és {MATRIX_SIZE_X} között.")
            except (ValueError, IndexError):
                print(f"Érvénytelen lépés. Kérlek adj meg egy sort 1 és {MATRIX_SIZE_X} között.")


    def bomb_move(self):
        while True:
            try:
                direction = input("Add meg, hogy sort (s) vagy oszlopot (o) szeretnél törölni: ").strip().lower()
                index = int(input("Add meg a törlendő sor vagy oszlop számát: ")) - 1
                if direction == 's' and 0 <= index < MATRIX_SIZE_X:
                    for y in range(MATRIX_SIZE_Y):
                        self.matrix[index][y] = 0  # Sor törlése
                    # Töröljük a lépéseket a moves listából is
                    self.moves = [(mx, my, c) for (mx, my, c) in self.moves if mx != index]
                    print(f"A(z) {index + 1}. sor törölve!")
                    break
                elif direction == 'o' and 0 <= index < MATRIX_SIZE_Y:
                    for x in range(MATRIX_SIZE_X):
                        self.matrix[x][index] = 0  # Oszlop törlése
                    # Töröljük a lépéseket a moves listából is
                    self.moves = [(mx, my, c) for (mx, my, c) in self.moves if my != index]
                    print(f"A(z) {index + 1}. oszlop törölve!")
                    break
                else:
                    print("Érvénytelen választás. Próbáld újra.")
            except (ValueError, IndexError):
                print("Érvénytelen választás. Próbáld újra.")


    def spawn_power_up(self):
        while True:
            x, y = random.randint(0, MATRIX_SIZE_X - 1), random.randint(0, MATRIX_SIZE_Y - 1)
            if self.matrix[x][y] == 0:
                self.power_up_position = (x, y)
                self.power_up_available = True
                break

    def hard_bot_move(self):
        # Bot lépése minimax algoritmussal
        move, ev = self.min_max(RECURSION_DEPTH, False, (), self.number_of_moves)
        self.last_evaluation = ev
        self.make_move(*move, -1)

    @lru_cache(None)
    def min_max(self, depth, player_move, moves1, number_of_moves, alpha=float('-inf'), beta=float('inf')):
        for move in moves1:
            self.matrix[move[0]][move[1]] = move[2]

        if depth == 0:
            t = sum([self.check_game_over(self.matrix, move) + self.evaluate_position(self.matrix, move) for move in moves1])
            for move in moves1:
                self.matrix[move[0]][move[1]] = 0
            return None, t 

        for move in moves1:
            c = self.check_game_over(self.matrix, move)
            if abs(c) >= 100:
                for move in moves1:
                    self.matrix[move[0]][move[1]] = 0
                return None, c

        moves = set()
        for x, y, _ in chain(moves1, self.moves[::-1]):
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if 0 <= x + dx < MATRIX_SIZE_X and 0 <= y + dy < MATRIX_SIZE_Y and not self.matrix[x + dx][y + dy]:
                        moves.add((x + dx, y + dy))

        for move in moves1:
            self.matrix[move[0]][move[1]] = 0

        if depth == RECURSION_DEPTH:
            self.moves_number = len(moves)
            self.moves_processed = 0

        moves_eval = []
        for move in moves:
            color = 1 if player_move else -1
            moves2 = list(moves1) + [(move[0], move[1], color)]
            _, ev = self.min_max(depth - 1, not player_move, frozenset(moves2), number_of_moves + 1, alpha, beta)

            ev += self.evaluate_position(self.matrix, (move[0], move[1], color))  # Az értékelést hozzáadjuk
            moves_eval.append((move, ev))

            # Alfa-béta metszés
            if player_move:
                alpha = max(alpha, ev)
                if beta <= alpha:
                    break
            else:
                beta = min(beta, ev)
                if beta <= alpha:
                    break

            if depth == RECURSION_DEPTH:
                self.moves_processed += 1

        if player_move:
            return max(moves_eval, key=lambda x: x[1])
        return min(moves_eval, key=lambda x: x[1])

    def check_game_over(self, board, move):
        """Győzelem ellenőrzése és részleges nyerési minták felismerése."""
        x, y, color = move
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

        for dx, dy in directions:
            count = 1
            # Előre ellenőrizzük az adott irányban a jeleket
            for i in range(1, WINNING_LENGTH):
                nx, ny = x + i*dx, y + i*dy
                if 0 <= nx < MATRIX_SIZE_X and 0 <= ny < MATRIX_SIZE_Y and board[nx][ny] == color:
                    count += 1
                else:
                    break

            # Hátrafelé ellenőrizzük az adott irányban a jeleket
            for i in range(1, WINNING_LENGTH):
                nx, ny = x - i*dx, y - i*dy
                if 0 <= nx < MATRIX_SIZE_X and 0 <= ny < MATRIX_SIZE_Y and board[nx][ny] == color:
                    count += 1
                else:
                    break

            # Ha a jelek száma eléri vagy meghaladja a győzelemhez szükséges hosszúságot
            if count >= WINNING_LENGTH:
                return color * 100  # Győzelem értéke

        return 0  # Nincs győzelem

    def evaluate_position(self, board, move):
        """Helyzet kiértékelése az alapján, hogy milyen közeli van a győzelemhez."""
        x, y, color = move
        score = 0
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

        for dx, dy in directions:
            count = 1
            empty_space = 0
            for i in range(1, WINNING_LENGTH):
                if 0 <= x + i*dx < MATRIX_SIZE_X and 0 <= y + i*dy < MATRIX_SIZE_Y:
                    if board[x + i*dx][y + i*dy] == color:
                        count += 1
                    elif board[x + i*dx][y + i*dy] == 0:
                        empty_space += 1
                        break
                    else:
                        break
            for i in range(1, WINNING_LENGTH):
                if 0 <= x - i*dx < MATRIX_SIZE_X and 0 <= y - i*dy < MATRIX_SIZE_Y:
                    if board[x - i*dx][y - i*dy] == color:
                        count += 1
                    elif board[x - i*dx][y - i*dy] == 0:
                        empty_space += 1
                        break
                    else:
                        break

            if count >= WINNING_LENGTH - 1:
                score += 10 * count
            score += count * empty_space  # Pontozás az üres helyek és saját jelek alapján

        return score

    def make_move(self, x, y, player):
        # Lépés rögzítése a táblán
        self.matrix[x][y] = player
        self.moves.append((x, y, player))
        self.number_of_moves += 1

    def start_game(self):
        # Játék indítása
        while True:
            self.clear_screen()
            self.display_board()

            if self.chaos_mode and self.number_of_moves % 10 == 0 and not self.power_up_available:
                self.spawn_power_up()

            if self.player_move or self.two_player_mode:
                self.player_turn('O' if self.player_move else 'X')
            else:
                self.hard_bot_move()

            winner = None
            for move in self.moves:
                if self.check_game_over(self.matrix, move) != 0:
                    winner = 'O' if move[2] == 1 else 'X'
                    break

            if winner:
                self.clear_screen()
                self.display_board()
                print(f"{winner} nyert!")
                break

            self.player_move = not self.player_move

if __name__ == "__main__":
    game = Game()
    game.start_game()
