import matplotlib.pyplot as plt
from math import (
    log,
    cos,
    pi,
    sqrt,
    floor
)
from PyQt6.QtWidgets import (
    QPushButton,
    QDoubleSpinBox,
    QLabel
)
from random import random
from objects import obj
from constants import chi_square_005


button: QPushButton = obj.objects.get('button')[0]


def start():
    spin_boxes: list[QDoubleSpinBox] = obj.objects.get('spinbox')
    labels: list[QLabel] = obj.objects.get('label')
    expected_mean = spin_boxes[0].value()
    expected_variance = spin_boxes[1].value()
    deviation = sqrt(expected_variance)

    sample_size: int = spin_boxes[2].value()
    sample = [get_normal_rv(deviation=deviation, mean=expected_mean) for i in range(sample_size)]

    intervals = get_intervals(sample)
    frequencies = get_freq(intervals=intervals, sample=sample)
    expected_probabilities = define_expected_probabilities(intervals=intervals, sample=sample)

    characteristics: tuple = get_characteristics_of_rvs(sample)
    relative_errors: tuple = get_relative_errors((expected_mean, expected_variance), characteristics)

    average = 'Average: ' + str(round(characteristics[0], 2)) + ' (error = ' + str(round(relative_errors[0], 2)) + ')'
    variance = 'Variance: ' + str(round(characteristics[1], 2)) + ' (error = ' + str(round(relative_errors[1], 2)) + ')'
    labels[0].setText(average)
    labels[1].setText(variance)

    result: tuple = chi_squared_test(sample_size, frequencies, expected_probabilities)
    chi_squared = 'Chi-squared: ' + str(round(result[1], 2)) + ' > ' + str(round(result[2], 2)) + ' is ' + str(
        result[0])
    labels[2].setText(chi_squared)

    draw_bar(frequencies=frequencies, intervals_v=intervals, min_v=min(sample))


def generator() -> float:
    """Returns a standard normal RV, based on Box-Muller transform"""
    return sqrt(-2 * log(random())) * cos(2 * pi * random())


def get_normal_rv(deviation: float, mean: float) -> float:
    """Returns a normal RV N(a, σ2)"""
    return deviation * generator() + mean


def count_intervals(size: int) -> int:
    """Returns the number of intervals, based on Sturges' rule"""
    return floor(log(size, 2)) + 1


def get_interval_step(max_v: float, min_v: float, count: int) -> float:
    return (max_v - min_v) / count


def get_intervals(sample: list[float]) -> list[float]:
    """Returns the right bounds of the intervals (first left - minimum value in the sample, last right - maximum)"""
    max_v: float = max(sample)
    min_v: float = min(sample)
    k: int = count_intervals(len(sample))
    print(k)
    step: float = get_interval_step(max_v, min_v, k)
    intervals: list[float] = [0.0 for i in range(k)]

    intervals[0] = min_v + step
    for i in range(1, k):
        intervals[i] = intervals[i - 1] + step

    return intervals


def get_freq(intervals: list[float], sample: list[float]) -> list[float]:
    """Counts the number of hits of RV in the interval, returns relative frequencies"""
    frequencies: list[float] = [0 for k in range(len(intervals))]
    for element in sample:
        if (element >= min(sample)) and (element <= intervals[0]):
            frequencies[0] += 1
        else:
            for i in range(1, len(intervals)):
                if (element > intervals[i - 1]) and (element <= intervals[i]):
                    frequencies[i] += 1
    size = len(sample)
    frequencies = [freq/size for freq in frequencies]
    return frequencies


def define_expected_probabilities(intervals: list[float], sample: list[float]) -> list[float]:
    """Returns approximate values of expected probabilities"""
    min_v: float = min(sample)
    step: float = get_interval_step(max(sample), min_v, len(intervals))

    expected_probabilities: list[float] = [0 for k in range(len(intervals))]
    for i, right in enumerate(intervals):
        if i == 0:
            for value in sample:
                if (value >= min_v) and (value <= right):
                    expected_probabilities[i] = step * value * ((right + min_v) / 2)
                    break
        else:
            left = intervals[i - 1]
            for value in sample:
                if (value > left) and (value <= right):
                    expected_probabilities[i] = step * value * ((right + left) / 2)
                    break
    return expected_probabilities


def chi_squared_test(sample_size: int, frequencies: list[float], expected_probabilities: list[float]) -> tuple:
    """Returns received value of chi-squared test, table value and the result of their comparison"""
    x = 0
    for i in range(len(frequencies)):
        x += frequencies[i] ** 2 / (sample_size * expected_probabilities[i])
    x -= sample_size
    x_ = chi_square_005.get(len(frequencies) - 1)
    if x > x_:
        return True, x, x_
    return False, x, x_


def get_characteristics_of_rvs(sample: list[float]) -> tuple:
    """Returns average and variance"""
    e: float = 0.0
    d: float = 0.0
    size = len(sample)
    for i in range(size):
        e += sample[i]
        d += sample[i] ** 2
    e *= 1 / size
    d *= 1 / size
    d -= e ** 2
    return e, d


def get_relative_errors(expected_characteristics: tuple, empiric_characteristics: tuple) -> tuple:
    e_err = abs(empiric_characteristics[0] - expected_characteristics[0]) / abs(expected_characteristics[0])
    d_err = abs(empiric_characteristics[1] - expected_characteristics[1]) / abs(expected_characteristics[1])
    return e_err, d_err


def draw_bar(frequencies: list[float], intervals_v: list[float], min_v: float) -> None:
    intervals_s: list[str] = ['' for k in range(len(intervals_v))]
    intervals_s[0] = '[' + str(round(min_v, 2)) + ';' + str(round(intervals_v[0], 2)) + ']'
    for i in range(1, len(intervals_v)):
        intervals_s[i] = '(' + str(round(intervals_v[i - 1], 2)) + ';' + str(round(intervals_v[i], 2)) + ']'
    width: list[int] = [1 for k in range(len(frequencies))]
    plt.bar(intervals_s, frequencies, width=width, edgecolor="k")
    plt.xlabel("Intervals")
    plt.ylabel("Frequencies")
    plt.show()


button.clicked.connect(start)
