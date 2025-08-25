import type { UserConfig } from "./storage";

declare global {
	namespace electronApi {
		function getConfig(): Promise<UserConfig>;
		function updateConfig(updates: Partial<UserConfig>): Promise<UserConfig>;
	}
}
