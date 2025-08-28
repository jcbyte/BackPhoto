// See the Electron documentation for details on how to use preload scripts:
// https://www.electronjs.org/docs/latest/tutorial/process-model#preload-scripts

// const { contextBridge, ipcRenderer } = require("electron");

import { contextBridge, ipcRenderer } from "electron";
import type { AdbDevice } from "./backendApi";
import type { UserConfig } from "./storage";

contextBridge.exposeInMainWorld("electronApi", {
	getConfig: (): Promise<UserConfig> => ipcRenderer.invoke("electronApi.getConfig"),
	updateConfig: (updates: Partial<UserConfig>): Promise<UserConfig> =>
		ipcRenderer.invoke("electronApi.updateConfig", updates),
});

contextBridge.exposeInMainWorld("backendApi", {
	getDevices: (): Promise<AdbDevice[]> => ipcRenderer.invoke("backendApi.getDevices"),
});
