import React from 'react'
import ReactMarkdown from 'react-markdown'
import ReactDom from 'react-dom'
import { useParams } from "react-router-dom";
import axios from 'axios';
import { useState, useEffect } from 'react';

export default function MarkdownView() {
    let params = useParams();
    
    const [markdown, setMarkdown] = useState(''); 

    useEffect(async () => {
        const response = await axios.get("http://127.0.0.1:8000/get_writeup/" + params.ticker);
        // add a space after each newline
        // replace newline with &#13;
        const markdown_fixed = response.data.writeup.replace(/(\r\n|\r|\n)/g, '&#13;');
        setMarkdown(response.data.writeup);
    });

    if(markdown === '') {
        return <div>No writeup found</div>
    }

    return <ReactMarkdown children={markdown}></ReactMarkdown>;
}
