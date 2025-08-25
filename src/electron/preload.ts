// See the Electron documentation for details on how to use preload scripts:
// https://www.electronjs.org/docs/latest/tutorial/process-model#preload-scripts

// const { contextBridge, ipcRenderer } = require("electron");

import { contextBridge, ipcRenderer } from "electron";
import { UserConfig } from "./storage";

contextBridge.exposeInMainWorld("electronApi", {
	getConfig: (): Promise<UserConfig> => ipcRenderer.invoke("getConfig"),
	updateConfig: (updates: Partial<UserConfig>): Promise<UserConfig> => ipcRenderer.invoke("updateConfig", updates),
});
