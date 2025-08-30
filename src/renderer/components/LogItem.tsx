import { CircleAlertIcon, CircleCheckIcon, InfoIcon, OctagonAlertIcon } from "lucide-react";

import { type LogEntry } from "@/../electron/api/backend";
export type { LogEntry };

export default function LogItem({ log }: { log: LogEntry }) {
	const getLogIcon = (type: LogEntry["type"]) => {
		switch (type) {
			case "success":
				return <CircleCheckIcon className="h-4 w-4 text-success shrink-0" />;
			case "warning":
				return <CircleAlertIcon className="h-4 w-4 text-warning shrink-0" />;
			case "error":
				return <OctagonAlertIcon className="h-4 w-4 text-destructive shrink-0" />;
			case "info":
				return <InfoIcon className="h-4 w-4 text-info shrink-0" />;
		}
	};

	return (
		<div className="flex items-center gap-2 px-2 py-1.5 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors">
			{getLogIcon(log.type)}
			<span className="text-xs text-muted-foreground font-mono tabular-nums w-16 shrink-0">
				{new Date(log.timestamp * 1000).toLocaleTimeString([], {
					hour: "2-digit",
					minute: "2-digit",
					second: "2-digit",
				})}
			</span>
			<span className="text-sm">{log.content}</span>
		</div>
	);
}
