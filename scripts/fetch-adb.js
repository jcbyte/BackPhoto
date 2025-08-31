import fs from "fs";
import https from "https";
import os from "os";
import path from "path";
import yauzl from "yauzl";

// type Platform = "win32" | "darwin" | "linux";
// interface AdbConfig {
// 	url: string;
// 	files: string[];
// }

const PLATFORM_CONFIGS = {
	win32: {
		url: "https://dl.google.com/android/repository/platform-tools-latest-windows.zip",
		files: ["adb.exe", "adbwinapi.dll", "adbwinusbapi.dll"],
	},
	darwin: { url: "https://dl.google.com/android/repository/platform-tools-latest-darwin.zip", files: ["adb"] },
	linux: { url: "https://dl.google.com/android/repository/platform-tools-latest-linux.zip", files: ["adb"] },
};

function downloadFile(url, dest) {
	return new Promise((resolve, reject) => {
		const file = fs.createWriteStream(dest);

		console.log(`Downloading file from: ${url}`);
		https
			.get(url, (response) => {
				if (response.statusCode && response.statusCode >= 400) {
					return reject(new Error(`Failed to download: ${response.statusCode}`));
				}

				response.pipe(file);

				file.on("finish", () => {
					console.log(`File download complete`);

					file.close();
					resolve();
				});
				file.on("error", (err) => {
					console.log(`Response error: ${err}`);
					fs.unlink(dest, () => reject(err)); // delete partial file
				});
			})
			.on("error", (err) => {
				console.log(`Https error: ${err}`);
				fs.unlink(dest, () => reject(err)); // delete partial file
			});
	});
}

function extractFiles(src, files, dest) {
	return new Promise((resolve, reject) => {
		console.log(`Extracting files from ${src}`);
		yauzl.open(src, { lazyEntries: true }, (err, zipfile) => {
			if (err) reject(err);

			zipfile.on("entry", (entry) => {
				const filename = path.basename(entry.fileName);
				// Only extract if this file is in our list
				if (files.includes(filename)) {
					console.log(`\t- ${filename}`);
					zipfile.openReadStream(entry, (err, readStream) => {
						if (err) reject(err);

						// Ensure the directory exists
						const filePath = path.join(dest, filename);
						fs.mkdirSync(path.dirname(filePath), { recursive: true });

						const writeStream = fs.createWriteStream(filePath);
						readStream.pipe(writeStream);

						writeStream.on("finish", () => {
							// Move to next entry
							zipfile.readEntry();
						});
					});
				} else {
					// Skip files not in the list
					zipfile.readEntry();
				}
			});

			zipfile.on("end", () => {
				// Finish reading all files
				console.log(`Finish reading from ${src}`);
				resolve();
			});

			zipfile.readEntry();
		});
	});
}

(async () => {
	const distDir = path.resolve("dist/adb");
	const tempDir = os.tmpdir();

	const system = os.platform();
	console.log(`Identified platform: ${system}`);
	if (!(system in PLATFORM_CONFIGS)) throw new Error(`Unsupported platform: ${system}`);
	const config = PLATFORM_CONFIGS[system];

	fs.mkdirSync(distDir, { recursive: true });

	const zipPath = path.join(tempDir, "platform-tools.zip");

	await downloadFile(config.url, zipPath);
	await extractFiles(
		zipPath,
		config.files.map((file) => path.normalize(file)),
		distDir
	);
})();
