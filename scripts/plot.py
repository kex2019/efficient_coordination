import configparser
import os
import sys
import pandas as pd
import numpy as np
import seaborn as sb
import matplotlib.pyplot as plt

LATENCY = "latency"
COLLISION = "collision"
THROUGHPUT = "throughput"
SIMULATION = "simulation"
EFFICIENCY = "efficiency"


class _plot_config():
    def __init__(self, names: [str], types: [int], merge: bool, data_dir: str,
                 output_dir: "str"):
        self.names = names
        self.types = types
        self.merge = merge
        self.data_dir = data_dir
        self.output_dir = output_dir

    def __str__(self):
        return "{} {} {} {}".format(self.names, self.types, self.merge,
                                    self.output_dir)


class _data():
    def __init__(self, name: str, type: str, data: pd.DataFrame):
        self.name = name
        self.type = type
        self.data = data


def _interactive(logger):
    print("interactive Plot")


def plot(logger):
    dirr = os.listdir(".")

    config_files = [f for f in os.listdir(".") if ".conf" in f]
    config_file = None
    if len(config_files) == 0:
        logger.warning(
            "No config file found - will ask for information on stdin when needed"
        )
        _interactive(logger)
        return

    if len(config_files) > 1:
        logger.warning(
            "There are more than one config file - please specify which one")
        logger.warning(" *** ".join(
            ["{} - {}".format(num, f) for num, f in enumerate(config_files)]))
        file_num = int(input("Number: "))

        config_file = config_files[file_num]
    else:
        config_file = config_files[0]

    config = configparser.ConfigParser()

    logger.info("Plotting with {}".format(config_file))
    config.read(config_file)

    if "names" not in config:
        logger.error("Config missing section names")
        return

    if "types" not in config:
        logger.error("Config missing section types")
        return

    if "meta" not in config:
        logger.error("Config missing section meta")
        return

    if "merge" not in config["meta"]:
        logger.error("section meta is missing field merge")
        return

    if "data_dir" not in config["meta"]:
        logger.error("section meta is missing field data_dir")
        return

    if "output_dir" not in config["meta"]:
        logger.error("section meta is missing field output_dir")
        return

    names = [n for n in config["names"] if config["names"].getboolean(n)]
    types = [t for t in config["types"] if config["types"].getboolean(t)]
    merge = config["meta"].getboolean("merge")
    data_dir = config["meta"]["data_dir"]
    output_dir = config["meta"]["output_dir"]

    _plot(logger, _plot_config(names, types, merge, data_dir, output_dir))


def _get_data(logger, data_dir: str, names: [str], types: [str]) -> [_data]:
    if not os.path.isdir(data_dir):
        logger.error("{} is not a directory".format(data_dir))
        return

    files = os.listdir(data_dir)

    datas = []
    for name in names:
        nfiles = [f for f in files if name in f]
        """ Get specified types """
        for t in types:
            """ Efficiency is a special case. """
            if t == EFFICIENCY:
                t = SIMULATION

            file = None
            for f in nfiles:
                if t in f:
                    file = f
                    break

            if file != None:
                try:
                    csv = pd.read_csv("{}/{}".format(data_dir, file))
                    datas.append(_data(name, t, csv))
                except pd.errors.EmptyDataError as e:
                    logger.error("Unable to parse {}/{} -- REASON: {}".format(
                        data_dir, file, e))

            else:
                logger.error(
                    "File with name {} & type {} not found in {}".format(
                        name, t, data_dir))

    return datas


