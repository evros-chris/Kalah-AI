import copy
import shlex
import subprocess

from agent import Move
from kalah import Board
from kalah import Kalah
from kalah import Side
import protocol


class KalahEnv():
    holes = 7
    seeds = 7
    starting_side = Side.SOUTH
    allow_swapping = True

    def __init__(self, command, agent_side=Side.SOUTH):
        self._command = command
        self._original_agent_side = agent_side
        self.agent_side = agent_side
        self._op_side = agent_side.opposite()
        self._active_side = KalahEnv.starting_side
        self.kalah = None
        self._op_process = None
        self.move_count = 1

    def reset(self):
        """
        Reset environment to starting state.
        """
        # Reset sides.
        self.agent_side = self._original_agent_side
        self._op_side = self.agent_side.opposite()
        self._active_side = KalahEnv.starting_side

        # Reset game.
        self.kalah = Kalah(Board(KalahEnv.holes, KalahEnv.seeds))

        # Create new opponent process.
        if self._op_process is not None:
            self._op_process.kill()
        self._op_process = subprocess.Popen(
            shlex.split(self._command),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
            universal_newlines=True,
        )

        # Reset move count.
        self.move_count = 1

        # Tell opponent which side it's on.
        self._op_process.stdin.write(protocol.createStartMsg(self._op_side))

        # Let opponent play until it is no longer their turn.
        while self._active_side == self._op_side:
            message = self._op_process.stdout.readline()
            self._handle_message(message)

    def step(self, action):
        if self._active_side != self.agent_side:
            raise protocol.IllegalMoveException('It is not your turn to move.')

        reward = 0

        done = self._handle_move(action)

        # If it is the opponent's turn, let them play until it is no longer
        # their turn.
        while self._active_side == self._op_side and not done:
            message = self._op_process.stdout.readline()
            done = self._handle_message(message)

        return self.get_state(), reward, done, {}

    def get_state(self):
        if self.kalah is None:
            return None

        state = copy.deepcopy(self.kalah.board.board)
        if self.agent_side == Side.SOUTH:
            state[0] = state[0][1:]
            state[1] = state[1][1:]
        else:
            state_0 = copy.deepcopy(state[0][1:])
            state[0] = state[1][1:]
            state[1] = state_0

        return state

    def get_score(self):
        return self.kalah.board.getSeedsInStore(
            self.agent_side
        ) - self.kalah.board.getSeedsInStore(self._op_side)

    def _handle_message(self, message):
        done = False
        msg_type = protocol.getMsgType(message)
        if (
            msg_type == protocol.MsgType.SWAP and KalahEnv.allow_swapping
            and self.move_count == 2
        ):
            # Swap player sides.
            self.agent_side, self._op_side = (
                self._op_side, self.agent_side
            )

            # Swap active side.
            # self._active_side = self._active_side.opposite()

            print('Move: Swap')

            if self._active_side == self._op_side:
                self._op_process.stdin.write(
                    protocol.createSwapInfoMsg(self.kalah.board)
                )

            self.move_count += 1
        else:
            if msg_type != protocol.MsgType.MOVE:
                raise protocol.InvalidMessageException(
                    'Expected a move message.'
                )

            hole = protocol.interpretMoveMsg(message)

            if hole < 1:
                raise protocol.InvalidMessageException(
                    f'Expected a positive integer but got {hole}.'
                )

            # Get move from opponent and make it.
            move = Move(self._active_side, hole)
            done = self._handle_move(move)

        return done

    def _handle_move(self, move):
        if not self.kalah.isLegalMove(move):
            raise protocol.IllegalMoveException(str(move.getSide()) + str(move.getHole()))
        turn = self.kalah.makeMove(move)

        # Update active side. On the first turn you can only make one move.
        if self.move_count == 1 or turn != self._active_side:
            self._active_side = self._active_side.opposite()

        # Check if game should end.
        done = self.kalah.gameOver()

        # Notify opponent of finished move.
        self._op_process.stdin.write(
            protocol.createStateMsg(
                move,
                self.kalah.board,
                done,
                self._active_side == self._op_side,
            )
        )

        self.move_count += 1

        return done


