import type { AdbDevice, BackendResponse, BackupStreamedResponse } from "./backendApi";
import type { UserConfig } from "./storage";

declare global {
	namespace electronApi {
		function getConfig(): Promise<UserConfig>;
		function updateConfig(updates: Partial<UserConfig>): Promise<UserConfig>;
	}

	namespace backendApi {
		function connectToADB(): Promise<BackendResponse>;
		function getDevices(): Promise<BackendResponse<AdbDevice[]>>;
		function backup(onUpdate?: (update: BackupStreamedResponse) => void): Promise<BackendResponse>;
	}
}
