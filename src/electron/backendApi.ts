import { ipcMain } from "electron";
import { EventSource } from "eventsource";
import { getUserConfig } from "./storage";
const API_URL = "http://localhost:8000";

export type BackendSuccessResponse<T = void> = { ok: true } & (T extends void ? {} : { data: T });
export type BackendErrorResponse = { ok: false; detail: string };
export type BackendResponse<T = void> = BackendSuccessResponse<T> | BackendErrorResponse;

export interface BackendApiError {
	detail?: string;
}

export type AdbDevice = {
	serial: string;
} & ({ authorised: true; name: string } | { authorised: false });

export interface BackupStreamedResponse {
	progress?: number;
	log?: {
		timestamp: number;
		type: "info" | "success" | "error" | "warning";
		content: string;
	};
}

ipcMain.handle("backendApi.connectToADB", async (_event): Promise<BackendResponse> => {
	try {
		const res = await fetch(`${API_URL}/connect`, { method: "POST" });

		if (!res.ok) {
			const data = (await res.json().catch(() => ({}))) as BackendApiError; // `catch` fallback if JSON invalid
			return { ok: false, detail: data.detail ?? "Error connecting to ADB" };
		}

		return { ok: true };
	} catch {
		return { ok: false, detail: "Unknown error connecting to ADB - Is the backend running?" };
	}
});

ipcMain.handle("backendApi.getDevices", async (_event): Promise<BackendResponse<AdbDevice[]>> => {
	type ExpectedResponse = { devices: AdbDevice[] };

	try {
		const res = await fetch(`${API_URL}/devices`);
		const data = (await res.json().catch(() => ({}))) as ExpectedResponse | BackendApiError; // `catch` fallback if JSON invalid

		if (!res.ok) {
			return { ok: false, detail: (data as BackendApiError).detail ?? "Error fetching devices" };
		}

		return { ok: true, data: (data as ExpectedResponse).devices };
	} catch {
		return { ok: false, detail: "Unknown error fetching devices - Is the backend running?" };
	}
});

let backupEs: EventSource | null = null;

ipcMain.handle("backendApi.backup", async (event): Promise<void> => {
	type ExpectedResponse = { jobId: string };

	// Get backup jobId
	let data: ExpectedResponse | BackendApiError;
	try {
		const userConfig = getUserConfig();
		const res = await fetch(`${API_URL}/backup/start`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({ config: userConfig }),
		});
		data = (await res.json().catch(() => ({}))) as ExpectedResponse | BackendApiError; // `catch` fallback if JSON invalid

		if (!res.ok) {
			const error: BackendErrorResponse = {
				ok: false,
				detail: (data as BackendApiError).detail ?? "Error starting backup",
			};
			event.sender.send("backendApi.backup:error", error);
			return;
		}
	} catch {
		const error: BackendErrorResponse = {
			ok: false,
			detail: "Unknown error starting the backup - Is the backend running?",
		};
		event.sender.send("backendApi.backup:error", error);
		return;
	}

	// SSE on backup
	if (backupEs) backupEs.close();
	const params = new URLSearchParams({ jobId: (data as ExpectedResponse).jobId });
	const es = new EventSource(`${API_URL}/backup?${params.toString()}`);
	backupEs = es;

	function throwEs(error: BackendErrorResponse) {
		event.sender.send("backendApi.backup:error", error);
		es.close();
	}

	es.onmessage = (ev) => {
		try {
			const data = JSON.parse(ev.data) as BackupStreamedResponse;
			event.sender.send("backendApi.backup:update", data);
		} catch {
			// Malformed data received from SSE
		}
	};

	es.addEventListener("backend-error", (ev) => {
		const data = ev.data as string;
		throwEs({ ok: false, detail: data });
	});

	es.onerror = (_ev) => {
		throwEs({ ok: false, detail: "Unknown error trying backup - Is the backend running?" });
		es.close();
	};
});
