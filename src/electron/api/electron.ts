import { dialog, ipcMain } from "electron";
import { isAppReady } from "../main";

ipcMain.handle("electron.pickFolder", async (_event) => {
	const result = await dialog.showOpenDialog({
		properties: ["openDirectory"],
	});

	if (result.canceled) return null;
	return result.filePaths[0]; // Returns the selected folder path
});

ipcMain.handle("electron._isAppReady", async (_event) => {
	return isAppReady();
});
