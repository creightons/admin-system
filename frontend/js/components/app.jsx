import React from 'react';
import { Route, Link } from 'react-router-dom';
import Login from './login';
import Display from './display';

export default function App({ match }) {
    return (
        <div>
            <div>This is the customer facing page</div>
            <Link to={`${match.url}display`}>Display</Link>
            <br />
            <Link to={`${match.url}login`}>Login</Link>

            <Route path={`${match.url}Login`} component={Login}/>
            <Route path={`${match.url}display`} component={Display}/>
        </div>
    );
}
