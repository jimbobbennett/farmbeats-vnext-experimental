/*
 * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 * See LICENSE in the project root for license information.
 */
// images references in the manifest
import "../../assets/icon-16.png";
import "../../assets/icon-32.png";
import "../../assets/icon-80.png";
/// <reference path="../globals.d.ts" />
/// <reference path="../shared.ts" />

import { check_device_id, check_and_set_device_id, get_device_id_from_sheet } from "../shared";
/* global window, console, document, Excel, Office, fetch , globalThis*/

var _error_label;
var _is_streaming = false;
var _device_id_title: HTMLElement;

async function getDataPollTime(): Promise<number> {
  return await Excel.run(async (context) => {
    try {
      console.log("Getting poll time...");
      const sheet = context.workbook.worksheets.getItem("Configuration");
      var range = sheet.getRange("DataPollTime");
      range.load("values");
      await context.sync();
      var poll_time = range.values[0][0];
      return poll_time * 1000;
    } catch (error) {
      console.error(error);
      return 60000;
    }
  });
}

async function getMaxDataRows(): Promise<number> {
  return await Excel.run(async (context) => {
    try {
      console.log("Getting max data rows ID...");
      const sheet = context.workbook.worksheets.getItem("Configuration");
      var range = sheet.getRange("MaxDataRows");
      range.load("values");
      await context.sync();
      return range.values[0][0];
    } catch (error) {
      console.error(error);
      return 500;
    }
  });
}

async function getDeviceId() {
  if (globalThis._host_name && check_device_id(globalThis._host_name)) {
    return;
  }

  await Excel.run(async (context) => {
    try {
      console.log("Getting device ID...");
      const sheet = context.workbook.worksheets.getItem("Configuration");
      var range = sheet.getRange("DeviceId");
      range.load("values");
      await context.sync();

      var device_id = range.values[0][0];

      await check_and_set_device_id(device_id);
      _device_id_title.textContent = "FarmBeats device ID - " + device_id;

      await context.sync();
      console.log("Device ID set to " + device_id);
      return true;
    } catch (error) {
      console.error(error);
      return false;
    }
  });
}

// The initialize function must be run each time a new page is loaded
Office.initialize = async () => {
  document.getElementById("sideload-msg").style.display = "none";
  document.getElementById("app-body").style.display = "flex";
  document.getElementById("relay_off").onclick = relay_off;
  document.getElementById("relay_on").onclick = relay_on;
  document.getElementById("start_streaming").onclick = start_streaming;
  document.getElementById("stop_streaming").onclick = stop_streaming;
  document.getElementById("clear_streaming").onclick = clear_streaming_data;
  _error_label = document.getElementById("error-label");
  _device_id_title = document.getElementById("device-id-title");

  await getDeviceId();

  globalThis._data_timer = window.setInterval(async () => {
    await getDeviceId();
  }, 10000);
};

export interface HistoryRow {
  date: number;
  soil_moisture: number;
  temperature: number;
  humidity: number;
  soil_temperature: number;
  visible: number;
  infra_red: number;
  ultra_violet: number;
  relay_state: number;
  button1_state: number;
  button2_state: number;
}

function build_data_range(row_number: number) {
  return "A" + row_number.toString() + ":L" + row_number.toString();
}

function writeRow(sheet: Excel.Worksheet, row_number: number, history_row: HistoryRow) {
  var range = sheet.getRange(build_data_range(row_number));
  range.values = [
    [
      history_row.date,
      "",
      history_row.soil_moisture,
      history_row.temperature,
      history_row.humidity,
      history_row.soil_temperature,
      history_row.visible,
      history_row.infra_red,
      history_row.ultra_violet,
      history_row.relay_state,
      history_row.button1_state,
      history_row.button2_state,
    ],
  ];

  range = sheet.getRange("B" + row_number.toString());
  range.formulas = [["=(((A" + row_number.toString() + "/60)/60)/24)+DATE(1970,1,1)"]];
}

async function writeData(history: HistoryRow[]) {
  await Excel.run(async (context) => {
    const sheet = context.workbook.worksheets.getItem("Data In");
    writeRow(sheet, 5, history[history.length - 1]);

    var last_date = await getLastDate();

    for (let history_row of history) {
      if (history_row.date > last_date && _is_streaming) {
        last_date = history_row.date;

        var range = sheet.getRange(build_data_range(9));
        range.insert(Excel.InsertShiftDirection.down);

        writeRow(sheet, 9, history_row);
      }
    }

    range = sheet.getRange(build_data_range(5));
    range.format.autofitColumns();

    var max_rows = await getMaxDataRows();
    range = sheet.getRange("A" + (max_rows + 9).toString() + ":L1048576");
    range.clear();

    await context.sync();
  });
}

async function getLastDate() {
  return await Excel.run(async (context) => {
    const sheet = context.workbook.worksheets.getItem("Data In");
    var range = sheet.getRange("A9");
    range.load("values");
    await context.sync();

    var last_date: number = range.values[0][0];
    if (!last_date) {
      last_date = 0;
    }

    console.log("Last date - " + last_date);

    await context.sync();
    return last_date;
  });
}

async function timer_tick() {
  try {
    const last_date = await getLastDate();
    await get_device_id_from_sheet();
    const response = await fetch(globalThis._host_name + "/history?from_date=" + last_date.toString());

    //Expect that status code is in 200-299 range
    if (!response.ok) {
      throw new Error(response.statusText);
    }

    const history = <HistoryRow[]>JSON.parse(await response.text());
    await writeData(history);
  } catch (error) {
    console.error(error);
  }
}

async function start_streaming() {
  stop_streaming();
  const poll_time = await getDataPollTime();
  console.log("Starting streaming. Will poll every " + poll_time.toString() + " ms");
  _is_streaming = true;
  await timer_tick();
  globalThis._data_timer = window.setInterval(async () => {
    await timer_tick();
  }, poll_time);
}

function stop_streaming() {
  console.log("Stopping streaming...");
  _is_streaming = false;
  if (globalThis._data_timer) {
    window.clearInterval(globalThis._data_timer);
    globalThis._data_timer = undefined;
  }
}

async function clear_streaming_data() {
  try {
    stop_streaming();
    await Excel.run(async (context) => {
      const sheet = context.workbook.worksheets.getItem("Data In");
      var range = sheet.getRange("A9:L1048576");
      range.clear();

      range = sheet.getRange("A5:L5");
      range.clear();

      await context.sync();
    });
  } catch (error) {
    console.error(error);
    _error_label.textContent = error;
  }
}

async function control_relay(value: boolean) {
  _error_label.textContent = "";
  try {
    await Excel.run(async (context) => {
      const data = {
        value: value,
      };
      const response = await fetch(globalThis._host_name + "/relay", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(response.statusText);
      }
      await context.sync();
    });
  } catch (error) {
    console.error(error);
    _error_label.textContent = error;
  }
}

async function relay_on() {
  await control_relay(true);
}

async function relay_off() {
  await control_relay(false);
}

// async function run() {
//   try {
//     await Excel.run(async (context) => {
//       /**
//        * Insert your Excel code here
//        */
//       const range = context.workbook.getSelectedRange();

//       // Read the range address
//       range.load("address");

//       // Update the fill color
//       range.format.fill.color = "yellow";

//       await context.sync();
//       console.log(`The range address was ${range.address}.`);
//     });
//   } catch (error) {
//     console.error(error);
//   }
// }
