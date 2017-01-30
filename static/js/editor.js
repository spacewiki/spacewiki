import $ from 'jquery-browserify';
import foundation from './lib/foundation/foundation';
import topbar from './lib/foundation/foundation.topbar';
import dropdown from './lib/foundation/foundation.dropdown';
import React from 'react';
import ReactDOM from 'react-dom';
import App from './components/App';

$(document).foundation();

var canvasDom = document.getElementById('canvas');

ReactDOM.render(
  <App initialConfig={GlobalConfiguration} />,
  canvasDom
);
