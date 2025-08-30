import { createContext, ReactNode, useContext, useEffect, useState } from "react";

import type { UserConfig } from "@/../electron/api/storage";
export type { UserConfig };

interface UserConfigContextType {
	userConfig: UserConfig | undefined;
	updateUserConfig: (updates: Partial<UserConfig>) => Promise<void>;
}

const UserConfigContext = createContext<UserConfigContextType | undefined>(undefined);

export function UserConfigProvider({ children }: { children: ReactNode }) {
	const [userConfig, setUserConfig] = useState<UserConfig>();

	useEffect(() => {
		async function loadUserConfig() {
			const config = await storageApi.getConfig();
			setUserConfig(config);
		}
		loadUserConfig();
	}, []);

	async function updateUserConfig(updates: Partial<UserConfig>) {
		const config = await storageApi.updateConfig(updates);
		setUserConfig(config);
	}

	return <UserConfigContext.Provider value={{ userConfig, updateUserConfig }}>{children}</UserConfigContext.Provider>;
}

export function useUserConfig() {
	const ctx = useContext(UserConfigContext);
	if (!ctx) {
		throw new Error("useUserConfig must be used inside a UserConfigProvider");
	}

	return ctx;
}
