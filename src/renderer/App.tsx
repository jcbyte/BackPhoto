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
					</div>

					<div className="flex-1 container mx-auto min-h-screen min-w-sm">
						<ActiveComponent />
					</div>
				</div>
			</div>

			<Toaster position="top-center" />

			<div className="fixed flex flex-col gap-1 bottom-4 right-4">
				<div
					className="bg-red-700"
					onClick={() => {
						backendApi.connectToADB().then((r) => console.log(r));
					}}
				>
					connect
				</div>
				<div
					className="bg-cyan-700"
					onClick={() => {
						backendApi.getDevices().then((r) => console.log(r));
					}}
				>
					devices
				</div>
				<div
					className="bg-purple-700"
					onClick={() => {
						backendApi.backup(
							(u) => console.log("update", u),
							(e) => console.log("error", e)
						);
					}}
				>
					backup
				</div>
			</div>
		</>
	);
}
