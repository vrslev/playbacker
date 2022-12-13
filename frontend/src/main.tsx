import { render } from "solid-js/web";
import App from "./App";
import "./main.css";

addEventListener("error", (event) => alert(event.error));

render(() => <App />, document.getElementById("root") as HTMLElement);
