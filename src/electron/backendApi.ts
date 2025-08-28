import { ipcMain } from "electron";

const API_URL = "http://localhost:8000";

export type BackendResponse<T = void> =
	| ({ ok: true } & (T extends void ? {} : { data: T }))
	| { ok: false; detail: string };

interface BackendError {
	detail?: string;
}

export type AdbDevice = {
	serial: string;
} & ({ authorised: true; name: string } | { authorised: false });

ipcMain.handle("backendApi.connectToADB", async (_event): Promise<BackendResponse> => {
	try {
		const res = await fetch(`${API_URL}/connect`);

		if (!res.ok) {
			const data = (await res.json().catch(() => ({}))) as BackendError; // `catch` fallback if JSON invalid
			return { ok: false, detail: (data as BackendError).detail ?? "Error connecting to ADB" };
		}

		return { ok: true };
	} catch (err: any) {
		return { ok: false, detail: "Unknown error connecting to ADB - Is the backend running?" };
	}
});

ipcMain.handle("backendApi.getDevices", async (_event): Promise<BackendResponse<AdbDevice[]>> => {
	type ExpectedResponse = { devices: AdbDevice[] };

	try {
		const res = await fetch(`${API_URL}/devices`);
		const data = (await res.json().catch(() => ({}))) as ExpectedResponse | BackendError; // `catch` fallback if JSON invalid

		if (!res.ok) {
			return { ok: false, detail: (data as BackendError).detail ?? "Error fetching devices" };
		}

		return { ok: true, data: (data as ExpectedResponse).devices };
	} catch (err: any) {
		return { ok: false, detail: "Unknown error fetching devices - Is the backend running?" };
	}
});
