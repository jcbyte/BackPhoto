import { ipcMain } from "electron";

export type BackendResponse<T> = { ok: true; data: T } | { ok: false; detail: string };

interface BackendError {
	detail?: string;
}

export type AdbDevice = {
	serial: string;
} & ({ authorised: true; name: string } | { authorised: false });

ipcMain.handle("backendApi.getDevices", async (event): Promise<BackendResponse<AdbDevice[]>> => {
	type ExpectedResponse = { devices: AdbDevice[] };

	try {
		const res = await fetch("http://localhost:8000/devices");
		const data = (await res.json()) as ExpectedResponse | BackendError;

		if (!res.ok) {
			return { ok: false, detail: (data as BackendError).detail ?? "Error fetching devices" };
		}

		return { ok: true, data: (data as ExpectedResponse).devices };
	} catch (err: any) {
		return { ok: false, detail: "Unknown error fetching devices - Is the backend running?" };
	}
});
