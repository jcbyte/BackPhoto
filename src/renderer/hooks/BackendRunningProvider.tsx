import { createContext, ReactNode, useContext, useState } from "react";

interface BackendRunningContextType {
	backendRunning: boolean;
	markBackendDown: () => void;
	tryFix(): Promise<boolean>;
}

const BackendRunningContext = createContext<BackendRunningContextType | undefined>(undefined);

export function BackendRunningProvider({ children }: { children: ReactNode }) {
	const [backendRunning, setBackendRunning] = useState<boolean>(true);

	async function tryFix(): Promise<boolean> {
		const res = await backendApi.connectToADB();

		if (!res.ok) {
			// todo try and fix

			return false;
		}

		setBackendRunning(true);
		return true;
	}

	function markBackendDown() {
		setBackendRunning(false);
	}

	return (
		<BackendRunningContext.Provider value={{ backendRunning, markBackendDown, tryFix }}>
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
