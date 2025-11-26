import math

class SunganRiverWaterQualityAnalyzer:
    def __init__(self):
        self.weights = {
            'DO': 0.27,
            'pH': 0.175,
            'nitrate': 0.159,
            'phosphate': 0.159,
            'turbidity': 0.127,
            'TDS': 0.111
        }
        self.standards = {
            'pH': (6.5, 8.5),
            'DO': (5.0, float('inf')),
            'turbidity': (0, 5),
            'TDS': (0, 100),
            'iron': (0, 0.3),
            'phosphate': (0, 0.4),
            'nitrate': (0, 10)
        }
        self.wqi_rating = {
            (91, 100): "Excellent Quality",
            (71, 90): "Good Quality",
            (51, 70): "Moderate Quality",
            (26, 50): "Poor Quality",
            (0, 25): "Very Poor Quality"
        }

    def predict_ph(self, distance):
        if distance <= 0:
            raise ValueError("Distance must be greater than 0")
        return -0.028 * distance + 7.909

    def predict_turbidity(self, distance):
        if distance <= 0:
            raise ValueError("Distance must be greater than 0")
        return 755.873 * (distance ** -2.945)

    def predict_tds(self, distance):
        if distance <= 0:
            raise ValueError("Distance must be greater than 0")
        return 86.24 * distance - 82.03

    def predict_iron(self, distance):
        if distance <= 0:
            raise ValueError("Distance must be greater than 0")
        return 12.803 * math.log(distance) + 2.271

    def predict_phosphate(self, distance):
        if distance <= 0:
            raise ValueError("Distance must be greater than 0")
        return 0.079 * distance + 0.958

    def predict_nitrate(self, distance):
        if distance <= 0:
            raise ValueError("Distance must be greater than 0")
        return -0.55 * math.log(distance) + 1.544

    def predict_do(self, distance):
        if distance <= 3:
            return 8.00
        elif distance <= 5:
            return 7.45
        else:
            return 8.20

    def get_q_value(self, parameter, value):
        if parameter == 'DO':
            if value >= 7.5: return 90
            elif value >= 7.0: return 85
            elif value >= 6.5: return 80
            elif value >= 6.0: return 75
            elif value >= 5.5: return 70
            elif value >= 5.0: return 65
            else: return max(0, int(value * 10))
        elif parameter == 'pH':
            if 7.0 <= value <= 8.0: return 90
            elif 6.5 <= value < 7.0 or 8.0 < value <= 8.5: return 80
            elif 6.0 <= value < 6.5 or 8.5 < value <= 9.0: return 60
            elif 5.5 <= value < 6.0 or 9.0 < value <= 9.5: return 40
            else: return 20
        elif parameter == 'nitrate':
            if value <= 1.0: return 95
            elif value <= 2.0: return 90
            elif value <= 5.0: return 80
            elif value <= 7.5: return 70
            elif value <= 10.0: return 60
            else: return max(0, 100 - value * 8)
        elif parameter == 'phosphate':
            if value <= 0.1: return 95
            elif value <= 0.2: return 90
            elif value <= 0.4: return 80
            elif value <= 0.8: return 60
            elif value <= 1.2: return 40
            elif value <= 1.6: return 30
            else: return max(0, 100 - value * 40)
        elif parameter == 'turbidity':
            if value <= 1.0: return 95
            elif value <= 5.0: return 90
            elif value <= 10.0: return 80
            elif value <= 20.0: return 70
            elif value <= 50.0: return 50
            elif value <= 100.0: return 30
            else: return max(0, 100 - value)
        elif parameter == 'TDS':
            if value <= 50: return 95
            elif value <= 100: return 85
            elif value <= 200: return 75
            elif value <= 300: return 65
            elif value <= 400: return 50
            elif value <= 500: return 35
            else: return max(0, 100 - value / 10)
        return 50

    def get_wqi_rating(self, wqi_score):
        for (min_score, max_score), rating in self.wqi_rating.items():
            if min_score <= wqi_score <= max_score:
                return rating
        return "Undefined"

    def assess_parameter_quality(self, parameter, value):
        if parameter in self.standards:
            min_std, max_std = self.standards[parameter]
            if min_std <= value <= max_std:
                return "Within Standard", "✓"
            else:
                return "Exceeds Standard", "✗"
        return "No Standard", "-"


    def predict_all_parameters(self, distance):
        predictions = {
            'pH': self.predict_ph(distance),
            'DO': self.predict_do(distance),
            'turbidity': self.predict_turbidity(distance),
            'TDS': self.predict_tds(distance),
            'iron': self.predict_iron(distance),
            'phosphate': self.predict_phosphate(distance),
            'nitrate': self.predict_nitrate(distance)
        }
        return predictions
