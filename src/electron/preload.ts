// See the Electron documentation for details on how to use preload scripts:
// https://www.electronjs.org/docs/latest/tutorial/process-model#preload-scripts

import { contextBridge, ipcRenderer } from "electron";
import type { AdbDevice, BackendResponse, BackupStreamedResponse } from "./api/backend";
import type { UserConfig } from "./api/storage";

let appReady: boolean = false;
let appReadyCallbacks: (() => void)[] = [];
ipcRenderer.once("electron.onLoaded", () => {
	appReady = true;

	while (appReadyCallbacks.length > 0) {
		appReadyCallbacks.pop()!();
	}
});

contextBridge.exposeInMainWorld("serverManagerApi", {
	startBackend: (): Promise<void> => ipcRenderer.invoke("serverManager.startBackend"),
	startADB: (): Promise<void> => ipcRenderer.invoke("serverManager.startADB"),
});

contextBridge.exposeInMainWorld("electronApi", {
	onLoaded: (callback: () => void): void => {
		if (appReady) callback();
		else appReadyCallbacks.push(callback);
	},
	pickFolder: (): Promise<string | null> => ipcRenderer.invoke("electron.pickFolder"),
});

contextBridge.exposeInMainWorld("storageApi", {
	getConfig: (): Promise<UserConfig> => ipcRenderer.invoke("storage.getConfig"),
	updateConfig: (updates: Partial<UserConfig>): Promise<UserConfig> =>
		ipcRenderer.invoke("storage.updateConfig", updates),
});

contextBridge.exposeInMainWorld("backendApi", {
	connectToADB: (): Promise<BackendResponse> => ipcRenderer.invoke("backend.connectToADB"),
	getDevices: (): Promise<BackendResponse<AdbDevice[]>> => ipcRenderer.invoke("backend.getDevices"),
	backup: (onUpdate?: (update: BackupStreamedResponse) => void): Promise<BackendResponse> => {
		ipcRenderer.removeAllListeners("backend.backup:update");
		if (onUpdate) {
			ipcRenderer.on("backend.backup:update", (_event, update: BackupStreamedResponse) => {
				onUpdate(update);
			});
		}
		return ipcRenderer.invoke("backend.backup");
	},
});
