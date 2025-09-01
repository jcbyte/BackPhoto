import { LoaderCircleIcon } from "lucide-react";

export default function Loading() {
	return (
		<div className="w-full h-full flex flex-col gap-4 justify-center items-center">
			<LoaderCircleIcon className="animate-spin w-20 h-20" />
			<span className="text-3xl font-bold tracking-tight">BackPhoto</span>
		</div>
	);
}
