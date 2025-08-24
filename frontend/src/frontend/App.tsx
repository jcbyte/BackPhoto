import { useCallback, useState } from "react";

function App() {
	/* snip... */
	const [nodeVersion, setNodeVersion] = useState<string | undefined>(undefined);

	const updateNodeVersion = useCallback(
		async () => setNodeVersion(await backend.nodeVersion("Hello from App.tsx!")),
		[]
	);

	return (
		<div>
			<span className="text-red-500">Hello world</span>
			<button onClick={updateNodeVersion}>Node version is {nodeVersion}</button>
		</div>
	);
}

export default App;
