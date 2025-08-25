import type { Configuration } from "webpack";

import { plugins } from "./webpack.plugins";
import { rules } from "./webpack.rules";

rules.push({
	test: /\.css$/,
	use: [
		{
			loader: "style-loader",
		},
		{
			loader: "css-loader",
			options: {
				importLoaders: 1,
			},
		},
		{
			loader: "postcss-loader",
		},
	],
});

export const rendererConfig: Configuration = {
	module: {
		rules,
	},
	plugins,
	resolve: {
		extensions: [".js", ".ts", ".jsx", ".tsx", ".css"],
	},
};
