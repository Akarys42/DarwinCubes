import pyxel_engine as eng
import logging
from random import choice, choices, randrange
from time import time


eng.engine_setting['logging_level'] = logging.INFO
eng.engine_setting['background_color'] = '#EEEEEE'
eng.engine_setting['TPS_counter'] = True
eng.engine_setting['TPS'] = 100

directions = ((0, 1), (0, -1), (1, 0), (-1, 0))

pop = []

gen = 0


class Goal:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.sprite = eng.Sprite(self, 'goal.png')

    def is_reached(self, cube):
        if cube.x in range(self.x, self.x + 20) and cube.y in range(self.y , self.y + 8):
            return True
        else:
            return False


class Brain:
    def __init__(self, gen_data):
        if gen_data is True:
            self.data = [choice(directions) for i in range(0, 350)]
        else:
            self.data = []
        self.data_index = -1

    def next(self):
        self.data_index += 1

        if self.data_index < len(self.data):
            return self.data[self.data_index]


class DarwinCube:
    def __init__(self, x, y, gen_data=True):
        self.x = x
        self.y = y
        self.anchor = (1, 1)
        self.score = 0

        self.sprite = eng.Sprite(self, 'cube.png')

        self.brain = Brain(gen_data=gen_data)
        self.goal_reached = False

        eng.engineTick.add(self.move)

    def move(self):
        move = self.brain.next()

        if move is None:
            end_sim()
            return

        self.x += move[0]
        self.y += move[1]

        if goal.is_reached(self) is True:
            self.goal_reached = True
            try:
                eng.engineTick.remove(self.move)
            except ValueError:
                pass

    def compute_score(self):
        self.score = (int(5000 - eng.distance({'x': int(eng.engine_setting['resolution'][0] / 2),
                                               'y': int(eng.engine_setting['resolution'][1] / 4)}, self) * 10 - self.brain.data_index)) * 2

    def evolve(self):
        for i in range(0, randrange(int(len(self.brain.data) / 100), int(len(self.brain.data) / 50) + 1)):
            self.brain.data[randrange(0, len(self.brain.data) - 1)] = choice(directions)


def spawn_pop(i, x, y):
    return [DarwinCube(x, y) for i in range(i)]


def select_pop(pop):
    scorces = [cube.score for cube in pop]
    pop = choices(pop, scorces, k=len(pop))
    return pop


@eng.onEngineStarted
def run_sim():
    global pop
    global goal
    global sim_status
    sim_status = 'run'
    goal = Goal(int(eng.engine_setting['resolution'][0] / 2) - 10, int(eng.engine_setting['resolution'][1] / 4))
    pop = spawn_pop(100, int(eng.engine_setting['resolution'][0] / 2), int(eng.engine_setting['resolution'][1] / 4 * 3))


def end_sim():
    global sim_status
    global pop
    if sim_status == 'end':
        return
    sim_status = 'end'
    eng.engineTick.purge()
    eng.schedule(5, restart_sim)
    logging.info(f'Simulation {gen} ended !')


def restart_sim():
    global sim_status
    global pop
    start = time()
    for cube in pop:
        cube.compute_score()

    for cube in pop:
        cube.sprite.delete()

    pop.sort(key=lambda x: x.score, reverse=True)
    best = pop[0]
    pop = select_pop(pop)
    pop[0] = best

    new_pop = []
    for old_cube in pop:
        new_cube = DarwinCube(int(eng.engine_setting['resolution'][0] / 2), int(eng.engine_setting['resolution'][1] / 4 * 3), gen_data=False)
        new_cube.brain.data = old_cube.brain.data.copy()
        new_pop.append(new_cube)
        del old_cube

    pop = new_pop
    for cube in pop:
        cube.evolve()

    sim_status = 'run'

    logging.info(f'Evolution calculated in {str(time() - start)[:5]}s. Best score was {best.score}.')


eng.start_engine()