class KalahEngine():
    """
    Java Kalah engine translated to Python. This is just here to refer to and
    we shouldn't actually use it.
    """
    starting_side = Side.SOUTH
    holes = 7
    seeds = 7
    print_board_to_stderr = True
    allow_swapping = True

    def __init__(self, kalah, player_north, player_south):
        self.kalah = kalah
        self.player_north = player_north
        self.player_south = player_south

    def run_match(self, starting_side):
        waiting_player = None
        active_player = None
        aborting_player = None

        if starting_side == Side.NORTH:
            active_player = self.player_north
            waiting_player = self.player_south
        else:
            active_player = self.player_south
            waiting_player = self.player_north

        try:
            try:
                self.player_north.send_message(
                    protocol.createStartMsg(Side.NORTH)
                )
            except IOError:
                aborting_player = self.player_north
                raise

            try:
                self.player_south.send_message(
                    protocol.createStartMsg(Side.SOUTH)
                )
            except IOError:
                aborting_player = self.player_south
                raise

            # Loop until game ends.
            game_over = False
            move_count = 1
            while not game_over:
                agent_message = active_player.get_reader_thread(
                ).receive_message()
                active_player.increment_move_count()
                active_player.increment_overall_response_time()
                msg_type = protocol.getMsgType(agent_message)

                if msg_type == protocol.MsgType.SWAP and move_count == 2:
                    # Swap player sides.
                    self.player_north.change_side()
                    self.player_south.change_side()
                    self.player_north, self.player_south = (
                        self.player_south, self.player_north
                    )

                    # Swap active and waiting player.
                    active_player, waiting_player = (
                        waiting_player, active_player
                    )

                    print('Move: Swap')

                    active_player.send_message(
                        protocol.createSwapInfoMsg(self.kalah.board)
                    )
                else:
                    if msg_type != protocol.MsgType.MOVE:
                        raise protocol.InvalidMessageException(
                            'Expected a move message.'
                        )

                    hole = protocol.interpretMoveMsg(agent_message)

                    if hole < 1:
                        raise protocol.InvalidMessageException(
                            f'Expected a positive integer but got {hole}.'
                        )

                    # Get move from player and make it.
                    move = Move(active_player.get_side(), hole)
                    if not self.kalah.isLegalMove(move):
                        raise protocol.IllegalMoveException()
                    turn = self.kalah.makeMove(move)

                    # On the first turn you can only make one move.
                    if move_count == 1:
                        turn = waiting_player.get_side()

                    # Check if game should end.
                    game_over = self.kalah.gameOver()

                    # Swap active and waiting player if necessary.
                    if turn != active_player.get_side():
                        active_player, waiting_player = (
                            waiting_player, active_player
                        )

                    # Notify waiting player of finished move.
                    try:
                        waiting_player.send_message(
                            protocol.createStateMsg(
                                move, self.kalah.board, game_over, False
                            )
                        )
                    except IOError:
                        aborting_player = waiting_player
                        raise
                    active_player.send_message(
                        protocol.createStateMsg(
                            move, self.kalah.board, game_over, True
                        )
                    )

                move_count += 1
        except protocol.InvalidMessageException as e:
            aborting_player = active_player
            print(
                f'Error: Invalid message. {e} Agent {aborting_player.name} '
                'does not obey the protocol.'
            )
        except protocol.IllegalMoveException:
            aborting_player = active_player
            print(
                f'Error: Agent {aborting_player.name} tried to perform an '
                'illegal move.'
            )
        except IOError as e:
            if aborting_player is None:
                aborting_player = active_player
            print(
                f'Error: Connection to agent {aborting_player.name} broke '
                f'down. {e}'
            )

            sane_player = None
            if aborting_player == self.player_north:
                sane_player = self.player_south
            else:
                sane_player = self.player_north

            try:
                sane_player.send_message(protocol.createEndMsg())
            except IOError:
                pass
            skip_end_messages = True

        if not skip_end_messages:
            end_message = protocol.createEndMsg()
            for player in (self.player_north, self.player_south):
                try:
                    player.send_message(end_message)
                except IOError:
                    pass

        return aborting_player
