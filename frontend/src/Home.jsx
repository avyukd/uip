import React from "react";
import { useState, useEffect, useReducer } from "react";
import StocksTable from "./components/StocksTable";
import InputForm from "./components/InputForm";
import axios from "axios";
import {Splitter, SplitterPanel} from 'primereact/splitter';
import "primereact/resources/themes/lara-light-indigo/theme.css";  //theme
// import "primereact/resources/themes/md-dark-indigo/theme.css";
//import "primereact/resources/themes/mdc-dark-deeppurple/theme.css

import "primereact/resources/primereact.min.css";                  //core css
import "primeicons/primeicons.css";                                //icons

const Home = () => {
    const [inputs, updateInputs] = useReducer((state, updates) => ({...state, ...updates}), {});

    const getDefaults = async () => {
        const response = await axios.get("http://127.0.0.1:8000/get_defaults");
        updateInputs(response.data);
    }

    useEffect(getDefaults, []); 

    return (
        <Splitter style={{height: "750px", maxWidth: "1500px"}} >
            <SplitterPanel size={30} style={{textAlign: "center"}}>
                <InputForm inputs={inputs} updateInputs={updateInputs} getDefaults={getDefaults}/>
            </SplitterPanel>
            <SplitterPanel size={70}>
                <StocksTable inputs={inputs}/>
            </SplitterPanel>
        </Splitter>
    );
}
    
export default Home;
