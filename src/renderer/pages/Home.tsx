import { type AdbDevice } from "@/../electron/backendApi";
import LogItem, { type LogEntry } from "@/components/LogItem";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useUserConfig } from "@/hooks/UserConfigProvider";
import { CircleAlertIcon, CircleCheckIcon, FolderOpen, Play, RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";
import Loading from "./Loading";

export default function Home() {
	const { userConfig, updateUserConfig } = useUserConfig();

	const [devices, setDevices] = useState<AdbDevice[]>([]);

	const [isRunning, setIsRunning] = useState(false);
	const [progress, setProgress] = useState(0);
	const [logs, setLogs] = useState<LogEntry[]>([
		{ timestamp: 1756509838, type: "info", content: "ADB Device Manager initialized" },
		{ timestamp: 234, type: "success", content: "Found 3 connected devices" },
		{ timestamp: 234, type: "warning", content: "Device authorization required for Pixel 7 Pro" },
		{ timestamp: 234, type: "error", content: "ERR Pixel 7 Pro" },
	]);

	async function refreshDevices() {
		const res = await backendApi.getDevices();
		if (!res.ok) {
			throw "handle err";
		}

		setDevices(res.data);
	}

	useEffect(() => {
		refreshDevices();
	}, []);

	if (!userConfig) {
		return <Loading />;
	}

	return (
		<div className="p-6 flex flex-col gap-4">
			{/* Header */}
			<div className="flex flex-col">
				<h1 className="text-3xl font-bold tracking-tight">BackPhoto</h1>
				<p className="text-muted-foreground">Back up your photos, save space</p>
			</div>

			<div className="flex flex-col items-stretch gap-3">
				<div className="flex gap-3">
					{/* Device Selection & Controls */}
					<Card className="min-w-96">
						<CardHeader>
							<CardTitle>Device Selection</CardTitle>
						</CardHeader>
						<CardContent>
							<div className="flex flex-col gap-4">
								<div className="flex flex-col gap-2">
									<div className="flex gap-2">
										<Select
											value={userConfig.adbDevice}
											onValueChange={(selected) => updateUserConfig({ adbDevice: selected })}
										>
											<SelectTrigger className="flex-1">
												<SelectValue placeholder={"Select device"} />
											</SelectTrigger>
											<SelectContent>
												{devices.map((device) => (
													<SelectItem key={device.serial} value={device.serial} disabled={!device.authorised}>
														<div className="flex items-center gap-2">
															{device.authorised ? (
																<CircleCheckIcon className="h-4 w-4 text-green-500" />
															) : (
																<CircleAlertIcon className="h-4 w-4 text-yellow-500" />
															)}
															<span>{device.authorised ? device.name : device.serial}</span>
														</div>
													</SelectItem>
												))}
												{userConfig.adbDevice && !devices.some((device) => device.serial === userConfig.adbDevice) && (
													<SelectItem value={userConfig.adbDevice} disabled>
														<div className="flex items-center gap-2">
															<CircleAlertIcon className="h-4 w-4 text-gray-400" />
															<span className="text-gray-400">{userConfig.adbDevice}</span>
														</div>
													</SelectItem>
												)}
											</SelectContent>
										</Select>
										<Button variant="outline" size="icon" onClick={refreshDevices}>
											<RefreshCw className="h-4 w-4" />
										</Button>
									</div>

									<div className="flex flex-col">
										<label className="text-sm font-semibold">Destination Path</label>
										<div className="flex gap-2">
											<Input
												className="flex-1"
												placeholder="D:\Photos\Phone"
												value={userConfig.destinationPath}
												onChange={(e) => updateUserConfig({ destinationPath: e.target.value })}
											/>
											<Button variant="outline" size="icon">
												<FolderOpen className="h-4 w-4" />
											</Button>
										</div>
									</div>
								</div>

								<Button
									disabled={!userConfig.adbDevice || !userConfig.destinationPath.trim() || isRunning}
									className="w-full"
									size="lg"
								>
									<Play className="h-4 w-4" />
									{isRunning ? "Running..." : "Back Up"}
								</Button>
							</div>
						</CardContent>
					</Card>

					{/* Progress */}
					<Card className="flex-1">
						<CardHeader>
							<CardTitle>Back Up Progress</CardTitle>
						</CardHeader>
						<CardContent>
							<div className="flex flex-col gap-2">
								<div className="flex justify-between">
									<span className="text-sm">Progress</span>
									<span className="text-sm">{Math.floor(progress)}%</span>
								</div>
								<Progress value={progress} className="h-2" />
								<p className="text-sm text-muted-foreground">{isRunning ? "In progress..." : "Ready to start"}</p>
							</div>
						</CardContent>
					</Card>
				</div>

				{/* Logs */}
				<div className="flex-1">
					<Card>
						<CardHeader>
							<CardTitle>Activity Log</CardTitle>
						</CardHeader>
						<CardContent>
							<ScrollArea className="min-h-40 max-h-[calc(100vh-30rem)] overflow-auto">
								<div className="flex flex-col gap-2">
									{logs.map((log, i) => (
										<LogItem key={`log-${i}`} log={log} />
									))}
								</div>
							</ScrollArea>
						</CardContent>
					</Card>
				</div>
			</div>
		</div>
	);
}
