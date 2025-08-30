import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useBackendRunning } from "@/hooks/BackendRunningProvider";
import { OctagonAlertIcon } from "lucide-react";
import { useState } from "react";

export default function BackendNotRunning() {
	const { tryFix } = useBackendRunning();
	const [tryingFix, setTryingFix] = useState<boolean>(false);

	async function handleTryFix() {
		setTryingFix(true);
		await tryFix();
		setTryingFix(false);
	}

	return (
		<div className="w-full h-screen flex flex-col justify-center items-center">
			<Card className="w-96 shadow-lg">
				<CardContent className="flex flex-col items-center gap-6">
					<div className="flex flex-col items-center">
						<OctagonAlertIcon className="h-10 w-10 text-red-500" />
						<span className="text-lg font-semibold">Backend Error</span>
						<span className="text-sm text-muted-foreground">The backend service is not running.</span>
					</div>

					<Button onClick={handleTryFix} className="w-32" disabled={tryingFix}>
						Try Fix
					</Button>
				</CardContent>
			</Card>
		</div>
	);
}
