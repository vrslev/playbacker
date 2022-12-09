import { render } from "solid-js/web";
import App from "./App";
import { apiPlayer } from "./core/api";
import { StoreProvider } from "./core/store";
import "./main.css";

render(
  () => (
    <StoreProvider player={apiPlayer()}>
      <App />
    </StoreProvider>
  ),
  document.getElementById("root") as HTMLElement
);
