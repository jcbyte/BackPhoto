import { type ChildProcessWithoutNullStreams, spawn } from "child_process";
import { app, ipcMain } from "electron";
import { DEV } from "../main";

interface Host {
	hostname: string;
	port: number;
}

let pyHost: Host | null = null;
let py: ChildProcessWithoutNullStreams | null = null;

export function getBackendHost(): string | null {
	if (!pyHost) return null;
	return `http://${pyHost.hostname}:${pyHost.port}`;
}

const NODE_SERVER_READY_STRING = "NODE_READ_SERVER_READY";

export function startPythonServer(): Promise<void> {
	if (py) py.kill();

	// todo need to run not in dev mode
	const pyPath = "./backend/server.py";

	return new Promise((resolve, reject) => {
		py = spawn("python", [pyPath], { env: { ...(DEV && { DEV: "true" }) } });

		py.stdout.on("data", (data: Buffer) => {
			const lines = data
				.toString()
				.split("\n")
				.filter((line) => line);

			if (DEV) console.log(lines.map((line) => `[PYTHON]: ${line.trim()}`).join("\n"));

			for (let line of lines) {
				if (line.startsWith(NODE_SERVER_READY_STRING)) {
					const lineData = line.replace(NODE_SERVER_READY_STRING, "").trim();
					const { host, port } = JSON.parse(lineData);
					pyHost = { hostname: host, port };
					console.log(`Python server started at: ${host}:${port}`);

					// Resolve once the server is ready
					resolve();
				}
			}
		});

		py.on("error", (err: any) => {
			console.error(`Python server error: ${err}`);
			reject();
		});

		py.on("exit", (code: any) => {
			console.log(`Python server exited, code: ${code}`);
		});
	});
}

ipcMain.handle("serverManager.startBackend", async (_event) => {
	await startPythonServer();
});

// Kill Python server when Electron quits
app.on("before-quit", () => {
	if (py) py.kill();
});
