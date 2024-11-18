import random

class Simulator:
    Factors = [-1, 1]
    
    def __init__(self, seed, mean, standard_deviation):
        self._random = random.Random(seed)
        self._mean = mean
        self._standard_deviation = abs(standard_deviation)
        self._step_size_factor = self._standard_deviation / 10
        self._value = self._mean - self._random.random()
    
    def calculate_next_value(self):
        # Calculate how much the value will change
        value_change = self._random.random() * self._step_size_factor
        # Decide if the value is increased or decreased
        factor = Simulator.Factors[self.decide_factor()]
        # Apply valueChange and factor to _value and return
        self._value += value_change * factor
        return self._value

    def decide_factor(self):
        # Distance from the mean
        if self._value > self._mean:
            distance = self._value - self._mean
            continue_direction = 1
            change_direction = 0
        else:
            distance = self._mean - self._value
            continue_direction = 0
            change_direction = 1
        
        # Chance calculation
        chance = (self._standard_deviation / 2) - (distance / 50)
        random_value = self._random.random() * self._standard_deviation
        
        # Determine direction based on chance
        return continue_direction if random_value < chance else change_direction