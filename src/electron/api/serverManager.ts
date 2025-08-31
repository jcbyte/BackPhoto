import { type ChildProcessWithoutNullStreams, spawn } from "child_process";
import { app, ipcMain } from "electron";
import getPort from "get-port";
import { DEV } from "../main";

let py: ChildProcessWithoutNullStreams | null = null;
let pyPort: number | null = null;

let adbPort: number | null = null;

export function getBackendHost(): string | null {
	if (!adbPort) return null;
	return `http://127.0.0.1:${pyPort}`;
}

export function getAdbPort(): number | null {
	return adbPort;
}

function logStd(label: string, buf: Buffer) {
	const lines = buf
		.toString()
		.split("\n")
		.map((line) => line.trim())
		.filter((line) => line);

	console.log(lines.map((line) => `[${label}]: ${line}`).join("\n"));
}

export async function startPythonServer(): Promise<void> {
	if (py) py.kill();

	// todo need to run not in dev mode
	const pyPath = "./backend/server.py";

	pyPort = await getPort({ host: "127.0.0.1" });

	return new Promise((resolve, reject) => {
		py = spawn("python", [pyPath], { env: { PORT: String(pyPort), ...(DEV && { DEV: "true" }) } });

		if (DEV) {
			py.stdout.on("data", (data: Buffer) => logStd("PYTHON STDOUT", data));
			py.stderr.on("data", (data: Buffer) => logStd("PYTHON STDERR", data));
		}

		function waitForStart(data: Buffer) {
			const NODE_SERVER_READY_STRING = "NODE_READ_SERVER_READY";

			const lines = data
				.toString()
				.split("\n")
				.map((line) => line.trim())
				.filter((line) => line);

			for (let line of lines) {
				// Resolve once the server is ready
				if (line.startsWith(NODE_SERVER_READY_STRING)) {
					// const lineData = line.replace(NODE_SERVER_READY_STRING, "").trim();
					// const { host, port } = JSON.parse(lineData);
					// pyHost = { hostname: host, port };
					console.log("Python server started");
					resolve();
					py?.stdout.off("data", waitForStart);
				}
			}
		}
		py.stdout.on("data", waitForStart);

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

export async function startAdbServer(): Promise<void> {
	if (adbPort) await killAdbServer(adbPort);

	// todo need to run not in dev mode
	const adbPath = "C:\\Users\\joel_\\Downloads\\platform-tools-latest-windows\\platform-tools\\adb.exe";

	adbPort = await getPort({ host: "127.0.0.1" });
	return new Promise((resolve, reject) => {
		const adb = spawn(adbPath, ["-P", String(adbPort), "start-server"], { env: {} });

		if (DEV) {
			adb.stdout.on("data", (data: Buffer) => logStd("ADB-START STDOUT", data));
			adb.stderr.on("data", (data: Buffer) => logStd("ADB-START STDERR", data));
		}

		adb.on("error", (err: any) => {
			console.error(`ADB start-server error: ${err}`);
			reject();
		});

		adb.on("exit", (code: any) => {
			console.log(`ADB start-server exited, code: ${code}`);
			resolve();
		});
	});
}

export async function killAdbServer(port: number): Promise<void> {
	// todo need to run not in dev mode
	const adbPath = "C:\\Users\\joel_\\Downloads\\platform-tools-latest-windows\\platform-tools\\adb.exe";

	return new Promise((resolve, reject) => {
		const adb = spawn(adbPath, ["-P", String(port), "kill-server"], { env: {} });

		if (DEV) {
			adb.stdout.on("data", (data: Buffer) => logStd("ADB-KILL STDOUT", data));
			adb.stderr.on("data", (data: Buffer) => logStd("ADB-KILL STDERR", data));
		}

		adb.on("error", (err: any) => {
			console.error(`ADB kill-server error: ${err}`);
			reject();
		});

		adb.on("exit", (code: any) => {
			console.log(`ADB kill-server exited, code: ${code}`);
			adbPort = null;
			resolve();
		});
	});
}

ipcMain.handle("serverManager.startADB", async (_event) => {
	await startAdbServer();
});

// Kill servers when Electron quits
app.on("before-quit", () => {
	if (py) py.kill();
	if (adbPort) killAdbServer(adbPort);
});
