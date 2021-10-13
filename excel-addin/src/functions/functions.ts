/* global clearInterval, CustomFunctions, console, setInterval, fetch */

function pollOnInterval<T>(
  url: string,
  interval: number,
  invocation: CustomFunctions.StreamingInvocation<T>,
  valueExtractor,
  error_value: T
) {
  const timer = setInterval(async () => {
    try {
      const response = await fetch(url);

      //Expect that status code is in 200-299 range
      if (!response.ok) {
        throw new Error(response.statusText);
      }
      const jsonResponse = await response.json();
      invocation.setResult(valueExtractor(jsonResponse));
    } catch (error) {
      console.error(error);
      invocation.setResult(error_value);
    }
  }, interval);

  invocation.onCanceled = () => {
    clearInterval(timer);
  };
}

/**
 * Gets the state of a relay.
 * @customfunction
 * @param invocation Custom function handler
 * @return {string} "on" if the relay is on, otherwise "off"
 */
export async function relayState(invocation: CustomFunctions.StreamingInvocation<string>) {
  pollOnInterval(
    "https://farmbeats.local/relay",
    1000,
    invocation,
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
    "https://farmbeats.local/soil-moisture",
    1000,
    invocation,
    (j) => {
      return j.value;
    },
    -1
  );
}
