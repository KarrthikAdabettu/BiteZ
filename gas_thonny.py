import machine
import time

# Analog pin connected to the MQ-135 sensor
analog_pin = machine.ADC(28)

# Calibration parameters
RO_CLEAN_AIR_FACTOR = 3.59  # RO value in clean air (change according to your sensor)
CALIBRATION_SAMPLE_TIMES = 50
CALIBRATION_SAMPLE_INTERVAL = 500  # milliseconds

# Gas concentration ratio for CO2, CO, and NH4
R0_RATIO_CO2 = 60
R0_RATIO_CO = 4.5
R0_RATIO_NH4 = 3.5

def read_R0():
    # Perform sensor calibration
    print("Calibrating MQ-135, please wait...")
    val = 0.0
    for _ in range(CALIBRATION_SAMPLE_TIMES):
        val += analog_pin.read_u16()
        time.sleep_ms(CALIBRATION_SAMPLE_INTERVAL)
    val /= CALIBRATION_SAMPLE_TIMES
    val = val / 65535 * 3.3  # Convert to voltage

    # Calculate R0 value
    RS_RO = val / RO_CLEAN_AIR_FACTOR
    return RS_RO

def calculate_gas_concentration(R0_ratio, RS_RO):
    # Calculate gas concentration based on the sensor ratio
    gas_concentration = (R0_ratio / RS_RO - 1) / 10
    return gas_concentration

def main():
    R0_CO2 = R0_RATIO_CO2 * read_R0()
    R0_CO = R0_RATIO_CO * read_R0()
    R0_NH4 = R0_RATIO_NH4 * read_R0()

    while True:
        # Read sensor value
        sensor_value = analog_pin.read_u16() / 65535 * 3.3  # Convert to voltage

        # Calculate gas concentrations
        RS_RO_CO2 = sensor_value / R0_CO2
        RS_RO_CO = sensor_value / R0_CO
        RS_RO_NH4 = sensor_value / R0_NH4

        CO2_concentration = calculate_gas_concentration(R0_RATIO_CO2, RS_RO_CO2)
        CO_concentration = calculate_gas_concentration(R0_RATIO_CO, RS_RO_CO)
        NH4_concentration = calculate_gas_concentration(R0_RATIO_NH4, RS_RO_NH4)

        # Display gas concentrations
        print("CO2 concentration: {:.2f} ppm".format(CO2_concentration))
        print("CO concentration: {:.2f} ppm".format(CO_concentration))
        print("NH4 concentration: {:.2f} ppm".format(NH4_concentration))
        
        time.sleep(1)  # Adjust this delay as needed

if __name__ == "__main__":
    main()