def _plot(logger, config: _plot_config) -> None:
    datas = _get_data(logger, config.data_dir, config.names, config.types)

    if config.merge:
        for t in config.types:
            """ Efficiency is a special case since it needs several data sources. """
            if t == EFFICIENCY:
                throughputs = [
                    data for data in datas if data.type == THROUGHPUT
                ]
                latencies = [data for data in datas if data.type == LATENCY]
                simulation = [
                    data for data in datas if data.type == SIMULATION
                ]

                if len(throughputs) == len(latencies) == len(
                        simulation) == len(config.names):
                    latencies = list(
                        map(lambda d: d.data,
                            sorted(
                                latencies,
                                key=lambda x: config.names.index(x.name))))
                    throughputs = list(
                        map(lambda d: d.data,
                            sorted(
                                throughputs,
                                key=lambda x: config.names.index(x.name))))
                    simulation = list(
                        map(lambda d: d.data,
                            sorted(
                                simulation,
                                key=lambda x: config.names.index(x.name))))
                    _plot_efficiency_group(logger, config.names,
                                           zip(throughputs, latencies,
                                               simulation), config.output_dir)
                else:
                    logger.error(
                        "Failed to plot efficiency group for {} because data were missing".
                        format(" ".join(config.names)))
            elif t == LATENCY:
                latencies = [data for data in datas if data.type == LATENCY]
                if len(throughputs) == len(config.names):
                    latencies = list(
                        map(lambda d: d.data,
                            sorted(
                                latencies,
                                key=lambda x: config.names.index(x.name))))
                    _plot_latency_group(logger, config.names, latencies,
                                        config.output_dir)
                else:
                    logger.error("Missing data for latency group plot")
            elif t == THROUGHPUT:
                throughputs = [
                    data for data in datas if data.type == THROUGHPUT
                ]
                if len(throughputs) == len(config.names):
                    throughputs = list(
                        map(lambda d: d.data,
                            sorted(
                                throughputs,
                                key=lambda x: config.names.index(x.name))))
                    _plot_throughput_group(logger, config.names, throughputs,
                                           config.output_dir)
                else:
                    logger.error("Missing data for throughputs group plot")
            elif t == COLLISION:
                collisions = [data for data in datas if data.type == COLLISION]
                if len(collisions) == len(config.names):
                    collisions = list(
                        map(lambda d: d.data,
                            sorted(
                                collisions,
                                key=lambda x: config.names.index(x.name))))
                    _plot_collisions(logger, config.names, collisions,
                                     config.output_dir)
                else:
                    logger.error("Missing data for collisions group plot")
            else:
                logger.error("Unknown plotting type {}".format(t))
    else:
        for d in datas:
            if d.type == LATENCY:
                _plot_latency(logger, d.name, d.data, config.output_dir)
            elif d.type == THROUGHPUT:
                _plot_throughput(logger, d.name, d.data, config.output_dir)
            elif d.type == COLLISION:
                _plot_collisions(logger, d.name, d.data, config.output_dir)
            elif d.type == SIMULATION:
                """ Need throughput & latency datas too """
                throughput = [
                    data for data in datas
                    if data.type == THROUGHPUT and data.name == d.name
                ]
                latency = [
                    data for data in datas
                    if data.type == LATENCY and data.name == d.name
                ]

                if len(throughput) == len(latency) == 1:
                    _plot_efficiency(
                        logger, d.name,
                        (throughput[0].data, latency[0].data, d.data),
                        config.output_dir)
                else:
                    logger.error(
                        "Missing data for efficiency plot of {}".format(
                            d.name))
            else:
                logger.error("Unknown plotting type {}".format(d.type))


""" These are simple plots we will have to think abit about how we want to plot it later. """


def _plot_latency(logger, name: str, latency: pd.DataFrame,
                  output_dir: str) -> None:
    logger.info("Plotting latency {} -- output {}".format(name, output_dir))


def _plot_throughput(logger, name: str, throughput: pd.DataFrame,
                     output_dir: str) -> None:
    logger.info("Plotting throughput {} -- output {}".format(name, output_dir))


def _plot_collisions(logger, name: str, collisions: pd.DataFrame,
                     output_dir: str) -> None:
    logger.info("Plotting collisions {} -- output {}".format(name, output_dir))


def _plot_efficiency(logger, name: str,
                     efficiency: (pd.DataFrame, pd.DataFrame,
                                  pd.DataFrame), output_dir: str) -> None:
    logger.info("Plotting efficiency {} -- output {}".format(name, output_dir))


def _plot_latency_group(logger, names: [str], latencies: [pd.DataFrame],
                        output_dir: str) -> None:
    logger.info("Plotting latency group {} -- output {}".format(
        " ".join(names), output_dir))

    fig, (drops, slowest, average) = plt.subplots(3, figsize=(20, 10))

    maxes = []
    averages = []
    for i, latency in enumerate(latencies):
        sb.lineplot(range(len(latency["latency"])), 
                y="latency", data=latency, ax=drops, label=names[i])
        drops.legend()


        maxes.append(max(latency["latency"]))
        averages.append(np.mean(latency["latency"]))


    sb.barplot(x=names, y=maxes, ax=slowest)
    sb.barplot(x=names, y=averages, ax=average)

    fig.savefig("{}/latencies.pdf".format(output_dir), bbox_inches='tight')


def _plot_throughput_group(logger, names: [str], throughputs: [pd.DataFrame],
                           output_dir: str) -> None:
    logger.info("Plotting throughput group {} -- output {}".format(
        " ".join(names), output_dir))


def _plot_collisions_group(logger, names: [str], collisions: [pd.DataFrame],
                           output_dir: str) -> None:
    logger.info("Plotting collisions group {} -- output {}".format(
        " ".join(names), output_dir))


def _plot_efficiency_group(logger, names: [str],
                           efficiencies: [(pd.DataFrame, pd.DataFrame,
                                           pd.DataFrame)],
                           output_dir: str) -> None:
    logger.info("Plotting efficiency group {} -- output {}".format(
        " ".join(names), output_dir))
