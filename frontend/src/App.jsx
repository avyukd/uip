import * as React from "react";
import { Routes, Route, Link, BrowserRouter } from "react-router-dom";
import Home from "./Home";
import MarkdownView from "./components/MarkdownView";

const App = () => {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route exact path="/" element={<Home/>} />
          <Route path="stocks/:ticker" element={<MarkdownView/>} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;