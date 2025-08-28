import type { AdbDevice } from "./backendApi";
import type { UserConfig } from "./storage";

declare global {
	namespace electronApi {
		function getConfig(): Promise<UserConfig>;
		function updateConfig(updates: Partial<UserConfig>): Promise<UserConfig>;
	}

	namespace backendApi {
		function getDevices(): Promise<AdbDevice[]>;
	}
}
