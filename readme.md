# StateSpaceGridLib

## Introduction

StateSpaceGridLib is a python library loosely based around replicating the
functionality of GridWare, a Java program for creating and analysing
state space grids for visualising dyadic mutuality in psychology.

The main features of StateSpaceGrid are Trajectory objects, Grid objects and
the associated GridStyle and GridQuantization objects which hold any extra data needed for drawing grids and calculating measures.

Trajectory objects hold the input data as a set of lists, along with a single ID number.

Grid objects hold trajectory objects and are the interface through which you
can display grids and calculate measures.

See unit_tests/test_end_to_end.py for a brief example of the code in action.

To install as a library with pip, use

pip install git+https://github.com/DyadicSolutions/StateSpaceGridLib

## Todos

- Add examples to readme
- General code cleanliness
- More unit tests :)

## Library API Reference

### Trajectory

```python
Trajectory(data_x, data_y, data_t, id=None)
```
Data in StateSpaceGridLib is organised via Trajectories. These objects take in data for the x axis of the grid, data for the y axis of the grid, and time data for the transitions between states (ie. the time data specifies the time at which each state starts, as well as the end time of the last state).
* `data_x`

   A list of state values for the x axis. The length of this list is expected to be the same as for the y data.

* `data_y`

   A list of state values for the y axis. The length of this list is expected to be the same as for the x data.
* `data_t`

   Time data: a list of length 1 longer than the x or y data, specifying the start time of each event in the data_x/data_y lists as well as the end point of the final event.

* `id`

   An integer id number for the Trajectory object. If left blank, this defaults to the global number of trajectory objects at time of creation. 
```python
Trajectory.get_num_visits()
```
Return number of "visits", defined as the number of state transitions plus 1 (the initial starting state) minus the number of transitions to the same state as where the transition is from (ie. `(x1, y1) -> (x2, y2)` where `x1 = x2` and `y1 = y2`).
```python
Trajectory.get_cell_range()
```
Return number of unique cells visited.
```python
Trajectory.get_states(x_ordering=None, y_ordering=None, merge_repeated_states=True)
```
Return formatted state data.
* `x_ordering`

   An optional list defining the ordering of the x data scale. If it is a numerical scale, this can be left blank.
   
   eg. `["low", "medium", "high"]`
* `y_ordering`

   An optional list defining the ordering of the y data scale. If it is a numerical scale, this can be left blank.
   
   eg. `["low", "medium", "high"]`
* `merge_repeated_states`

   Boolean flag to control whether or not adjacent events with repeated states should be merged. This defaults to True.
```python
Trajectory.calculate_dispersion(total_cells)
```
Return dispersion for trajectory.
* `total_cells`

   Total number of cells in the state space grid.

```python
Trajectory.from_legacy_trj(filename, params=(1,2))
```
Return a trajectory object initialised from a GridWare trajectory file.
* `filename`

   The path to the trajectory file.
* `params`

   A tuple containing the two column names of the parameters of interest.
### Grid
```python
Grid(trajectory_list, quantization=GridQuantization())
```
Data now formatted as `Trajectory` objects can be collated within a `Grid` object for visualisation and the calculation of grid measures.
* `trajectory_list`
   
   A list of `Trajectory` objects containing the input data.

* `quantization`

   A GridQuantization object containing data relevant to the calculation of grid measures. If left blank, this defaults to the default settings in GridQuantization.
```python
Grid.draw(save_as=None, style=GridStyle())
```
   Draw visualisation of state space grid.
* `save_as`

   If provided, this is the name of the png file that the image of the grid is saved as.  If left blank, the grid will be displayed in a new window using whichever gui library matplotlib has access to.
* `style`

   GridStyle object containing options for the display of the grid in MatPLotLib.
```python
Grid.get_measures()
```
Calculate cumulative measures from all trajectories provided to the grid and return as a `GridMeasures` object.
### GridStyle
```python
GridStyle(title="", label_font_size=14, tick_font_size=14, title_font_size=14, x_label=None, y_label=None, rotate_xlabels=False, checker_light=(220/256, 220/256, 220/256), checker_dark=(1, 1, 1), connection_style="arc3,rad=0.0", arrow_style="-|>")
```
Object containing visualisation customisation.
* `title`

   Grid title
