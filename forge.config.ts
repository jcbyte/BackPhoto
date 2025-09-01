import { MakerDeb } from "@electron-forge/maker-deb";
import { MakerSquirrel } from "@electron-forge/maker-squirrel";
import { MakerZIP } from "@electron-forge/maker-zip";
import { AutoUnpackNativesPlugin } from "@electron-forge/plugin-auto-unpack-natives";
import { FusesPlugin } from "@electron-forge/plugin-fuses";
import { WebpackPlugin } from "@electron-forge/plugin-webpack";
import type { ForgeConfig } from "@electron-forge/shared-types";
import { FuseV1Options, FuseVersion } from "@electron/fuses";

import { mainConfig } from "./webpack.main.config";
import { rendererConfig } from "./webpack.renderer.config";

const config: ForgeConfig = {
	packagerConfig: {
		asar: true,
		extraResource: ["./dist", "./assets"],
		icon: "./assets/icon",
	},
	rebuildConfig: {},
	makers: [
		new MakerSquirrel({
			setupIcon: "./assets/icon.ico",
			iconUrl: "https://raw.githubusercontent.com/jcbyte/BackPhoto/refs/heads/main/assets/icon.ico",
		}),
		new MakerZIP({}, ["darwin"]), // ! Untested on macos
		new MakerDeb({
			options: {
				icon: "./assets/icon.png",
			},
		}),
	],
	plugins: [
		new AutoUnpackNativesPlugin({}),
		new WebpackPlugin({
			mainConfig,
			renderer: {
				config: rendererConfig,
				entryPoints: [
					{
						html: "./src/renderer/index.html",
						js: "./src/renderer/renderer.tsx",
						name: "main_window",
						preload: {
							js: "./src/electron/preload.ts",
						},
					},
				],
			},
		}),
		// Fuses are used to enable/disable various Electron functionality
		// at package time, before code signing the application
		new FusesPlugin({
			version: FuseVersion.V1,
			[FuseV1Options.RunAsNode]: false,
			[FuseV1Options.EnableCookieEncryption]: true,
			[FuseV1Options.EnableNodeOptionsEnvironmentVariable]: false,
			[FuseV1Options.EnableNodeCliInspectArguments]: false,
			[FuseV1Options.EnableEmbeddedAsarIntegrityValidation]: true,
			[FuseV1Options.OnlyLoadAppFromAsar]: true,
		}),
	],
	publishers: [
		{
			name: "@electron-forge/publisher-github",
			config: {
				repository: {
					owner: "jcbyte",
					name: "BackPhoto",
				},
				prerelease: false,
			},
		},
	],
};

export default config;
