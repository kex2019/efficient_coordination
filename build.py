import robotic_warehouse_utils.data_collection as data_collection
import importlib
import logging
import colorlog
import pandas as pd
import argparse
import time
import scripts.install
logger = logging.getLogger("Kex2019")

handler = colorlog.StreamHandler()
formatter = colorlog.ColoredFormatter(
    fmt=('%(log_color)s[%(asctime)s %(levelname)8s] --'
         ' %(message)s (%(filename)s:%(lineno)s)'),
    datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)

logger.setLevel(20)
logger.addHandler(handler)


def rprd_eval(name: str, module: "f: eval") -> None:
    module.evaluate(
        render=False,
        robots=20,
        spawn=100,
        shelve_length=5,
        shelve_width=5,
        shelve_height=5,
        steps=1000)


def cwcw_eval(name: str, module: "f: eval") -> None:
    module.evaluate(
        render=False,
        robots=20,
        spawn=100,
        shelve_length=5,
        shelve_width=5,
        shelve_height=5,
        steps=1000)


STRATEGIES = {
    "random_package_random_drop":
    ["baselines_random.random_package_random_drop", rprd_eval],
    "closest_ware_closest_drop":
    ["baseline_greedy_closest_wares.closest_ware_closest_drop", cwcw_eval]
    # TODO ... add more
}


def eval_strategies() -> None:
    """ This should populate the data directory with data from all evaluations. """
    logger.info("Evaluating Strategies")
    for index, (name, (module_name, E)) in enumerate(STRATEGIES.items()):
        module_spec = importlib.util.find_spec(module_name)
        if module_spec:
            logger.info("Strategy {} - {}".format(index, name))
            timestamp = time.time()
            try:
                E(name, importlib.import_module(module_name))
            except data_collection.EvaluationDone:
                logger.info(
                    "Duration {} seconds".format(time.time() - timestamp))
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
        "--make_plots", help="Make plots for results", action="store_true")
    parser.add_argument(
        "--install",
        help="Install everything -- submodules -- deps -- the whole bunch",
        action="store_true")
    args = parser.parse_args()

    if args.install:
        scripts.install.run(logger)

    if args.evaluate:
        eval_strategies()

    if args.make_plots:
        make_plots()
