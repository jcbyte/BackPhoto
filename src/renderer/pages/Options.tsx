import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { useUserConfig } from "@/hooks/UserConfigProvider";
import { AlertTriangleIcon, Folder, Plus, X } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import Loading from "./Loading";

export default function Options() {
	const { userConfig, updateUserConfig } = useUserConfig();

	const [newDirectory, setNewDirectory] = useState("");
	const [newFileType, setNewFileType] = useState("");

	function toPosix(path: string): string {
		let p = path.trim();
		if (!p) return "/";
		p = p.replace(/\\/g, "/"); // replace backslashes with forward slashes
		p = p.replace(/\/+/g, "/"); // remove duplicate slashes
		if (!p.startsWith("/")) p = "/" + p; // ensure leading slash
		if (p.length > 1 && p.endsWith("/")) p = p.slice(0, -1); // remove trailing slash (unless root "/")

		return p;
	}

	function handleAddIgnoredDir() {
		if (!newDirectory.trim()) return;

		const normalisedDir = toPosix(newDirectory);

		if (!userConfig || userConfig.ignoredDirs.includes(normalisedDir)) {
			toast.warning("That directory already exists!");
			return;
		}

		updateUserConfig({ ignoredDirs: [...userConfig.ignoredDirs, normalisedDir] });
		setNewDirectory("");
	}

	function handleRemoveIgnoredDir(dir: string) {
		if (!userConfig) return;

		updateUserConfig({ ignoredDirs: userConfig.ignoredDirs.filter((d) => d !== dir) });
	}

	function toExt(ext: string): string {
		let e = ext.trim();
		if (!e.startsWith(".")) e = "." + e; // ensure leading dot
		return e;
	}

	function handleAddFileType() {
		if (!newFileType.trim()) return;

		const normalisedFileType = toExt(newFileType);
		if (!userConfig || userConfig.fileTypes.includes(normalisedFileType)) {
			toast.warning("That file type already exists!");
			return;
		}

		updateUserConfig({ fileTypes: [...userConfig.fileTypes, normalisedFileType] });
		setNewFileType("");
	}

	function handleRemoveFileType(fileType: string) {
		if (!userConfig) return;

		updateUserConfig({ fileTypes: userConfig.fileTypes.filter((ft) => ft !== fileType) });
	}

	if (!userConfig) {
		return <Loading />;
	}

	return (
		<div className="p-6 flex flex-col gap-4">
			{/* Header */}
			<div className="flex flex-col">
				<h1 className="text-3xl font-bold tracking-tight">Settings</h1>
				<p className="text-muted-foreground">Configure your preferences</p>
			</div>

			{/* Ignored Directories */}
			<div className="col-span-4">
				<Card className="h-full">
					<CardHeader>
						<CardTitle>Ignored Directories</CardTitle>
						<span className="text-sm text-muted-foreground">These directories will be excluded from scanning</span>
					</CardHeader>
					<CardContent className="flex flex-col gap-3">
						<div className="flex gap-3 items-center">
							<Input
								placeholder="Enter directory name (e.g., /sdcard/DCIM/Ollie)"
								className="flex-1"
								value={newDirectory}
								onChange={(e) => setNewDirectory(e.target.value)}
								onKeyDown={(e) => e.key === "Enter" && handleAddIgnoredDir()}
							/>
							<Button variant="outline" size="icon" onClick={handleAddIgnoredDir}>
								<Plus className="h-6 w-6" />
							</Button>
						</div>

						<div className="flex flex-col">
							<span className="text-sm font-semibold">Currently Ignored ({userConfig.ignoredDirs.length})</span>
						</div>
						<div className="grid grid-cols-3 gap-3">
							{userConfig.ignoredDirs.map((dir) => (
								<div
									key={dir}
									className="flex items-center justify-between p-1 px-3 rounded-lg border border-border bg-muted/30 hover:bg-muted/50 transition-colors"
								>
									<div className="flex items-center gap-2">
										<Folder className="h-4 w-4" />
										<span className="font-medium text-sm">{dir}</span>
									</div>
									<Button
										variant="ghost"
										size="icon"
										className="h-6 w-6 p-4 hover:bg-red-500/20 hover:text-red-400"
										onClick={() => {
											handleRemoveIgnoredDir(dir);
										}}
									>
										<X className="h-3 w-3" />
									</Button>
								</div>
							))}
						</div>
					</CardContent>
				</Card>
			</div>

			{/* Included File Types */}
			<div className="col-span-4">
				<Card className="h-full">
					<CardHeader>
						<CardTitle>Included File Types</CardTitle>
						<span className="text-sm text-muted-foreground">These file types will be backed up</span>
					</CardHeader>
					<CardContent className="flex flex-col gap-3">
						<div className="flex gap-3 items-center">
							<Input
								placeholder="Enter file extension (e.g., .jpg, .mp4)"
								className="flex-1"
								value={newFileType}
								onChange={(e) => setNewFileType(e.target.value)}
								onKeyDown={(e) => e.key === "Enter" && handleAddFileType()}
							/>
							<Button variant="outline" size="icon" onClick={handleAddFileType}>
								<Plus className="h-6 w-6" />
							</Button>
						</div>

						<div className="flex flex-col">
							<span className="text-sm font-semibold">Currently Included ({userConfig.fileTypes.length})</span>
						</div>
						<div className="grid grid-cols-3 gap-2">
							{userConfig.fileTypes.map((fileType) => (
								<div
									key={fileType}
									className="flex items-center justify-between p-1 px-3 rounded-lg border border-border bg-muted/30 hover:bg-muted/50 transition-colors"
								>
									<div className="flex items-center gap-2">
										<Folder className="h-4 w-4" />
										<span className="font-medium text-sm">{fileType}</span>
									</div>
									<Button
										variant="ghost"
										size="icon"
										className="h-6 w-6 p-4 hover:bg-red-500/20 hover:text-red-400"
										onClick={() => {
											handleRemoveFileType(fileType);
										}}
									>
										<X className="h-3 w-3" />
									</Button>
								</div>
							))}
						</div>
					</CardContent>
				</Card>
			</div>

			{/* Boolean Toggles */}
			<div className="col-span-4">
				<Card className="h-full">
					<CardHeader>
						<CardTitle>General Settings</CardTitle>
					</CardHeader>
					<CardContent>
						<div className="flex flex-col gap-2">
							<div className="flex items-center gap-2">
								<Switch
									checked={userConfig.setExif}
									onCheckedChange={(value) => updateUserConfig({ setExif: value })}
								/>
								<div className="flex flex-col">
									<span className="text-sm font-medium">Set Missing EXIF Timestamps</span>
									<span className="text-xs text-muted-foreground">
										Automatically add timestamps to photos without EXIF data (existing timestamps remain unchanged).
									</span>
								</div>
							</div>

							<div className="flex items-center gap-2">
								<Switch
									checked={userConfig.skipDot}
									onCheckedChange={(value) => updateUserConfig({ skipDot: value })}
								/>
								<div className="flex flex-col">
									<span className="text-sm font-medium">Skip Hidden Files</span>
									<span className="text-xs text-muted-foreground">
										Ignore files and folders starting with a dot (.).
									</span>
								</div>
							</div>

							<div className="flex items-center gap-2">
								<Switch
									checked={userConfig.moveFiles}
									onCheckedChange={(value) => updateUserConfig({ moveFiles: value })}
								/>
								<div className="flex flex-col">
									<span className="text-sm font-medium">Move Files Instead of Copying</span>
									<span className="text-xs text-muted-foreground">Remove files from the device after backup.</span>
								</div>
							</div>

							{!userConfig.moveFiles && (
								<Alert variant="destructive">
									<AlertTriangleIcon className="h-4 w-4" />
									<AlertDescription>
										<span>
											<span className="font-semibold">Warning:</span> Copying files may create duplicates in destination
											folder when re-run.
										</span>
									</AlertDescription>
								</Alert>
							)}

							<div className="flex items-center gap-2">
								<Switch
									checked={userConfig.removeTempFiles}
									onCheckedChange={(value) => updateUserConfig({ removeTempFiles: value })}
								/>
								<div className="flex flex-col">
									<span className="text-sm font-medium">Remove Temporary Files</span>
									<span className="text-xs text-muted-foreground">
										Remove BackPhoto's temporary files after backup is complete.
									</span>
								</div>
							</div>
						</div>
					</CardContent>
				</Card>
			</div>
		</div>
	);
}
