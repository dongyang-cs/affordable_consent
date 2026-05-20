import datetime
import json
from matplotlib import spines
import pandas as pd
from tqdm import tqdm
import argparse

from Consent_Model import (
    Base_Contract,
    Contract_Affordable,
    Contract_Baseline,
    Env,
    Provider,
    Requester,
    DUO,
    TestEnum,
    RESULT_CODE,
    Environment,
    Contract,
    Contracts,
    Contract_Offline,
)

from Consent_Model import (
    disease_list,
    disease_dict,
    profile_list,
    profile_open,
    profile_medium,
    profile_strict,
    logger,
    country_code_name_dict,
    country_code_dict,
    country_order_dict,
)
import path as path
import string
import random
import matplotlib.pyplot as plt
import numpy as np
from multiprocessing import Pool, cpu_count

from enum import Enum


class Experiment_Performance:

    def __init__(
        self,
        contract_baseline: Contract_Baseline,
        contract_affordable: Contract_Affordable,
        contract_offline: Contract_Offline,
        enable_online=False,
    ):
        self.enable_online = enable_online
        self.env = contract_affordable.env
        self.contract_baseline = contract_baseline
        self.contract_affordable = contract_affordable
        self.contract_offline = contract_offline
        self.contract_list = [contract_baseline, contract_affordable, contract_offline]
        # self.contract_list = [contract_offline]
        # self.intervals = [100]
        self.intervals = [20, 40, 60, 80, 100]
        self.result_folder = path.RESULT_DIR / "performance"

    def start(self):
        for contract in self.contract_list:
            result_area = self._test_area(contract)
            result_disease_one_group = self._test_disease(contract, one_group=True)
            result_disease_whole_group = self._test_disease(contract, one_group=False)
            result = {
                "area": result_area,
                "disease_one": result_disease_one_group,
                "disease_whole": result_disease_whole_group
            }
            result_fp = (
            self.result_folder
                / f"{self.env.name}_{contract.name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            json.dump(result, open(result_fp, "w"), indent=4)


    def _test_disease(self, contract, one_group=False):
        provider1, requester1 = self._initialize_provider_requester("disease")
        disease_list_all = disease_dict["A"] if one_group else disease_list
        return self._test_upload("disease", provider1, requester1, contract, disease_list_all)

        # result_affordable_fp = (
        #     path.RESULT_DIR
        #     / f"{self.env.name}_disease_{'one' if one_group else 'whole'}_affordable_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
        # )
        # json.dump(result_affordable, open(result_affordable_fp, "w"), indent=4)
        # result_baseline_fp = (
        #     path.RESULT_DIR
        #     / f"{self.env.name}_disease_{'one' if one_group else 'whole'}_baseline_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
        # )
        # json.dump(result_baseline, open(result_baseline_fp, "w"), indent=4)
        # result_offline_fp = (
        #     self.result_folder
        #     / f"{self.env.name}_disease_{'one' if one_group else 'whole'}_offline_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
        # )
        # json.dump(result_offline, open(result_offline_fp, "w"), indent=4)

    
    

    def _test_upload(self, entity_type, provider, requester, contract, items_source=None):
        """Generic upload tester for 'area' or 'disease'.

        - entity_type: 'area' or 'disease'
        - items_source: optional list to sample from for diseases
        """
        result_list = []
        for interval in self.intervals:
            if entity_type == "area":
                items = self._generate_items(list(country_code_dict.keys()), interval)
                # logger.debug(f"Testing {entity_type} with interval {interval}%: {len(items)} items")
                provider.country_names = items
                requester.country_names = items
            elif entity_type == "disease":
                source = items_source if items_source is not None else disease_list
                items = self._generate_items(source, interval)
                provider.disease_items = items
                requester.disease_items = items
            else:
                raise ValueError(f"Unknown entity_type: {entity_type}")

            self._prepare_entities(provider, requester)

            if entity_type == "area":
                result_provider = contract.upload_area(provider)
                result_requester = contract.upload_area(requester)
            else:
                result_provider = contract.upload_disease(provider)
                result_requester = contract.upload_disease(requester)

            result_list.append(
                {
                    "interval": interval,
                    "provider": result_provider.to_dict(),
                    "requester": result_requester.to_dict(),
                }
            )
        return result_list

    def _test_area(self, contract, label=""):
        provider1, requester1 = self._initialize_provider_requester("area")
        return self._test_upload("area", provider1, requester1, contract)

        # json.dump(
        #     data_result_affordable,
        #     open(self.result_folder / f"{self.env.name}_area{label}_affordable_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json", "w"),
        #     indent=4,
        # )
        # json.dump(
        #     data_result_baseline,
        #     open(self.result_folder / f"{self.env.name}_area{label}_baseline_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json", "w"),
        #     indent=4,
        # )
        # json.dump(
        #     data_result,
        #     open(self.result_folder / f"{self.env.name}_area{label}_offline_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json", "w"),
        #     indent=4,
        # )

    def _initialize_provider_requester(self, entity_type):
        provider = Provider(
            env=self.env,
            name=f"Provider_{entity_type}",
            description=f"Provider_{entity_type}",
        )
        requester = Requester(
            env=self.env,
            name=f"Requester_{entity_type}",
            description=f"Requester_{entity_type}",
        )
        return provider, requester

    def _generate_items(self, items_list, interval):
        choiced_number = int(interval / 100 * len(items_list))
        return random.choices(items_list, k=max(1, choiced_number))

    def _prepare_entities(self, provider, requester):
        # if self.env.name == TestEnum.polygon.name:
        for contract in self.contract_list:
            contract.delete_area(provider)
            contract.delete_disease(provider)

            contract.delete_disease(requester)
            contract.delete_area(requester)
        # else:
        #     provider.address = self.env.accounts[0]
        #     requester.address = self.env.accounts[0]


class Experiment_Performance_Plotter:
    def __init__(
        self,
        env_name,
        result_folder,
        intervals,
        font_size="20",
        column_width=2.5,
        column_styles: dict | None = None,
    ):
        self.env_name = env_name
        self.result_folder = result_folder
        self.intervals = intervals
        self.font_size = font_size
        self.column_width = column_width
        self.local_baseline = json.load(
            open(f"{self.result_folder}/Local_baseline_20260517_104616.json", "r")
        )
        self.local_affordable = json.load(
            open(f"{self.result_folder}/Local_affordable_20260517_000802.json", "r")
        )
        self.local_offline = json.load(
            open(f"{self.result_folder}/Local_offline_20260517_001020.json", "r")
        )

        self.polygon_offline = json.load(
            open(f"{self.result_folder}/Polygon_offline_20260516_130700.json", "r")
        )
        self.polygon_baseline = json.load(
            open(f"{self.result_folder}/Polygon_baseline_20260516_125600.json", "r")
        )
        self.polygon_affordable = json.load(
            open(f"{self.result_folder}/Polygon_affordable_20260516_130115.json", "r")
        )

        # single source of truth for column layout and appearance
        default_styles = {
            "baseline_local": {
                "offset": -2.7,
                "label": "Baseline\n(Ganache)",
                "color": "lightcoral",
            },
            "affordable_local": {
                "offset": -1.7,
                "label": "Proposed\n(Ganache)",
                "color": "yellow",
            },
            "offline_local": {
                "offset": -0.7,
                "label": "Offline\n(Ganache)",
                "color": "violet",
            },
            "baseline_polygon": {
                "offset": 0.7,
                "label": "Baseline\n(Amoy)",
                "color": "royalblue",
            },
            "affordable_polygon": {
                "offset": 1.7,
                "label": "Proposed\n(Amoy)",
                "color": "turquoise",
            },
            "offline_polygon": {
                "offset": 2.7,
                "label": "Offline\n(Amoy)",
                "color": "skyblue",
            },
        }

        # allow caller to override styles for columns
        self.column_styles = default_styles if column_styles is None else {**default_styles, **column_styles}
        # compatibility view: label/color map derived from column_styles
 

    def _load_and_filter_results(self, polygon_name, result_type, label=""):
        # result_polygon = json.load(
        #     open(f"{self.result_folder}/{polygon_name}_{result_type}{label}.json", "r")
        # )
        polygon_baseline = self.polygon_baseline[result_type]
        polygon_affordable = self.polygon_affordable[result_type]
        polygon_offline = self.polygon_offline[result_type]

        local_baseline = self.local_baseline[result_type]
        local_affordable = self.local_affordable[result_type]
        local_offline = self.local_offline[result_type]
        result_local = [
            {
                "interval": baseline["interval"],
                "baseline": baseline,
                "affordable": affordable,
                "offline": offline,
            }
            for baseline, affordable, offline in zip(
                local_baseline, local_affordable, local_offline
            )
        ]

        result_polygon = [
             {
                "interval": baseline["interval"],
                "baseline": baseline,
                "affordable": affordable,
                "offline": offline,
            }
            for baseline, affordable, offline in zip(
                polygon_baseline, polygon_affordable, polygon_offline
            )
        ]

        # polygon_offline = json.load(
        #     open(f"{self.result_folder}/Polygon_offline_2026-05-15_09-29-28.json", "r")
        # )[result_type]
        # polygon_offline_key_interval_map = {d["interval"]: d for d in polygon_offline}
        # for d in result_polygon:
        #     interval = d["interval"]
        #     if interval in polygon_offline_key_interval_map:
        #         d["offline"] = polygon_offline_key_interval_map[interval]
        #     else:
        #         d["offline"] = None
       
        result_local = [d for d in result_local if d["interval"] in self.intervals]
        result_polygon = [d for d in result_polygon if d["interval"] in self.intervals]


        assert len(result_polygon) == len(
            result_local
        ), f"Length mismatch: {len(result_polygon)} vs {len(result_local)}"
        return result_polygon, result_local

    def _merge_plot_data(
        self, result_polygon, result_local, key_index_name, polygon_label, local_label
    ):
        return {
            f"baseline{local_label}": [
                item["baseline"]["provider"][key_index_name] for item in result_local
            ],
            f"affordable{local_label}": [
                item["affordable"]["provider"][key_index_name] for item in result_local
            ],
            f"offline{local_label}": [
                item["offline"]["provider"][key_index_name] for item in result_local
            ],
            f"baseline{polygon_label}": [
                item["baseline"]["provider"][key_index_name] for item in result_polygon
            ],
            f"affordable{polygon_label}": [
                item["affordable"]["provider"][key_index_name] for item in result_polygon
            ],
            f"offline{polygon_label}": [
                item["offline"]["provider"][key_index_name] for item in result_polygon
            ],
            "interval": [item["interval"] for item in result_local],
        }

    def _generate_column_chart(self, data, task, y_label, factor=1e3):
        data_frame = pd.DataFrame(data)
        fig, ax1 = plt.subplots(figsize=(11, 5), dpi=300)
        alpha = 1.0
        # compute x positions from configurable column_styles
        pos = {}
        for name, style in self.column_styles.items():
            pos[name] = data_frame["interval"] + style.get("offset", 0) * self.column_width

        keys = [key for key in data.keys() if key != "interval"]
        for k in keys:
            data_frame[k] = data_frame[k].astype(int)
            data_frame[k] = (data_frame[k] / factor)

        # draw bars according to configured styles
        for col_name in [
            "baseline_local",
            "affordable_local",
            "offline_local",
            "baseline_polygon",
            "affordable_polygon",
            "offline_polygon",
        ]:
            if col_name not in data_frame.columns:
                continue
            style = self.column_styles.get(col_name, {})
            x = pos.get(col_name, data_frame["interval"]) 
            label = style.get("label", col_name)
            color = style.get("color", "grey")
            ax1.bar(
                x,
                data_frame[col_name],
                width=self.column_width,
                label=label,
                color=color,
                alpha=alpha,
                edgecolor="black",
            )
        y_ticks = ax1.get_yticks()
        ax1.set_yticklabels([f"{int(y)}" for y in y_ticks], fontsize=self.font_size)
        y_max = max([data_frame[k].max() for k in keys])
        ax1.set_ylim(0, y_max * 1.05)
        ax1.set_ylabel(y_label, fontsize=self.font_size)
        intervals = [0] + data_frame["interval"].tolist()
        xticklabels = [f"{int(interval)}%" for interval in intervals]
        ax1.set_xticks(intervals)
        ax1.set_xticklabels(xticklabels, fontsize=self.font_size)

        plt.savefig(path.FIGURE_DIR / f"column_{task}_provider.pdf")

    def plot(self, label=""):
        plot_specs = [
            ("area", "time_used", "Time usage (milliseconds)", 1e6),
            ("disease_one", "time_used", "Time usage (milliseconds)", 1e6),
            ("disease_whole", "time_used", "Time usage (milliseconds)", 1e6),
            ("area", "gas_used", "Gas usage (thousand gas)", 1e3),
            ("disease_one", "gas_used", "Gas usage (thousand gas)", 1e3),
            ("disease_whole", "gas_used", "Gas usage (thousand gas)", 1e3),
        ]

        for result_type, key_index_name, y_label, factor in plot_specs:
            result_polygon, result_local = self._load_and_filter_results(
                TestEnum.polygon.name, result_type, label=label
            )
            data = self._merge_plot_data(
                result_polygon,
                result_local,
                key_index_name,
                "_polygon",
                "_local",
            )
            self._generate_column_chart(
                data,
                f"{result_type}_{key_index_name}_{label}",
                y_label,
                factor,
            )


class Simulation_Scenarios:
    def __init__(
        self, contract: Base_Contract, proportion: list, size, requesters: list
    ) -> None:
        self.proportion = proportion
        self.size = size
        self.env = contract.env
        self.contract = contract

        self.levels = (
            [profile_open for _ in range(round(proportion[0] * size))]
            + [profile_medium for _ in range(round(proportion[1] * size))]
            + [profile_strict for _ in range(round(proportion[2] * size))]
        )

        random.shuffle(self.levels)
        logger.info(f"Initial provider levels: {len(self.levels)}")
        self.provider_list = self.initial_scenarios()
        self.requester_list = requesters

    def initial_scenarios(self) -> list[Provider]:
        provider_list = []
        for i, level in enumerate(self.levels):
            provider = Provider(
                name=f"provider_{i}",
                description=f"provider_{i}",
                env=self.env,
                level=level,
                profile_dict=PROVIDER_PROFILES[level],
            )
            self.contract.upload(provider)
            provider_list.append(provider)
            # purpose = self.contract.get_purpose(provider)
            # print(
            #     f"Provider {i} with level {level} has purpose: {purpose}, profile: {provider.profile_dict}"
            # )
        return provider_list

    def _process_provider(self, provider: Provider, requesters: list[Requester]):
        provider_result = {
            "total": 0,
            "success": 0,
            "error": {},
        }

        for requester in requesters:
            access_result = self.contract.access(provider, requester=requester)
            provider_result["total"] += 1
            if not access_result:
                provider_result["success"] += 1
            else:
                for error_name in access_result:
                    if error_name in provider_result["error"]:
                        provider_result["error"][error_name] += 1
                    else:
                        provider_result["error"][error_name] = 1
        return provider_result

    def start(self):
        result_map = {}
        for provider in tqdm(self.provider_list):
            provider_result = self._process_provider(provider, self.requester_list)

            if provider.level not in result_map:
                result_map[provider.level] = {"total": 0, "success": 0, "error": {}}
            result_map[provider.level]["total"] += provider_result["total"]
            result_map[provider.level]["success"] += provider_result["success"]
            for error_name, count in provider_result["error"].items():
                if error_name in result_map[provider.level]["error"]:
                    result_map[provider.level]["error"][error_name] += count
                else:
                    result_map[provider.level]["error"][error_name] = count

        return result_map


PROVIDER_PROFILES = {
    profile_strict: {
        "purpose": [
            DUO.DiseaseSpecific,
            DUO.GeographicSpecific,
            DUO.TimeLimitOnUse,
            # DUO.GeneticStudiesOnly,
            # DUO.NonGeneralMethodResearch,
        ],
        "geography": {
            "group": 2,
            "country": 50,
        },
        "disease": ["A**", "B**", "C**"],
        "date": {
            "start_year": 2026,
            "start_month": 6,
            "start_day": 1,
            "hold_month": 6,
        },
    },
    profile_medium: {
        "purpose": [DUO.GeographicSpecific, DUO.HMBResearch, DUO.TimeLimitOnUse],
        "geography": {
            "group": 2,
            "country": 50,
        },
        "disease": ["A**", "B**", "C**"],
        "date": {
            "start_year": 2026,
            "start_month": 6,
            "start_day": 1,
            "hold_month": 12,
        },
    },
    profile_open: {
        "purpose": [DUO.HMBResearch, DUO.TimeLimitOnUse],
        "geography": {
            "group": 1.0,
            "country": ["NLD"],
        },
        "disease": 1.0,
        "date": {
            "start_year": 2026,
            "start_month": 6,
            "start_day": 1,
            "hold_month": 60,
        },
    },
}

REQUESTER_PROFILES = {
    profile_strict: {
        "purpose": [DUO.GeographicSpecific, DUO.DiseaseSpecific, DUO.TimeLimitOnUse],
        "geography": {
            "group": 0,
            "country": 1,
        },
        "disease": 1,
        "date": {
            "start_year": (2026, 2030),
            "start_month": (1, 12),
            "start_day": (1, 30),
            "hold_month": (3, 24),
        },
    },
}


class Experiment_Simulation:
    def __init__(
        self,
        contract: Base_Contract,
        requester_number=200,
        provider_number=100,
        result_fp=None,
    ):
        self.env = contract.env
        self.contract = contract
        self.requester_number = requester_number
        self.provider_number = provider_number
        self.requester_list = []
        current_time = datetime.datetime.now().strftime("%m-%d")
        if result_fp is None:
            self.result_fp = (
                path.OUTPUT_DIR / f"result/result_simulation_{current_time}.json"
            )
        else:
            self.result_fp = result_fp

        self.requester_proportion = [0, 0, 1]

        # print(random.random())

        # self.requester_list[0].update_area_group_relation()

    def init_requesters(self):

        levels = (
            [
                profile_open
                for _ in range(
                    round(self.requester_proportion[0] * self.requester_number)
                )
            ]
            + [
                profile_medium
                for _ in range(
                    round(self.requester_proportion[1] * self.requester_number)
                )
            ]
            + [
                profile_strict
                for _ in range(
                    round(self.requester_proportion[2] * self.requester_number)
                )
            ]
        )
        random.shuffle(levels)

        for i in range(self.requester_number):
            requester = Requester(
                name=f"requester_{i}",
                description=f"requester_{i}",
                env=self.env,
                profile_dict=REQUESTER_PROFILES[levels[i]],
            )
            self.contract.upload(requester)
            self.requester_list.append(requester)

            # purpose = self.contract.get_purpose(requester)
            # print(
            #     f"Requester {i} with level {levels[i]} has purpose: {purpose}, profile: {requester.profile_dict}"
            # )

    def start(self):
        self.contract.update_area_group_relation()
        self.init_requesters()
        scenarios_1 = Simulation_Scenarios(
            contract=self.contract,
            proportion=[1, 0, 0],
            size=self.provider_number,
            requesters=self.requester_list,
        )
        scenarios_2 = Simulation_Scenarios(
            contract=self.contract,
            proportion=[0.5, 0.25, 0.25],
            size=self.provider_number,
            requesters=self.requester_list,
        )
        scenarios_3 = Simulation_Scenarios(
            contract=self.contract,
            proportion=[0.2, 0.4, 0.4],
            size=self.provider_number,
            requesters=self.requester_list,
        )

        result_map_2 = scenarios_2.start()
        logger.critical(json.dumps(result_map_2))
        result_map_3 = scenarios_3.start()
        logger.critical(json.dumps(result_map_3))
        result_map_1 = scenarios_1.start()
        logger.critical(json.dumps(result_map_1))

        result_dict = {
            "scenario_1": result_map_1,
            "scenario_2": result_map_2,
            "scenario_3": result_map_3,
        }
        # logger.info(json.dumps(result_dict, indent=2))

        json.dump(result_dict, open(self.result_fp, "w"), indent=4)

    def _plot_simulation(self, data, x_stick_labels, y_label, file_name):

        alpha = 1
        if x_stick_labels is None:
            x_stick_labels = list(data.keys())
        # Extract data points

        success_rates = [
            data[label]["success"] * 100 / data[label]["total"]
            for label in x_stick_labels
        ]

        # Create a bar chart
        x = np.arange(len(x_stick_labels))  # the label locations
        width = 0.4  # the width of the bars

        fig, ax = plt.subplots(figsize=(5, 3))
        bars = ax.bar(
            x,
            success_rates,
            width,
            label="Success Rate",
            alpha=alpha,
            color="royalblue",
            edgecolor="black",
        )

        # Add some text for labels, title and custom x-axis tick labels, etc.
        # ax.set_xlabel("Categories" if title is None else title)
        ax.set_ylabel(y_label)
        ax.set_xticks(x)
        ax.set_ylim(0, max(success_rates) + 10)
        ax.set_xticklabels(x_stick_labels)

        # Add labels to the bars
        def add_labels(bars):
            for bar in bars:
                height = bar.get_height()
                ax.annotate(
                    f"{height:.2f}%",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                )

        add_labels(bars)

        # Save the chart
        plt.savefig(file_name)

    def plot_simulation_category(self):
        data = json.load(open(self.result_fp, "r"))
        category_dict = dict()

        for k, v in data.items():
            for category, value in v.items():
                total = value["total"]
                success = value["success"]
                error = value["error"]
                if category not in category_dict:
                    category_dict[category] = {
                        "total": 0,
                        "success": 0,
                        "error": {},
                    }

                category_dict[category]["total"] += total
                category_dict[category]["success"] += success
                for k, v in error.items():
                    if k not in category_dict[category]["error"]:
                        category_dict[category]["error"][k] = 0
                    category_dict[category]["error"][k] += v

        self._plot_simulation(
            data=category_dict,
            x_stick_labels=profile_list,
            y_label="Success Rate (%)",
            file_name=path.FIGURE_DIR / "simulation_category.pdf",
            # title="Categories",
        )

    def plot(self, result_fp=None):
        if result_fp is not None:
            self.result_fp = result_fp
        self.plot_simulation_category()
        self.plot_simulation_scenario()

    def plot_simulation_scenario(self):
        data = json.load(open(self.result_fp, "r"))
        scenario_dict = dict()
        for k, v in data.items():
            total = sum([value["total"] for value in v.values()])
            success = sum([value["success"] for value in v.values()])
            error = {k: v for value in v.values() for k, v in value["error"].items()}
            scenario_dict[k] = {
                "total": total,
                "success": success,
                "error": error,
            }
        x_labels = list(scenario_dict.keys())
        # x_labels = [label.capitalize() for label in x_labels]

        self._plot_simulation(
            data=scenario_dict,
            x_stick_labels=x_labels,
            y_label="Success Rate (%)",
            file_name=path.FIGURE_DIR / "simulation_scenario.pdf",
            # title="Scenarios",
        )


class Experiment_Case_Study:
    def __init__(self, contract: Base_Contract):
        if contract.env.name != TestEnum.local.name:
            raise ValueError("Case study is only supported in local environment")
        self.env = contract.env
        self.contract = contract
        self.init_person()
        self.result_map = {
            RESULT_CODE.GeographicSpecific.name: r"\faFlag[regular]",
            RESULT_CODE.DiseaseSpecific.name: r"\faCapsules",
            RESULT_CODE.TimeLimitOnUse.name: r"\faCalendar*[regular]",
            # RESULT_CODE.GeographicSpecificRestriction: r"\circletfillhl",
        }
        self.error_other = r"\circletfillhl"

    def init_person(self):
        provider1 = Provider(
            name="Provider a",
            env=self.env,
            description=r"Provider.\ref{provider:a}",
            bool_items={DUO.DiseaseSpecific, DUO.GeographicSpecific},
            country_names=["USA"],
            group_names=["EU"],
            disease_items=["A**", "B**"],
            address=self.env.accounts.pop(),
        )
        provider2 = Provider(
            name="Provider b",
            env=self.env,
            description=r"Provider.\ref{provider:b}",
            bool_items={DUO.DiseaseSpecific, DUO.GeographicSpecific},
            country_names=["USA"],
            group_names=["EU"],
            disease_items=["A**", "B01"],
            address=self.env.accounts.pop(),
        )

        provider3 = Provider(
            name="Provider c",
            env=self.env,
            description=r"Provider.\ref{provider:c}",
            bool_items={
                DUO.GeographicSpecific,
                DUO.TimeLimitOnUse,
                DUO.DiseaseSpecific,
                DUO.GeneticStudiesOnly,
            },
            group_names=["EU"],
            disease_items=["A**"],
            start_year=2026,
            start_month=1,
            start_day=1,
            hold_month=6,
            address=self.env.accounts.pop(),
        )


        requester1 = Requester(
            name="Requester 1",
            env=self.env,
            description=r"Requester.\ref{requester:1}",
            bool_items={DUO.DiseaseSpecific, DUO.GeographicSpecific, DUO.TimeLimitOnUse},
            disease_items=["A01"],
            country_names=["USA"],
            start_year=2026,
            start_month=1,
            start_day=1,
            hold_month=6,
            address=self.env.accounts.pop(),
        )
        requester2 = Requester(
            name="Requester 2",
            env=self.env,
            description=r"Requester.\ref{requester:2}",
            bool_items={DUO.DiseaseSpecific, DUO.GeographicSpecific, DUO.TimeLimitOnUse},
            disease_items=["B02"],
            country_names=["THA", "USA"],
            start_year=2026,
            start_month=1,
            start_day=1,
            hold_month=6,
            address=self.env.accounts.pop(),
        )

        requester3 = Requester(
            name="Requester 3",
            env=self.env,
            description=r"Requester.\ref{requester:3}",
            bool_items={DUO.DiseaseSpecific, DUO.GeographicSpecific, DUO.TimeLimitOnUse},
            disease_items=["B01"],
            country_names=["NLD"],
            group_names=["EU"],
            start_year=2026,
            start_month=1,
            start_day=1,
            hold_month=6,
            address=self.env.accounts.pop(),
        )

        requester4 = Requester(
            name="Requester 4",
            env=self.env,
            description=r"Requester.\ref{requester:4}",
            bool_items={DUO.DiseaseSpecific, DUO.GeographicSpecific, DUO.TimeLimitOnUse},
            disease_items=["A02"],
            country_names=["USA"],
            start_year=2026,
            start_month=1,
            start_day=1,
            hold_month=12,
            address=self.env.accounts.pop(),
        )

        requester5 = Requester(
            name="Requester 5",
            env=self.env,
            description=r"Requester.\ref{requester:5}",
            bool_items={
                DUO.GeographicSpecific,
                DUO.DiseaseSpecific,
                DUO.TimeLimitOnUse,
                DUO.GeneticStudiesOnly,
            },
            disease_items=["A01"],
            group_names=["EU"],
            start_year=2026,
            start_month=1,
            start_day=1,
            hold_month=6,
            address=self.env.accounts.pop(),
        )


        r = self.contract.update_area_group_relation()
        # v,c,g = provider1.contract.functions.DisplayCountryGroupRelation().call()
        print("update_area_group_code ", r)

        self.provider_list = [provider1, provider2, provider3]
        self.requester_list = [
            requester1,
            requester2,
            requester3,
            requester4,
            requester5,
        ]
        try:
            for i, requester in enumerate(self.requester_list):
                requester.description = f"Requester.\\ref{{requester:{i+1}}}"
                self.contract.upload(requester)
        except:
            logger.info(f"requester {requester.name} address {requester.address}")
            # print(w3.eth.block_number)

        for provider in self.provider_list:
            self.contract.upload(provider)

    def start(self):

        result_list = []
        header_list = [""]
        for provider in self.provider_list:
            header_list.append(provider.description)

        result_list.append("&".join(header_list) + r"\\")
        for ir, requester in enumerate(self.requester_list):
            row_list = []
            row_list.append(requester.description)
            for ip, provider in enumerate(self.provider_list):
                access_result = self.contract.access(provider, requester)
                access_str = []
                for error in access_result:
                    access_str.append(self.result_map.get(error, self.error_other))

                if len(access_str) == 0:
                    access_result = r"\cmark"
                else:
                    access_result = " ".join(access_str)
                row_list.append(access_result)
                # requester.access_area_simple(provider)
                # requester.access_disease(provider)
            result_list.append("&".join(row_list) + r"\\")

        print("\n".join(result_list))


def main():
    parser = argparse.ArgumentParser(description="Consent Experiments Runner")
    parser.add_argument(
        "--env",
        choices=["local", "polygon"],
        default="local",
        help="Environment to use: local or polygon",
    )
    parser.add_argument("--case_study", default=True, action="store_true", help="Run case study experiment")
    parser.add_argument("--simulation", default=False, action="store_true", help="Run simulation experiment")    
    parser.add_argument("--performance", default=False, action="store_true", help="Run performance experiment")

    force_deploy = False

    args = parser.parse_args()
    contracts = Contracts()
    # Setup environment
    environment = Environment()
    if args.env == "local":
        baseline_contract = Contract_Baseline(
            environment.deploy_contract_local(contracts.interface_baseline)
        )
        affordable_contract = Contract_Affordable(
            environment.deploy_contract_local(contracts.interface_affordable)
        )
        offline_contract = Contract_Offline(environment.deploy_contract_local(contracts.interface_offline))
    else:
        baseline_contract = Contract_Baseline(
            environment.deploy_contract_polygon(contracts.interface_baseline, force_deploy=force_deploy)
        )
        affordable_contract = Contract_Affordable(
            environment.deploy_contract_polygon(contracts.interface_affordable, force_deploy=force_deploy)
        )
        offline_contract = Contract_Offline(
            environment.deploy_contract_polygon(contracts.interface_offline, force_deploy=force_deploy)
        )
    # Run experiments
    if args.case_study:
        Experiment_Case_Study(affordable_contract).start()

    if args.simulation:
        experiment_simulation = Experiment_Simulation(
            affordable_contract, provider_number=100, requester_number=1000
        )
        # experiment_simulation.start()
        result_fp = args.result_fp or (path.RESULT_DIR / "result_simulation_09-04-11-44.json")
        experiment_simulation.plot()

    if args.performance:
        performance = Experiment_Performance(
            contract_affordable=affordable_contract, contract_baseline=baseline_contract, contract_offline=offline_contract
        )
        performance.start()
        performance_plotter =Experiment_Performance_Plotter(args.env, performance.result_folder, performance.intervals)
        performance_plotter.plot()


if __name__ == "__main__":
    main()
