import math
from collections import Counter
from dataclasses import dataclass, field
from typing import Optional, Union, List, Any, Sequence
from numbers import Number
from statistics import mean

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.colors import ListedColormap
import numpy as np

from .trajectory import Trajectory
from . import util


@dataclass
class GridStyle:
    title: str = ""
    label_font_size: int = 14
    tick_font_size: int = 14
    title_font_size: int = 14
    # todo :: with so many optionals maybe this is a mess :)
    # todo :: the following labels are unused, do we want to support?
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    rotate_x_labels: bool = False
    checker_light: Sequence[float] = (220 / 256, ) * 3
    checker_dark: Sequence[float] = (1, ) * 3
    connection_style: str = "arc3,rad=0.0",
    arrow_style: str = "-|>",


# todo :: is this ideal class name? maybe.
@dataclass
class GridQuantization:
    cell_size_x: Optional[int] = None
    cell_size_y: Optional[int] = None
    # todo :: consider axis-values type for str, Number
    x_order: Optional[List[Union[str, Number]]] = None
    y_order: Optional[List[Union[str, Number]]] = None
    # todo :: the following x/y_min/max are unused, do we want to support?
    x_min: Optional[int] = None  # todo :: are they floats?
    x_max: Optional[int] = None
    y_min: Optional[int] = None
    y_max: Optional[int] = None


@dataclass
class GridMeasures:
    # todo :: all of these fields probably want to be methods
    trajectory_ids: list = field(default_factory=lambda: [])
    mean_duration: float = 0
    mean_number_of_events: float = 0  # todo float ye?
    mean_number_of_visits: float = 0
    mean_cell_range: float = 0
    overall_cell_range: float = 0
    mean_duration_per_event: float = 0
    mean_duration_per_visit: float = 0
    mean_duration_per_cell: float = 0
    dispersion: float = 0
    #mean_missing_events: float = 0
    #mean_missing_duration: float = 0
    visited_entropy: float = 0
    #duration_entropy: float = 0


