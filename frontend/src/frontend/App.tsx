import { useCallback, useState } from "react";

function App() {
	/* snip... */
	const [nodeVersion, setNodeVersion] = useState<string | undefined>(undefined);

	const updateNodeVersion = useCallback(
		async () => setNodeVersion(await backend.nodeVersion("Hello from App.tsx!")),
		[]
	);

	return (
		<div className="App">
			{/* snip... */}
			<button onClick={updateNodeVersion}>Node version is {nodeVersion}</button>
			{/* snip... */}
		</div>
	);
}

export default App;
