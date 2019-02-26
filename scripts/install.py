import os
import sys
import subprocess

SUBMODULES = [
    "robotic_warehouse", "utilities",
    "strategies/baselines_greedy_closest_wares", "strategies/baselines_random"
]


class InstallationException(Exception):
    def __init__(self, cause):
        self.cause = cause

    def __str__(self):
        return "Installation Exception: {}".format(self.cause)


def setup_submodules(logger) -> bool:
    logger.info("Installing git submodules")
    try:
        subprocess.run(["git", "submodule", "init"]).check_returncode()
        subprocess.run(
            ["git", "submodule", "update", "--recursive",
             "--remote"]).check_returncode()
    except subprocess.CalledProcessError as e:
        logger.error("Failed to install submodules: {}".format(e))
        return False
    else:
        logger.info("Installing git submodules was successful")
        return True


def validate_submodules(logger) -> bool:
    def validate(name):
        content = None
        try:
            content = os.listdir(name)
        except FileNotFoundError:
            raise InstallationException("No such directory {}".format(name))

        if len(content) < 2:
            raise InstallationException(
                "Module does not seem to be initialized {} - {}".format(
                    name, content))

    try:
        for module in SUBMODULES:
            validate(module)
    except InstallationException as e:
        logger.error("Cannot validate submodules\n   {}".format(e))
        return False
    else:
        logger.info("Submodules validated")
        return True


def install_submodule_dependencies(logger) -> bool:
    cwd = os.getcwd()
    success = True
    for module in SUBMODULES:
        if os.path.isdir(module):
            os.chdir(module)

            if os.path.isfile("setup.py"):
                logger.info("Installing {}".format(module))

                try:
                    subprocess.run(["python3", "setup.py",
                                    "install"]).check_returncode()
                except subprocess.CalledProcessError as e:
                    logger.error(
                        "Setup of {} failed -- Reason: {} -- Continuing with others".
                        format(module, e))
                    success = False
                else:
                    logger.info("{} installed".format(module))

            else:
                logger.error(
                    "Cannot find setup.py in {} -- ls gives {} -- Ignoring..".
                    format(os.getcwd(), os.listdir(".")))
                success = False
        else:
            logger.error(
                "Cannot find directory {} -- current CWD {} -- Ignoring..".
                format(module, os.getcwd()))
            success = False

        os.chdir(cwd)

    return success


def run(logger) -> None:
    if not setup_submodules(logger):
        logger.error("Stopping installation -- Submodule setup failed")

    # TODO: Add some fall back?
    if not validate_submodules(logger):
        logger.error("Stopping installation -- Submodule validation failed")

    # TODO: Add some fall backs?
    if not install_submodule_dependencies(logger):
        logger.error(
            "Installation of some dependencies failed -- maybe that is ok?")

    if not os.path.isdir("data"):
        os.mkdir("data")
