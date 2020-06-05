import Adafruit_MCP3008
import os


class MoistureSensor(object):

    # Analog mix and max
    max_humidity_reading = 650  # Dry in air
    min_humidity_reading = 385  # In water
    # Define delay between readings
    delay = 60

    def __init__(self):
        self.mcp = Adafruit_MCP3008.MCP3008(
            clk=int(os.environ.get("pin_clk")),
            cs=int(os.environ.get("pin_cs")),
            miso=int(os.environ.get("pin_miso")),
            mosi=int(os.environ.get("pin_mosi"))
        )
        # Define sensor channel
        self.moisture_channel = int(os.environ.get("analogue_channel"))
        self.max_humidity_reading = 650  # Dry in air
        self.min_humidity_reading = 385  # In water

    # Function to read SPI data from MCP3008 chip
    # Channel must be an integer 0-7
    def ReadChannel(self):
    #     adc = spi.xfer2([1,(8+channel)<<4,0])
    #     data = ((adc[1]&3) << 8) + adc[2]
            # data = mcp.read_adc(channel)
        return self.mcp.read_adc(self.moisture_channel)
        
    def ConverttoPercent(self, data):
        percent = int(round(data/10.24))
        return percent

    def ConverttoPercentScaled(self, data):
        max_value = self.max_humidity_reading - self.min_humidity_reading
        percent = round((1-((data-self.min_humidity_reading)/max_value)) * 100)
        return percent

    def GetScaledPercent(self):
        return self.ConverttoPercentScaled(self.ReadChannel())

    def GetScaledMaxValue(self):
        return self.max_humidity_reading - self.min_humidity_reading

    def GetMaxHumidityReading(self):
        return self.max_humidity_reading

    def GetMinHunidityReading(self):
        return self.min_humidity_reading
