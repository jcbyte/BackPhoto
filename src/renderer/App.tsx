import { Button } from "@/components/ui/button";
import { Toaster } from "@/components/ui/sonner";
import { useBackendRunning } from "@/hooks/BackendRunningProvider";
import BackendNotRunning from "@/pages/BackendNotRunning";
import Home from "@/pages/Home";
import Loading from "@/pages/Loading";
import Options from "@/pages/Options";
import type { LucideIcon } from "lucide-react";
import { HomeIcon, SettingsIcon } from "lucide-react";
import { useState } from "react";

type Tab = "home" | "options";
interface TabConfig {
	icon: LucideIcon;
	component: React.FC;
}
const TAB_CONFIG: Record<Tab, TabConfig> = {
	home: { icon: HomeIcon, component: Home },
	options: { icon: SettingsIcon, component: Options },
};

export default function App() {
	const { isLoading: backendLoading, backendRunning } = useBackendRunning();

	const [activeTab, setActiveTab] = useState<Tab>("home");
	const ActiveComponent = TAB_CONFIG[activeTab].component;

	if (backendLoading) {
		return (
			<div className="w-full h-screen">
				<Loading />
			</div>
		);
	}

	return (
		<>
			<div className="min-h-screen bg-background">
				{backendRunning ? (
					<div className="flex">
						<div className="w-16 min-h-screen bg-sidebar border-r border-sidebar-border flex flex-col items-center gap-4 py-4">
							{(Object.keys(TAB_CONFIG) as Tab[]).map((tab) => {
								const Icon = TAB_CONFIG[tab].icon;
								return (
									<Button
										key={tab}
										variant={tab === activeTab ? "default" : "ghost"}
										size="icon"
										onClick={() => setActiveTab(tab)}
										className="w-10 h-10"
									>
										<Icon className="h-5 w-5" />
									</Button>
								);
							})}
						</div>

						<div className="flex-1 container mx-auto min-h-screen min-w-sm">
							<ActiveComponent />
						</div>
					</div>
				) : (
					<BackendNotRunning />
				)}
			</div>

			<Toaster position="top-center" />
		</>
	);
}