@dataclass
class Grid:
    trajectory_list: List[Trajectory]
    quantization: GridQuantization = field(default=GridQuantization)

    def __shared_all_trajectory_process(self):
        # todo :: sensible name :)
        x_min = self.trajectory_list[0].data_x[0]
        y_min = self.trajectory_list[0].data_y[0]
        x_max = x_min
        y_max = y_min

        # todo :: consider this logic when a subset is None?
        # does that even make any sense?
        # if not, can cover with some simpler logic
        if self.quantization.x_min is not None:
            x_min = self.quantization.x_min
        if self.quantization.x_max is not None:
            x_max = self.quantization.x_max

        if self.quantization.y_min is not None:
            y_min = self.quantization.y_min
        if self.quantization.y_max is not None:
            y_max = self.quantization.y_max

        max_duration = 0
        loops_list = []
        for trajectory in self.trajectory_list:
            x_data, y_data, t_data, loops = trajectory.get_states(
                self.quantization.x_order,
                self.quantization.y_order,
            )

            # Get min and max values
            # todo :: this is probably silly...

            def calculate_min_max(values):
                """assumes categorical = string, ordinal = numeric"""
                # todo :: there may be a better way to deal with these multiple cases
                if isinstance(values[0], str):
                    return 0, len(values)
                return int(min(values)), math.ceil(max(values))

            temp_x_min, temp_x_max = calculate_min_max(x_data)
            temp_y_min, temp_y_max = calculate_min_max(y_data)

            max_duration = max(*(t2 - t1 for t1, t2 in zip(t_data, t_data[1:])), max_duration)
            x_min = min(x_min, int(temp_x_min))
            y_min = min(y_min, int(temp_y_min))
            x_max = max(x_max, int(temp_x_max))
            y_max = max(y_max, int(temp_y_max))
            # todo :: is there a necessary loops reset I've accidentally removed?
            loops_list.append(loops)
        return max_duration, x_min, y_min, x_max, y_max, loops_list

    def __get_rounded_parameters(self, x_min, x_max, y_min, y_max):
        # todo :: types will make the weird rounding behaviour here obvious, I hope...
        """returns:
        (
            cell width,
            cell height,
            rounded x min,
            rounded y min,
            rounded x max,
            rounded y max,
        )
        """

        def calculate_scale(difference):
            """
            return desired scale
            implemented as the biggest power of 10 smaller than the difference
            """
            scale_factor = 1
            while scale_factor < difference:
                scale_factor *= 10
            while scale_factor > difference:
                scale_factor /= 10
            return scale_factor

        cell_size_x = self.quantization.cell_size_x or calculate_scale(x_max - x_min)
        cell_size_y = self.quantization.cell_size_y or calculate_scale(y_max - y_min)
        def something_round(v, cell):
            # todo :: what is this surely there's builtins
            return v + cell - (v % cell or cell)
        return (
            cell_size_x,
            cell_size_y,
            x_min - (x_min % cell_size_x),
            y_min - (y_min % cell_size_y),
            something_round(x_max, cell_size_x),
            something_round(y_max, cell_size_y),
        )

    def draw(
        self,
        save_as: Optional[str] = None,
        style: GridStyle = field(default_factory=GridStyle),
    ):
        """
        if save_as is None, will .show() the plot
        """
        graph = nx.Graph()
        ax = plt.gca()

        # todo :: seems like some weirdness in what we're actually getting out here
        # probably should refactor return values etc (separate functions?)
        max_duration, x_min, y_min, x_max, y_max, loops_list = self.__shared_all_trajectory_process()

        cell_size_x, cell_size_y, rounded_x_min, rounded_y_min, rounded_x_max, rounded_y_max \
            = self.__get_rounded_parameters(x_min, x_max, y_min, y_max)

        # draw background
        # todo :: whole bunch of stuff that is a bit messy here
        # Make an estimate for scale size of checkerboard grid sizing
        ax.set_xlim([
            rounded_x_min - cell_size_x / 2,
            rounded_x_max + cell_size_x / 2,
        ])
        ax.set_ylim([
            rounded_y_min - cell_size_y / 2,
            rounded_y_max + cell_size_y / 2,
        ])
        ax.imshow(
            # checkerboard
            sum(
                np.mgrid[
                    int(rounded_y_min / cell_size_y):int(rounded_y_max / cell_size_y) + 1,
                    int(rounded_x_min / cell_size_x):int(rounded_x_max / cell_size_x) + 1,
                ]
            ) % 2,
            extent=[
                int(rounded_x_min) - 0.5 * cell_size_x,
                int(rounded_x_max) + 0.5 * cell_size_x,
                int(rounded_y_min) - 0.5 * cell_size_y,
                int(rounded_y_max) + 0.5 * cell_size_y,
            ],
            cmap=ListedColormap([
                style.checker_dark,
                style.checker_light,
            ]),
            interpolation='none',
        )

        # now we draw trajectories
        for offset_trajectory, loops in zip(
            offset_trajectories(
                self.trajectory_list,
                cell_size_x,
                cell_size_y,
                x_order=self.quantization.x_order,
                y_order=self.quantization.y_order,
            ),
            loops_list,
        ):
            x_data, y_data, t_data, _ = offset_trajectory.get_states(
                self.quantization.x_order, self.quantization.y_order
            )
            node_number_positions = dict(enumerate(zip(x_data, y_data)))

            # List of tuples to define edges between nodes
            # todo :: I wonder if python has a built in multigraph datatype for this
            edges = (
                # todo :: it may be nice if these were ordered? :)
                # i.e. loops interleaved appropriately between links
                [(i, i + 1) for i in range(len(x_data) - 1)]
                + [(loop_node, loop_node) for loop_node in loops]
            )
            node_sizes = (1000 / max_duration) * np.diff(t_data)

            # Add nodes and edges to graph
            graph.add_nodes_from(node_number_positions.keys())
            # todo :: is this needed? edges specified twice for nx?
            graph.add_edges_from(edges)

            # Draw graphs
            nx.draw_networkx_nodes(
                graph,
                node_number_positions,
                node_size=node_sizes,
                node_color="indigo",
            )
            nx.draw_networkx_edges(
                graph,
                node_number_positions,
                node_size=node_sizes,
                nodelist=list(range(len(x_data))),
                edgelist=edges,
                arrows=True,
                arrowstyle=arrow_style,
                node_shape=".",
                arrowsize=10,
                width=2,
                connectionstyle=connection_style,
            )

        # all of this needs to go in a separate function, called with show()
        # we need to store which axis is which column - kick up a fuss if future plots don't match this
        # we also need to store an idea of minimum scale - this is going to fuck us if scales don't match
        # - maybe just tell people if they have scale adjustment problems to specify their own

        # Get tick labels - either numeric or categories
        # todo :: this bit is a bit of a mess
        rounded_x_points = range(
            int(rounded_x_min),
            int(rounded_x_max + 1),
            int(cell_size_x),
        )
        rounded_y_points = range(
            int(rounded_y_min),
            int(rounded_y_max + 1),
            int(cell_size_y),
        )
        # Set ticks for states
        ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
        ax.tick_params(
            axis='x',
            labelsize=style.tick_font_size,
            rotation=90 * style.rotate_x_labels,
        )
        ax.tick_params(
            axis='y',
            labelsize=style.tick_font_size,
        )
        ax.xaxis.set_major_locator(ticker.FixedLocator(rounded_x_points))
        ax.yaxis.set_major_locator(ticker.FixedLocator(rounded_y_points))
        ax.xaxis.set_major_formatter(ticker.FixedFormatter(
            self.quantization.x_order
            or [str(i) for i in rounded_x_points]
        ))
        ax.yaxis.set_major_formatter(ticker.FixedFormatter(
            self.quantization.y_order
            or [str(i) for i in rounded_y_points]
        ))

        # Set axis labels
        ax.set_xlabel(style.x_label, fontsize=style.label_font_size)
        ax.set_ylabel(style.y_label, fontsize=style.label_font_size)

        if style.title:
            ax.set_title(style.title, fontsize=style.title_font_size)

        ax.set_aspect('auto')
        plt.tight_layout()

        if save_as is not None:
            ax.savefig(save_as)
        else:
            plt.show()

    def get_measures(self):
        max_duration, x_min, y_min, x_max, y_max, _ = self.__shared_all_trajectory_process()

        cell_size_x, cell_size_y, rounded_x_min, rounded_y_min, rounded_x_max, rounded_y_max \
            = self.__get_rounded_parameters(x_min, x_max, y_min, y_max)

        trajectory_durations, event_numbers, visit_numbers, cell_ranges = zip(*[
            (
                traj.data_t[-1] - traj.data_t[0],
                len(traj.data_x),
                traj.get_num_visits(),
                traj.get_cell_range()
            )
            for traj in self.trajectory_list
        ])

        def maybe_reorder(data, ordering: Optional[list] = None):
            if ordering is None:
                return data
            return [ordering.index(val) for val in data]

        bin_counts = [
            Counter(
                zip(
                    # todo :: should factor out uses of .style that affect computation,
                    # as opposed to uses that only affect rendering
                    maybe_reorder(trajectory.data_x, self.quantization.x_order),
                    maybe_reorder(trajectory.data_y, self.quantization.y_order),
                )
            )
            for trajectory in self.trajectory_list
        ]
        cumulative_bin_counts = sum(bin_counts,Counter())

        # todo :: hmmmmmmMMMMM
        return GridMeasures(
            trajectory_ids=[trajectory.id for trajectory in self.trajectory_list],
            mean_duration=mean(trajectory_durations),
            mean_number_of_events=mean(event_numbers),
            mean_number_of_visits=mean(visit_numbers),
            mean_cell_range=mean(cell_ranges),
            overall_cell_range=len(cumulative_bin_counts),
            # todo :: these should likely be the responsibility of GridMeasures

            mean_duration_per_event=mean(
                map(lambda x, y: x / y, trajectory_durations, event_numbers)
            ),
            mean_duration_per_visit=mean(
                map(lambda x, y: x / y, trajectory_durations, visit_numbers)
            ),
            mean_duration_per_cell=mean(
                map(lambda x, y: x / y, trajectory_durations, cell_ranges)
            ),
            dispersion=mean(
                trajectory.calculate_dispersion(
                    # todo :: what is this nonsense :)
                    (int((x_max - x_min) / cell_size_x) + 1) * (int((y_max - y_min) / cell_size_y) + 1),
                )
                for trajectory in self.trajectory_list
            ),
            visited_entropy=mean(
                sum(x / total_count for x in cell_counts.values())
                for cell_counts, total_count in zip(bin_counts, visit_numbers)),
        )


