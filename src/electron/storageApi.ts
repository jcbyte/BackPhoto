import { ipcMain } from "electron";
import Store from "electron-store";

export interface UserConfig {
	adbDevice?: string;
	destinationPath: string;
	ignoredDirs: string[];
	fileTypes: string[];
	setExif: boolean;
	skipDot: boolean;
	moveFiles: boolean;
	removeTempFiles: boolean;
}
const DEFAULT_USER_CONFIG: UserConfig = {
	destinationPath: "",
	ignoredDirs: ["/sdcard/Android", "/sdcard/storage"],
	fileTypes: [".jpg", ".jpeg", ".webp", ".png", ".mp4"],
	setExif: true,
	skipDot: true,
	moveFiles: true,
	removeTempFiles: true,
};

const store = new Store<UserConfig>({
	defaults: {
		userConfig: DEFAULT_USER_CONFIG,
	},
});

export function getUserConfig(): UserConfig {
	const config = store.get("userConfig", DEFAULT_USER_CONFIG);
	return config;
}

ipcMain.handle("storageApi.getConfig", (_event) => {
	return getUserConfig();
});

ipcMain.handle("storageApi.updateConfig", (_event, updates: Partial<UserConfig>) => {
	const currentConfig = store.get("userConfig");
	const updatedConfig = { ...currentConfig, ...updates };

	store.set("userConfig", updatedConfig);

	return updatedConfig;
});
