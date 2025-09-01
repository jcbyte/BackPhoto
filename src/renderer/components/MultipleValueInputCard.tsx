import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { type LucideIcon, PlusIcon, XIcon } from "lucide-react";
import { useState } from "react";

export default function MultipleValueInputCard({
	title,
	subtitle,
	placeholder,
	currentlyText,
	Icon,
	values,
	onAddValue,
	onRemoveValue,
}: {
	title: string;
	subtitle?: string;
	placeholder?: string;
	currentlyText?: string;
	Icon?: LucideIcon;
	values: string[];
	onAddValue?: (value: string) => boolean;
	onRemoveValue?: (value: string) => void;
}) {
	const [newValue, setNewValue] = useState("");

	const handleAdd = () => {
		const formattedNewValue = newValue.trim();
		if (!formattedNewValue) return;
		if (onAddValue && onAddValue(formattedNewValue)) setNewValue("");
	};

	return (
		<Card className="h-full">
			<CardHeader>
				<CardTitle>{title}</CardTitle>
				{subtitle && <span className="text-sm text-muted-foreground">{subtitle}</span>}
			</CardHeader>
			<CardContent className="flex flex-col gap-3">
				<div className="flex gap-2 items-center">
					<Input
						placeholder={placeholder}
						className="flex-1"
						value={newValue}
						onChange={(e) => setNewValue(e.target.value)}
						onKeyDown={(e) => e.key === "Enter" && handleAdd()}
					/>
					<Button variant="outline" size="icon" onClick={handleAdd}>
						<PlusIcon className="h-6 w-6" />
					</Button>
				</div>

				{currentlyText && (
					<span className="text-sm font-semibold">
						{currentlyText} ({values.length})
					</span>
				)}

				<div className="flex flex-wrap gap-3">
					{values.map((value) => (
						<div
							key={value}
							className="flex items-center justify-between gap-2 py-1 px-3 rounded-lg border border-border bg-muted/30 hover:bg-muted/50 transition-colors"
						>
							<div className="flex items-center gap-2">
								{Icon && <Icon className="h-4 w-4" />}
								<span className="font-medium text-sm">{value}</span>
							</div>
							<Button
								variant="ghost"
								size="icon"
								className="h-6 w-6 p-4 hover:!bg-destructive/20 hover:!text-destructive/80"
								onClick={onRemoveValue ? () => onRemoveValue(value) : undefined}
							>
								<XIcon className="h-3 w-3" />
							</Button>
						</div>
					))}
				</div>
			</CardContent>
		</Card>
	);
}
