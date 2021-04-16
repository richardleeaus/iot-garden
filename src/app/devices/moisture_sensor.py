from grove.grove_moisture_sensor import GroveMoistureSensor

class MoistureSensor(object):

    def __init__(self):
        # Define sensor channel
        self.moisture_channel = int(os.environ.get("analogue_channel"))
        self.max_humidity_reading = 650  # Dry in air
        self.min_humidity_reading = 385  # In water

        self.moisture_sensor = GroveMoistureSensor(4)

    def get_moisture(self):
        return self.moisture_sensor.moisture

    def ConverttoPercent(self, data):
        percent = int(round(data/10.24))
        return percent

    def ConverttoPercentScaled(self, data):
        max_value = self.max_humidity_reading - self.min_humidity_reading
        percent = round((1-((data-self.min_humidity_reading)/max_value)) * 100)
        return percent

    def GetScaledPercent(self):
        return self.ConverttoPercentScaled(self.get_moisture())

    def GetScaledMaxValue(self):
        return self.max_humidity_reading - self.min_humidity_reading

    def GetMaxHumidityReading(self):
        return self.max_humidity_reading

    def GetMinHunidityReading(self):
        return self.min_humidity_reading