import React from "react";
import { useState, useEffect, useReducer } from "react";
import StocksTable from "./components/StocksTable";
import InputForm from "./components/InputForm";
import axios from "axios";
import {Splitter, SplitterPanel} from 'primereact/splitter';
import { ScrollPanel } from 'primereact/scrollpanel';
import "primereact/resources/themes/lara-light-indigo/theme.css";  //theme
// import "primereact/resources/themes/md-dark-indigo/theme.css";
import "primereact/resources/primereact.min.css";                  //core css
import "primeicons/primeicons.css";                                //icons

export default () => {
    const [inputs, updateInputs] = useReducer((state, updates) => ({...state, ...updates}), {});

    useEffect(async () => {
        const response = await axios.get("http://127.0.0.1:8000/get_defaults");
        updateInputs(response.data);
    }, []); 

    return (
        <Splitter>
            <SplitterPanel size={20}>
                <ScrollPanel>
                    <InputForm inputs={inputs} updateInputs={updateInputs}/>
                </ScrollPanel>
            </SplitterPanel>
            <SplitterPanel size={80}>
                <StocksTable inputs={inputs}/>
            </SplitterPanel>
        </Splitter>
    );
}
    
