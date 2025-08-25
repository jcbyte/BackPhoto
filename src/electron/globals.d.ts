import type { UserConfig } from "./storage";

declare global {
	namespace electronApi {
		function getConfig(): Promise<UserConfig>;
	}
}
