import { LoaderCircleIcon } from "lucide-react";

export default function Loading() {
	return (
		<div className="w-full h-full flex flex-col gap-2 justify-center items-center">
			<LoaderCircleIcon className="animate-spin w-18 h-18" />
			<span className="text-3xl font-bold tracking-tight">BackPhoto</span>
		</div>
	);
}
