import { BackendResponse } from "@/../electron/api/backend";
import { createContext, ReactNode, useContext, useEffect, useState } from "react";

interface BackendRunningContextType {
	isLoading: boolean;
	backendRunning: boolean;
	markBackendDown: () => void;
	tryFix(): Promise<boolean>;
}

const BackendRunningContext = createContext<BackendRunningContextType | undefined>(undefined);

export function BackendRunningProvider({ children }: { children: ReactNode }) {
	const [isLoading, setIsLoading] = useState(true);
	const [backendRunning, setBackendRunning] = useState<boolean>(false);

	useEffect(() => {
		async function checkRunning() {
			const res = await backendApi.connectToADB();
			setBackendRunning(res.ok);
			setIsLoading(false);
		}

		electronApi.onLoaded(() => checkRunning());
	}, []);

	async function tryFix(): Promise<boolean> {
		async function runFix(): Promise<boolean> {
			let res: BackendResponse = await backendApi.connectToADB();

			if (res.ok) return true;

			if (res.backendError === "backend") {
				await serverManagerApi.startBackend();
				res = await backendApi.connectToADB(); // Call again to check if its now an adb error
				if (res.ok) return true;
			}

			if (res.backendError === "adb") {
				await serverManagerApi.startADB();
				res = await backendApi.connectToADB();
				if (res.ok) return true;
			}

			return false;
		}

		const fixed = await runFix();
		setBackendRunning(fixed);
		return fixed;
	}

	function markBackendDown() {
		setBackendRunning(false);
	}

	return (
		<BackendRunningContext.Provider value={{ isLoading: isLoading, backendRunning, markBackendDown, tryFix }}>
			{children}
		</BackendRunningContext.Provider>
	);
}

export function useBackendRunning() {
	const ctx = useContext(BackendRunningContext);
	if (!ctx) {
		throw new Error("useBackendRunning must be used inside a BackendRunningProvider");
	}

	return ctx;
}
