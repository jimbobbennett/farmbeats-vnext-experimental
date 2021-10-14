/// <reference path="../globals.d.ts" />
/// <reference path="../shared.ts" />

import { get_device_id_from_sheet } from "../shared";

/* global clearInterval, CustomFunctions, setInterval, fetch, globalThis */

function pollOnInterval<T>(
  url_part: string,
  interval: number,
  invocation: CustomFunctions.StreamingInvocation<T>,
  valueExtractor,
  error_value: T
) {
  const timer = setInterval(async () => {
    try {
      await get_device_id_from_sheet();
      const response = await fetch(globalThis._host_name + url_part);

      //Expect that status code is in 200-299 range
      if (!response.ok) {
        throw new Error(response.statusText);
      }
      const jsonResponse = await response.json();
      invocation.setResult(valueExtractor(jsonResponse));
    } catch (error) {
      //console.error(error);
      invocation.setResult(error_value);
    }
  }, interval);

  invocation.onCanceled = () => {
    clearInterval(timer);
  };
}

async function latestValue<T>(url_part: string, valueExtractor, error_value: T) {
  try {
    await get_device_id_from_sheet();
    const response = await fetch(globalThis._host_name + url_part);

    //Expect that status code is in 200-299 range
    if (!response.ok) {
      throw new Error(response.statusText);
    }
    const jsonResponse = await response.json();
    return valueExtractor(jsonResponse);
  } catch (error) {
    //console.error(error);
    return error_value;
  }
}

/**
 * Gets the state of a relay.
 * @customfunction
 * @param invocation Custom function handler
 * @return {string} "on" if the relay is on, otherwise "off"
 */
export async function relayState(invocation: CustomFunctions.StreamingInvocation<string>) {
  pollOnInterval(
    "/relay",
    5000,
    invocation,
    (j) => {
      if (j.value) return "On";
      else return "Off";
    },
    "Error"
  );
}

/**
 * Gets the current state of a relay.
 * @customfunction
 * @return {string} "on" if the relay is on, otherwise "off"
 */
export async function currentRelayState() {
  return latestValue(
    "/relay",
    (j) => {
      if (j.value) return "On";
      else return "Off";
    },
    "Error"
  );
}

/**
 * Gets the soil moisture reading once a second.
 * @customfunction
 * @param invocation Custom function handler
 * @return {number} The soil moisture value from 0-1023
 */
export function soilMoisture(invocation: CustomFunctions.StreamingInvocation<number>) {
  pollOnInterval(
    "/soil-moisture",
    5000,
    invocation,
    (j) => {
      return j.value;
    },
    -1
  );
}

/**
 * Gets the current soil moisture reading
 * @customfunction
 * @return {number} The soil moisture value from 0-1023
 */
export function currentSoilMoisture() {
  return latestValue(
    "/soil-moisture",
    (j) => {
      return j.value;
    },
    -1
  );
}

/**
 * Gets the soil temperature reading once a second.
 * @customfunction
 * @param invocation Custom function handler
 * @return {number} The soil temperature value in Celsius
 */
export function soilTemperature(invocation: CustomFunctions.StreamingInvocation<number>) {
  pollOnInterval(
    "/temperature-humidity",
    5000,
    invocation,
    (j) => {
      return j.soil_temperature;
    },
    -1
  );
}

/**
 * Gets the soil temperature reading once a second.
 * @customfunction
 * @param invocation Custom function handler
 * @return {number} The soil temperature value in fahrenheit
 */
export function soilTemperatureInFahrenheit(invocation: CustomFunctions.StreamingInvocation<number>) {
  pollOnInterval(
    "/temperature-humidity",
    5000,
    invocation,
    (j) => {
      var f = j.soil_temperature * (9 / 5) + 32;
      return Math.round(f * 100) / 100;
    },
    -1
  );
}

/**
 * Gets the current soil temperature reading.
 * @customfunction
 * @return {number} The soil temperature value in Celsius
 */
export function currentSoilTemperature() {
  return latestValue(
    "/temperature-humidity",
    (j) => {
      return j.soil_temperature;
    },
    -1
  );
}

/**
 * Gets the current soil temperature reading.
 * @customfunction
 * @return {number} The soil temperature value in fahrenheit
 */
export function currentSoilTemperatureInFahrenheit() {
  return latestValue(
    "/temperature-humidity",
    (j) => {
      var f = j.soil_temperature * (9 / 5) + 32;
      return Math.round(f * 100) / 100;
    },
    -1
  );
}

/**
 * Gets the temperature reading once a second.
 * @customfunction
 * @param invocation Custom function handler
 * @return {number} The temperature value in Celsius
 */
export function temperature(invocation: CustomFunctions.StreamingInvocation<number>) {
  pollOnInterval(
    "/temperature-humidity",
    5000,
    invocation,
    (j) => {
      return j.temperature;
    },
    -1
  );
}

/**
 * Gets the temperature reading once a second.
 * @customfunction
 * @param invocation Custom function handler
 * @return {number} The temperature value in fahrenheit
 */
export function temperatureInFahrenheit(invocation: CustomFunctions.StreamingInvocation<number>) {
  pollOnInterval(
    "/temperature-humidity",
    5000,
    invocation,
    (j) => {
      var f = j.temperature * (9 / 5) + 32;
      return Math.round(f * 100) / 100;
    },
    -1
  );
}

/**
 * Gets the current temperature.
 * @customfunction
 * @return {number} The temperature value in Celsius
 */
export function currentTemperature() {
  return latestValue(
    "/temperature-humidity",
    (j) => {
      return j.temperature;
    },
    -1
  );
}

/**
 * Gets the current temperature reading.
 * @customfunction
 * @return {number} The temperature value in fahrenheit
 */
export function currentTemperatureInFahrenheit() {
  return latestValue(
    "/temperature-humidity",
    (j) => {
      var f = j.temperature * (9 / 5) + 32;
      return Math.round(f * 100) / 100;
    },
    -1
  );
}

/**
 * Gets the humidity reading once a second.
 * @customfunction
 * @param invocation Custom function handler
 * @return {number} The humidity value in Celsius
 */
export function humidity(invocation: CustomFunctions.StreamingInvocation<number>) {
  pollOnInterval(
    "/temperature-humidity",
    5000,
    invocation,
    (j) => {
      return j.humidity;
    },
    -1
  );
}

/**
 * Gets the current humidity reading.
 * @customfunction
 * @return {number} The humidity value in Celsius
 */
export function currentHumidity() {
  return latestValue(
    "/temperature-humidity",
    (j) => {
      return j.humidity;
    },
    -1
  );
}
