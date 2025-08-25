import LogItem, { type LogEntry } from "@/components/LogItem";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { CircleAlertIcon, CircleCheckIcon, FolderOpen, Play, RefreshCw } from "lucide-react";
import { useState } from "react";

interface Device {
	serial: string;
	name: string;
	status: "connected" | "unauthorised";
}

export default function Home() {
	const [devices, setDevices] = useState<Device[]>([
		{ serial: "device1", name: "Samsung Galaxy S23", status: "connected" },
		{ serial: "device2", name: "Pixel 7 Pro", status: "unauthorised" },
	]);
	const [selectedDevice, setSelectedDevice] = useState<string>("");
	const [destinationPath, setDestinationPath] = useState("");

	const [isRunning, setIsRunning] = useState(false);
	const [progress, setProgress] = useState(0);
	const [logs, setLogs] = useState<LogEntry[]>([
		{ timestamp: "14:32:15", type: "info", message: "ADB Device Manager initialized" },
		{ timestamp: "14:32:16", type: "success", message: "Found 3 connected devices" },
		{ timestamp: "14:32:17", type: "warning", message: "Device authorization required for Pixel 7 Pro" },
		{ timestamp: "14:32:17", type: "error", message: "ERR Pixel 7 Pro" },
	]);

	return (
		<div className="p-6 flex flex-col gap-4 h-screen">
			{/* Header */}
			<div className="flex flex-col">
				<h1 className="text-3xl font-bold tracking-tight">BackPhoto</h1>
				<p className="text-muted-foreground">Back up your photos, and save space</p>
			</div>

			<div className="flex flex-col gap-3">
				<div className="grid grid-cols-6 gap-3">
					{/* Device Selection & Controls */}
					<div className="col-span-2">
						<Card className="h-full">
							<CardHeader>
								<CardTitle>Device Selection</CardTitle>
							</CardHeader>
							<CardContent>
								<div className="flex flex-col gap-4">
									<div className="flex flex-col gap-2">
										<div className="flex gap-2">
											<Select value={selectedDevice} onValueChange={setSelectedDevice}>
												<SelectTrigger className="flex-1">
													<SelectValue placeholder="Select device" />
												</SelectTrigger>
												<SelectContent>
													{devices.map((device) => (
														<SelectItem
															key={device.serial}
															value={device.serial}
															disabled={device.status !== "connected"}
														>
															<div className="flex items-center gap-2">
																{device.status === "connected" ? (
																	<CircleCheckIcon className="h-4 w-4 text-green-500" />
																) : (
																	<CircleAlertIcon className="h-4 w-4 text-yellow-500" />
																)}
																<span>{device.name}</span>
															</div>
														</SelectItem>
													))}
												</SelectContent>
											</Select>
											<Button variant="outline" size="icon">
												<RefreshCw className="h-4 w-4" />
											</Button>
										</div>

										<div className="flex flex-col">
											<label className="text-sm font-semibold">Destination Path</label>
											<div className="flex gap-2">
												<Input
													className="flex-1"
													placeholder="D:\Photos\Phone"
													value={destinationPath}
													onChange={(e) => setDestinationPath(e.target.value)}
												/>
												<Button variant="outline" size="icon">
													<FolderOpen className="h-4 w-4" />
												</Button>
											</div>
										</div>
									</div>

									<Button disabled={!selectedDevice || !destinationPath || isRunning} className="w-full" size="lg">
										<Play className="h-4 w-4" />
										{isRunning ? "Running..." : "Back Up"}
									</Button>
								</div>
							</CardContent>
						</Card>
					</div>

					{/* Progress */}
					<div className="col-span-4">
						<Card className="h-full">
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
				</div>

				{/* Logs */}
				<div className="flex-1">
					<Card>
						<CardHeader>
							<CardTitle>Activity Log</CardTitle>
						</CardHeader>
						<CardContent>
							<ScrollArea className="max-h-[calc(100vh-30rem)] overflow-auto">
								<div className="flex flex-col gap-2">
									{logs.map((log, i) => (
										<LogItem key={`log-${i}`} entry={log} />
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