def offset_trajectories(
    trajectories: Sequence[Trajectory],
    cell_size_x: float,  # todo :: I actually don't know what these are
    cell_size_y: float,  # todo :: I actually don't know what these are
    # todo :: better abstraction/etc for these orderings...?
    x_order=None,
    y_order=None,
) -> List[Trajectory]:
    """
    perturbs (quantized?) trajectory x and y values
    to not overlap, by mapping overlapping values to angular
    spaced points within a circle in each cell

    amount to perturb by is based on cell_size_x and cell_size_y
    """
    # todo :: later -- need to think about what this actually does
    # get total bin counts
    new_trajectories = []
    # todo :: are we independently getting bin counts in many places...
    bin_counts = Counter(
        (x, y)
        for trajectory in trajectories
        for (x, y) in zip(*trajectory.get_states(x_order, y_order)[:2])
    )
    current_bin_counter = Counter()
    for trajectory in trajectories:
        # todo :: I imagine there's a cleaner way to do this...
        # If same state is repeated, offset states
        # so they don't sit on top of one another:
        x_data, y_data, t_data, _ = trajectory.get_states(x_order, y_order)
        new_trajectories.append(
            Trajectory(
                *util.offset_within_bin(
                    x_data,
                    cell_size_x,
                    y_data,
                    cell_size_y,
                    bin_counts,
                    current_bin_counter,
                ),
                t_data,
            )
        )
    return new_trajectories
