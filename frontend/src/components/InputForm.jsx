import React, { useEffect, useState } from "react";
import {InputText} from 'primereact/inputtext';
import {Accordion, AccordionTab} from 'primereact/accordion';
import { useReducer } from "react";
import { Button } from 'primereact/button';
import { ScrollPanel } from 'primereact/scrollpanel';
import { Dialog } from 'primereact/dialog';
import { Dropdown } from 'primereact/dropdown';
import axios from 'axios';

const InputForm = (props) => {

    const [tempInputs, updateTempInputs] = 
        useReducer((state, updates) => ({...state, ...updates}), {});
    
    const [scenarioName, setScenarioName] = useState("Scenario Name");

    const [displayResponsive, setDisplayResponsive] = useState(false);

    const [scenarioItems, setScenarioItems] = useState([]);

    const [chosenScenario, setChosenScenario] = useState(null);

    const [scenarioCreatedFlag, setScenarioCreatedFlag] = useState(false);

    useEffect(() => {
        updateTempInputs(props.inputs);
    }, [props]);

    useEffect(async () => {
        const response = await axios.get("http://127.0.0.1:8000/load_all_scenarios");
        const scenarios = response.data.scenarios.map(scenario => ({
            label: scenario,
            value: scenario
        }))
        setScenarioItems(scenarios);
        setScenarioCreatedFlag(false);
    }, [chosenScenario, scenarioCreatedFlag]);

    const handleTextChange = (event, ticker, label) => {
        updateTempInputs({[ticker]: {...tempInputs[ticker], 
            [label]: event.target.value}});
    }

    const saveScenario = async () => {
        const response = await axios.post("http://127.0.0.1:8000/save_scenario", props.inputs,
            {params: {
                name: scenarioName
            }});
        setScenarioCreatedFlag(true);
        setDisplayResponsive(false);
    }

    const handleSubmit = () => {
        const tempObj = {...tempInputs};
        Object.keys(tempObj).forEach(key => {
            Object.keys(tempObj[key]).forEach(label => {
                tempObj[key][label] = parseFloat(tempObj[key][label]);
            });
        });
        props.updateInputs(tempObj);
    }

    const handleReset = () => {
        props.getDefaults();
    }

    const handleScenarioDelete = async () => {
        const response = await axios.delete("http://127.0.0.1:8000/delete_scenario/" + chosenScenario);
        setChosenScenario(null);
    }

    const loadScenario = async () => {
        const response = await axios.get("http://127.0.0.1:8000/load_scenario/" + chosenScenario);
        props.updateInputs(response.data);
    }

    const formatTab = (header) => {
        if(header == "generics") {
            return "General";
        }
        return header;
    }

    const formatLabel = (label) => {
        const words = label.split("_");
        words.forEach((word, index) => {
            words[index] = word.charAt(0).toUpperCase() + word.slice(1);
        });
        return words.join(" ");
    }

    if (tempInputs === undefined || Object.keys(tempInputs).length == 0) {
        return (
            <div>
                <h1>Loading...</h1>
            </div>
        );
    }

    const input_components = Object.keys(props.inputs).map((ticker) => {
        const inner_inputs = Object.keys(props.inputs[ticker]).map((value) => {
            return (
                <div>
                    <label style={{display: "block"}}>{formatLabel(value)}</label>
                    <InputText value={tempInputs[ticker][value]}
                        onChange={(event) => handleTextChange(event, ticker, value)}/>
                </div>
            );
        })
        return (
            <AccordionTab header={formatTab(ticker)} >
                {inner_inputs}
            </AccordionTab>
        );
    });

    return (
        <>
            <span className="p-toolbar">
                <Button icon="pi pi-trash" className="p-button-outlined p-button-secondary"
                onClick={handleScenarioDelete}
                />
                <Dropdown optionLabel="label" options={scenarioItems}
                    onChange={(event) => {
                        setChosenScenario(event.value);
                    }}
                    placeholder="Select Scenario"
                    value={chosenScenario}
                />
                <Button icon="pi pi-download" className="p-button-outlined p-button-secondary"
                onClick={loadScenario}
                />
            </span>
            <ScrollPanel style={{height: "80%"}}>
                <Accordion style={{textAlign: "left", border: 'none'}}>
                    {input_components}
                </Accordion>
            </ScrollPanel>
            <span className="p-buttonset" >
                <Button icon="pi pi-save" className="p-button-outlined p-button-secondary" 
                    onClick={() => setDisplayResponsive(true)}/> 
                <Button label="Submit" className="p-button-outlined p-button-secondary" 
                        onClick={handleSubmit} style={{marginTop: "10px"}}
                />
                <Button icon="pi pi-refresh" className="p-button-outlined p-button-secondary"
                    onClick={handleReset}
                />
            </span>
            <Dialog header="Save scenario" visible={displayResponsive} onHide={() => setDisplayResponsive(false)} breakpoints={{'960px': '75vw'}} style={{width: '50vw'}}>
                <span>
                    <InputText value={scenarioName} onChange={(event) => setScenarioName(event.target.value)}/>
                    <Button icon="pi pi-check" className="p-button-outlined p-button-secondary"
                        onClick={saveScenario}
                    />
                </span>
            </Dialog>        
        </>  
    );
}

export default InputForm;