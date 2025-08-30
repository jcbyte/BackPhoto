import { Switch } from "@/components/ui/switch";

export default function DescriptiveSwitch({
	checked,
	onChange = () => {},
	title,
	description,
}: {
	checked: boolean;
	onChange?: (value: boolean) => void;
	title: string;
	description?: string;
}) {
	return (
		<div className="flex items-center gap-2" onClick={() => onChange(!checked)}>
			<Switch checked={checked} />
			<div className="flex flex-col">
				<span className="text-sm font-medium">{title}</span>
				{description && <span className="text-xs text-muted-foreground">{description}</span>}
			</div>
		</div>
	);
}
