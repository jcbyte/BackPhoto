import { Button } from "@/components/ui/button";
import { Toaster } from "@/components/ui/sonner";
import Home from "@/pages/Home";
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
	const [activeTab, setActiveTab] = useState<Tab>("home");
	const ActiveComponent = TAB_CONFIG[activeTab].component;

	return (
		<>
			<div className="min-h-screen bg-background">
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
						<Button
							variant="secondary"
							size="icon"
							onClick={() => {
								backendApi.getDevices().then((r) => console.log(r));
							}}
							className="w-10 h-10"
						>
							T
						</Button>
					</div>

					<div className="flex-1">
						<ActiveComponent />
					</div>
				</div>
			</div>
			<Toaster position="top-center" />
		</>
	);
}
