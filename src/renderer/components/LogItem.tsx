import { CircleAlertIcon, CircleCheckIcon, InfoIcon, OctagonAlertIcon } from "lucide-react";

export interface LogEntry {
	timestamp: string;
	type: "info" | "success" | "error" | "warning";
	message: string;
}

export default function LogItem({ entry }: { entry: LogEntry }) {
	const getLogIcon = (type: LogEntry["type"]) => {
		switch (type) {
			case "success":
				return <CircleCheckIcon className="h-4 w-4 text-green-500" />;
			case "warning":
				return <CircleAlertIcon className="h-4 w-4 text-yellow-500" />;
			case "error":
				return <OctagonAlertIcon className="h-4 w-4 text-red-500" />;
			case "info":
				return <InfoIcon className="h-4 w-4 text-blue-500" />;
		}
	};

	return (
		<div className="flex gap-3 p-3 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors">
			{getLogIcon(entry.type)}
			<div className="flex-1 flex flex-col gap-1">
				<span className="text-xs text-muted-foreground font-mono">{entry.timestamp}</span>
				<span className="text-sm">{entry.message}</span>
			</div>
		</div>
	);
}
