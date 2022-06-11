import React, { useState, useEffect } from 'react';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import axios from 'axios';

const StocksTable = (props) => {
    
    const [stocks, setStocks] = useState([]);

    useEffect(async () => {
        const response = await axios.post("http://127.0.0.1:8000/load_stocks", props.inputs);
        setStocks(response.data.stocks);
    }, [props.inputs]); 

    const formatPrice = (value) => {
        return `$${value.toFixed(2)}`;
    }

    const formatPercent = (value) => {
        return (value * 100).toFixed(2) + '%';
    }

    const discountBodyTemplate = (rowData) => {
        return formatPercent(rowData.discount);
    }

    const upsideBodyTemplate = (rowData) => {
        return formatPercent(rowData.upside);
    }

    const priceBodyTemplate = (rowData) => {
        return formatPrice(rowData.share_price);
    }

    const valueBodyTemplate = (rowData) => {
        return formatPrice(rowData.intrinsic_value);
    }

    return (
        <div>
            <div className="card">
                <DataTable value={stocks} responsiveLayout="scroll" size="small">
                    <Column field="ticker" header="Ticker"></Column>
                    <Column field="sector" header="Sector"></Column>
                    <Column field="industry" header="Industry"></Column>
                    <Column field="share_price" header="Price" body={priceBodyTemplate}></Column>
                    <Column field="intrinsic_value" header="Value" body={valueBodyTemplate}></Column>
                    <Column field="discount" header="Discount" body={discountBodyTemplate}></Column>
                    <Column field="upside" header="Upside" body={upsideBodyTemplate} sortable></Column>
                </DataTable>
            </div>
        </div>
    );
}

export default StocksTable;