/// <reference path="globals.d.ts" />
/* global console, Excel, fetch, globalThis */

export async function check_device_id(device_id: string) {
  const response = await fetch(device_id);
  return response.ok;
}

export async function check_and_set_device_id(device_id: string) {
  var host = device_id;
  if (!host.toLowerCase().startsWith("https://")) {
    host = "https://" + host;
  }

  if (host.endsWith("/")) {
    host = host.slice(0, -1);
  }

  if (host.indexOf(".") < 0) {
    host = host + ".local";
  }

  // Test it out
  console.log("Checking host " + host);
  if (!(await check_device_id(host))) {
    throw new Error("Device " + host + " not found");
  }

  globalThis._host_name = host;
}

export async function get_device_id_from_sheet() {
  if (!globalThis._host_name) {
    await Excel.run(async (context) => {
      try {
        console.log("Getting device ID...");
        let sheet = context.workbook.worksheets.getItem("Configuration");
        var range = sheet.getRange("DeviceId");
        range.load("values");
        await context.sync();

        var device_id = range.values[0][0];

        await check_and_set_device_id(device_id);

        await context.sync();
        console.log("Device ID set to " + device_id);
      } catch (error) {
        console.error(error);
      }
    });
  }
}
