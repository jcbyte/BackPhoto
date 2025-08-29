// See the Electron documentation for details on how to use preload scripts:
// https://www.electronjs.org/docs/latest/tutorial/process-model#preload-scripts

import { contextBridge, ipcRenderer } from "electron";
import type { AdbDevice, BackendErrorResponse, BackendResponse, BackupStreamedResponse } from "./backendApi";
import type { UserConfig } from "./storage";

contextBridge.exposeInMainWorld("electronApi", {
	getConfig: (): Promise<UserConfig> => ipcRenderer.invoke("electronApi.getConfig"),
	updateConfig: (updates: Partial<UserConfig>): Promise<UserConfig> =>
		ipcRenderer.invoke("electronApi.updateConfig", updates),
});

contextBridge.exposeInMainWorld("backendApi", {
	connectToADB: (): Promise<BackendResponse> => ipcRenderer.invoke("backendApi.connectToADB"),
	getDevices: (): Promise<BackendResponse<AdbDevice[]>> => ipcRenderer.invoke("backendApi.getDevices"),
	backup: (
		onUpdate?: (update: BackupStreamedResponse) => void,
		onError?: (error: BackendErrorResponse) => void
	): Promise<void> => {
		ipcRenderer.removeAllListeners("backendApi.backup:update");
		if (onUpdate) {
			ipcRenderer.on("backendApi.backup:update", (_event, update: BackupStreamedResponse) => {
				onUpdate(update);
			});
		}

		ipcRenderer.removeAllListeners("backendApi.backup:error");
		if (onError) {
			ipcRenderer.on("backendApi.backup:error", (_event, error: BackendErrorResponse) => {
				onError(error);
			});
		}

		return ipcRenderer.invoke("backendApi.backup");
	},
});
