import { dialog, ipcMain } from "electron";

ipcMain.handle("electronApi.pickFolder", async (_event) => {
	const result = await dialog.showOpenDialog({
		properties: ["openDirectory"],
	});

	if (result.canceled) return null;
	return result.filePaths[0]; // Returns the selected folder path
});