* `label_font_size`

   Axis label font size
* `tick_font_size`

   Axis tick font size
* `title_font_size`

   Title font size
* `x_label`

   X axis label
* `y_label`

   Y axis label
* `rotate_xlabels`

   Rotate x axis tick labels by 90°.
* `checker_light`

   Colour of light squares on state space grid.
   
* `checker_dark`

   Colour of dark squares on state space grid.
* `connection_style`

   Style of curve connecting nodes on the trajectory graph. See https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.patches.FancyArrowPatch.html#matplotlib.patches.FancyArrowPatch for more information on the options.
* `arrow_style`

   Style of arrow on edges connecting nodes on the trajectory graph. See https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.patches.ArrowStyle.html#matplotlib.patches.ArrowStyle for more information on the options.

### GridQuantization
```python
GridQuantization(cell_size_x=None, cell_size_y=None, x_order=None, y_order=None, x_min=None, x_max=None, y_min=None, y_max=None)
```
Object containing extra data relevant to grid measure calculation and visualisation.
* `cell_size_x`
    
   Width of a cell in the x axis. If left blank, a best guess will be calculated from the data available.
* `cell_size_y`
   
   Height of a cell in the y axis. If left blank, a best guess will be calculated from the data available.
* `x_order`

   An optional list defining the ordering of the x data scale.
   
   eg. `["low", "medium", "high"]` 
   
   If it is a numerical scale, this can be left blank.
* `y_order`

   An optional list defining the ordering of the y data scale.
   
   eg. `["low", "medium", "high"]`
   
    If it is a numerical scale, this can be left blank.
* `x_min`

   The lowest value in the x measurement scale. If left blank this is the lowest value in the data given.
* `x_max`

   The highest value in the x measurement scale. If left blank, this is the highest value in the data given.
* `y_min`

   The lowest value in the y measurement scale. If left blank this is the lowest value in the data given.
* `y_max`

   The highest value in the y measurement scale. If left blank, this is the highest value in the data given.
### GridMeasures
```python
GridMeasures()    
```
Data container for all measure data. Individual values can be read off, or the entire thing may be printed as is.
```python
GridMeasures.trajectory_ids
```
IDs of all trajectories in grid.
```python
GridMeasures.mean_duration
```
Mean total duration of the trajectories
```python
GridMeasures.mean_number_of_events
```
Mean number of events in the trajectories
```python
GridMeasures.mean_number_of_visits
```
Mean number of visits in the trajectories.

A visit is defined as being an entrance and then an exit of a cell.
```python
GridMeasures.mean_cell_range
```
Mean number of different cells reached by the trajectories.
```python
GridMeasures.overall_cell_range
```
Total number of cells visited cumulatively by the trajectories. 
```python
GridMeasures.mean_duration_per_event
```
Mean duration per event

Defined as mean of trajectory duration divided by number of trajectory events.
```python
GridMeasures.mean_duration_per_visit
```
Mean duration per visit

Defined as mean of trajectory duration divided by number of trajectory visits.
```python
GridMeasures.mean_duration_per_cell
```
Mean duration spent in each cell

Defined as mean of trajectory duration divided by trajectory cell range.
```python
GridMeasures.dispersion
```
Mean of trajectory dispersion across all trajectories. Dispersion for a single trajectory is calculated by the formula
$$\text{dispersion}=\frac{n(\sum_{i}{(\frac{d_i}{D})^2})-1}{n-1}$$
```python
GridMeasures.visited_entropy
```
Entropy of visits, defined as 
$$\sum_{i}{\frac{P_i}{\ln(P_i)}}$$
where $P_i$ is the probablity of visiting cell $i$, defined as
$$P_i = \frac{\text{Number of visits to cell i}}{\text{total number of visits}}$$

#Exa