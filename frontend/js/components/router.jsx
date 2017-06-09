import React from 'react';
import { BrowserRouter, Route, Link } from 'react-router-dom';
import App from './app';

export default function Router() {
    return (
        <BrowserRouter>
            <Route path='/' component={App}/>
        </BrowserRouter>
    );
}
