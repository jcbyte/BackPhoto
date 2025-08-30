// See the Electron documentation for details on how to use preload scripts:
// https://www.electronjs.org/docs/latest/tutorial/process-model#preload-scripts

import { contextBridge, ipcRenderer } from "electron";
import type { AdbDevice, BackendResponse, BackupStreamedResponse } from "./api/backend";
import type { UserConfig } from "./api/storage";

contextBridge.exposeInMainWorld("electronApi", {
	pickFolder: (): Promise<string | null> => ipcRenderer.invoke("electronApi.pickFolder"),
});

contextBridge.exposeInMainWorld("storageApi", {
	getConfig: (): Promise<UserConfig> => ipcRenderer.invoke("storageApi.getConfig"),
	updateConfig: (updates: Partial<UserConfig>): Promise<UserConfig> =>
		ipcRenderer.invoke("storageApi.updateConfig", updates),
});

contextBridge.exposeInMainWorld("backendApi", {
	connectToADB: (): Promise<BackendResponse> => ipcRenderer.invoke("backendApi.connectToADB"),
	getDevices: (): Promise<BackendResponse<AdbDevice[]>> => ipcRenderer.invoke("backendApi.getDevices"),
	backup: (onUpdate?: (update: BackupStreamedResponse) => void): Promise<BackendResponse> => {
		ipcRenderer.removeAllListeners("backendApi.backup:update");
		if (onUpdate) {
			ipcRenderer.on("backendApi.backup:update", (_event, update: BackupStreamedResponse) => {
				onUpdate(update);
			});
		}
		return ipcRenderer.invoke("backendApi.backup");
	},
});
