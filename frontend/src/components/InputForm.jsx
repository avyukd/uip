import React, { useEffect, useRef } from "react";
import {InputText} from 'primereact/inputtext';
import {Accordion, AccordionTab} from 'primereact/accordion';
import { useReducer } from "react";
import { Button } from 'primereact/button';
import { ScrollPanel } from 'primereact/scrollpanel';

const InputForm = (props) => {

    const [tempInputs, updateTempInputs] = 
        useReducer((state, updates) => ({...state, ...updates}), {});

    useEffect(() => {
        updateTempInputs(props.inputs);
    }, [props]);

    const handleTextChange = (event, ticker, label) => {
        updateTempInputs({[ticker]: {...tempInputs[ticker], 
            [label]: event.target.value}});
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
                    <label style={{display: "block"}}>{value}</label>
                    <InputText value={tempInputs[ticker][value]}
                        onChange={(event) => handleTextChange(event, ticker, value)}/>
                </div>
            );
        })
        return (
            <AccordionTab header={ticker} >
                {inner_inputs}
            </AccordionTab>
        );
    });


    return (
        <>
            <ScrollPanel style={{height: "80%"}}>
                <Accordion style={{textAlign: "left", border: 'none'}}>
                    {input_components}
                </Accordion>
            </ScrollPanel>
            <Button label="Submit" className="p-button-outlined p-button-secondary" 
                onClick={handleSubmit} 
                //center it
                style={{marginTop: "10px"}}
            />
        </>  
    );
}

export default InputForm;