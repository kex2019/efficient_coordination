import robotic_warehouse_utils.data_collection as data_collection
import importlib
import logging
import colorlog
import pandas as pd
import argparse
import time
import scripts.install
import scripts.plot
import matplotlib.pyplot as plt
import numpy as np
logger = logging.getLogger("Kex2019")

handler = colorlog.StreamHandler()
formatter = colorlog.ColoredFormatter(
    fmt=('%(log_color)s[%(asctime)s %(levelname)8s] --'
         ' %(message)s (%(filename)s:%(lineno)s)'),
    datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)

logger.setLevel(20)
logger.addHandler(handler)

RENDER = False
DEFAULT_ROBOTS = 5
DEFAULT_SPAWN = 40
DEFAULT_SHELVE_LENGTH = 3
DEFAULT_SHELVE_WIDTH = 3
DEFAULT_SHELVE_HEIGHT = 3
DEFAULT_PERIODICITY_LOWER = 500
DEFAULT_PERIODICITY_UPPER = 700
DEFAULT_STEPS = 4000
DEFAULT_SEED = int(np.random.rand() * 3000)


def rprd_eval(name: str, module: "f: eval") -> None:
    timestamp = time.time()
    try:
        module.evaluate(
            render=RENDER,
            robots=DEFAULT_ROBOTS,
            spawn=DEFAULT_SPAWN,
            shelve_length=DEFAULT_SHELVE_LENGTH,
            shelve_width=DEFAULT_SHELVE_WIDTH,
            shelve_height=DEFAULT_SHELVE_HEIGHT,
            periodicity_lower=DEFAULT_PERIODICITY_LOWER,
            periodicity_upper=DEFAULT_PERIODICITY_UPPER,
            steps=DEFAULT_STEPS,
            seed=DEFAULT_SEED,
            name="rprd")
    except data_collection.EvaluationDone:
        logger.info("Duration {} seconds".format(time.time() - timestamp))


def cwcw_eval(name: str, module: "f: eval") -> None:
    timestamp = time.time()
    try:
        module.evaluate(
            render=RENDER,
            robots=DEFAULT_ROBOTS,
            spawn=DEFAULT_SPAWN,
            shelve_length=DEFAULT_SHELVE_LENGTH,
            shelve_width=DEFAULT_SHELVE_WIDTH,
            shelve_height=DEFAULT_SHELVE_HEIGHT,
            periodicity_lower=DEFAULT_PERIODICITY_LOWER,
            periodicity_upper=DEFAULT_PERIODICITY_UPPER,
            steps=DEFAULT_STEPS,
            seed=DEFAULT_SEED,
            name="cgw")
    except data_collection.EvaluationDone:
        logger.info("Duration {} seconds".format(time.time() - timestamp))


def sh_eval(name, module: "f: eval") -> None:
    timestamp = time.time()
    try:
        module.evaluate(
            render=RENDER,
            robots=DEFAULT_ROBOTS,
            spawn=DEFAULT_SPAWN,
            shelve_length=DEFAULT_SHELVE_LENGTH,
            shelve_width=DEFAULT_SHELVE_WIDTH,
            shelve_height=DEFAULT_SHELVE_HEIGHT,
            periodicity_lower=DEFAULT_PERIODICITY_LOWER,
            periodicity_upper=DEFAULT_PERIODICITY_UPPER,
            steps=DEFAULT_STEPS,
            seed=DEFAULT_SEED,
            name="center")
    except data_collection.EvaluationDone:
        logger.info("Duration {} seconds".format(time.time() - timestamp))

    timestamp = time.time()
    try:
        module.evaluate(
            render=RENDER,
            robots=DEFAULT_ROBOTS,
            spawn=DEFAULT_SPAWN,
            shelve_length=DEFAULT_SHELVE_LENGTH,
            shelve_width=DEFAULT_SHELVE_WIDTH,
            shelve_height=DEFAULT_SHELVE_HEIGHT,
            periodicity_lower=DEFAULT_PERIODICITY_LOWER,
            periodicity_upper=DEFAULT_PERIODICITY_UPPER,
            steps=DEFAULT_STEPS,
            even=True,
            seed=DEFAULT_SEED,
            name="even")
    except data_collection.EvaluationDone:
        logger.info("Duration {} seconds".format(time.time() - timestamp))


def pfe_eval(name, module: "f: eval") -> None:
    timestamp = time.time()
    try:
        module.evaluate(
            render=RENDER,
            robots=DEFAULT_ROBOTS,
            spawn=DEFAULT_SPAWN,
            shelve_length=DEFAULT_SHELVE_LENGTH,
            shelve_width=DEFAULT_SHELVE_WIDTH,
            shelve_height=DEFAULT_SHELVE_HEIGHT,
            periodicity_lower=DEFAULT_PERIODICITY_LOWER,
            periodicity_upper=DEFAULT_PERIODICITY_UPPER,
            steps=DEFAULT_STEPS,
            seed=DEFAULT_SEED,
            name="pfe")
    except data_collection.EvaluationDone:
        logger.info("Duration {} seconds".format(time.time() - timestamp))


STRATEGIES = {
    "random_package_random_drop":
    ["baselines_random.random_package_random_drop", rprd_eval],
    "closest_ware_closest_drop":
    ["baseline_greedy_closest_wares.closest_ware_closest_drop", cwcw_eval],
    "strategy_heuristic": ["strategy_heuristic.strategy_heuristic", sh_eval],
    "potential_field_evolution": ["potential_field_evolution.pfe", pfe_eval]
}


def eval_strategies() -> None:
    """ This should populate the data directory with data from all evaluations. """
    logger.info("Evaluating Strategies")
    for index, (name, (module_name, E)) in enumerate(STRATEGIES.items()):
        module_spec = importlib.util.find_spec(module_name)
        if module_spec:
            logger.info("Strategy {} - {}".format(index, name))
            E(name, importlib.import_module(module_name))
        else:
            logger.error("Strategy {} - {} Cannot find Module {}".format(
                index, name, module_name))

    logger.info("Evaulation Done")


def make_plots() -> None:
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--evaluate", help="Evaluate Strategies", action="store_true")
    parser.add_argument(
        "--install",
        help="Install everything -- submodules -- deps -- the whole bunch",
        action="store_true")
    parser.add_argument("--user", help="Install in user", action="store_true")
    parser.add_argument("--show", help="Show plots", action="store_true")

    parser.add_argument("--plot", help="Create plots", action="store_true")
    args = parser.parse_args()

    if args.install:
        scripts.install.run(logger, args.user)

    if args.evaluate:
        eval_strategies()

    if args.plot:
        scripts.plot.plot(logger)

    if args.show:
        plt.show()
