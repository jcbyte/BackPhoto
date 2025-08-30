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

		checkRunning();
	}, []);

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
